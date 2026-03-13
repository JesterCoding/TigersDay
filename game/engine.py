import numpy as np
from state import GameState

class MoveEngine:
    EDGE_SOURCES = np.array([
    # 0: Bombay      | 1: Hyderabad       | 2: Madras               | 3: Srirangapatna
    0, 0,              1, 1, 1,             2, 2, 2, 2,               3, 3, 3, 3,
    # 4: Coimbatore  | 5: Pune            | 6: Koppal               | 7: Vizag
    4, 4, 4, 4,        5, 5, 5, 5,          6, 6, 6, 6,               7, 7,
    # 8: Goa         | 9: Darwar          | 10: Anantapur           | 11: Bednore
    8, 8, 8, 8,        9, 9, 9,             10, 10, 10, 10,           11, 11, 11, 11,
    # 12: Mangalore  | 13: Bangalore      | 14: Vellore             | 15: Mahé
    12, 12, 12,        13, 13, 13,          14, 14, 14, 14,           15, 15, 15,
    # 16: Pondicherry| 17: Erode          | 18: Trichy              | 19: Palgautcherry
    16, 16, 16,        17, 17, 17, 17, 17,  18, 18, 18,               19, 19, 19,
    # 20: Dindigul   | 21: Travancore     | 22: Ceylon
    20, 20, 20, 20,    21, 21, 21,          22, 22
    ])

    EDGE_DESTS = np.array([
    # 0: Bombay      | 1: Hyderabad       | 2: Madras               | 3: Srirangapatna
    5, 8,              6, 7, 10,            7, 10, 14, 16,            12, 13, 15, 17,
    # 4: Coimbatore  | 5: Pune            | 6: Koppal               | 7: Vizag
    15, 17, 19, 20,    0, 6, 8, 9,          1, 5, 10, 11,             1, 2,
    # 8: Goa         | 9: Darwar          | 10: Anantapur           | 11: Bednore
    0, 5, 9, 12,       5, 8, 11,            1, 2, 6, 14,              6, 9, 12, 13,
    # 12: Mangalore  | 13: Bangalore      | 14: Vellore             | 15: Mahé
    3, 8, 11,          3, 11, 14,           2, 10, 13, 17,            3, 4, 19,
    # 16: Pondicherry| 17: Erode          | 18: Trichy              | 19: Palgautcherry
    2, 17, 18,         3, 4, 14, 16, 18,    16, 17, 20,               4, 15, 21,
    # 20: Dindigul   | 21: Travancore     | 22: Ceylon
    4, 18, 21, 22,     19, 20, 22,          20, 21
    ])

    EDGES = 78

    NODES = 23

    CARDS = 6

    INDEX_MAP = {
    0: "Bombay",
    1: "Hyderabad",
    2: "Madras",
    3: "Srirangapatna",
    4: "Coimbatore",
    5: "Pune",
    6: "Koppal",
    7: "Vizag",
    8: "Goa",
    9: "Darwar",
    10: "Anantapur",
    11: "Bednore",
    12: "Mangalore",
    13: "Bangalore",
    14: "Vellore",
    15: "Mahé",
    16: "Pondicherry",
    17: "Erode",
    18: "Trichy",
    19: "Palgautcherry",
    20: "Dindigul",
    21: "Travancore",
    22: "Ceylon"
    }

    ADJACENCY_MATRIX = np.array([
        [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0],
        [1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
    ], dtype=bool)   

    # (Bombay, Hyderabad, Madras, Srirangapatna, Coimbatore)
    KEYS = np.array([
        True,  True,  True,  True,  True,  False, False, False, 
        False, False, False, False, False, False, False, False, 
        False, False, False, False, False, False, False
    ], dtype=bool)

    # (Bombay, Madras, Vizag, Goa, Mangalore, Mahé, Pondicherry, Travancore, Ceylon)
    COASTAL = np.array([
        True,  False, True,  False, False, False, False, True,  
        True,  False, False, False, True,  False, False, True,  
        True,  False, False, False, False, True,  True
    ], dtype=bool)

    KEY_INDICES = np.where(KEYS)[0]

    COASTAL_INDICES = np.where(COASTAL)[0]

    MOVE_SPACE = [
        ("Move", EDGES, "edge"),
        ("Tire", NODES, "node"),
        ("Sepoy Mutiny", NODES, "node"),
        ("French Alliance", NODES, "node"),
        ("Monsoon", NODES, "node"),
        ("Cavalry Raid", 1, "blank"),
        ("Sea Trade", CARDS, "mcard"),
        ("Mysore Power", CARDS, "mcard"),
        ("Draw Iron Rockets", CARDS, "mcard"),
        ("Draw Sepoy Mutiny", CARDS, "mcard"),
        ("Draw French Alliance", CARDS, "mcard"),
        ("Pass Mysore", 1, "blank"),
        ("Highlanders", NODES, "node"),
        ("Royal Navy", NODES*len(COASTAL_INDICES), "rn_matrix"),
        ("Divide and Rule", EDGES, "edge"),
        ("Force March", EDGES, "edge"),
        ("Princely States", NODES, "node"),
        ("British Power", CARDS, "bcard"),
        ("Draw Wall Breach", CARDS, "bcard"),
        ("Draw Highlanders", CARDS, "bcard"),
        ("Draw Royal Navy", CARDS, "bcard"),
        ("Pass British", 1, "blank")
    ]

    def __init__(self):
        self.vector = np.zeros(636, dtype=float)
    
    def get_legal_moves(self, state: GameState):
        fresh_army=state.vector[state.IDX_TERRITORIES_OFFSET:state.IDX_TURN_ORDER_OFFSET:3]
        tired_army=state.vector[state.IDX_TERRITORIES_OFFSET+1:state.IDX_TURN_ORDER_OFFSET:3]
        fort = state.vector[state.IDX_TERRITORIES_OFFSET+2:state.IDX_TURN_ORDER_OFFSET:3]
        empty = ~(fresh_army + tired_army + fort)
        mysore_cards = state.vector[state.IDX_MYSORE_CARDS_OFFSET:state.IDX_MYSORE_CARDS_OFFSET+6]
        british_cards = state.vector[state.IDX_BRITISH_CARDS_OFFSET:state.IDX_BRITISH_CARDS_OFFSET+6]
        legal_dest = empty + fort

        is_british_move = state.vector[state.IDX_WHO_TO_MOVE_OFFSET]
        is_mysore_card = state.vector[state.IDX_WHO_TO_MOVE_OFFSET + 1]
        is_british_card = state.vector[state.IDX_WHO_TO_MOVE_OFFSET + 2]

        attacker = state.vector[state.IDX_COMBATANTS_OFFSET:state.IDX_COMBATANTS_OFFSET+self.NODES]
        defender = state.vector[state.IDX_COMBATANTS_OFFSET+self.NODES:state.IDX_COMBATANTS_OFFSET+2*self.NODES]
        is_battle = np.sum(attacker)==1

        if is_british_move:
            legal_moves = (fresh_army[self.EDGE_SOURCES] & legal_dest[self.EDGE_DESTS])

            trapped_army = (fresh_army & (np.bincount(self.EDGE_SOURCES,weights=legal_moves,minlength=self.NODES)==0))

            phase1 = np.concatenate((
                legal_moves,
                trapped_army
            ))
        else:
            phase1 = np.zeros(101, dtype=bool)

        if is_mysore_card:
            sepoy_mutiny = mysore_cards[1] * ((fresh_army + tired_army) & ~self.KEYS)

            french_alliance = mysore_cards[2] * ((fort.dot(self.ADJACENCY_MATRIX) > 0) & empty)

            monsoon = mysore_cards[3] * fresh_army

            cavalry_raid = [mysore_cards[4]]

            forts_on_coast = np.dot(fort.astype(int),self.COASTAL)
            valid_trades = ~mysore_cards & (state.CARD_VALUE == forts_on_coast)
            sea_trade = mysore_cards[5] * valid_trades

            mysore_power = mysore_cards * is_battle

            mysore3draw = np.zeros(6, dtype=bool)
            mysore21draw = np.zeros(6, dtype=bool)
            mysore22draw = np.zeros(6, dtype=bool)
            mysore3draw[1:6] = mysore_cards[0] * ~mysore_cards[1:6]
            mysore21draw[3:6] = mysore_cards[1] * ~mysore_cards[3:6]
            mysore22draw[3:6] = mysore_cards[2] * ~mysore_cards[3:6]
            mysore_draw = np.concatenate((mysore3draw,mysore21draw,mysore22draw))

            mysore_pass = [True]

            phase2 = np.concatenate((
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
            phase2 = np.zeros(101, dtype=bool)

        if is_british_card:
            highlanders = british_cards[1] * (empty & self.COASTAL)

            royal_navy = british_cards[2] * np.outer((fresh_army + tired_army), (legal_dest & ~defender)[self.COASTAL_INDICES]).flatten()

            divide_and_rule = british_cards[3] * ((fort & ~self.KEYS)[self.EDGE_SOURCES] & empty[self.EDGE_DESTS])

            force_march = british_cards[4] * (tired_army[self.EDGE_SOURCES] & (legal_dest & ~defender)[self.EDGE_DESTS])

            princely_states = british_cards[5] * (empty & self.KEYS)

            british_power = british_cards * is_battle

            british3draw = np.zeros(6, dtype=bool)
            british21draw = np.zeros(6, dtype=bool)
            british22draw = np.zeros(6, dtype=bool)
            british3draw[1:6] = british_cards[0] * ~british_cards[1:6]
            british21draw[3:6] = british_cards[1] * ~british_cards[3:6]
            british22draw[3:6] = british_cards[2] * ~british_cards[3:6]
            british_draw = np.concatenate((british3draw,british21draw,british22draw))

            british_pass = [True]

            phase3 = np.concatenate((
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
            phase3 = np.zeros(434, dtype=bool)

        mask = np.concatenate((
            phase1,
            phase2,
            phase3
        ))

        return mask
    

    def print_legal_moves(self, mask):
        offset = 0
        for name, size, move_type in MoveEngine.MOVE_SPACE:
            memory_chunk = mask[offset: offset+size]
            valid_local_moves = np.where(memory_chunk)[0]

            for idx in valid_local_moves:
                if move_type == "node":
                    node_name = self.INDEX_MAP[idx]
                    print(f"{name}: {node_name}")
                elif move_type == "edge":
                    src_name = self.INDEX_MAP[int(self.EDGE_SOURCES[idx])] 
                    dest_name = self.INDEX_MAP[int(self.EDGE_DESTS[idx])] 
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
                    source_node = self.INDEX_MAP[idx // len(self.COASTAL_INDICES)]
                    dest_node = self.INDEX_MAP[int(self.COASTAL_INDICES[idx % len(self.COASTAL_INDICES)])] 
                    print(f"{name}: {source_node} -> {dest_node}")

            
            offset += size


def main():
    a = MoveEngine()
    default = GameState()
    default.default_setup()
    default.set_who_to_move_by_name("Mysore Card")

    a.print_legal_moves(a.get_legal_moves(default))
    

if __name__ == "__main__":
    main()
