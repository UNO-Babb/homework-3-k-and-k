from flask import Flask, render_template, request, redirect
import random

app = Flask(__name__)

# ---------------- GRID MAP ----------------
GRID_WIDTH = 5
GRID_HEIGHT = 4
TOTAL_TILES = GRID_WIDTH * GRID_HEIGHT

ISLAND_GRID = [
    ("Beach", None), ("Beach", None), ("Village Path", None), ("Village Path", None), ("Jungle", "trap"),
    ("Jungle", None), ("Bridge", None), ("River", "storm"), ("Lake Edge", "boost"), ("Lake", None),
    ("Lake", None), ("Lake", None), ("Mountain", None), ("Cave", "trap"), ("Lava Crack", "quicksand"),
    ("Volcano", None), ("Volcano Top", None), ("Cliffside", None), ("Market Road", "boost"), ("FINISH", None)
]

# ---------------- GAME STATE ----------------
game_started = False
positions = []
skip_turn = []
current_player = 0
winner = None
last_action = ""

# ---------------- EFFECTS ----------------
def apply_effect(pos):
    name, effect = ISLAND_GRID[pos]

    if effect is None:
        return pos, False, f"Landed on {name}. No effect."

    if effect == "boost":
        new = min(pos + 3, TOTAL_TILES - 1)
        return new, False, f"Boost! Move +3 to {new} ({ISLAND_GRID[new][0]})"

    if effect == "trap":
        new = max(pos - 2, 0)
        return new, False, f"Trap! Move -2 to {new} ({ISLAND_GRID[new][0]})"

    if effect == "storm":
        return pos, True, f"Storm! Lose next turn."

    if effect == "quicksand":
        return 0, False, f"Quicksand! Back to start."

    return pos, False, ""

# ---------------- ROUTES ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    global game_started, positions, skip_turn
    global current_player, winner, last_action

    # Start game
    if request.method == "POST" and "players" in request.form:
        n = int(request.form["players"])
        positions = [0] * n
        skip_turn = [False] * n
        current_player = 0
        winner = None
        last_action = ""
        game_started = True
        return redirect("/")

    # Player turn
    if request.method == "POST" and game_started and winner is None:

        if skip_turn[current_player]:
            last_action = f"Player {current_player+1} skipped a turn (storm)."
            skip_turn[current_player] = False
        else:
            roll = random.randint(1, 6)
            old_pos = positions[current_player]
            positions[current_player] += roll

            if positions[current_player] >= TOTAL_TILES - 1:
                positions[current_player] = TOTAL_TILES - 1
                winner = current_player
                last_action = f"Player {current_player+1} rolled {roll} and REACHED THE FINISH!"
            else:
                new_pos, skip, effect_msg = apply_effect(positions[current_player])
                positions[current_player] = new_pos
                skip_turn[current_player] = skip
                tile_name = ISLAND_GRID[new_pos][0]
                last_action = f"Player {current_player+1} rolled {roll}. Moved from {old_pos} to {positions[current_player]} ({tile_name}). {effect_msg}"

        current_player = (current_player + 1) % len(positions)
        return redirect("/")

    return render_template(
        "index.html",
        game_started=game_started,
        grid=ISLAND_GRID,
        width=GRID_WIDTH,
        positions=positions,
        current=current_player + 1,
        winner=winner,
        last_action=last_action
    )

# ---------------- OPEN PORT ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
