import numpy as np
import math
from game.state import GameState
from game.engine import MoveEngine
from game.updater import GameUpdater


class MCTSNode:
    __slots__ = ['state', 'parent', 'parent_action', 'children',
                 'visit_count', 'total_value', 'prior', 'is_terminal',
                 'game_result', 'is_expanded']

    def __init__(self, state, parent=None, parent_action=None, prior=0.0):
        self.state = state
        self.parent = parent
        self.parent_action = parent_action
        self.children = {}              # {move_idx: MCTSNode}
        self.visit_count = 0
        self.total_value = 0.0
        self.prior = prior              # P(a|s) from neural net
        self.is_terminal = False
        self.game_result = 0
        self.is_expanded = False


class MCTS:

    def __init__(self, model, num_simulations=100, c_puct=1.5,
                 dirichlet_alpha=0.3, dirichlet_epsilon=0.25):
        self.model = model
        self.num_simulations = num_simulations
        self.c_puct = c_puct
        self.dirichlet_alpha = dirichlet_alpha
        self.dirichlet_epsilon = dirichlet_epsilon
        self.engine = MoveEngine()
        self.updater = GameUpdater()

    def search(self, root_state):
        """Run MCTS from root_state.
        Returns: 636-element policy vector (normalized visit counts).
        """
        root = MCTSNode(root_state)
        self._expand(root)
        self._add_dirichlet_noise(root)

        for _ in range(self.num_simulations):
            node = root

            # SELECT: traverse tree using PUCT
            while node.is_expanded and not node.is_terminal:
                node = self._select_child(node)

            # EXPAND & EVALUATE
            if node.is_terminal:
                value = node.game_result
            else:
                value = self._expand(node)

            # BACKUP
            self._backup(node, value)

        # Build visit count distribution
        visit_counts = np.zeros(636)
        for action, child in root.children.items():
            visit_counts[action] = child.visit_count

        total = visit_counts.sum()
        if total > 0:
            visit_counts /= total

        return visit_counts

    def select_move(self, root_state, temperature=1.0):
        """Run MCTS and select a move.
        Returns: (move_idx, mcts_policy)
        """
        mcts_policy = self.search(root_state)

        if temperature == 0:
            move = int(np.argmax(mcts_policy))
        else:
            adjusted = mcts_policy ** (1.0 / temperature)
            total = adjusted.sum()
            if total > 0:
                adjusted /= total
            else:
                # Fallback: uniform over legal moves
                legal = self.engine.get_legal_moves(root_state)
                adjusted = legal.astype(float)
                adjusted /= adjusted.sum()
            move = int(np.random.choice(636, p=adjusted))

        return move, mcts_policy

    def reuse_subtree(self, root, chosen_action):
        """Keep the subtree rooted at the chosen action's child, discard rest."""
        if chosen_action in root.children:
            child = root.children[chosen_action]
            child.parent = None
            return child
        return None

    def _select_child(self, node):
        """Select child via PUCT: Q(s,a) + c_puct * P(s,a) * sqrt(N_parent) / (1 + N_child)"""
        best_score = -float('inf')
        best_child = None
        sqrt_parent = math.sqrt(node.visit_count)

        for action, child in node.children.items():
            q_value = child.total_value / max(child.visit_count, 1)
            u_value = self.c_puct * child.prior * sqrt_parent / (1 + child.visit_count)
            score = q_value + u_value
            if score > best_score:
                best_score = score
                best_child = child

        return best_child

    def _expand(self, node):
        """Expand a leaf node. Returns the neural net value estimate."""
        legal_mask = self.engine.get_legal_moves(node.state)
        legal_indices = np.where(legal_mask)[0]

        if len(legal_indices) == 0:
            node.is_terminal = True
            node.game_result = 0
            return 0.0

        # Neural net evaluation
        policy_logits, value = self.model.predict(
            node.state.vector.astype(np.float32))

        # Mask illegal moves to -inf, then softmax for priors
        masked_logits = np.full(636, -np.inf)
        masked_logits[legal_indices] = policy_logits[legal_indices]
        max_logit = np.max(masked_logits)
        exp_logits = np.exp(masked_logits - max_logit)
        priors = exp_logits / exp_logits.sum()

        # Create child nodes for each legal move
        for action in legal_indices:
            new_state, game_result, luck_info = self.updater.apply_move(
                node.state, int(action))

            # Handle luck turns (random card discard, not saved for training)
            if luck_info is not None:
                new_state = self.resolve_luck(new_state, luck_info)

            child = MCTSNode(new_state, parent=node, parent_action=action,
                             prior=priors[action])

            if game_result != 0:
                child.is_terminal = True
                child.game_result = game_result

            node.children[int(action)] = child

        node.is_expanded = True
        return value

    def _backup(self, node, value):
        """Propagate value up the tree, flipping sign at each edge.
        Value convention: +1 = good for the player who just acted at the leaf.
        Phases alternate British(0)/Mysore(1)/British(2), so flipping at each
        edge correctly handles the perspective change.
        """
        current = node
        while current is not None:
            current.visit_count += 1
            current.total_value += value
            value = -value
            current = current.parent

    def _add_dirichlet_noise(self, root):
        """Add Dirichlet noise to root priors for exploration."""
        actions = list(root.children.keys())
        if len(actions) == 0:
            return
        noise = np.random.dirichlet([self.dirichlet_alpha] * len(actions))
        for i, action in enumerate(actions):
            root.children[action].prior = (
                (1 - self.dirichlet_epsilon) * root.children[action].prior
                + self.dirichlet_epsilon * noise[i]
            )

    @staticmethod
    def resolve_luck(state, luck_info):
        """Handle random card discard (luck turn). Not saved for training."""
        new_state = state.copy()
        player = luck_info["player"]

        if player == "mysore":
            available = np.where(new_state.vector[GameState.IDX_MYSORE_CARDS])[0]
            if len(available) > 0:
                discard = np.random.choice(available)
                new_state.use_card_mysore_by_value(int(discard))
        else:
            available = np.where(new_state.vector[GameState.IDX_BRITISH_CARDS])[0]
            if len(available) > 0:
                discard = np.random.choice(available)
                new_state.use_card_british_by_value(int(discard))

        return new_state
