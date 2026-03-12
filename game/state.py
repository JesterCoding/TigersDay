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

    """
        Bombay:        { x:110, y: 74,  owner:'british', key:true,  coast:true,  labelAnchor:{anchor:'middle', dx:0,   dy:-24} },
        Hyderabad:     { x:515, y:100,  owner:'british', key:true,  coast:false, labelAnchor:{anchor:'middle', dx:0,   dy:-24} },
        Madras:        { x:618, y:322,  owner:'british', key:true,  coast:true,  labelAnchor:{anchor:'end',    dx:-18, dy:-24} },
        Srirangapatna: { x:230, y:480,  owner:'mysore',  key:true,  coast:false, labelAnchor:{anchor:'middle', dx:0,   dy:-24} },
        Coimbatore:    { x:305, y:600,  owner:'mysore',  key:true,  coast:false, labelAnchor:{anchor:'middle', dx:0,   dy:-24} },
        Pune:          { x:255, y:128,  owner:'empty',   key:false, coast:false },
        Koppal:        { x:390, y:178,  owner:'empty',   key:false, coast:false },
        Vizag:         { x:656, y:162,  owner:'empty',   key:false, coast:true,  labelAnchor:{anchor:'end',   dx:-12, dy:-16} },
        Goa:           { x: 94, y:262,  owner:'empty',   key:false, coast:true,  labelAnchor:{anchor:'start', dx: 12, dy:-16} },
        Darwar:        { x:232, y:232,  owner:'mysore',  key:false, coast:false },
        Anantapur:     { x:470, y:228,  owner:'empty',   key:false, coast:false },
        Bednore:       { x:300, y:295,  owner:'mysore',  key:false, coast:false },
        Mangalore:     { x:118, y:398,  owner:'mysore',  key:false, coast:true,  labelAnchor:{anchor:'start', dx: 12, dy:-16} },
        Bangalore:     { x:350, y:400,  owner:'mysore',  key:false, coast:false },
        Vellore:       { x:460, y:340,  owner:'empty',   key:false, coast:false },
        Mahé:          { x:145, y:586,  owner:'mysore',  key:false, coast:true,  labelAnchor:{anchor:'start', dx: 12, dy:-16} },
        Pondicherry:   { x:610, y:446,  owner:'empty',   key:false, coast:true,  labelAnchor:{anchor:'end',   dx:-12, dy:-16} },
        Erode:         { x:405, y:515,  owner:'mysore',  key:false, coast:false },
        Trichy:        { x:516, y:580,  owner:'empty',   key:false, coast:false },
        Palgautcherry: { x:248, y:680,  owner:'mysore',  key:false, coast:false },
        Dindigul:      { x:445, y:670,  owner:'empty',   key:false, coast:false },
        Travancore:    { x:260, y:830,  owner:'british', key:false, coast:true,  labelAnchor:{anchor:'start', dx: 12, dy:-16} },
        Ceylon:        { x:534, y:735,  owner:'empty',   key:false, coast:true  },
    """

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

    def set_turn(self, turn_number):
        """Sets the turn using one-hot encoding (e.g., Turn 2 -> [0, 1, 0, 0])"""

        self.vector[self.IDX_TURN_ORDER] = False
        self.vector[self.IDX_TURN_ORDER_OFFSET + (turn_number - 1)] = 1

    def get_turn(self):
        return np.argmax(self.vector[self.IDX_TURN_ORDER]) + 1
    
    def update_turn(self):
        self.set_turn(self.get_turn() + 1)
    
    def set_who_to_move_by_name(self, who_to_move):
        self.set_who_to_move_by_value(self.WHO_TO_MOVE_TO_IDX[who_to_move])

    def set_who_to_move_by_value(self, who_to_move_idx):
        self.vector[self.IDX_WHO_TO_MOVE] = False
        self.vector[self.IDX_WHO_TO_MOVE_OFFSET + (who_to_move_idx % 3)] = True

    def get_who_to_move(self):
        """Returns 0 (British), 1 (Mysore Card), or 2 (British Card)"""
        return np.argmax(self.vector[self.IDX_WHO_TO_MOVE])
    
    def update_who_to_move(self):
        self.set_who_to_move_by_value(self.get_who_to_move() + 1)

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
    