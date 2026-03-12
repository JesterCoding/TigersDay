import numpy as np

class GameState:
    def __init__(self):
        self.vector = np.zeros(138, dtype=np.bool)
        
        self.IDX_BRITISH_CARDS = slice(0, 6)
        self.IDX_MYSORE_CARDS = slice(6, 12)
        self.IDX_TERRITORIES = slice(12, 81)    # 23 territories * 3D vectors = 69
        self.IDX_TURN_ORDER = slice(81, 85)     # 4 turns (One-hot)
        self.IDX_WHO_TO_MOVE = slice(85, 88)    # 3 options (One-hot)
        self.IDX_COMBAT_STRENGTH = slice(88, 92) # 4 options (One-hot)
        self.IDX_COMBATANTS = slice(92, 138)    # 23x2 Attacker/Defender (One-hot)

    def defaultGame(self):
        self.vector[self.IDX_BRITISH_CARDS] = True
        self.vector[self.IDX_MYSORE_CARDS] = True

    def copy(self):
        """Crucial for MCTS: Creates a fast, deep copy of the state."""
        new_state = GameState()
        new_state.vector = np.copy(self.vector)
        return new_state

    # --- Helper methods to read/write without messing with raw indices ---
    def set_turn(self, turn_number):
        """Sets the turn using one-hot encoding (e.g., Turn 2 -> [0, 1, 0, 0])"""
        self.vector[self.IDX_TURN_ORDER] = 0.0
        self.vector[81 + (turn_number - 1)] = 1.0

    def get_who_to_move(self):
        """Returns 0 (British), 1 (Mysore Card), or 2 (British Card)"""
        return np.argmax(self.vector[self.IDX_WHO_TO_MOVE])