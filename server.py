import asyncio
import json
import argparse
import os
import threading
import http.server
import functools
import numpy as np

from game.state import GameState
from game.engine import MoveEngine
from game.updater import GameUpdater
from ai.model import TigerNet, load_checkpoint
from ai.mcts import MCTS

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

try:
    import websockets
except ImportError:
    print("Missing dependency: pip install websockets")
    raise


def state_to_message(state, checker):
    """Convert GameState to the JSON dict the frontend expects."""
    territories = []
    for i, name in enumerate(GameState.TERRITORIES):
        offset = GameState.IDX_TERRITORIES_OFFSET + 3 * i
        fresh = bool(state.vector[offset])
        tired = bool(state.vector[offset + 1])
        fort = bool(state.vector[offset + 2])

        if fresh:
            owner, army_type = "british", "active"
        elif tired:
            owner, army_type = "british", "tired"
        elif fort:
            owner, army_type = "mysore", "fort"
        else:
            owner, army_type = "empty", "empty"

        territories.append({"name": name, "owner": owner, "armyType": army_type})

    british_cards = [bool(state.vector[GameState.IDX_BRITISH_CARDS_OFFSET + i]) for i in range(6)]
    mysore_cards = [bool(state.vector[GameState.IDX_MYSORE_CARDS_OFFSET + i]) for i in range(6)]

    result = checker.check(state)
    winner = None
    if result == WinChecker.RESULT_BRITISH_WIN:
        winner = "british"
    elif result == WinChecker.RESULT_MYSORE_WIN:
        winner = "mysore"

    return {
        "type": "STATE",
        "territories": territories,
        "britishCards": british_cards,
        "mysoreCards": mysore_cards,
        "turn": int(state.get_turn()),
        "maxTurns": 4,
        "whoToMove": GameState.WHO_TO_MOVE[state.get_who_to_move()],
        "winner": winner,
    }


def describe_move(move_idx):
    """Convert a move index to a human-readable string."""
    offset = 0
    for name, size, move_type in MoveEngine.MOVE_SPACE:
        if offset <= move_idx < offset + size:
            local = move_idx - offset
            if move_type == "node":
                return f"{name}: {GameState.TERRITORIES[local]}"
            elif move_type == "edge":
                src = MoveEngine.EDGE_SOURCES[local]
                dst = MoveEngine.EDGE_DESTS[local]
                return f"{name}: {GameState.TERRITORIES[src]} -> {GameState.TERRITORIES[dst]}"
            elif move_type == "rn_matrix":
                num_coastal = len(MoveEngine.COASTAL_INDICES)
                src = local // num_coastal
                dst = int(MoveEngine.COASTAL_INDICES[local % num_coastal])
                return f"{name}: {GameState.TERRITORIES[src]} -> {GameState.TERRITORIES[dst]}"
            elif move_type == "bcard":
                return f"{name}: {GameState.BRITISH_CARDS[local]}"
            elif move_type == "mcard":
                return f"{name}: {GameState.MYSORE_CARDS[local]}"
            else:
                return name
        offset += size
    return f"Unknown move {move_idx}"


def start_http_server(port, directory):
    """Serve frontend/ as static files on the given port."""
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=directory)
    httpd = http.server.HTTPServer(("", port), handler)
    httpd.serve_forever()


async def game_handler(websocket, model, num_simulations, delay):
    """Handle a single WebSocket connection: run AI self-play and stream states."""
    engine = MoveEngine()
    updater = GameUpdater()
    checker = WinChecker()
    mcts = MCTS(model, num_simulations=num_simulations)

    state = GameState()
    state.default_setup()

    # Send initial state
    await websocket.send(json.dumps(state_to_message(state, checker)))
    await asyncio.sleep(delay)

    game_result = 0
    move_count = 0

    print("\n=== New Game Started ===")
    print(f"MCTS simulations per move: {num_simulations}")
    print(f"Delay between moves: {delay}s\n")

    while game_result == 0:
        who = GameState.WHO_TO_MOVE[state.get_who_to_move()]
        turn = state.get_turn()

        # MCTS selects move
        move_idx, _ = mcts.select_move(state, temperature=1.0 if move_count < 15 else 0.0)
        move_count += 1

        desc = describe_move(move_idx)
        print(f"  Turn {turn} | {who:15s} | {desc}")

        # Apply move
        state, game_result, luck_info = updater.apply_move(state, move_idx)

        # Handle luck turns
        if luck_info is not None:
            state = MCTS.resolve_luck(state, luck_info)
            print(f"  {'':6s} | {'LUCK':15s} | {luck_info['player']} discards (random)")
            game_result = checker.check(state)

        # Send updated state to frontend
        msg = state_to_message(state, checker)
        try:
            await websocket.send(json.dumps(msg))
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected.")
            return

        await asyncio.sleep(delay)

        if move_count > 2000:
            game_result = -1
            break

    # Send game over
    winner = "british" if game_result == 1 else "mysore"
    print(f"\n=== Game Over: {winner.upper()} wins after {move_count} moves ===\n")

    try:
        await websocket.send(json.dumps({"type": "GAME_OVER", "winner": winner}))
    except websockets.exceptions.ConnectionClosed:
        pass


async def ws_server(model, num_simulations, delay, ws_port):
    """Run the WebSocket server."""
    async with websockets.serve(
        lambda ws: game_handler(ws, model, num_simulations, delay),
        "", ws_port
    ):
        await asyncio.Future()  # run forever


def main():
    parser = argparse.ArgumentParser(description="Tiger's Day AI Demo Server")
    parser.add_argument('--checkpoint', type=str, default=None,
                        help="Path to trained model checkpoint")
    parser.add_argument('--simulations', type=int, default=50,
                        help="MCTS simulations per move")
    parser.add_argument('--delay', type=float, default=0.8,
                        help="Seconds between moves (for watchability)")
    parser.add_argument('--port', type=int, default=8080,
                        help="HTTP server port for frontend")
    parser.add_argument('--ws-port', type=int, default=8887,
                        help="WebSocket server port")
    args = parser.parse_args()

    # Load model
    model = TigerNet()
    if args.checkpoint and os.path.exists(args.checkpoint):
        load_checkpoint(model, None, args.checkpoint)
        print(f"Loaded checkpoint: {args.checkpoint}")
    else:
        print("No checkpoint loaded — using untrained model (random play)")

    # Start HTTP server in background thread
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game", "frontend")
    http_thread = threading.Thread(
        target=start_http_server, args=(args.port, frontend_dir), daemon=True)
    http_thread.start()

    print(f"\nHTTP server:      http://localhost:{args.port}")
    print(f"WebSocket server: ws://localhost:{args.ws_port}")
    print(f"Open http://localhost:{args.port} in your browser to watch the AI play.\n")

    # Start WebSocket server
    asyncio.run(ws_server(model, args.simulations, args.delay, args.ws_port))


if __name__ == "__main__":
    main()

app = FastAPI()

# 1. Mount the game folder FIRST so the browser can access the .py files
app.mount("/game", StaticFiles(directory="game"), name="game")

# 2. Mount the frontend folder SECOND to serve your index.html
app.mount("/", StaticFiles(directory="game/frontend", html=True), name="frontend")