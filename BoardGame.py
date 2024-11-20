
from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# Initialize game state
grid = [["" for _ in range(7)] for _ in range(6)]  # 6x7 grid
current_player = "Player 1"
player_colors = {"Player 1": "pink", "Player 2": "blue"}
player_names = {"Player 1": "", "Player 2": ""}

# Path to track wins
wins_file = "wins.txt"
if not os.path.exists(wins_file):
    with open(wins_file, "w") as f:
        f.write("Player 1: 0\nPlayer 2: 0\n")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/set_names", methods=["POST"])
def set_names():
    global player_names
    player_names["Player 1"] = request.form.get("player1")
    player_names["Player 2"] = request.form.get("player2")
    return jsonify({"message": "Names set successfully!"})


@app.route("/play", methods=["POST"])
def play():
    global current_player, grid

    column = int(request.json.get("column"))
    
    # Find the first available row in the selected column
    for row in range(5, -1, -1):
        if grid[row][column] == "":
            grid[row][column] = player_colors[current_player]
            break
    else:
        return jsonify({"error": "Column is full"}), 400

    # Check for steals
    for r in range(6):
        for c in range(7):
            if grid[r][c] == player_colors["Player 2"]:
                surrounding = [
                    (r + dr, c + dc)
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                    if 0 <= r + dr < 6 and 0 <= c + dc < 7
                ]
                pink_neighbors = sum(
                    grid[nr][nc] == "pink" for nr, nc in surrounding
                )
                if pink_neighbors >= 2:
                    grid[r][c] = "pink"

    # Check for a winner
    if check_winner(player_colors[current_player]):
        update_wins(current_player)
        winner = player_names[current_player]
        grid = [["" for _ in range(7)] for _ in range(6)]  # Reset grid
        return jsonify({"winner": winner})

    # Switch player
    current_player = "Player 2" if current_player == "Player 1" else "Player 1"
    return jsonify({"grid": grid})


def check_winner(color):
    # Check rows, columns, and diagonals for a 4-in-a-row
    for r in range(6):
        for c in range(7):
            if (
                c + 3 < 7
                and all(grid[r][c + i] == color for i in range(4))
                or r + 3 < 6
                and all(grid[r + i][c] == color for i in range(4))
                or r + 3 < 6
                and c + 3 < 7
                and all(grid[r + i][c + i] == color for i in range(4))
                or r + 3 < 6
                and c - 3 >= 0
                and all(grid[r + i][c - i] == color for i in range(4))
            ):
                return True
    return False


def update_wins(player):
    wins = {}
    with open(wins_file, "r") as f:
        for line in f:
            name, count = line.strip().split(": ")
            wins[name] = int(count)

    wins[player] += 1

    with open(wins_file, "w") as f:
        for name, count in wins.items():
            f.write(f"{name}: {count}\n")


if __name__ == "__main__":
    app.run(debug=True)
