import numpy as np
import time
from constants import *
from state import GameState

class MoveEngine:
    
    def get_legal_moves(self, state: GameState):
        legal_dest = state.empty | state.forts

        if state.to_move == 0:
            legal_moves = (state.fresh_armies[EDGE_SOURCES] & legal_dest[EDGE_DESTS])

            trapped_army = (state.fresh_armies & (np.bincount(EDGE_SOURCES,weights=legal_moves,minlength=NODES)==0))

            phase0 = np.concatenate((
                legal_moves,
                trapped_army
            ))
        else:
            phase0 = np.zeros(101, dtype=bool)

        if state.to_move == 1:
            sepoy_mutiny = state.mysore_cards[1] * ((state.fresh_armies | state.tired_armies) & ~KEYS)

            french_alliance = state.mysore_cards[2] * (np.any(ADJACENCY_MATRIX[state.forts], axis=0) & state.empty)

            monsoon = state.mysore_cards[3] * state.fresh_armies

            cavalry_raid = np.array([state.mysore_cards[4]])

            forts_on_coast = np.dot(state.forts.astype(int),COASTAL)
            valid_trades = ~state.mysore_cards & (CARD_VALUE == forts_on_coast)
            sea_trade = state.mysore_cards[5] * valid_trades

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
            phase1 = np.zeros(101, dtype=bool)

        if state.to_move == 2:
            highlanders = state.british_cards[1] * (state.empty & COASTAL)

            royal_navy = state.british_cards[2] * np.outer((state.fresh_armies | state.tired_armies), (legal_dest & ~state.defender)[COASTAL_INDICES]).flatten()

            divide_and_rule = state.british_cards[3] * ((state.forts & ~KEYS)[EDGE_SOURCES] & state.empty[EDGE_DESTS])

            force_march = state.british_cards[4] * (state.tired_armies[EDGE_SOURCES] & (legal_dest & ~state.defender)[EDGE_DESTS])

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
            phase2 = np.zeros(434, dtype=bool)

        mask = np.concatenate((
            phase0,
            phase1,
            phase2
        ))

        return mask
    

    def print_legal_moves(self, mask):
        offset = 0
        for name, size, move_type in MOVE_SPACE:
            memory_chunk = mask[offset: offset+size]
            valid_local_moves = np.where(memory_chunk)[0]

            for idx in valid_local_moves:
                if move_type == "node":
                    node_name = INDEX_MAP[idx]
                    print(f"{name}: {node_name}")
                elif move_type == "edge":
                    src_name = INDEX_MAP[int(EDGE_SOURCES[idx])] 
                    dest_name = INDEX_MAP[int(EDGE_DESTS[idx])] 
                    print(f"{name}: {src_name} -> {dest_name}")
                elif move_type == "bcard":
                    card_name = BRITISH_CARDS[idx]
                    print(f"{name}: {card_name}")
                elif move_type == "mcard":
                    card_name = MYSORE_CARDS[idx]
                    print(f"{name}: {card_name}")
                elif move_type == "blank":
                    print(f"{name}")
                elif move_type == "rn_matrix":
                    source_node = INDEX_MAP[idx // len(COASTAL_INDICES)]
                    dest_node = INDEX_MAP[int(COASTAL_INDICES[idx % len(COASTAL_INDICES)])] 
                    print(f"{name}: {source_node} -> {dest_node}")

            
            offset += size


def main():
    a = MoveEngine()
    default = GameState()
    default.default_setup()
    default.to_move = 2
    default.mysore_cards[1:4] = False
    start_time = time.perf_counter()
    iterations = 1000000
    for _ in range(iterations):
        _ = a.get_legal_moves(default)
    end_time = time.perf_counter()
    total_time = end_time - start_time
    iters_per_sec = iterations / total_time
    
    print("-" * 30)
    print(f"Total Time: {total_time:.2f} seconds")
    print(f"Speed:      {iters_per_sec:,.0f} iterations / second")
    print("-" * 30)
    
def main2():
    a = MoveEngine()
    a.print_legal_moves([True]*636)



if __name__ == "__main__":
    main2()
