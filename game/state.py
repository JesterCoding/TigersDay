import numpy as np

class GameState:

    TERRITORIES = [
    "Bombay", "Hyderabad", "Madras", "Srirangapatna", "Coimbatore",
    "Pune", "Koppal", "Vizag", "Goa", "Darwar", "Anantapur",
    "Bednore", "Mangalore", "Bangalore", "Vellore", "Mahé",
    "Pondicherry", "Erode", "Trichy", "Palgautcherry", "Dindigul",
    "Travancore", "Ceylon"
    ]

    WHO_TO_MOVE = ["British Move", "Mysore Card", "British Card"]

    MYSORE_CARDS = ["Iron Rockets", "Sepoy Mutiny", "French Alliance", "Monsoon", "Cavalry Raid", "Sea Trade"]
    BRITISH_CARDS = ["Wall Breach", "Highlanders", "Royal Navy", "Divide and Rule", "Force March", "Princely States"]

    NODE_TO_IDX = {name: i for i, name in enumerate(TERRITORIES)}
    WHO_TO_MOVE_TO_IDX = {name: i for i, name in enumerate(WHO_TO_MOVE)}
    MYSORE_CARDS_TO_IDX = {name: i for i, name in enumerate(MYSORE_CARDS)}
    BRITISH_CARDS_TO_IDX = {name: i for i, name in enumerate(BRITISH_CARDS)}

    CARD_VALUE = [3, 2, 2, 1, 1, 1]

    IDX_BRITISH_CARDS_OFFSET = 0   #index where this information begins
    IDX_MYSORE_CARDS_OFFSET = 6    # 6 cards for both mysore and british
    IDX_TERRITORIES_OFFSET = 12    # 23 territories * 3D vectors = 69
    IDX_TURN_ORDER_OFFSET = 81     # 4 turns (One-hot)
    IDX_WHO_TO_MOVE_OFFSET = 85    # 3 options (One-hot)
    IDX_COMBAT_STRENGTH_OFFSET = 88 # 4 options (One-hot): Only ever stored for Mysore
    IDX_ATTACKER_OFFSET = 92    # 23x2 Attacker/Defender (One-hot)
    IDX_DEFENDER_OFFSET = 115 #Index from which Defender values start showing up

    IDX_BRITISH_CARDS = slice(IDX_BRITISH_CARDS_OFFSET, IDX_BRITISH_CARDS_OFFSET + 6)
    IDX_MYSORE_CARDS = slice(IDX_MYSORE_CARDS_OFFSET, IDX_MYSORE_CARDS_OFFSET + 6)
    IDX_TURN_ORDER = slice(IDX_TURN_ORDER_OFFSET, IDX_TURN_ORDER_OFFSET + 4)
    IDX_WHO_TO_MOVE = slice(IDX_WHO_TO_MOVE_OFFSET, IDX_WHO_TO_MOVE_OFFSET + 3)
    IDX_COMBAT_STRENGTH = slice(IDX_COMBAT_STRENGTH_OFFSET, IDX_COMBAT_STRENGTH_OFFSET + 4)
    IDX_ATTACKER = slice(IDX_ATTACKER_OFFSET, IDX_ATTACKER_OFFSET + 23)
    IDX_DEFENDER = slice(IDX_DEFENDER_OFFSET, IDX_DEFENDER_OFFSET + 23)


    def __init__(self):
        self.vector = np.zeros(138, dtype=bool)
        # store as integer behind the scenes, one hot for the AI, -1 is blank
        self._attacker = -1
        self._defender = -1
        self._card_strength = -1

    def default_setup(self):
        self.reset_cards()

        self.set_node_fresh_army("Bombay")
        self.set_node_fresh_army("Hyderabad")
        self.set_node_fresh_army("Madras")
        self.set_node_fresh_army("Travancore")

        self.set_node_fort("Darwar")
        self.set_node_fort("Bednore")
        self.set_node_fort("Mangalore")
        self.set_node_fort("Bangalore")
        self.set_node_fort("Srirangapatna")
        self.set_node_fort("Erode")
        self.set_node_fort("Coimbatore")
        self.set_node_fort("Mahé")
        self.set_node_fort("Palgautcherry")

        self.set_turn(1)
        self.set_who_to_move_by_name("British Move")

    def copy(self):
        """Crucial for MCTS: Creates a fast, deep copy of the state."""
        new_state = GameState()
        new_state.vector = np.copy(self.vector)
        return new_state

    def set_node_fresh_army(self, node):
        self.set_node_empty(node)
        self.vector[self.IDX_TERRITORIES_OFFSET + 3 * self.NODE_TO_IDX[node]] = True

    def set_node_tired_army(self, node):
        self.set_node_empty(node)
        self.vector[self.IDX_TERRITORIES_OFFSET + 3 * self.NODE_TO_IDX[node] + 1] = True

    def set_node_fort(self, node):
        self.set_node_empty(node)
        self.vector[self.IDX_TERRITORIES_OFFSET + 3 * self.NODE_TO_IDX[node] + 2] = True

    def set_node_empty(self, node):
        start_idx = self.IDX_TERRITORIES_OFFSET + 3 * self.NODE_TO_IDX[node]
        self.vector[start_idx : start_idx + 3] = False

    def clear_combat(self):
        self.attacker = -1 
        self.defender = -1
        self.card_strength =- 1

    def turn_refresh(self):
        self.turn += 1
        self.mysore_cards = True
        self.british_cards = True

    @property
    def fresh_armies(self):
        return self.vector[self.IDX_TERRITORIES_OFFSET : self.IDX_TURN_ORDER_OFFSET : 3]

    @property
    def tired_armies(self):
        return self.vector[self.IDX_TERRITORIES_OFFSET + 1 : self.IDX_TURN_ORDER_OFFSET : 3]

    @property
    def forts(self):
        return self.vector[self.IDX_TERRITORIES_OFFSET + 2 : self.IDX_TURN_ORDER_OFFSET : 3]

    @property
    def empty(self):
        return ~(self.fresh_armies | self.tired_armies | self.forts)
    
    @property
    def mysore_cards(self):
        return self.vector[self.IDX_MYSORE_CARDS]
    
    @mysore_cards.setter
    def mysore_cards(self, values):
        self.vector[self.IDX_MYSORE_CARDS] = values

    @property
    def british_cards(self):
        return self.vector[self.IDX_BRITISH_CARDS]
    
    @british_cards.setter
    def british_cards(self, values):
        self.vector[self.IDX_BRITISH_CARDS] = values

    @property
    def to_move(self):
        return np.argmax(self.vector[self.IDX_WHO_TO_MOVE])
    
    @to_move.setter
    def to_move(self, to_move_idx):
        self.vector[self.IDX_WHO_TO_MOVE] = False
        self.vector[self.IDX_WHO_TO_MOVE_OFFSET + (to_move_idx % 3)] = True

    @property
    def turn(self):
        return np.argmax(self.vector[self.IDX_TURN_ORDER]) + 1
    
    @turn.setter
    def turn(self, turn_number):
        self.vector[self.IDX_TURN_ORDER] = False
        self.vector[self.IDX_TURN_ORDER_OFFSET + (turn_number - 1)] = 1

    @property
    def attacker(self):
        return self._attacker
    
    @attacker.setter
    def attacker(self, value: int):
        self._attacker = value
        self.vector[self.IDX_ATTACKER] = False
        if value != -1:
            self.vector[self.IDX_ATTACKER_OFFSET + value] = True

    @property
    def defender(self):
        return self._defender
    
    @defender.setter
    def defender(self, value: int):
        self._defender = value
        self.vector[self.IDX_DEFENDER] = False
        if value != -1:
            self.vector[self.IDX_DEFENDER_OFFSET + value] = True
    
    @property
    def card_strength(self):
        return self._card_strength
    
    @card_strength.setter
    def card_strength(self, value: int):
        self._card_strength = value
        self.vector[self.IDX_COMBAT_STRENGTH] = False
        if value != -1:
            self.vector[self.IDX_COMBAT_STRENGTH_OFFSET + value] = True

    def __str__(self):
        str = ""
        for i in range(138):
            if self.vector[i]:
                str += "1"
            else:
                str += "0"
        return str

def main():
    default = GameState()
    default.default_setup()
    default.set_node_tired_army("Travancore")
    default.queue_combat_by_name("Travancore", "Palgautcherry")
    default.set_combat_strength(0)
    default.use_card_mysore_by_name("Iron Rockets")
    default.set_who_to_move_by_name("British Card")

    print(default)

if __name__ == "__main__":
    main()
    