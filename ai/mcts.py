import numpy as np
import random
import game.updater as Updater
import game.engine as Engine

class Node:
    def __init__(self, state, parent = None, move = None, prior = 0.0):
        self.state = state
        self.parent = parent
        # move to get here
        self.move = move
        self.children = {}
        
        self.visit_count = 0
        self.value_sum = 0.0
        self.prior = prior

    @property
    def eval(self):
        if self.visit_count == 0:
            return 0.0
        return self.value_sum / self.visit_count
    
    @property
    def is_expanded(self):
        return len(self.children) > 0
    
    # lazy evaluation, generate state before querying
 
    @property
    def is_luck(self):
        return self.state.is_luck
    
    # mask and normalize before this
    def expand_decision(self, action_priors):
        for move, prior in enumerate(action_priors):
            if prior > 0.0 and move not in self.children:
                self.children[move] = Node(None, self, move, prior)
                # lazy evaluation, leave game state unexplored

    def expand_luck(self):
        luck_outcomes = Updater.get_luck_outcomes(self.state)
        prior = 1.0 / len(luck_outcomes)

        for i, outcome in enumerate(luck_outcomes):
            if i not in self.children:
                self.children[i] = Node(outcome, self, i, prior)

class MCTS:
    def __init__(self, model, simulations = 100, puct = 1.5):
        self.model = model
        self.simulations = simulations
        self.puct = puct

    def search(self, root_state):
        root = Node(state=root_state)

        for _ in range(self.simulations):
            node = root

            while node.is_expanded:
                node = self.select_child(node)

            # lazy evaluation, actually do it
            if node.state == None:
                assert node.parent != None
                node.state = Updater.get_next_state(node.parent.state, node.move)
            
            reward = Updater.get_state_winner(node.state)
            if reward != 0:
                self.backpropagate(node, reward)
                # skip expansion if this is a win
                continue

            #luck is slippery
            while node.is_luck:
                if not node.is_expanded:
                    node.expand_luck()   
                node = random.choice(list(node.children.values()))

            value, raw_logits = self.model.predict(node.state)
            legal_mask = Engine.get_legal_moves(node.state)
            masked_logits = np.where(legal_mask == 1, raw_logits, -np.inf)
            max_logit = np.max(masked_logits)
            exp_logits = np.exp(masked_logits - max_logit)
            policy = exp_logits / np.sum(exp_logits)
            node.expand_decision(policy)
            self.backpropagate(node, value)
        
        return root

    def backpropagate(self, node, value):
        while node is not None:
            node.visit_count += 1
            node.value_sum += value
            node = node.parent

    def select_child(self, node):
        best_score, best_child = -np.inf, None
        for child in node.children.values():
            exploitation = child.eval
            exploration = self.puct * child.prior * (np.sqrt(node.visit_count) / (1 + child.visit_count))
            score = exploitation + exploration
            if score > best_score:
                best_score = score
                best_child = child
        assert best_child != None
        return best_child
