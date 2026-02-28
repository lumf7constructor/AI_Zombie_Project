import pygame
import sys
import time
from config import (
    TILE_SIZE_LARGE, GRID_WIDTH_LARGE, GRID_HEIGHT_LARGE, FPS,
    BG_COLOR, WALL_COLOR, PLAYER_COLOR, GOAL_COLOR, GRID_LINE_COLOR,
    GRID_LARGE, PLAYER_START_POS_LARGE, GOAL_POS_LARGE
)
from utils import get_bfs_path

# --- Configuration ---
# (All imported from config.py for large grid)

# Positions [x, y]
player_pos = PLAYER_START_POS_LARGE.copy()
goal_pos = GOAL_POS_LARGE.copy()

# --- Pygame Setup ---
pygame.init()
PANEL_HEIGHT = 60  # Space for UI panel at the top
screen = pygame.display.set_mode((GRID_WIDTH_LARGE * TILE_SIZE_LARGE, GRID_HEIGHT_LARGE * TILE_SIZE_LARGE + PANEL_HEIGHT))
pygame.display.set_caption("AI Phase 2: BFS Search on Large Grid (30x30)")
clock = pygame.time.Clock()

# Calculate the path once at the beginning
start_time = time.time()
calculated_path = get_bfs_path(player_pos, goal_pos, GRID_LARGE)
end_time = time.time()
algorithm_time = end_time - start_time
path_index = 0

# Debug: Print path info
print(f"Start position: {player_pos}")
print(f"Goal position: {goal_pos}")
print(f"Path found: {len(calculated_path)} steps")
print(f"Algorithm time: {algorithm_time:.4f} seconds")
if len(calculated_path) > 0:
    print(f"First few steps: {calculated_path[:5]}")
else:
    print("WARNING: No path found! Check if start and goal are accessible.")

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
    
    # Draw UI panel at the top
    pygame.draw.rect(screen, (50, 50, 50), (0, 0, GRID_WIDTH_LARGE * TILE_SIZE_LARGE, PANEL_HEIGHT))
    pygame.draw.line(screen, GRID_LINE_COLOR, (0, PANEL_HEIGHT), (GRID_WIDTH_LARGE * TILE_SIZE_LARGE, PANEL_HEIGHT), 2)
    
    # Display timing info in the panel
    font = pygame.font.Font(None, 32)
    timer_text = font.render(f"BFS Time: {algorithm_time:.4f}s | Path: {len(calculated_path)} steps", True, PLAYER_COLOR)
    screen.blit(timer_text, (15, 15))
    
    # Draw grid with offset for panel
    for r in range(GRID_HEIGHT_LARGE):
        for c in range(GRID_WIDTH_LARGE):
            rect = pygame.Rect(c*TILE_SIZE_LARGE, r*TILE_SIZE_LARGE + PANEL_HEIGHT, TILE_SIZE_LARGE, TILE_SIZE_LARGE)
            if GRID_LARGE[r][c] == 1:
                pygame.draw.rect(screen, WALL_COLOR, rect)
            pygame.draw.rect(screen, GRID_LINE_COLOR, rect, 1) # Grid lines

    # Draw Goal
    pygame.draw.rect(screen, GOAL_COLOR, (goal_pos[0]*TILE_SIZE_LARGE, goal_pos[1]*TILE_SIZE_LARGE + PANEL_HEIGHT, TILE_SIZE_LARGE, TILE_SIZE_LARGE))
    
    # Draw Player
    pygame.draw.rect(screen, PLAYER_COLOR, (player_pos[0]*TILE_SIZE_LARGE, player_pos[1]*TILE_SIZE_LARGE + PANEL_HEIGHT, TILE_SIZE_LARGE, TILE_SIZE_LARGE))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
