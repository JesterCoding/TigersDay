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

    EDGE_MAP = {
        (src, dst): i 
        for i, (src, dst) in enumerate(zip(EDGE_SOURCES, EDGE_DESTS))
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

    def __init__(self):
        self.vector = np.zeros(568, dtype=float)
        
    def get_edge_id(cls, source, dest):
        """Returns the unique index for a directed edge, or None if no edge exists."""
        return cls.EDGE_MAP.get((source, dest))
    
    def get_legal_moves(self, state: GameState):
        fresh_army=state.vector[state.IDX_TERRITORIES_OFFSET:state.IDX_TURN_ORDER_OFFSET:3]
        tired_army=state.vector[state.IDX_TERRITORIES_OFFSET+1:state.IDX_TURN_ORDER_OFFSET:3]
        fort = state.vector[state.IDX_TERRITORIES_OFFSET+2:state.IDX_TURN_ORDER_OFFSET:3]
        empty = ~(fresh_army + tired_army + fort)

        is_british_move = state.vector[state.IDX_WHO_TO_MOVE_OFFSET]
        is_mysore_card = state.vector[state.IDX_WHO_TO_MOVE_OFFSET + 1]
        is_british_card = state.vector[state.IDX_WHO_TO_MOVE_OFFSET + 2]
        is_battle = np.sum(state.vector[state.IDX_COMBATANTS_OFFSET:state.IDX_COMBATANTS_OFFSET+23])==1

        legal_space = empty + fort
        can_move_from = fresh_army[self.EDGE_SOURCES]
        can_move_to = legal_space[self.EDGE_DESTS]
        legal_moves = (can_move_from & can_move_to) * is_british_move
        trapped_army = (fresh_army & (np.bincount(self.EDGE_SOURCES,weights=legal_moves,minlength=23)==0)) * is_british_move

        sepoy_mutiny = state.vector[state.IDX_MYSORE_CARDS_OFFSET + 1] * ((fresh_army + tired_army) & ~self.KEYS) * is_mysore_card

        french_alliance = state.vector[state.IDX_MYSORE_CARDS_OFFSET + 2] * ((fort.dot(self.ADJACENCY_MATRIX) > 0) & empty) * is_mysore_card

        monsoon = state.vector[state.IDX_MYSORE_CARDS_OFFSET + 3] * fresh_army * is_mysore_card

        cavalry_raid = [state.vector[state.IDX_MYSORE_CARDS_OFFSET + 4] * is_mysore_card]

        forts_on_coast = np.dot(fort.astype(int),self.COASTAL) * is_mysore_card
        valid_trades = ~(state.vector[state.IDX_MYSORE_CARDS_OFFSET:state.IDX_MYSORE_CARDS_OFFSET+6]) & (state.CARD_VALUE == forts_on_coast)
        sea_trade = state.vector[state.IDX_MYSORE_CARDS_OFFSET + 5] * valid_trades * is_mysore_card

        mysore_power = state.vector[state.IDX_MYSORE_CARDS_OFFSET:state.IDX_MYSORE_CARDS_OFFSET+6] * is_mysore_card * is_battle

        mysore3draw = state.vector[state.IDX_MYSORE_CARDS_OFFSET] * ~(state.vector[state.IDX_MYSORE_CARDS_OFFSET+1:state.IDX_MYSORE_CARDS_OFFSET+6])
        mysore21draw = state.vector[state.IDX_MYSORE_CARDS_OFFSET+1] * ~(state.vector[state.IDX_MYSORE_CARDS_OFFSET+3:state.IDX_MYSORE_CARDS_OFFSET+6])
        mysore22draw = state.vector[state.IDX_MYSORE_CARDS_OFFSET+2] * ~(state.vector[state.IDX_MYSORE_CARDS_OFFSET+3:state.IDX_MYSORE_CARDS_OFFSET+6])
        mysore_draw = np.concatenate((mysore3draw,mysore21draw,mysore22draw)) * is_mysore_card

        mysore_pass = [is_mysore_card]

        mask = np.concatenate((
            legal_moves,
            trapped_army,
            sepoy_mutiny,
            french_alliance,
            monsoon,
            cavalry_raid,
            sea_trade,
            mysore_power,
            mysore_draw,
            mysore_pass
            ))

        #return mask



def main():
    a = MoveEngine()
    default = GameState()
    default.default_setup()
    default.set_territory_vector_tired_army("Travancore")
    default.queue_combat_by_name("Travancore", "Palgautcherry")
    default.set_who_to_move_by_name("Mysore Card")
    default.use_card_mysore_by_name("French Alliance")
    default.use_card_mysore_by_name("Monsoon")
    #print(a.get_legal_moves(default))

    for i in range(1000):
        a.get_legal_moves(default)   

if __name__ == "__main__":
    main()
