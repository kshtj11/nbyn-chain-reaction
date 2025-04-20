import streamlit as st
import numpy as np

# Game setup
class Cell:
    def __init__(self):
        self.owner = None
        self.count = 0

@st.cache_resource
def init_grid(n):
    return [[Cell() for _ in range(n)] for _ in range(n)]

# Emoji display
def cell_display(cell):
    if cell.owner == "Blue":
        return "🔵" * cell.count
    elif cell.owner == "Red":
        return "🔴" * cell.count
    else:
        return "◻️"

def critical_mass(x, y, n):
    return len(get_neighbors(x, y, n))

def get_neighbors(x, y, n):
    directions = [(-1,0), (1,0), (0,-1), (0,1)]
    return [(x+dx, y+dy) for dx, dy in directions if 0 <= x+dx < n and 0 <= y+dy < n]

def resolve_chain_reaction(grid, x, y, player, n):
    queue = [(x, y)]
    exploded_this_turn = set()

    while queue:
        cx, cy = queue.pop(0)
        if (cx, cy) in exploded_this_turn:
            continue

        cell = grid[cx][cy]
        if cell.count < critical_mass(cx, cy, n):
            continue

        # Explosion
        cell.count -= critical_mass(cx, cy, n)
        if cell.count == 0:
            cell.owner = None
        exploded_this_turn.add((cx, cy))

        for nx, ny in get_neighbors(cx, cy, n):
            if (nx, ny) in exploded_this_turn:
                continue
            neighbor = grid[nx][ny]
            neighbor.count += 1
            neighbor.owner = player
            if neighbor.count >= critical_mass(nx, ny, n):
                queue.append((nx, ny))

def is_game_over(grid, move_count):
    alive = set()
    for row in grid:
        for cell in row:
            if cell.owner:
                alive.add(cell.owner)
    return len(alive) == 1 and all(count > 0 for count in move_count.values())

# Streamlit UI
st.title("🧨 Chain Reaction - Streamlit Edition")
n = st.sidebar.slider("Grid Size", 3, 8, 5)

if "grid" not in st.session_state or st.button("🔄 Restart Game"):
    st.session_state.grid = init_grid(n)
    st.session_state.players = ["Blue", "Red"]
    st.session_state.colors = {"Blue": "🔵", "Red": "🔴"}
    st.session_state.current_player = 0
    st.session_state.move_count = {p: 0 for p in st.session_state.players}
    st.experimental_rerun()

grid = st.session_state.grid
players = st.session_state.players
player = players[st.session_state.current_player]
move_count = st.session_state.move_count

st.markdown(f"### Player Turn: {st.session_state.colors[player]} {player}")

cols = st.columns(n)
for i in range(n):
    for j in range(n):
        cell = grid[i][j]
        with cols[j]:
            if st.button(cell_display(cell), key=f"{i}-{j}"):
                if not is_game_over(grid, move_count) and (cell.owner in [None, player]):
                    cell.owner = player
                    cell.count += 1
                    move_count[player] += 1
                    resolve_chain_reaction(grid, i, j, player, n)
                    if not is_game_over(grid, move_count):
                        st.session_state.current_player = 1 - st.session_state.current_player
                    else:
                        winner = next(p for p in players if any(c.owner == p for row in grid for c in row))
                        st.success(f"🏆 Game Over! Winner: {st.session_state.colors[winner]} {winner}")
                    st.experimental_rerun()

