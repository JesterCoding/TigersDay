import numpy as np
import time
from game.constants import *
from game.state import GameState
    
def get_legal_moves(state: GameState):
    legal_dest = state.empty | state.forts
    if state.is_battle:
        legal_dest[state.defender] = False

    if state.to_move == 0:
        legal_moves = (state.fresh_armies[EDGE_SOURCES] & legal_dest[EDGE_DESTS])

        trapped_army = (state.fresh_armies & (np.bincount(EDGE_SOURCES,weights=legal_moves,minlength=NODES)==0))

        phase0 = np.concatenate((
            legal_moves,
            trapped_army
        ))
    else:
        phase0 = np.zeros(103, dtype=bool)

    if state.to_move == 1:
        sepoy_mutiny = state.mysore_cards[1] * ((state.fresh_armies | state.tired_armies) & ~KEYS)

        french_alliance = state.mysore_cards[2] * (np.any(ADJACENCY_MATRIX[state.forts], axis=0) & state.empty)

        monsoon = state.mysore_cards[3] * state.fresh_armies

        cavalry_raid = np.array([state.mysore_cards[4]])

        sea_trade = state.mysore_cards[5] * np.outer(state.empty, state.forts[COASTAL_INDICES]).flatten()

        mysore_power = state.mysore_cards * state.is_battle

        mysore3draw = np.zeros(6, dtype=bool)
        mysore21draw = np.zeros(6, dtype=bool)
        mysore22draw = np.zeros(6, dtype=bool)
        mysore3draw[1:6] = state.mysore_cards[0] * ~state.mysore_cards[1:6]
        mysore21draw[3:6] = state.mysore_cards[1] * ~state.mysore_cards[3:6]
        mysore22draw[3:6] = state.mysore_cards[2] * ~state.mysore_cards[3:6]
        mysore_draw = np.concatenate((mysore3draw,mysore21draw,mysore22draw))

        mysore_pass = np.array([True])

        phase1 = np.concatenate((
            sepoy_mutiny,
            french_alliance,
            monsoon,
            cavalry_raid,
            sea_trade,
            mysore_power,
            mysore_draw,
            mysore_pass
        ))
    else:
        phase1 = np.zeros(302, dtype=bool)

    if state.to_move == 2:
        highlanders = state.british_cards[1] * (state.empty & COASTAL)

        royal_navy = state.british_cards[2] * np.outer((state.fresh_armies | state.tired_armies), legal_dest[COASTAL_INDICES]).flatten()

        divide_and_rule = state.british_cards[3] * ((state.forts & ~KEYS)[EDGE_SOURCES] & state.empty[EDGE_DESTS])

        force_march = state.british_cards[4] * (state.tired_armies[EDGE_SOURCES] & legal_dest[EDGE_DESTS])

        princely_states = state.british_cards[5] * (state.empty & KEYS)

        british_power = state.british_cards * state.is_battle

        british3draw = np.zeros(6, dtype=bool)
        british21draw = np.zeros(6, dtype=bool)
        british22draw = np.zeros(6, dtype=bool)
        british3draw[1:6] = state.british_cards[0] * ~state.british_cards[1:6]
        british21draw[3:6] = state.british_cards[1] * ~state.british_cards[3:6]
        british22draw[3:6] = state.british_cards[2] * ~state.british_cards[3:6]
        british_draw = np.concatenate((british3draw,british21draw,british22draw))

        british_pass = np.array([True])

        phase2 = np.concatenate((
            highlanders,
            royal_navy,
            divide_and_rule,
            force_march,
            princely_states,
            british_power,
            british_draw,
            british_pass
        ))
    else:
        phase2 = np.zeros(438, dtype=bool)

    mask = np.concatenate((
        phase0,
        phase1,
        phase2
    ))

    return mask


def print_legal_moves(mask):
    offset = 0
    for name, size, move_type in MOVE_SPACE:
        memory_chunk = mask[offset : offset+size]
        valid_local_moves = np.where(memory_chunk)[0]

        for idx in valid_local_moves:
            number = offset + idx
            if move_type == "node":
                node_name = INDEX_MAP[idx]
                print(f"{number} {name}: {node_name}")
            elif move_type == "edge":
                src_name = INDEX_MAP[int(EDGE_SOURCES[idx])] 
                dest_name = INDEX_MAP[int(EDGE_DESTS[idx])] 
                print(f"{number} {name}: {src_name} -> {dest_name}")
            elif move_type == "bcard":
                card_name = BRITISH_CARDS[idx]
                print(f"{number} {name}: {card_name}")
            elif move_type == "mcard":
                card_name = MYSORE_CARDS[idx]
                print(f"{number} {name}: {card_name}")
            elif move_type == "blank":
                print(f"{number} {name}")
            elif move_type == "coastal":
                node = INDEX_MAP[idx // len(COASTAL_INDICES)]
                coast = INDEX_MAP[int(COASTAL_INDICES[idx % len(COASTAL_INDICES)])]
                if name == "Royal Navy":
                    print(f"{number} {name}: {node} -> {coast}")
                elif name == "Sea Trade":
                    print(f"{number} {name}: {coast} -> {node}")

        offset += size


def main():
    default = GameState()
    default.default_setup()
    default.to_move = 2
    default.set_node_fort(NODE_TO_IDX["Ceylon"])
    default.set_node_tired_army(NODE_TO_IDX["Travancore"])
    print_legal_moves(get_legal_moves(default))


if __name__ == "__main__":
    main()
