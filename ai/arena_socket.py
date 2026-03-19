import asyncio
import websockets
import json
import os
import random
import argparse
import torch

import game.updater as Updater
from game.state import GameState
from ai.mcts import MCTS
from ai.neural import AlphaTiger, load_checkpoint

def get_state_binary(state: GameState) -> str:
    return "".join(["1" if bool(x) else "0" for x in state.vector])

async def handle_game(websocket, args, model):
    print("🌐 Client connected to frontend!")
    
    state = GameState()
    state.default_setup()
    mcts = MCTS(model, simulations=args.sims)
    human_side = 1 if args.human.lower() == "british" else -1
    
    async def send_state():
        await websocket.send(json.dumps({
            "type": "state",
            "binary": get_state_binary(state),
            "winner": Updater.get_state_winner(state),
            "is_luck": state.is_luck,
            "is_human_turn": (state.to_move == human_side) and not state.is_luck
        }))

    # Send initial board to kick things off
    await send_state()

    # Pure event-driven listener (No more blocked while loops!)
    async for msg in websocket:
        data = json.loads(msg)
        
        # 1. HUMAN MAKES A MOVE
        if data.get("type") == "move" and state.to_move == human_side and not state.is_luck:
            state = Updater.get_next_state(state, data["move_idx"])
            mcts.root = None # Reset AI memory for the new board
            await send_state()
            
        # 2. FRONTEND REQUESTS THE NEXT AI/LUCK STEP
        elif data.get("type") == "request_auto":
            if state.is_luck:
                # Process exactly ONE random event
                outcomes = Updater.get_luck_outcomes(state)
                state = outcomes[random.randrange(len(outcomes))]
                await send_state()
                
            elif state.to_move != human_side:
                # Process exactly ONE AI turn
                root = await asyncio.to_thread(mcts.search, state)
                best_move = max(root.children.items(), key=lambda x: x[1].visit_count)[0]
                state = Updater.get_next_state(state, best_move)
                mcts.root = None
                print(f"♟️ AI played move: {best_move}")
                await send_state()

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ckpt", type=str, required=True)
    parser.add_argument("--sims", type=int, default=1000)
    parser.add_argument("--mode", type=str, choices=["human", "ai"], default="human")
    parser.add_argument("--human", type=str, choices=["british", "mysore"], default="british")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AlphaTiger().to(device)
    load_checkpoint(model, None, args.ckpt)
    model.eval()
    
    print(f"✅ Model loaded. Ready for pure turn-based connections.")

    async with websockets.serve(lambda ws: handle_game(ws, args, model), "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())