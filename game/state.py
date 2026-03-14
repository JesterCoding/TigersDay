import numpy as np
from constants import *

class GameState:

    IDX_BRITISH_CARDS_OFFSET = 0   #index where this information begins
    IDX_MYSORE_CARDS_OFFSET = 6    # 6 cards for both mysore and british
    IDX_NODES_OFFSET = 12    # 23 nodes * 3D vectors = 69
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
        self._to_move = 0
        self._turn = 1
        self._winner = 0
        self._luck = []

    def default_setup(self):
        self.mysore_cards[:] = True
        self.british_cards[:] = True

        self.set_node_fresh_army(NODE_TO_IDX["Bombay"])
        self.set_node_fresh_army(NODE_TO_IDX["Hyderabad"])
        self.set_node_fresh_army(NODE_TO_IDX["Madras"])
        self.set_node_fresh_army(NODE_TO_IDX["Travancore"])

        self.set_node_fort(NODE_TO_IDX["Darwar"])
        self.set_node_fort(NODE_TO_IDX["Bednore"])
        self.set_node_fort(NODE_TO_IDX["Mangalore"])
        self.set_node_fort(NODE_TO_IDX["Bangalore"])
        self.set_node_fort(NODE_TO_IDX["Srirangapatna"])
        self.set_node_fort(NODE_TO_IDX["Erode"])
        self.set_node_fort(NODE_TO_IDX["Coimbatore"])
        self.set_node_fort(NODE_TO_IDX["Mahé"])
        self.set_node_fort(NODE_TO_IDX["Palgautcherry"])

        self.turn = 1
        self.to_move = 0

    def copy(self):
        """Crucial for MCTS: Creates a fast, deep copy of the state."""
        new_state = GameState()
        new_state.vector = np.copy(self.vector)
        new_state._attacker = self._attacker
        new_state._defender = self._defender
        new_state._card_strength = self._card_strength
        new_state._to_move = self._to_move
        new_state._turn = self._turn
        new_state._winner = self._winner
        new_state._luck = list(self._luck)
        return new_state

    def set_node_fresh_army(self, node):
        self.set_node_empty(node)
        self.vector[self.IDX_NODES_OFFSET + 3 * node] = True

    def set_node_tired_army(self, node):
        self.set_node_empty(node)
        self.vector[self.IDX_NODES_OFFSET + 3 * node + 1] = True

    def set_node_fort(self, node):
        self.set_node_empty(node)
        self.vector[self.IDX_NODES_OFFSET + 3 * node + 2] = True

    def set_node_empty(self, node):
        start_idx = self.IDX_NODES_OFFSET + 3 * node
        self.vector[start_idx : start_idx + 3] = False

    def clear_combat(self):
        self.attacker = -1 
        self.defender = -1
        self.card_strength = -1

    @property
    def fresh_armies(self):
        return self.vector[self.IDX_NODES_OFFSET : self.IDX_TURN_ORDER_OFFSET : 3]

    @property
    def tired_armies(self):
        return self.vector[self.IDX_NODES_OFFSET + 1 : self.IDX_TURN_ORDER_OFFSET : 3]

    @property
    def forts(self):
        return self.vector[self.IDX_NODES_OFFSET + 2 : self.IDX_TURN_ORDER_OFFSET : 3]

    @property
    def empty(self):
        return ~(self.fresh_armies | self.tired_armies | self.forts)
    
    @property
    def mysore_cards(self):
        return self.vector[self.IDX_MYSORE_CARDS]

    @property
    def british_cards(self):
        return self.vector[self.IDX_BRITISH_CARDS]

    @property
    def to_move(self):
        return self._to_move
    
    @to_move.setter
    def to_move(self, to_move_idx):
        self._to_move = to_move_idx % 3
        self.vector[self.IDX_WHO_TO_MOVE] = False
        self.vector[self.IDX_WHO_TO_MOVE_OFFSET + (to_move_idx % 3)] = True

    @property
    def turn(self):
        return self._turn
    
    @turn.setter
    def turn(self, turn_number):
        self._turn = turn_number
        self.vector[self.IDX_TURN_ORDER] = False
        self.vector[self.IDX_TURN_ORDER_OFFSET + (turn_number - 1)] = True

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

    @property
    def is_battle(self):
        return self.attacker != -1
    
    def turn_refresh(self):
        self.turn += 1
        self.fresh_armies[:] = self.tired_armies
        self.tired_armies[:] = False
        self.mysore_cards[:] = True
        self.british_cards[:] = True

    def __str__(self):
        save = ""
        for i in range(138):
            if self.vector[i]:
                save += "1"
            else:
                save += "0"
        return save

def main():
    default = GameState()
    print(default)

if __name__ == "__main__":
    main()
    