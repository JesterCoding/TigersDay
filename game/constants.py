import numpy as np

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

ADJACENCY_MATRIX = np.zeros((NODES, NODES), dtype = bool)
ADJACENCY_MATRIX[EDGE_SOURCES, EDGE_DESTS] = True

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

WHO_TO_MOVE = ["British Move", "Mysore Card", "British Card"]

MYSORE_CARDS = ["Iron Rockets", "Sepoy Mutiny", "French Alliance", "Monsoon", "Cavalry Raid", "Sea Trade"]
BRITISH_CARDS = ["Wall Breach", "Highlanders", "Royal Navy", "Divide and Rule", "Force March", "Princely States"]

NODE_TO_IDX = {value: i for i, (_, value) in enumerate(INDEX_MAP.items())}
WHO_TO_MOVE_TO_IDX = {name: i for i, name in enumerate(WHO_TO_MOVE)}
MYSORE_CARDS_TO_IDX = {name: i for i, name in enumerate(MYSORE_CARDS)}
BRITISH_CARDS_TO_IDX = {name: i for i, name in enumerate(BRITISH_CARDS)}

CARD_VALUE = np.array([3, 2, 2, 1, 1, 1])

GAME_VECTOR_LENGTH = 138
MOVE_VECTOR_LENGTH = 636