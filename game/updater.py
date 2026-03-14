import numpy as np
from state import GameState
from constants import *

def main():
    default = GameState()
    default.default_setup()
    print(get_next_state(default, 227))

def get_next_state(state, move):
    #todo: optimize get_next_state function with direct indexing
    # state GSR vector, move int
    next_state = state.copy()
    offset = 0
    for name, size, move_type in MOVE_SPACE:
        if offset <= move < offset + size:
            idx = move - offset
            if move_type == "node":
                if name == "Tire":
                    next_state.set_node_tired_army(idx)
                elif name == "Sepoy Mutiny":
                    next_state.mysore_cards[1] = False
                    next_state.set_node_empty(idx)
                elif name == "French Alliance":
                    next_state.mysore_cards[2] = False
                    next_state.set_node_fort(idx)
                elif name == "Monsoon":
                    next_state.mysore_cards[3] = False
                    next_state.set_node_tired_army(idx)
                elif name == "Highlanders":
                    next_state.british_cards[1] = False
                    next_state.set_node_fresh_army(idx)
                elif name == "Princely States":
                    next_state.british_cards[5] = False
                    next_state.set_node_tired_army(idx)
            elif move_type == "edge":
                src = EDGE_SOURCES[idx]
                dest = EDGE_DESTS[idx]
                is_fort_defending = state.forts[dest]
                if name == "Move":
                    if is_fort_defending:
                        next_state.set_node_tired_army(src)
                        next_state.attacker = src
                        next_state.defender = dest
                        next_state.card_strength = 0
                    else:
                        next_state.set_node_empty(src)
                        next_state.set_node_tired_army(dest)
                elif name == "Force March":
                    next_state.british_cards[4] = False
                    if is_fort_defending:
                        # todo
                        break
                    else:
                        next_state.set_node_empty(src)
                        next_state.set_node_tired_army(dest)
                elif name == "Divide and Rule":
                    next_state.british_cards[3] = False
                    next_state.set_node_empty(src)
                    next_state.set_node_fort(dest)
            elif move_type == "bcard":
                if name == "British Power":
                    next_state.british_cards[idx] = False
                    # todo
                    break
                elif name == "Draw Wall Breach":
                    next_state.british_cards[0] = False
                    next_state.british_cards[idx] = True
                elif name == "Draw Highlanders":
                    next_state.british_cards[1] = False
                    next_state.british_cards[idx] = True
                elif name == "Draw Royal Navy":
                    next_state.british_cards[2] = False
                    next_state.british_cards[idx] = True
            elif move_type == "mcard":
                if name == "Sea Trade":
                    next_state.mysore_cards[5] = False
                    next_state.mysore_cards[idx] = True
                elif name == "Mysore Power":
                    next_state.mysore_cards[idx] = False
                    next_state.card_strength = CARD_VALUE[idx]
                elif name == "Draw Iron Rockets":
                    next_state.mysore_cards[0] = False
                    next_state.mysore_cards[idx] = True
                elif name == "Draw Sepoy Mutiny":
                    next_state.mysore_cards[1] = False
                    next_state.mysore_cards[idx] = True
                elif name == "Draw French Alliance":
                    next_state.mysore_cards[2] = False
                    next_state.mysore_cards[idx] = True
            elif move_type == "blank":
                if name == "Cavalry Raid":
                    next_state.mysore_cards[4] = False
                    # todo
                    break
                elif name == "Pass Mysore":
                    break
                elif name == "Pass British":
                    break
            elif move_type == "rn_matrix":
                next_state.british_cards[2] = False
                src = idx // len(COASTAL_INDICES)
                dest = COASTAL_INDICES[idx % len(COASTAL_INDICES)]
                is_fort_defending = state.forts[dest]
                if is_fort_defending:
                    # todo
                    break
                else:
                    is_fresh = state.fresh_armies[src]
                    next_state.set_node_empty(src)
                    if is_fresh:
                        next_state.set_node_fresh_army(dest)
                    else:
                        next_state.set_node_tired_army(dest)
                print(f"{name}: {src} -> {dest}")  

            break

        offset += size

    if state.to_move == 2:
        # resolve_battles
        if state.turn != 4 and not state.fresh_armies.any():
            next_state.turn_refresh()
    next_state.to_move += 1
    return next_state

def get_state_winner(state):
    if np.sum((state.tired_armies | state.fresh_armies) & KEYS) == 5:
        return 1
    elif state.turn == 4 and not state.fresh_armies.any() and state.to_move == 0:
        return -1
    else:
        return 0

def is_battle_won(state, defender, net_card_strength):
    #todo
    adjacent_mask = ADJACENCY_MATRIX[defender]
    return True

def resolve_battles(state, attacker, defender, net_card_strength):
    #todo
    #first battle from state, second battle from parameters
    #preserve fresh/tired state of attacker
    #check if attacker or defender moved away with FM, RN, or DR
    discards = []
    return discards

"""
1) All the cards effects + Power play by either side
2) Random discards
3) Resolve battles  
"""
if __name__ == "__main__":
    main()