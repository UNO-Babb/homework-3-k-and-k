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

 

posEvents = ["You find some berries", "A jungle dweler spares you some food", "You have a successful hunting trip", "You catch a fish", "You discover a new kind of fruit", "You stumble across a coconut tree","A jungle dweller teaches you to identify edible plants"]

 

negEvents = ["You wake up a sleeping tiger", "While picking coconuts you discover a jaguar sleeping in the branches", "You accidentally eat some poisonous berries", "While fishing you encounter an angry hippo", "After accidentally interrupting a ritual you are chased out of a village"]

 

import random

 

posEvents = [

    "You find some berries",

    "A jungle dweller spares you some food",

    "You have a successful hunting trip",

    "You catch a fish",

    "You discover a new kind of fruit",

    "You stumble across a coconut tree",

    "A jungle dweller teaches you to identify edible plants"

]

 

negEvents = [

    "You wake up a sleeping tiger",

    "While picking coconuts you discover a jaguar sleeping in the branches",

    "You accidentally eat some poisonous berries",

    "While fishing you encounter an angry hippo",

    "After accidentally interrupting a ritual you are chased out of a village"

]

 

food = 10  

 

def update_food_file(current_food):

    """Overwrite food.txt with the latest food value."""

    with open("food.txt", "w") as f:

        f.write(f"Food: {current_food}\n")

 

def jungle_event():

    """Return a jungle event description and food change."""

   

 

    if random.random() < 0.5:

        event = random.choice(posEvents)

        food_change = random.randint(1, 3)  # gain 1–3 food

    else:

        event = random.choice(negEvents)

        food_change = -random.randint(1, 3)  # lose 1–3 food

 

    return event, food_change

 

def apply_effect(pos):

    global food

 

    name, effect = ISLAND_GRID[pos]

 

    # ---- Apply tile effect (existing code) ----

    if effect == "boost":

        new = min(pos + 3, TOTAL_TILES - 1)

        result = f"Boost! Move +3 to {new} ({ISLAND_GRID[new][0]})"

 

    elif effect == "trap":

        new = max(pos - 2, 0)

        result = f"Trap! Move -2 to {new} ({ISLAND_GRID[new][0]})"

 

    elif effect == "storm":

        return pos, True, "Storm! Lose next turn."

 

    elif effect == "quicksand":

        return 0, False, "Quicksand! Back to start."

 

    else:

        new = pos

        result = ""

 

    # ---- Add jungle event ----

    event_text, food_change = jungle_event()

    food += food_change

 

    # Save updated food to file

    update_food_file(food)

 

    # Build full description

    if food_change > 0:

        result += f"\nPositive event: {event_text} (+{food_change} food)"

    else:

        result += f"\nNegative event: {event_text} ({food_change} food)"

 

    if food <= 0:

        return new, False, f"You have run out of food and are unable to escape the jungle. Game over!"

   

    

    result += f"\nCurrent Food: {food}"

  

 

    return new, False, result

 


 

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

 

    app.run(host="0.0.0.0", port=5001)