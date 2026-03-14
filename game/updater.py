import numpy as np
from state import GameState
from engine import MoveEngine

def main():
    default = GameState()
    default.default_setup()
    get_next_state(default, 0)

def get_next_state(state, move):
    # state GSR vector, move int
    next_state = state.copy()
    offset = 0
    for name, size, move_type in MoveEngine.MOVE_SPACE:
        if offset <= move < offset + size:
            idx = move - offset
            if move_type == "node":
                if name == "Tire":
                    next_state.set_node_tired_army(idx)
                elif name == "Sepoy Mutiny":
                    next_state.set_node_empty(idx)
                elif name == "French Alliance":
                    next_state.set_node_fort(idx)
                elif name == "Monsoon":
                    next_state.set_node_tired_army(idx)
                elif name == "Highlanders":
                    next_state.set_node_fresh_army(idx)
                elif name == "Princely States":
                    next_state.set_node_tired_army(idx)
            elif move_type == "edge":
                src = MoveEngine.EDGE_SOURCES[idx]
                dest = MoveEngine.EDGE_DESTS[idx]
                is_fort_defending = state.forts[dest]
                if name == "Move":
                    if is_fort_defending:
                        next_state.attacker = src
                        next_state.defender = dest
                        next_state.card_strength = 0
                    else:
                        next_state.set_node_empty(src)
                        next_state.set_node_tired_army(dest)
                elif name == "Force March":
                    if is_fort_defending:
                        # todo
                        break
                    else:
                        next_state.set_node_empty(src)
                        next_state.set_node_tired_army(dest)
                elif name == "Divide and Rule":
                    next_state.set_node_empty(src)
                    next_state.set_node_fort(dest)
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

        if next_state.turn != 4 and not next_state.fresh_armies.any() and state.to_move == 2:
                next_state.turn_refresh()
        next_state.to_move += 1
    return next_state

def get_state_winner(state):
    if np.dot((state.tired_armies | state.fresh_armies).astype(int),MoveEngine.KEYS) == 5:
        return 1
    elif state.turn == 4 and not state.fresh_armies.any() and state.to_move == 0:
        return -1
    else:
        return 0

def is_battle_won(state, defender, net_card_strength):
    #todo
    adjacent_mask = MoveEngine.ADJACENCY_MATRIX[defender]
    return True

def resolve_battles(state, attacker, defender, net_card_strength):
    #todo
    #first battle from state, second battle from parameters
    discards = []
    return discards

if __name__ == "__main__":
    main()