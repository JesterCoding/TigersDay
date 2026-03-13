import numpy as np
from state import GameState
from engine import MoveEngine

# meant to be utilized at the end of the impulse

def isMysoreWin(state):
    fresh_army=state.vector[state.IDX_TERRITORIES_OFFSET:state.IDX_TURN_ORDER_OFFSET:3]
    return state.vector[state.IDX_TURN_ORDER_OFFSET + 3] and (np.sum(fresh_army) == 0)

def isBritishWin(state):
    fresh_army=state.vector[state.IDX_TERRITORIES_OFFSET:state.IDX_TURN_ORDER_OFFSET:3]
    tired_army=state.vector[state.IDX_TERRITORIES_OFFSET+1:state.IDX_TURN_ORDER_OFFSET:3]
    return np.dot((tired_army+fresh_army).astype(int),MoveEngine.KEYS) == 5

def main():
    default = GameState()
    default.default_setup()
    default.set_territory_vector_tired_army("Travancore")
    default.set_territory_vector_tired_army("Coimbatore")
    default.set_territory_vector_tired_army("Srirangapatna")
    default.set_combat_strength(0)
    default.use_card_mysore_by_name("Iron Rockets")
    default.set_who_to_move_by_name("British Card")

    print(isMysoreWin(default))
    print(isBritishWin(default))

    get_next_state(default, 0)

def get_next_state(state, move):
    # state GSR vector, move int
    next_state = state.copy()
    offset = 0
    for name, size, move_type in MoveEngine.MOVE_SPACE:
        if offset <= move < offset + size:
            idx = move - offset
            if move_type == "node":
                node_name = MoveEngine.INDEX_MAP[idx]
                if name == "Tire":
                    next_state.set_territory_vector_tired_army(node_name)
                elif name == "Sepoy Mutiny":
                    next_state.set_territory_vector_empty(node_name)
                elif name == "French Alliance":
                    next_state.set_territory_vector_fort(node_name)
                elif name == "Monsoon":
                    next_state.set_territory_vector_tired_army(node_name)
                elif name == "Highlanders":
                    next_state.set_territory_vector_fresh_army(node_name)
                elif name == "Princely States":
                    next_state.set_territory_vector_tired_army(node_name)
            elif move_type == "edge":
                src_name = MoveEngine.INDEX_MAP[int(MoveEngine.EDGE_SOURCES[idx])] 
                dest_name = MoveEngine.INDEX_MAP[int(MoveEngine.EDGE_DESTS[idx])] 
                print(f"{name}: {src_name} -> {dest_name}")
            elif move_type == "bcard":
                card_name = GameState.BRITISH_CARDS[idx]
                print(f"{name}: {card_name}")
            elif move_type == "mcard":
                card_name = GameState.MYSORE_CARDS[idx]
                print(f"{name}: {card_name}")
            elif move_type == "blank":
                print(f"{name}")
            elif move_type == "rn_matrix":
                source_node = MoveEngine.INDEX_MAP[idx // len(MoveEngine.COASTAL_INDICES)]
                dest_node = MoveEngine.INDEX_MAP[int(MoveEngine.COASTAL_INDICES[idx % len(MoveEngine.COASTAL_INDICES)])] 
                print(f"{name}: {source_node} -> {dest_node}")
            break
        offset += size
    return next_state

if __name__ == "__main__":
    main()