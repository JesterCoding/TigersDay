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

    TERRITORY_TO_IDX = {name: i for i, name in enumerate(TERRITORIES)}
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
    IDX_COMBATANTS_OFFSET = 92    # 23x2 Attacker/Defender (One-hot)
    IDX_COMBATANTS_DEFENDER_OFFSET = 115 #Index from which Defender values start showing up

    IDX_BRITISH_CARDS = slice(IDX_BRITISH_CARDS_OFFSET, IDX_BRITISH_CARDS_OFFSET + 6)
    IDX_MYSORE_CARDS = slice(IDX_MYSORE_CARDS_OFFSET, IDX_MYSORE_CARDS_OFFSET + 6)
    IDX_TURN_ORDER = slice(IDX_TURN_ORDER_OFFSET, IDX_TURN_ORDER_OFFSET + 4)
    IDX_WHO_TO_MOVE = slice(IDX_WHO_TO_MOVE_OFFSET, IDX_WHO_TO_MOVE_OFFSET + 3)
    IDX_COMBAT_STRENGTH = slice(IDX_COMBAT_STRENGTH_OFFSET, IDX_COMBAT_STRENGTH_OFFSET + 4)
    IDX_COMBATANTS = slice(IDX_COMBATANTS_OFFSET, IDX_COMBATANTS_OFFSET + 46)


    def __init__(self):
        self.vector = np.zeros(138, dtype=bool)

    def default_setup(self):
        self.reset_cards()

        self.set_territory_vector_fresh_army("Bombay")
        self.set_territory_vector_fresh_army("Hyderabad")
        self.set_territory_vector_fresh_army("Madras")
        self.set_territory_vector_fresh_army("Travancore")

        self.set_territory_vector_fort("Darwar")
        self.set_territory_vector_fort("Bednore")
        self.set_territory_vector_fort("Mangalore")
        self.set_territory_vector_fort("Bangalore")
        self.set_territory_vector_fort("Srirangapatna")
        self.set_territory_vector_fort("Erode")
        self.set_territory_vector_fort("Coimbatore")
        self.set_territory_vector_fort("Mahé")
        self.set_territory_vector_fort("Palgautcherry")

        self.set_turn(1)
        self.set_who_to_move_by_name("British Move")

    def copy(self):
        """Crucial for MCTS: Creates a fast, deep copy of the state."""
        new_state = GameState()
        new_state.vector = np.copy(self.vector)
        return new_state
    
    def reset_cards(self):
        self.vector[self.IDX_BRITISH_CARDS] = True
        self.vector[self.IDX_MYSORE_CARDS] = True

    def use_card_mysore_by_name(self, mysore_card):
        self.use_card_mysore_by_value(self.MYSORE_CARDS_TO_IDX[mysore_card])

    def use_card_mysore_by_value(self, mysore_card_value):
        self.vector[self.IDX_MYSORE_CARDS_OFFSET + mysore_card_value] = False

    def use_card_british_by_name(self, british_card):
        self.use_card_british_by_value(self.BRITISH_CARDS_TO_IDX[british_card])

    def use_card_british_by_value(self, british_card_value):
        self.vector[self.IDX_BRITISH_CARDS_OFFSET + british_card_value] = False

    def set_territory_vector_fresh_army(self, territory):
        self.set_territory_vector_empty(territory)
        self.vector[self.IDX_TERRITORIES_OFFSET + 3 * self.TERRITORY_TO_IDX[territory]] = True

    def set_territory_vector_tired_army(self, territory):
        self.set_territory_vector_empty(territory)
        self.vector[self.IDX_TERRITORIES_OFFSET + 3 * self.TERRITORY_TO_IDX[territory] + 1] = True

    def set_territory_vector_fort(self, territory):
        self.set_territory_vector_empty(territory)
        self.vector[self.IDX_TERRITORIES_OFFSET + 3 * self.TERRITORY_TO_IDX[territory] + 2] = True

    def set_territory_vector_empty(self, territory):
        start_idx = self.IDX_TERRITORIES_OFFSET + 3 * self.TERRITORY_TO_IDX[territory]
        self.vector[start_idx : start_idx + 3] = False
    
    def next_turn(self):
        self.turn += 1
    
    def set_who_to_move_by_name(self, who_to_move):
        self.set_who_to_move_by_value(self.WHO_TO_MOVE_TO_IDX[who_to_move])

    def set_who_to_move_by_value(self, who_to_move_idx):
        self.vector[self.IDX_WHO_TO_MOVE] = False
        self.vector[self.IDX_WHO_TO_MOVE_OFFSET + (who_to_move_idx % 3)] = True
    
    def next_to_move(self):
        self.set_who_to_move_by_value(self.to_move + 1)

    def clear_combat(self):
        self.vector[self.IDX_COMBATANTS] = False
        self.vector[self.IDX_COMBAT_STRENGTH] = False
    
    def queue_combat_by_name(self, attacker_name, defender_name):
        self.vector[self.IDX_COMBAT_STRENGTH_OFFSET] = True
        self.queue_combat_by_value(self.TERRITORY_TO_IDX[attacker_name], self.TERRITORY_TO_IDX[defender_name])

    def queue_combat_by_value(self, attacker_idx, defender_idx):
        self.vector[self.IDX_COMBATANTS_OFFSET + attacker_idx] = True
        self.vector[self.IDX_COMBATANTS_DEFENDER_OFFSET + defender_idx] = True

    def set_combat_strength(self, card_idx):
        self.vector[self.IDX_COMBAT_STRENGTH_OFFSET] = False
        self.vector[self.IDX_COMBAT_STRENGTH_OFFSET + self.CARD_VALUE[card_idx]] = True

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
    default.set_territory_vector_tired_army("Travancore")
    default.queue_combat_by_name("Travancore", "Palgautcherry")
    default.set_combat_strength(0)
    default.use_card_mysore_by_name("Iron Rockets")
    default.set_who_to_move_by_name("British Card")

    print(default)

if __name__ == "__main__":
    main()
    