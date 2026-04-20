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

def get_best_move(root):
    """Helper to extract the most visited move from an MCTS root."""
    best_move = None
    most_visits = -1
    best_child = None
    
    for move, child in root.children.items():
        if child.visit_count > most_visits:
            most_visits = child.visit_count
            best_child = child
            best_move = move
            
    return best_move, best_child

def play_match(ckpt_mysore: str, ckpt_british: str, sims_mysore: int, sims_british: int):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 1. Load both models separately
    model_mysore = AlphaTiger().to(device)
    model_british = AlphaTiger().to(device)
    
    if not os.path.exists(ckpt_mysore) or not os.path.exists(ckpt_british):
        print(f"Missing one or both checkpoints!\nMysore: {ckpt_mysore}\nBritish: {ckpt_british}")
        return

    load_checkpoint(model_mysore, None, ckpt_mysore)
    load_checkpoint(model_british, None, ckpt_british)
    
    model_mysore.eval()
    model_british.eval()
    print(f"Loaded Mysore AI from {ckpt_mysore}")
    print(f"Loaded British AI from {ckpt_british}")

    state = GameState()
    state.default_setup()
    state, _ , _ = _resolve_luck_verbose(state)
    
    # 2. Spin up two separate MCTS brains
    mcts_mysore = MCTS(model_mysore, simulations=sims_mysore, depsilon=0)
    mcts_british = MCTS(model_british, simulations=sims_british, depsilon=0)

    move_num = 1
    luck_branching_factors = []
    decision_branching_factors = []
    disagreement_count = 0
    
    print(f"\n=== STARTING MATCH: CLASH OF THE AIs ===")
    
    while Updater.get_state_winner(state) == 0:
        current_player = 'Mysore' if state.to_move == 1 else 'British'
        
        print("-" * 60)
        print(f"MOVE {move_num} | Turn: {state.turn} | To Move: {current_player}")
        print(state)

        decision_branching_factors.append(int(np.sum(Engine.get_legal_moves(state))))
        
        # 3. BOTH models evaluate the board
        root_mysore = mcts_mysore.search(state)
        root_british = mcts_british.search(state)
        
        move_m, child_m = get_best_move(root_mysore)
        move_b, child_b = get_best_move(root_british)
        
        # 4. Check for disagreement
        if move_m != move_b:
            disagreement_count += 1
            print("\n🚨 AIS DISAGREE ON THE BEST MOVE! 🚨")
            print(f"--> Mysore AI prefers (Eval: {root_mysore.eval:+.3f}):")
            Engine.print_legal_moves(np.arange(MOVE_VECTOR_LENGTH) == move_m)
            
            print(f"--> British AI prefers (Eval: {root_british.eval:+.3f}):")
            Engine.print_legal_moves(np.arange(MOVE_VECTOR_LENGTH) == move_b)
            print("-" * 30)
        else:
            print("\n🤝 AIs agree on the best move.")

        # 5. The actual player's AI makes the move
        if current_player == 'Mysore':
            best_move = move_m
            best_child = child_m
            active_eval = root_mysore.eval
        else:
            best_move = move_b
            best_child = child_b
            active_eval = root_british.eval
            
        print(f"\n{current_player} AI executes:")
        Engine.print_legal_moves(np.arange(MOVE_VECTOR_LENGTH) == best_move)
        print(f"prior: {best_child.prior:.3f} | eval: {active_eval:+.3f}")
            
        # 6. Execute move and resolve luck
        state = Updater.get_next_state(state, best_move)
        state, luck_history, luck_branches = _resolve_luck_verbose(state)
        luck_branching_factors.extend(luck_branches)

        # 7. CRUCIAL: Update BOTH MCTS trees so they stay on the same game path
        mcts_mysore.update_root(best_move, luck_history)
        mcts_british.update_root(best_move, luck_history)
        
        move_num += 1

    winner = Updater.get_state_winner(state)
    print("=" * 60)
    print("MATCH OVER")
    if winner == -1: 
        print("Winner: Mysore!")
    else: 
        print("Winner: British!")
    print("=" * 60)
    print(f"Total Disagreements: {disagreement_count}/{move_num - 1} turns")
    print(f"Game Tree Complexity: {math.prod(decision_branching_factors)}")
    print(f"Average Choices per Turn: {np.mean(decision_branching_factors):.2f}")
    print(f"Luck happened {len(luck_branching_factors)} times with {np.prod(luck_branching_factors)} Possibilities")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Watch two AlphaTigers fight and disagree.")
    
    parser.add_argument("--ckpt_mysore", type=str, required=True, help="Path to Mysore AI checkpoint")
    parser.add_argument("--ckpt_british", type=str, required=True, help="Path to British AI checkpoint")
    parser.add_argument("--sims_mysore", type=int, default=400, help="Number of MCTS simulations for Mysore AI")
    parser.add_argument("--sims_british", type=int, default=400, help="Number of MCTS simulations for British AI")
    
    args = parser.parse_args()
    play_match(args.ckpt_mysore, args.ckpt_british, args.sims_mysore, args.sims_british)