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

def parse_replay_log(filepath):
    """Reads the log file and extracts just the move lists."""
    games = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('['):
                continue
            
            moves = line.split()
            games.append(moves)        
    return games

def build_move_tree(games, max_depth=4):
    """
    Builds a tree structure tracking how many times each sequence was played.
    Structure: { 'mad>pdc': {'count': 45, 'next': { 'SM:trv': ... } } }
    """
    tree = {}
    
    for game in games:
        current_node = tree
        
        # Only look as deep as the max_depth (or the end of a short game)
        for i in range(min(max_depth, len(game))):
            move = game[i]
            
            if move not in current_node:
                current_node[move] = {"count": 0, "next": {}}
            
            # Increment the count for this specific sequence
            current_node[move]["count"] += 1
            
            # Move down into the next level of the tree
            current_node = current_node[move]["next"]
    return tree

def print_tree(tree, total_games, current_depth=1, max_depth=4, indent=""):
    """Recursively prints the tree sorted by the most popular moves."""
    
    # Sort the current branches by count (highest to lowest)
    sorted_moves = sorted(tree.items(), key=lambda item: item[1]["count"], reverse=True)
    
    for move, data in sorted_moves:
        count = data["count"]
        percentage = (count / total_games) * 100
        
        # Print the move and its stats
        print(f"{indent}Move {current_depth}: {move} [{count} games, {percentage:.1f}%]")
        
        # If we haven't hit our depth limit, dive into the responses
        if current_depth < max_depth and data["next"]:
            print_tree(data["next"], count, current_depth + 1, max_depth, indent + "    |-- ")

if __name__ == "__main__":
    filepath = 'replay_log.txt'  # Make sure this is in the same folder as the script
    
    games = parse_replay_log(filepath)
    print(f"Total Games Parsed: {len(games)}\n")
    print("OPENING RESPONSE TREE:")
    print("======================")
    
    # Set how many moves deep you want to look (4 means looking at the first 4 moves)
    depth_to_analyze = 4 
    
    move_tree = build_move_tree(games, max_depth=depth_to_analyze)
    print_tree(move_tree, total_games=len(games), max_depth=depth_to_analyze)