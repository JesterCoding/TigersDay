from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from game.state import GameState
from game.engine import get_legal_moves, legal_moves_dict
from game.updater import get_next_state, get_state_winner, get_luck_outcomes
from game.constants import INDEX_MAP, WHO_TO_MOVE
import random

app = FastAPI()

class MoveRequest(BaseModel):
    state_str: str
    move_idx: int

class LoadRequest(BaseModel):
    state_str: str

def generate_game_data(state: GameState):
    """Translates the Python GameState into a clean dictionary for JavaScript."""
    
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
    moves = legal_moves_dict(mask)

    return {
        "state_str": "".join(["1" if bool(x) else "0" for x in state.vector]),
        "winner": get_state_winner(state),
        "moves": moves,
        "ui_state": {
            "british_cards": [bool(x) for x in state.british_cards],
            "mysore_cards": [bool(x) for x in state.mysore_cards],
            "turn": int(state.turn),
            "who_to_move": WHO_TO_MOVE[state.to_move],
            "attacker": INDEX_MAP[state.attacker] if state.attacker != -1 else "None",
            "defender": INDEX_MAP[state.defender] if state.defender != -1 else "None",
            "card_strength": int(state.card_strength) if state.card_strength != -1 else 0,
            "nodes": nodes
        }
    }

@app.get("/api/init")
async def init_game():
    """Called when the page first loads."""
    state = GameState()
    state.default_setup()
    return generate_game_data(state)

@app.post("/api/load-state")
async def load_state(req: LoadRequest):
    """Called when the user pastes a bit-string."""
    try:
        state = GameState().read_str(req.state_str)
        return generate_game_data(state)
    except ValueError as e:
        return {"error": str(e)}

@app.post("/api/play-move")
async def play_move(req: MoveRequest):
    """Called when the user clicks a legal move."""
    try:
        state = GameState().read_str(req.state_str)
    
        state = get_next_state(state, req.move_idx)
        
        state = random.choice(get_luck_outcomes(state)) 
        state = random.choice(get_luck_outcomes(state))
        
        return generate_game_data(state)
    except Exception as e:
        return {"error": str(e)}

# May or may not need this code
#app.mount("/", StaticFiles(directory="public", html=True), name="public")