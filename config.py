"""
Shared configuration and constants for the AI Zombie Project.
Centralized location for grid layouts, colors, positions, and settings.
"""

# --- Grid Configuration ---
TILE_SIZE = 40
GRID_WIDTH = 15
GRID_HEIGHT = 10

# The main game grid (0 = Empty, 1 = Wall, 2 = Player/Monster, 3 = Prize)
GRID = [
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 3]
]

# --- Starting Positions ---
PLAYER_START_POS = [2, 4]
GOAL_POS = [14, 9]

# --- Colors (RGB) ---
# Core colors
BG_COLOR = (30, 30, 30)
BLACK = (0, 0, 0)
DARK_GRAY = (30, 30, 35)
MED_GRAY = (70, 65, 60)
LIGHT_GRAY = (110, 100, 90)

# Entity colors
WALL_COLOR = (100, 100, 100)
PLAYER_COLOR = (0, 150, 255)
GOAL_COLOR = (0, 255, 100)
PATH_COLOR = (60, 60, 60)

# Monster colors
RED = (180, 30, 20)
DARK_RED = (100, 20, 10)
PURPLE = (120, 40, 160)
DARK_PURPLE = (70, 20, 100)

# Prize colors
PRIZE_GOLD = (255, 215, 0)
DARK_GOLD = (150, 120, 0)

# --- Game Settings ---
FPS = 10  # Speed of agent steps
GRID_LINE_COLOR = (50, 50, 50)

# --- Large Grid Configuration (30x30) ---
TILE_SIZE_LARGE = 20
GRID_WIDTH_LARGE = 30
GRID_HEIGHT_LARGE = 30

# Generate a 30x30 maze-like grid with walls
GRID_LARGE = [
    [0]*30 for _ in range(30)
]

# Add walls to create maze structure
for row in range(30):
    for col in range(30):
        # Create a pattern of walls
        if (row % 5 == 0 or col % 5 == 0) and not (row == 0 or col == 0 or row == 29 or col == 29):
            if (row + col) % 3 == 0:
                GRID_LARGE[row][col] = 1

# Ensure start and goal are accessible
GRID_LARGE[1][1] = 0
GRID_LARGE[28][28] = 3

# --- Starting Positions (Large Grid) ---
PLAYER_START_POS_LARGE = [1, 1]
GOAL_POS_LARGE = [28, 28]

# --- Extra Large Grid Configuration (40x30) ---
TILE_SIZE_XLARGE = 20
GRID_WIDTH_XLARGE = 40
GRID_HEIGHT_XLARGE = 30
# --- Extra Large Maze (40x30) ---
import random
random.seed(0)

# Start with all walls
GRID_XLARGE = [[1 for _ in range(GRID_WIDTH_XLARGE)] for _ in range(GRID_HEIGHT_XLARGE)]

# Maze generation using recursive backtracker (DFS) on odd cells
def _generate_maze(width, height):
    stack = []
    start = (1, 1)
    stack.append(start)
    GRID_XLARGE[1][1] = 0
    visited = {start}
    dirs = [(-2, 0), (2, 0), (0, -2), (0, 2)]
    while stack:
        r, c = stack[-1]
        neighbors = []
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 1 <= nr < height-1 and 1 <= nc < width-1 and (nr, nc) not in visited:
                neighbors.append((nr, nc))
        if neighbors:
            nr, nc = random.choice(neighbors)
            # remove wall between
            wall_r, wall_c = (r + nr)//2, (c + nc)//2
            GRID_XLARGE[wall_r][wall_c] = 0
            GRID_XLARGE[nr][nc] = 0
            visited.add((nr, nc))
            stack.append((nr, nc))
        else:
            stack.pop()

_generate_maze(GRID_WIDTH_XLARGE, GRID_HEIGHT_XLARGE)

# Clear small start area and goal area to ensure accessibility
for rr in range(0, 3):
    for cc in range(0, 3):
        GRID_XLARGE[1+rr][1+cc] = 0

for rr in range(0, 3):
    for cc in range(0, 3):
        GRID_XLARGE[GRID_HEIGHT_XLARGE-2-rr][GRID_WIDTH_XLARGE-2-cc] = 0

# --- Starting Positions (Extra Large Grid) ---
PLAYER_START_POS_XLARGE = [2, 15]
GOAL_POS_XLARGE = [37, 15]

