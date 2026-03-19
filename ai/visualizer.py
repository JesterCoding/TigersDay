import os
import random
import torch
import numpy as np

import argparse
import game.updater as Updater
from game.state import GameState
from game.constants import *
from ai.mcts import MCTS
from ai.neural import AlphaTiger, load_checkpoint
from ai.train import *

def _resolve_luck_verbose(state: GameState):
    """Resolves luck and prints what happened."""
    luck_trajectory = []
    while state.is_luck:
        outcomes = Updater.get_luck_outcomes(state)
        idx = random.randrange(len(outcomes))
        state = outcomes[idx]
        luck_trajectory.append(idx)
        print(f"🎲 Luck resolved! Outcome index: {idx}")
        print(state)
    return state, luck_trajectory

def watch_ai_vs_ai(checkpoint_path: str, simulations: int = 500):
    """Loads a checkpoint and makes the AI play both sides."""
    
    # 1. Load the Model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AlphaTiger().to(device)
    
    if not os.path.exists(checkpoint_path):
        print(f"Cannot find checkpoint: {checkpoint_path}")
        return

    # Pass None for the optimizer since we aren't training
    load_checkpoint(model, None, checkpoint_path)
    model.eval() # CRITICAL: Turn off training mode
    print(f"Loaded model from {checkpoint_path} onto {device}\n")

    # 2. Setup the Game and MCTS
    state = GameState()
    state.default_setup()

    
    # Resolve any starting luck (e.g., initial card draws)
    state, _ = _resolve_luck_verbose(state)
    
    mcts = MCTS(model, simulations=simulations)

    move_num = 1
    
    print("=== STARTING MATCH: AI vs AI ===")
    
    # 3. The Game Loop
    while Updater.get_state_winner(state) == 0:
        print("-" * 40)
        print(f"MOVE {move_num} | Turn: {state.turn} | To Move: {'Mysore' if state.to_move == 1 else 'British'}")
        print(state)
        
        # If you have a __str__ or print_board method, call it here!
        # print(state)
        
        # Run MCTS
        root = mcts.search(state)
        
        # Temperature = 0.0 (Greedy play). Find the child with the most visits.
        best_move = None
        most_visits = -1
        
        for move, child_node in root.children.items():
            if child_node.visit_count > most_visits:
                most_visits = child_node.visit_count
                best_child = child_node
                best_move = move
        print(f"prior: {best_child.prior}")

        # Evaluate how confident the AI is (Value is between -1 and 1)
        win_chance = root.eval
        print(f"eval: {win_chance:+.3f}")
        Engine.print_legal_moves(np.arange(MOVE_VECTOR_LENGTH) == best_move)
        print(f"(Visits: {most_visits}/{simulations})")
        
        # Apply the move
        state = Updater.get_next_state(state, best_move)
        
        # Resolve any luck caused by the move
        state, luck_history = _resolve_luck_verbose(state)
        
        # Keep the MCTS tree for the next turn to save compute
        # mcts.update_root(best_move, luck_history)
        mcts.root = None
        
        move_num += 1

    # 4. Game Over
    winner = Updater.get_state_winner(state)
    print("=" * 40)
    print("MATCH OVER")
    if winner == 1: # Assuming 1 is British
        print("Winner: British!")
    elif winner == -1: # Assuming -1 is Mysore
        print("Winner: Mysore (Tipu Sultan)!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Watch AlphaTiger AI play against itself.")
    
    # Flag for the checkpoint path
    parser.add_argument(
        "--ckpt", 
        type=str, 
        default="ai/training_results/goated_ai2.pt", 
        help="Path to the model checkpoint file (e.g., checkpoints/goated_ai.pt)"
    )
    
    # Flag for the number of simulations
    parser.add_argument(
        "--sims", 
        type=int, 
        default=500, 
        help="Number of MCTS simulations per move (default: 500)"
    )
    
    args = parser.parse_args()
    
    # Run the game using the CLI arguments
    watch_ai_vs_ai(checkpoint_path=args.ckpt, simulations=args.sims)