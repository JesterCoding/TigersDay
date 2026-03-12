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

    # (Bombay, Hyderabad, Madras, Srirangapatna, Coimbatore)
    KEYS = np.array([0, 1, 2, 3, 4], dtype=np.int8)

    # (Bombay, Madras, Vizag, Goa, Mangalore, Mahé, Pondicherry, Travancore, Ceylon)
    COASTAL = np.array([0, 2, 7, 8, 12, 15, 16, 21, 22], dtype=np.int8)

    def __init__(self):
        self.vector = np.zeros(562, dtype=float)
    
    def mask(self, game: GameState):
        