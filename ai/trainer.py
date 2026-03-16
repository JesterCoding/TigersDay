import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

from neural import AlphaTiger, save_checkpoint
from mcts import MCTS
from game.state import GameState
import game.updater as Updater
from game.constants import MOVE_VECTOR_LENGTH

class Trainer:
    def __init__(self, model, learning_rate=0.001, mcts_simulations=100, epochs=10, batch_size=64):
        self.model = model
        self.mcts_simulations = mcts_simulations
        self.epochs = epochs
        self.batch_size = batch_size
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.value_loss_fn = nn.MSELoss()
        self.policy_loss_fn = nn.CrossEntropyLoss()

    def execute_episode(self, start_state):
        """Runs a single game of self-play starting from a specific state."""
        # Store (state_vector, action_probs, turn) — reward filled in at the end
        train_examples = []
        state = start_state  
        mcts = MCTS(self.model, simulations=self.mcts_simulations)

        while True:
            # 1. Resolve luck states — no decision to make, skip storing examples
            while state.is_luck:
                luck_outcomes = Updater.get_luck_outcomes(state)
                state = np.random.choice(luck_outcomes)

            # 2. Check if the game is over
            # get_state_winner returns +1 (British win), -1 (Mysore win), 0 (ongoing)
            reward = Updater.get_state_winner(state)
            if reward != 0:
                # Assign reward from each step's player perspective:
                # if the player who moved at that step matches the winner, they get +reward
                # otherwise they get -reward
                return [
                    (vec, policy, reward if turn == reward else -reward)
                    for vec, policy, turn in train_examples
                ]

            # 3. Run MCTS to get the improved policy
            root = mcts.search(state)

            # 4. Extract target policy from visit counts
            action_probs = np.zeros(MOVE_VECTOR_LENGTH)
            for move, child in root.children.items():
                action_probs[move] = child.visit_count
            action_probs /= np.sum(action_probs)

            # 5. Store (vector, policy, turn) — turn is +1 for British, -1 for Mysore
            #    to match the reward convention from get_state_winner
            train_examples.append((state.vector, action_probs, state.turn))

            # 6. Sample and play a move
            action = np.random.choice(len(action_probs), p=action_probs)
            state = Updater.get_next_state(state, action)

    def train(self, examples):
        """Trains the neural network on the accumulated self-play examples."""
        states, target_policies, target_values = list(zip(*examples))
        
        states = torch.tensor(np.array(states), dtype=torch.float32)
        target_policies = torch.tensor(np.array(target_policies), dtype=torch.float32)
        target_values = torch.tensor(np.array(target_values), dtype=torch.float32).unsqueeze(1)

        dataset = TensorDataset(states, target_policies, target_values)
        dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        self.model.train()

        for epoch in range(self.epochs):
            total_loss = 0.0
            for batch_states, batch_policies, batch_values in dataloader:
                self.optimizer.zero_grad()

                pred_values, pred_policy_logits = self.model(batch_states)

                value_loss = self.value_loss_fn(pred_values, batch_values)
                policy_loss = self.policy_loss_fn(pred_policy_logits, batch_policies)
                loss = value_loss + policy_loss

                loss.backward()
                self.optimizer.step()

                total_loss += loss.item()
            
            print(f"Epoch {epoch+1}/{self.epochs} - Loss: {total_loss/len(dataloader):.4f}")

    def run(self, num_iterations=50, episodes_per_iter=100, checkpoint_path="/ai/checkpoints/temp_model.pth", curriculum_generator=None):
        """Main training loop with optional curriculum learning."""
        for i in range(1, num_iterations + 1):
            print(f"\n--- Starting Iteration {i}/{num_iterations} ---")
            
            iteration_examples = []
            
            print(f"Running {episodes_per_iter} self-play episodes...")
            for e in range(episodes_per_iter):
                if curriculum_generator:
                    start_state = curriculum_generator(iteration=i, max_iterations=num_iterations)
                else:
                    start_state = GameState()
                    start_state.default_setup()
                
                iteration_examples.extend(self.execute_episode(start_state))
                
                if (e + 1) % 10 == 0:
                    print(f"Completed {e + 1} episodes...")

            print("Training model...")
            self.train(iteration_examples)

            save_checkpoint(self.model, self.optimizer, i, checkpoint_path)
            print(f"Checkpoint saved to {checkpoint_path}")