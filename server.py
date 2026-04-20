import os
import random
import torch
import numpy as np
import argparse
import uvicorn

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from game.engine import *
from game.updater import *
from game.state import GameState
from game.constants import INDEX_MAP, WHO_TO_MOVE
from ai.mcts import MCTS
from ai.neural import AlphaTiger, load_checkpoint


app = FastAPI()

ai_model_british = None
ai_model_mysore = None

mcts_sims = 500
match_mode = "human_vs_ai"
human_player_side = "british"
threshold = 0.1


class MoveRequest(BaseModel):
    state_str: str
    move_idx: int

class LoadRequest(BaseModel):
    state_str: str


def _resolve_luck(state: GameState) -> GameState:
    """Loops until all luck states are resolved, picking a random outcome each time."""
    """Runs in constant time since will only loop twice in the worst case scenario."""
    while state.is_luck:
        outcomes = get_luck_outcomes(state)
        idx = random.randrange(len(outcomes))
        state = outcomes[idx]
        print(f"🎲 Luck resolved — outcome index: {idx}")
    return state


def _ai_move(state: GameState) -> GameState:
    """Runs MCTS and applies the best move, then resolves any luck."""
    print("\n*** AI IS THINKING ***")
    
    current_side = str(WHO_TO_MOVE[state.to_move]).lower()
    active_model = ai_model_british if "british" in current_side else ai_model_mysore
    
    mcts = MCTS(active_model, simulations=mcts_sims, depsilon=0)
    root = mcts.search(state)

    move_idx_dict = {}
    best_move, most_visits = None, 0
    for move, child in root.children.items():
        if child.visit_count > most_visits:
            most_visits = child.visit_count
            best_move = move
        if child.visit_count/mcts.root.visit_count >= threshold:
            move_idx_dict[move] = (round(child.visit_count/mcts.root.visit_count, 3),round(float(child.prior),3))

    print("---------------------------")
    print(f"AI eval: {root.eval:+.3f}")
    print_legal_moves(np.arange(MOVE_VECTOR_LENGTH) == best_move)

    print("---------------------------")
    print(f"Moves above threshold of {threshold}")
    for move in move_idx_dict:
        print_legal_moves(np.arange(MOVE_VECTOR_LENGTH) == move)
        print(f"Visit Count, Prior: {move_idx_dict[move]}")
    print("---------------------------")    

    state = get_next_state(state, best_move)
    return _resolve_luck(state)

def generate_game_data(state: GameState) -> dict:
    """Serialises GameState into a JSON-friendly dict for the frontend."""
    nodes = []
    for i, name in enumerate(INDEX_MAP.values()):
        if state.fresh_armies[i]:
            a_type = "fresh"
        elif state.tired_armies[i]:
            a_type = "tired"
        elif state.forts[i]:
            a_type = "fort"
        else:
            a_type = "empty"
        nodes.append({"name": name, "armyType": a_type})

    mask = get_legal_moves(state)
    try:
        moves = legal_moves_dict(mask)
    except AttributeError:
        moves = {int(i): f"Move ID {i}" for i in np.where(mask)[0]}

    return {
        "state_str": "".join(["1" if bool(x) else "0" for x in state.vector]),
        "winner": get_state_winner(state),
        "moves": moves,
        "match_mode": match_mode,
        "human_side": human_player_side,
        "ui_state": {
            "british_cards": [bool(x) for x in state.british_cards],
            "mysore_cards": [bool(x) for x in state.mysore_cards],
            "turn": int(state.turn),
            "who_to_move": WHO_TO_MOVE[state.to_move],
            "attacker": INDEX_MAP.get(state.attacker, "None") if state.attacker != -1 else "None",
            "defender": INDEX_MAP.get(state.defender, "None") if state.defender != -1 else "None",
            "card_strength": int(state.card_strength) if state.card_strength != -1 else 0,
            "nodes": nodes,
        },
    }


@app.get("/api/init")
async def init_game():
    """Initialises a fresh board and resolves any opening luck states."""
    state = GameState()
    state.default_setup()
    state = _resolve_luck(state)
    return generate_game_data(state)

