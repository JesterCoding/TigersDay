import numpy as np
import torch
import torch.optim as optim
from collections import deque
from game.state import GameState
from game.updater import GameUpdater
from game.winchecker import WinChecker
from ai.model import TigerNet, save_checkpoint, load_checkpoint
from ai.mcts import MCTS


class TrainingExample:
    __slots__ = ['state_vector', 'mcts_policy', 'outcome']

    def __init__(self, state_vector, mcts_policy, outcome=None):
        self.state_vector = state_vector    # np.array (138,)
        self.mcts_policy = mcts_policy      # np.array (636,)
        self.outcome = outcome              # float: +1 or -1 (filled after game)


class Trainer:

    DEFAULT_CONFIG = {
        'lr': 1e-3,
        'l2_reg': 1e-4,
        'buffer_size': 50000,
        'num_simulations': 100,
        'batch_size': 256,
        'num_games_per_iteration': 50,
        'num_training_steps': 100,
        'num_iterations': 100,
        'temperature_threshold': 15,
        'checkpoint_dir': 'ai/checkpoints/',
    }

    def __init__(self, config=None):
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        self.model = TigerNet()
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=self.config['lr'],
            weight_decay=self.config['l2_reg']
        )
        self.replay_buffer = deque(maxlen=self.config['buffer_size'])
        self.mcts = MCTS(self.model, num_simulations=self.config['num_simulations'])
        self.updater = GameUpdater()
        self.checker = WinChecker()

    def self_play_game(self):
        """Play one full game via self-play, collecting training examples.
        Returns list of TrainingExample (outcomes filled in at the end).
        """
        state = GameState()
        state.default_setup()

        examples = []
        move_count = 0
        game_result = 0

        while game_result == 0:
            temperature = 1.0 if move_count < self.config['temperature_threshold'] else 0.0

            move_idx, mcts_policy = self.mcts.select_move(state, temperature)

            # Save training example (outcome filled after game ends)
            examples.append(TrainingExample(
                state_vector=state.vector.astype(np.float32).copy(),
                mcts_policy=mcts_policy.copy(),
            ))

            # Apply move
            state, game_result, luck_info = self.updater.apply_move(state, move_idx)

            # Handle luck turns (not saved for training)
            if luck_info is not None:
                state = MCTS.resolve_luck(state, luck_info)
                # Re-check win after luck resolution
                game_result = self.checker.check(state)

            move_count += 1

            # Safety: prevent infinite games
            if move_count > 2000:
                game_result = -1  # Mysore wins by timeout
                break

        # Fill in outcomes based on game result
        # game_result: +1 = British win, -1 = Mysore win
        for ex in examples:
            # Determine which player was acting at this state
            who = int(np.argmax(ex.state_vector[85:88]))
            is_british = (who != 1)  # 0=British Move, 2=British Card

            if is_british:
                ex.outcome = float(game_result)
            else:
                ex.outcome = float(-game_result)

        return examples

    def train_step(self):
        """Sample a batch from replay buffer and perform one gradient step.
        Returns the loss value.
        """
        if len(self.replay_buffer) < self.config['batch_size']:
            return 0.0

        # Sample batch
        indices = np.random.choice(
            len(self.replay_buffer), self.config['batch_size'], replace=False)
        batch = [self.replay_buffer[i] for i in indices]

        states = torch.FloatTensor(np.array([ex.state_vector for ex in batch]))
        target_policies = torch.FloatTensor(np.array([ex.mcts_policy for ex in batch]))
        target_values = torch.FloatTensor(np.array([ex.outcome for ex in batch]))

        self.model.train()
        policy_logits, values = self.model(states)

        # Value loss: MSE between predicted value and actual game outcome
        value_loss = torch.mean((target_values - values) ** 2)

        # Policy loss: cross-entropy between MCTS policy and predicted policy
        log_probs = torch.log_softmax(policy_logits, dim=1)
        policy_loss = -torch.mean(torch.sum(target_policies * log_probs, dim=1))

        # Total loss (L2 regularization handled by optimizer weight_decay)
        loss = value_loss + policy_loss

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()

    def run_iteration(self, iteration_num):
        """One iteration of AlphaZero: self-play + training."""
        # Self-play phase
        print(f"Iteration {iteration_num}: Self-play...")
        for game_num in range(self.config['num_games_per_iteration']):
            examples = self.self_play_game()
            self.replay_buffer.extend(examples)
            print(f"  Game {game_num + 1}/{self.config['num_games_per_iteration']}: "
                  f"{len(examples)} moves")

        # Training phase
        print(f"Iteration {iteration_num}: Training...")
        total_loss = 0.0
        for step in range(self.config['num_training_steps']):
            loss = self.train_step()
            total_loss += loss
        avg_loss = total_loss / max(self.config['num_training_steps'], 1)
        print(f"  Avg loss: {avg_loss:.4f}")

        # Save checkpoint
        save_checkpoint(
            self.model, self.optimizer, iteration_num,
            f"{self.config['checkpoint_dir']}temp_model.pth"
        )
        print(f"  Checkpoint saved.")
