import pygame
import collections
import sys

# --- Configuration ---
TILE_SIZE = 40
GRID_WIDTH, GRID_HEIGHT = 15, 10
FPS = 10 # Speed of the agent's "steps"

# Colors
BG_COLOR = (30, 30, 30)
WALL_COLOR = (100, 100, 100)
PLAYER_COLOR = (0, 150, 255)
GOAL_COLOR = (0, 255, 100)
PATH_COLOR = (60, 60, 60)

# 0 = Empty, 1 = Wall
grid = [
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
]

# Positions [x, y]
player_pos = [0, 0]
goal_pos = [14, 9]

# --- THE SEARCH ALGORITHM (BFS) ---
def get_bfs_path(start, goal):
    """Finds the shortest path from start to goal avoiding walls."""
    queue = collections.deque([[tuple(start)]])
    visited = {tuple(start)}
    
    while queue:
        path = queue.popleft()
        x, y = path[-1]
        
        if [x, y] == goal:
            return path # Success! Returns the list of coordinates
            
        # Check neighbors: Down, Up, Right, Left
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                if grid[ny][nx] == 0 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(path + [(nx, ny)])
    return [] # No path found

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((GRID_WIDTH * TILE_SIZE, GRID_HEIGHT * TILE_SIZE))
pygame.display.set_caption("AI Phase 1: BFS Search")
clock = pygame.time.Clock()

# Calculate the path once at the beginning
calculated_path = get_bfs_path(player_pos, goal_pos)
path_index = 0

# --- Main Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move the agent automatically along the calculated path
    if path_index < len(calculated_path):
        player_pos = list(calculated_path[path_index])
        path_index += 1

    # Drawing
    screen.fill(BG_COLOR)
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            rect = pygame.Rect(c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if grid[r][c] == 1:
                pygame.draw.rect(screen, WALL_COLOR, rect)
            pygame.draw.rect(screen, (50, 50, 50), rect, 1) # Grid lines

    # Draw Goal
    pygame.draw.rect(screen, GOAL_COLOR, (goal_pos[0]*TILE_SIZE, goal_pos[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE))
    
    # Draw Player
    pygame.draw.rect(screen, PLAYER_COLOR, (player_pos[0]*TILE_SIZE, player_pos[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

