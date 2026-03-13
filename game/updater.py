import numpy as np
from state import GameState
from engine import MoveEngine


def isMysoreWin(state):
    fresh_army=state.vector[state.IDX_TERRITORIES_OFFSET:state.IDX_TURN_ORDER_OFFSET:3]
    return state.vector[state.IDX_TURN_ORDER_OFFSET + 3] and (np.sum(fresh_army) == 0)

def isBritishWin(state):
    fresh_army=state.vector[state.IDX_TERRITORIES_OFFSET:state.IDX_TURN_ORDER_OFFSET:3]
    tired_army=state.vector[state.IDX_TERRITORIES_OFFSET+1:state.IDX_TURN_ORDER_OFFSET:3]
    return np.dot((tired_army+fresh_army).astype(int),MoveEngine.KEYS) == 5

def main():
    default = GameState()
    default.default_setup()
    default.set_territory_vector_tired_army("Travancore")
    default.set_territory_vector_tired_army("Coimbatore")
    default.set_territory_vector_tired_army("Srirangapatna")
    default.set_combat_strength(0)
    default.use_card_mysore_by_name("Iron Rockets")
    default.set_who_to_move_by_name("British Card")

    print(isMysoreWin(default))
    print(isBritishWin(default))

    default2 = GameState()
    default2.default_setup()
    default2.set_turn(4)
    print(isMysoreWin(default2))
    print(isBritishWin(default2))

    default2.set_territory_vector_tired_army("Travancore")
    default2.set_territory_vector_tired_army("Bombay")
    default2.set_territory_vector_tired_army("Madras")
    default2.set_territory_vector_tired_army("Hyderabad")

    print(isMysoreWin(default2))
    print(isBritishWin(default2))

if __name__ == "__main__":
    main()