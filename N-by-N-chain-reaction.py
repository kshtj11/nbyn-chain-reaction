import tkinter as tk
from tkinter import simpledialog, messagebox
import time

class Cell:
    def __init__(self):
        self.owner = None
        self.count = 0

class ChainReactionGUI:
    def __init__(self):
        self.ask_grid_size()
        if self.n is None:
            return  # User cancelled input

        self.cell_size = 60
        self.init_game()
        self.root.mainloop()

    def ask_grid_size(self):
        temp_root = tk.Tk()
        temp_root.withdraw()
        self.n = simpledialog.askinteger("Grid Size", "Enter grid size (n):", minvalue=3, maxvalue=12)
        temp_root.destroy()

    def init_game(self):
        self.grid = [[Cell() for _ in range(self.n)] for _ in range(self.n)]
        self.players = ["A", "B"]
        self.colors = {"A": "red", "B": "blue"}
        self.current_player = 0
        self.move_count = {player: 0 for player in self.players}

        self.root = tk.Tk()
        self.root.title("Chain Reaction")
        self.canvas = tk.Canvas(self.root, width=self.n * self.cell_size, height=self.n * self.cell_size)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handle_click)

        controls = tk.Frame(self.root)
        controls.pack()

        self.status = tk.Label(controls, text="", font=("Arial", 14))
        self.status.pack(side="left", padx=10)

        self.restart_button = tk.Button(controls, text="Restart", command=self.restart_game)
        self.restart_button.pack(side="right")

        self.draw_grid()
        self.update_status()

    def draw_grid(self):
        self.canvas.delete("all")
        for i in range(self.n):
            for j in range(self.n):
                x0 = j * self.cell_size
                y0 = i * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                self.canvas.create_rectangle(x0, y0, x1, y1, fill="lightgray", outline="white")

                cell = self.grid[i][j]
                if cell.count > 0:
                    color = self.colors[cell.owner]
                    r = 8
                    for k in range(cell.count):
                        cx = x0 + self.cell_size // 2 + (k % 2) * 10 - 5
                        cy = y0 + self.cell_size // 2 + (k // 2) * 10 - 5
                        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=color, outline="")

    def handle_click(self, event):
        if self.is_game_over():
            return

        row, col = self.get_cell_coords(event)
        if not (0 <= row < self.n and 0 <= col < self.n):
            return

        cell = self.grid[row][col]
        player = self.players[self.current_player]

        if cell.owner not in (None, player):
            return  # Invalid move

        # Place orb
        cell.owner = player
        cell.count += 1
        self.move_count[player] += 1

        self.resolve_chain_reaction(row, col)
        self.draw_grid()
        self.root.update()
        self.update_status()

        if not self.is_game_over():
            self.current_player = 1 - self.current_player
            self.update_status()
        else:
            winner = self.get_remaining_player()
            self.status.config(text=f"Game Over! Winner: Player {winner}")
            messagebox.showinfo("Game Over", f"Winner: Player {winner}")

    def get_cell_coords(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        return row, col

    def critical_mass(self, x, y):
        return len(self.get_neighbors(x, y))

    def get_neighbors(self, x, y):
        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        return [(x+dx, y+dy) for dx, dy in directions if 0 <= x+dx < self.n and 0 <= y+dy < self.n]

    def resolve_chain_reaction(self, x, y):
        queue = [(x, y)]
        exploded_this_turn = set()

        while queue:
            cx, cy = queue.pop(0)
            if (cx, cy) in exploded_this_turn:
                continue  # Already exploded in this turn

            cell = self.grid[cx][cy]
            if cell.count < self.critical_mass(cx, cy):
                continue

            # Explosion
            owner = cell.owner
            cell.count -= self.critical_mass(cx, cy)
            if cell.count == 0:
                cell.owner = None
            exploded_this_turn.add((cx, cy))

            for nx, ny in self.get_neighbors(cx, cy):
                if (nx, ny) in exploded_this_turn:
                    continue  # No backflow into already exploded cell

                neighbor = self.grid[nx][ny]
                neighbor.count += 1
                neighbor.owner = owner
                self.draw_grid()
                self.root.update()
                time.sleep(0.05)
                if neighbor.count >= self.critical_mass(nx, ny):
                    queue.append((nx, ny))


    def is_game_over(self):
        alive_players = set()
        for row in self.grid:
            for cell in row:
                if cell.owner:
                    alive_players.add(cell.owner)
        if len(alive_players) == 1 and all(count > 0 for count in self.move_count.values()):
            return True
        return False

    def get_remaining_player(self):
        for player in self.players:
            if any(cell.owner == player for row in self.grid for cell in row):
                return player
        return None

    def update_status(self):
        if not self.is_game_over():
            player = self.players[self.current_player]
            self.status.config(text=f"Player {player}'s Turn", fg=self.colors[player])

    def restart_game(self):
        self.root.destroy()
        self.init_game()

# Start the game
ChainReactionGUI()
