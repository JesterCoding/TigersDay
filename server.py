import asyncio
import json
import websockets
import torch
import numpy as np

# Import your game engine modules
import game.engine as Engine
import game.updater as Updater
from game.state import GameState
from game.constants import *
from ai.mcts import MCTS
from ai.neural import AlphaTiger, load_checkpoint

# Configuration
PORT = 8887
CHECKPOINT_PATH = "ai/training_results/alphatigerv1.pt"
SIMULATIONS = 500
HUMAN_SIDE = 1 # Assuming 1 is British, -1 is Mysore. Adjust as needed.

class GameServer:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = AlphaTiger().to(self.device)
        load_checkpoint(self.model, None, CHECKPOINT_PATH)
        self.model.eval()
        
        self.mcts = MCTS(self.model, simulations=SIMULATIONS)
        
        # Initialize Game State
        self.state = GameState()
        self.state.default_setup()
        self._resolve_luck()

    def _resolve_luck(self):
        """Automatically resolve random events/luck before user input."""
        while getattr(self.state, 'is_luck', False):
            outcomes = Updater.get_luck_outcomes(self.state)
            # For simplicity, picking the first outcome or randomly.
            # Adjust if you want the UI to show dice rolls!
            self.state = outcomes[0] 

    def serialize_state(self):
        """
        Converts the Python GameState into the JSON format expected by script.js.
        You will need to adapt the mappings here to match your Python GameState structure.
        """
        # Example mapping: convert your Python board array/objects to the JS format
        territories_list = []
        
        # NOTE: You will need to loop through your actual Python state representation here.
        # This is pseudo-code for the translation:
        # for territory_name, data in self.state.board.items():
        #     territories_list.append({
        #         "name": territory_name,
        #         "owner": "british" if data.owner == 1 else "mysore" if data.owner == -1 else "empty",
        #         "armyType": data.army_type # 'active', 'tired', 'fort', 'empty'
        #     })

        who_to_move = "British Move" if self.state.to_move == 1 else "Mysore Move"
        winner = Updater.get_state_winner(self.state)
        
        winner_str = None
        if winner == 1: winner_str = "british"
        elif winner == -1: winner_str = "mysore"

        return {
            "type": "STATE",
            "territories": territories_list,
            "britishCards": [True] * 6, # Replace with actual card state from self.state
            "mysoreCards": [True] * 6,  # Replace with actual card state from self.state
            "turn": getattr(self.state, 'turn', 1),
            "maxTurns": 12,
            "whoToMove": who_to_move,
            "winner": winner_str
        }

    async def handle_ai_turn(self, websocket):
        """Runs the MCTS and applies the AI's move."""
        if Updater.get_state_winner(self.state) != 0:
            return # Game over

        # Tell UI AI is thinking
        await websocket.send(json.dumps({"type": "STATUS", "message": "🤖 AI is thinking..."}))
        
        # Run search
        root = self.mcts.search(self.state)
        best_move = max(root.children.items(), key=lambda item: item[1].visit_count)[0]
        
        # Apply move
        self.state = Updater.get_next_state(self.state, best_move)
        self._resolve_luck()
        self.mcts.root = None # Reset tree for next turn
        
        # Send updated state to client
        await websocket.send(json.dumps(self.serialize_state()))

    async def handler(self, websocket, path):
        print("Client connected!")
        
        # Send initial state
        await websocket.send(json.dumps(self.serialize_state()))

        # Check if AI goes first
        if self.state.to_move != HUMAN_SIDE:
            await self.handle_ai_turn(websocket)

        async for message in websocket:
            data = json.loads(message)
            
            if data['type'] == 'MOVE_IDX':
                # User submitted a move ID via the console UI
                move_idx = data['idx']
                
                legal_mask = Engine.get_legal_moves(self.state)
                valid_moves = np.where(legal_mask)[0]
                
                if move_idx in valid_moves:
                    self.state = Updater.get_next_state(self.state, move_idx)
                    self._resolve_luck()
                    
                    # Send updated state
                    await websocket.send(json.dumps(self.serialize_state()))
                    
                    # Trigger AI turn immediately if it's the AI's turn
                    if self.state.to_move != HUMAN_SIDE:
                        # Give the UI a tiny moment to render the player's move first
                        await asyncio.sleep(0.1) 
                        await self.handle_ai_turn(websocket)
                else:
                    await websocket.send(json.dumps({"type": "MOVE_RESULT", "status": "invalid", "reason": "Illegal Move ID"}))

            elif data['type'] == 'MOVE':
                # User clicked two nodes on the map: data['from'] and data['to']
                # NOTE: You must map 'from' and 'to' strings to your Engine's integer move ID here.
                # move_idx = self.map_ui_to_move_idx(data['from'], data['to'])
                pass 
                
            elif data['type'] == 'RESET':
                self.__init__() # Reset the game
                await websocket.send(json.dumps(self.serialize_state()))

async def main():
    server = GameServer()
    print(f"Starting AI WebSocket server on ws://localhost:{PORT}")
    async with websockets.serve(server.handler, "localhost", PORT):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())