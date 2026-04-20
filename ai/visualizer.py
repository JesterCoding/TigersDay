import math
import os
import random
import torch
import numpy as np
import argparse

import game.engine as Engine
import game.updater as Updater
from game.state import GameState
from game.constants import *
from ai.mcts import MCTS
from ai.neural import AlphaTiger, load_checkpoint
from ai.train import *

def _resolve_luck_verbose(state: GameState):
    """Resolves luck and prints what happened."""
    luck_trajectory = []
    luck_branches = []
    while state.is_luck:
        outcomes = Updater.get_luck_outcomes(state)
        luck_branches.append(len(outcomes))
        idx = random.randrange(len(outcomes))
        state = outcomes[idx]
        luck_trajectory.append(idx)
        print(f"🎲 Luck resolved! Outcome index: {idx} of {len(outcomes)}")
        print(state)
    return state, luck_trajectory, luck_branches

def play_match(checkpoint_path: str, simulations: int, mode: str, human_side: str):
    """Loads a checkpoint and plays a match (AI vs AI or Human vs AI)."""
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AlphaTiger().to(device)
    
    if not os.path.exists(checkpoint_path):
        print(f"Cannot find checkpoint: {checkpoint_path}")
        return

    load_checkpoint(model, None, checkpoint_path)
    model.eval() 
    print(f"Loaded model from {checkpoint_path} onto {device}\n")

    state = GameState()
    state.default_setup()
    
    state, _ , _ = _resolve_luck_verbose(state)
    
    mcts = MCTS(model, simulations=simulations, depsilon = 0)
    # turn off dirichlet noise

    move_num = 1

    luck_branching_factors = []
    decision_branching_factors = []
    
    match_title = "AI vs AI" if mode == "ai" else f"Human ({human_side.capitalize()}) vs AI"
    print(f"=== STARTING MATCH: {match_title} ===")
    
    while Updater.get_state_winner(state) == 0:
        current_player = 'Mysore' if state.to_move == 1 else 'British'
        
        print("-" * 40)
        print(f"MOVE {move_num} | Turn: {state.turn} | To Move: {current_player}")
        print(state)

        decision_branching_factors.append(int(np.sum(Engine.get_legal_moves(state))))
        
        is_human_turn = False
        if mode == "human":
            if (human_side == "mysore" and state.to_move == 1) or \
               (human_side == "british" and state.to_move != 1):
                is_human_turn = True

        if is_human_turn:
            print("\n*** YOUR TURN ***")
            legal_mask = Engine.get_legal_moves(state)
            valid_moves = np.where(legal_mask)[0]
            
            print(f"{decision_branching_factors[-1]} Legal Moves:")
            Engine.print_legal_moves(legal_mask)
            
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
            print("\n*** AI IS PLAYING ***")
            root = mcts.search(state)
            
            best_move = None
            most_visits = -1
            best_child = None
            
            for move, child_node in root.children.items():
                if child_node.visit_count > most_visits:
                    most_visits = child_node.visit_count
                    best_child = child_node
                    best_move = move
                    
            Engine.print_legal_moves(np.arange(MOVE_VECTOR_LENGTH) == best_move)
            print(f"prior: {best_child.prior:.3f} | eval: {root.eval:+.3f}")
            print(f"(Visits: {most_visits}/{root.visit_count})")
            
        state = Updater.get_next_state(state, best_move)
        
        state, luck_history, luck_branches = _resolve_luck_verbose(state)
        luck_branching_factors.extend(luck_branches)

        mcts.update_root(best_move, luck_history)
        
        move_num += 1

    winner = Updater.get_state_winner(state)
    print("=" * 40)
    print("MATCH OVER")
    if winner == -1: 
        print("Winner: Mysore!")
    else: 
        print("Winner: British!")
    print("=" * 40)
    print(f"Game Tree Complexity: {math.prod(decision_branching_factors)}")
    print(f"Average Choices per Turn: {np.mean(decision_branching_factors):.2f}")
    print(f"Luck happened {len(luck_branching_factors)} times with {np.prod(luck_branching_factors)} Possibilities")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play against AlphaTiger or watch it play itself.")
    
    parser.add_argument(
        "--ckpt", 
        type=str, 
        default=DEFAULT_MODEL, 
        help="Path to the model checkpoint file"
    )
    parser.add_argument(
        "--sims", 
        type=int, 
        default=DEFAULT_SIMS, 
        help="Number of MCTS simulations for the AI"
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