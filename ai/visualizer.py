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
from ai.train import stage_late_game

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
    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
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
    state.set_node_fort(NODE_TO_IDX["Srirangapatna"])
    state.set_node_fort(NODE_TO_IDX["Bangalore"])
    state.set_node_fort(NODE_TO_IDX["Mangalore"])
    state.set_node_fort(NODE_TO_IDX["Bednore"])

    state.set_node_fresh_army(NODE_TO_IDX["Anantapur"])
    state.set_node_fresh_army(NODE_TO_IDX["Hyderabad"])
    state.set_node_fresh_army(NODE_TO_IDX["Bombay"])
    state.set_node_fresh_army(NODE_TO_IDX["Darwar"])
    state.set_node_fresh_army(NODE_TO_IDX["Erode"])
    state.set_node_fresh_army(NODE_TO_IDX["Coimbatore"])
    state.set_node_fresh_army(NODE_TO_IDX["Palgautcherry"])

    state.turn = 3
    
    # Resolve any starting luck (e.g., initial card draws)
    state, _ = _resolve_luck_verbose(state)
    
    mcts = MCTS(model, simulations=simulations, puct=1.0) # lower PUCT for actual play

    move_num = 1
    
    print("=== STARTING MATCH: AI vs AI ===")
    print(state)
    
    # 3. The Game Loop
    while Updater.get_state_winner(state) == 0:
        print("-" * 40)
        print(f"MOVE {move_num} | Turn: {state.turn} | To Move: {'Mysore' if state.to_move == 1 else 'British'}")
        
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
                best_move = move
                
        # Evaluate how confident the AI is (Value is between -1 and 1)
        win_chance = root.eval 
        print(f"eval: {win_chance:+.3f}")
        print(f"AI chose move ID: {best_move} (Visits: {most_visits}/{simulations})")
        
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
        default="ai/training_results/ckpt_004950.pt", 
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