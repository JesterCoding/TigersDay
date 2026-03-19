import os
import random
import torch
import numpy as np
import argparse

import game.engine as Engine  # Make sure Engine is imported!
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

def play_match(checkpoint_path: str, simulations: int = 500, mode: str = "ai", human_side: str = "british"):
    """Loads a checkpoint and plays a match (AI vs AI or Human vs AI)."""
    
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
    state.set_node_empty(NODE_TO_IDX["Mahé"])
    state.set_node_empty(NODE_TO_IDX["Bednore"])
    state.set_node_fresh_army(NODE_TO_IDX["Pune"])

    
    # Resolve any starting luck (e.g., initial card draws)
    state, _ = _resolve_luck_verbose(state)
    
    mcts = MCTS(model, simulations=simulations)

    move_num = 1
    
    match_title = "AI vs AI" if mode == "ai" else f"Human ({human_side.capitalize()}) vs AI"
    print(f"=== STARTING MATCH: {match_title} ===")
    
    # 3. The Game Loop
    while Updater.get_state_winner(state) == 0:
        current_player = 'Mysore' if state.to_move == 1 else 'British'
        
        print("-" * 40)
        print(f"MOVE {move_num} | Turn: {state.turn} | To Move: {current_player}")
        print(state)
        
        # Determine if it is the human's turn
        is_human_turn = False
        if mode == "human":
            if (human_side == "mysore" and state.to_move == 1) or \
               (human_side == "british" and state.to_move != 1):
                is_human_turn = True

        if is_human_turn:
            # --- HUMAN TURN LOGIC ---
            print("\n*** YOUR TURN ***")
            legal_mask = Engine.get_legal_moves(state)
            valid_moves = np.where(legal_mask)[0]
            
            print("Legal Moves:")
            Engine.print_legal_moves(legal_mask)
            
            # Input validation loop
            while True:
                try:
                    user_input = input(f"\nEnter move ID to play (or 'q' to quit): ")
                    if user_input.lower() == 'q':
                        print("Match aborted by user.")
                        return
                        
                    chosen_move = int(user_input)
                    if chosen_move in valid_moves:
                        best_move = chosen_move
                        break
                    else:
                        print("❌ Invalid move ID. Please choose an ID from the list above.")
                except ValueError:
                    print("❌ Please enter a valid integer ID.")
                    
            print(f"\nYou played:")
            Engine.print_legal_moves(np.arange(MOVE_VECTOR_LENGTH) == best_move)
            
        else:
            # --- AI TURN LOGIC ---
            print("\n*** AI IS THINKING ***")
            root = mcts.search(state)
            
            # Temperature = 0.0 (Greedy play). Find the child with the most visits.
            best_move = None
            most_visits = -1
            best_child = None
            
            for move, child_node in root.children.items():
                if child_node.visit_count > most_visits:
                    most_visits = child_node.visit_count
                    best_child = child_node
                    best_move = move
                    
            print(f"AI prior: {best_child.prior:.4f}")
            print(f"AI eval: {root.eval:+.3f}")
            print(f"(Visits: {most_visits}/{simulations})")
            
            print(f"\nAI played:")
            Engine.print_legal_moves(np.arange(MOVE_VECTOR_LENGTH) == best_move)
            
        # Apply the move
        state = Updater.get_next_state(state, best_move)
        
        # Resolve any luck caused by the move
        state, luck_history = _resolve_luck_verbose(state)
        
        # Clear the MCTS tree for the next turn
        mcts.root = None
        
        move_num += 1

    # 4. Game Over
    winner = Updater.get_state_winner(state)
    print("=" * 40)
    print("MATCH OVER")
    if winner == 1: # Assuming 1 is Mysore
        print("Winner: Mysore (Tipu Sultan)!")
    else: 
        print("Winner: British!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play against AlphaTiger or watch it play itself.")
    
    parser.add_argument(
        "--ckpt", 
        type=str, 
        default="ai/training_results/alphatigerv1.pt", 
        help="Path to the model checkpoint file"
    )
    parser.add_argument(
        "--sims", 
        type=int, 
        default=500, 
        help="Number of MCTS simulations for the AI (default: 500)"
    )
    parser.add_argument(
        "--mode", 
        type=str, 
        choices=["ai", "human"], 
        default="ai", 
        help="Choose whether to watch AI play itself or play against it"
    )
    parser.add_argument(
        "--human", 
        type=str, 
        choices=["british", "mysore"], 
        default="british", 
        help="Which side you want to play as (only used if mode is human_vs_ai)"
    )
    
    args = parser.parse_args()
    
    play_match(
        checkpoint_path=args.ckpt, 
        simulations=args.sims, 
        mode=args.mode, 
        human_side=args.human
    )