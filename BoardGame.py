#Example Flask App for a hexaganal tile game
#Logic is in this python file

from flask import Flask, render_template, jsonify

app = Flask(__name__)

import random

# ----- GAME SETTINGS -----
BOARD_SIZE = 20

# Special spaces
SPECIAL_SPACES = {
    3: "boost",
    6: "trap",
    10: "storm",
    15: "quicksand"
}

# ----- FUNCTIONS -----

def roll_dice():
    return random.randint(1, 6)

def print_board(player_positions):
    board = ["_"] * BOARD_SIZE
    for i, pos in enumerate(player_positions):
        if pos >= BOARD_SIZE:
            board[-1] = f"P{i+1}"
        else:
            board[pos] = f"P{i+1}"
    print("Board:", " ".join(board))

def apply_special_space(position):
    if position not in SPECIAL_SPACES:
        return position, False

    event = SPECIAL_SPACES[position]
    print(f"*** SPECIAL SPACE! → {event.upper()} ***")
    skip_turn = False

    if event == "boost":
        print("Boost! Move forward +3 spaces.")
        position += 3

    elif event == "trap":
        print("Trap! Move back -2 spaces.")
        position -= 2
        if position < 0:
            position = 0

    elif event == "storm":
        print("Storm! You lose your next turn.")
        skip_turn = True

    elif event == "quicksand":
        print("Quicksand! Back to the start!")
        position = 0

    return position, skip_turn

def play_game():
    print("🎲 Welcome to the Multiplayer Dice Adventure!")
    print("Special spaces:", SPECIAL_SPACES)
    print()

    # ----- SETUP PLAYERS -----
    num_players = int(input("How many players? (2–6): "))
    player_positions = [0] * num_players
    skip_turns = [False] * num_players

    winner = None

    # ----- GAME LOOP -----
    while winner is None:
        for player in range(num_players):
            print(f"\n--- Player {player+1}'s turn ---")

            # Skip turn if needed
            if skip_turns[player]:
                print("You lose this turn (storm effect).")
                skip_turns[player] = False
                continue

            input("Press ENTER to roll the dice...")
            dice = roll_dice()
            print(f"Player {player+1} rolled: {dice}")

            # Move player
            player_positions[player] += dice
            if player_positions[player] >= BOARD_SIZE:
                winner = player
                break

            # Apply special space effects
            new_pos, skip = apply_special_space(player_positions[player])
            player_positions[player] = new_pos
            skip_turns[player] = skip

            # Print updated board
            print_board(player_positions)

    # ----- WINNER -----
    print(f"\n🎉 Player {winner+1} has reached the finish and WINS!")
if __name__ == "__main__":
    app.run(debug=True)
