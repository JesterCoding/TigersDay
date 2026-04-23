import game.updater as Updater
from game.state import GameState
from game.constants import *

def interpret(replay_log):
    state = GameState()
    state.default_setup()

    algebraic = ""
    state_history = [state.vector.copy()]
    turn = state.turn

    for move in replay_log:
        if not state.is_luck:
            algebraic += notate(state, move) + " "
            state = Updater.get_next_state(state,move)
        else:
            state = Updater.get_luck_outcomes(state)[move]
            if len(np.where(state_history[-1] != state.vector)[0]) > 0:
                index = np.where(state_history[-1] ^ state.vector)[0][0]
                if index >= CARDS:
                    algebraic += CARDS_ABBREV[MYSORE_CARDS[index - CARDS]] + " "
                else:
                    algebraic += CARDS_ABBREV[BRITISH_CARDS[index]] + " "

        if state.turn != turn:
            algebraic += "+ "
            turn = state.turn

        state_history.append(state.vector.copy())

    algebraic += "# "
    if Updater.get_state_winner(state) == 1:
        algebraic += "1-0"
    else:
        algebraic += "0-1"

    return algebraic, state_history

def notate(state, move):
    offset = 0
    gap = ">"
    move_string = ""
    for name, size, move_type in MOVE_SPACE:
        if offset <= move < offset + size:
            idx = move - offset
            if name in CARDS_ABBREV:
                move_string += CARDS_ABBREV[name] + ":"
            if move_type == "node":
                move_string += NODES_ABBREV[idx]
                return move_string
            elif move_type == "edge":
                if state.forts[int(EDGE_DESTS[idx])]:
                    if name == "Move" or name == "Force March":
                        gap = "x"
                src_name = NODES_ABBREV[int(EDGE_SOURCES[idx])] 
                dest_name = NODES_ABBREV[int(EDGE_DESTS[idx])] 
                return move_string + src_name + gap + dest_name
            elif move_type == "bcard":
                if name == "British Power":
                    move_string += CARDS_ABBREV[BRITISH_CARDS[idx]] + ":"
                    card_name = "x"
                else:
                    card_name = CARDS_ABBREV[BRITISH_CARDS[idx]]
                return move_string + card_name
            elif move_type == "mcard":
                if name == "Mysore Power":
                    move_string += CARDS_ABBREV[MYSORE_CARDS[idx]] + ":"
                    card_name = "x"
                else:
                    card_name = CARDS_ABBREV[MYSORE_CARDS[idx]]
                return move_string + card_name
            elif move_type == "blank":
                if name == "Cavalry Raid":
                    return move_string
                else:
                    return "pass"
            elif move_type == "coastal":
                node = NODES_ABBREV[idx // len(COASTAL_INDICES)]
                coast = NODES_ABBREV[int(COASTAL_INDICES[idx % len(COASTAL_INDICES)])]
                if name == "Royal Navy":
                    if state.forts[int(COASTAL_INDICES[idx % len(COASTAL_INDICES)])]:
                        gap = "x"
                    return move_string + node + gap + coast
                elif name == "Sea Trade":
                    return move_string + coast + gap + node
        offset += size
    return "none"

if __name__ == "__main__":
    print(interpret([78, 186, 2, 776, 10, 147, 485, 80, 132, 941, 3, 442, 483, 0, 74, 444, 911, 0, 1, 461, 958, 64, 131, 939, 0, 31, 439, 483, 0, 74, 186, 2, 785, 9, 461, 957, 1, 3, 440, 909, 0, 102, 461, 958, 70, 128, 938, 1, 56, 186, 2, 911, 31, 437, 779, 1, 51, 442, 934, 0, 87, 461, 958, 86, 461, 958, 31, 439, 573, 15, 437, 781, 1, 46, 124, 958, 58, 186, 2, 934, 1])[0])