@app.post("/api/load-state")
async def load_state(req: LoadRequest):
    """Restores a game from a saved bit-string."""
    try:
        state = GameState().read_str(req.state_str)
        return generate_game_data(state)
    except ValueError as e:
        return {"error": str(e)}
    
@app.post("/api/play-move")
async def play_move(req: MoveRequest):
    """Executes a human move and resolves any luck states."""
    try:
        state = GameState().read_str(req.state_str)
        state = get_next_state(state, req.move_idx)
        state = _resolve_luck(state)
        return generate_game_data(state)
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/play-ai")
async def play_ai(req: LoadRequest):
    """
    Advances the game by one AI move.

    - In ai_vs_ai mode the frontend calls this repeatedly to drive both sides.
    - In human_vs_ai mode it can be called to nudge a stuck AI turn.
    - Returns an error if called in pure-human mode.
    """
    if match_mode == "human":
        return {"error": "AI moves are disabled in human-vs-human mode."}

    try:
        state = GameState().read_str(req.state_str)

        if get_state_winner(state) != 0:
            return generate_game_data(state)

        state = _ai_move(state)
        return generate_game_data(state)
    except Exception as e:
        return {"error": str(e)}


app.mount("/", StaticFiles(directory="public", html=True), name="public")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Serve the game UI. Supports human/human, human/AI, and AI/AI spectator modes."
    )
    parser.add_argument(
        "--ckpt",
        type=str,
        default="ai/models/alphatigerv8.pt",
        help="Path to the default AlphaTiger checkpoint file",
    )
    parser.add_argument(
        "--ckpt_british",
        type=str,
        default=None,
        help="Path to the checkpoint file specifically for the British AI (overrides --ckpt)",
    )
    parser.add_argument(
        "--ckpt_mysore",
        type=str,
        default=None,
        help="Path to the checkpoint file specifically for the Mysore AI (overrides --ckpt)",
    )
    parser.add_argument(
        "--sims",
        type=int,
        default=500,
        help="Number of MCTS simulations per move (default: 500)",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["human", "human_vs_ai", "ai_vs_ai"],
        default="human_vs_ai",
        help=(
            "human      — two humans take turns in the browser\n"
            "human_vs_ai — one human plays, AI responds automatically\n"
            "ai_vs_ai   — AI controls both sides; humans watch the frontend update"
        ),
    )
    parser.add_argument(
        "--human",
        type=str,
        choices=["british", "mysore"],
        default="british",
        help="Which side the human plays in human_vs_ai mode (default: british)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for the web server (default: 8000)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.1,
        help="Threshold for showing top-K AI moves",
    )

    args = parser.parse_args()

    mcts_sims = args.sims
    match_mode = args.mode
    human_player_side = args.human
    threshold = args.threshold

    if match_mode != "human":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        def load_ai(ckpt_path):
            model = AlphaTiger().to(device)
            if os.path.exists(ckpt_path):
                load_checkpoint(model, None, ckpt_path)
                model.eval()
                print(f"✅ Loaded model from {ckpt_path} onto {device}")
            else:
                print(f"⚠️  Checkpoint '{ckpt_path}' not found. AI will play with uninitialised weights.")
            return model

        # Determine which checkpoint to use for each side
        path_british = args.ckpt_british if args.ckpt_british else args.ckpt
        path_mysore = args.ckpt_mysore if args.ckpt_mysore else args.ckpt

        print("Initializing British AI...")
        ai_model_british = load_ai(path_british)

        # Optimize memory: if they point to the same path, just reference the same model object
        if path_british == path_mysore:
            print("Initializing Mysore AI... (Mirroring British AI model)")
            ai_model_mysore = ai_model_british
        else:
            print("Initializing Mysore AI...")
            ai_model_mysore = load_ai(path_mysore)
            
    else:
        print("ℹ️  Running in human-vs-human mode — AI models not loaded.")

    print(f"🚀 Starting server → http://localhost:{args.port}")
    print(f"   Mode : {match_mode}")
    if match_mode == "human_vs_ai":
        print(f"   Human side : {human_player_side}")

    uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="info")