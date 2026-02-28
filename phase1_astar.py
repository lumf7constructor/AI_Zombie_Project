import pygame
import sys
import time
from config import (
    TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, FPS,
    BG_COLOR, WALL_COLOR, PLAYER_COLOR, GOAL_COLOR, GRID_LINE_COLOR,
    GRID, PLAYER_START_POS, GOAL_POS
)
from utils import get_astar_path

# --- Configuration ---
# (All imported from config.py)

# Positions [x, y]
player_pos = PLAYER_START_POS.copy()
goal_pos = GOAL_POS.copy()

# --- Pygame Setup ---
pygame.init()
PANEL_HEIGHT = 60  # Space for UI panel at the top
screen = pygame.display.set_mode((GRID_WIDTH * TILE_SIZE, GRID_HEIGHT * TILE_SIZE + PANEL_HEIGHT))
pygame.display.set_caption("AI Phase 1: A* Search")
clock = pygame.time.Clock()

# Calculate the path once at the beginning
start_time = time.time()
calculated_path = get_astar_path(player_pos, goal_pos, GRID)
end_time = time.time()
algorithm_time = end_time - start_time
path_index = 0

# Debug: Print path info
print(f"Start position: {player_pos}")
print(f"Goal position: {goal_pos}")
print(f"Path found: {len(calculated_path)} steps")
print(f"Algorithm time: {algorithm_time:.4f} seconds")

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
    pygame.draw.rect(screen, (50, 50, 50), (0, 0, GRID_WIDTH * TILE_SIZE, PANEL_HEIGHT))
    pygame.draw.line(screen, GRID_LINE_COLOR, (0, PANEL_HEIGHT), (GRID_WIDTH * TILE_SIZE, PANEL_HEIGHT), 2)
    
    # Display timing info in the panel
    font = pygame.font.Font(None, 32)
    timer_text = font.render(f"A* Time: {algorithm_time:.4f}s | Path: {len(calculated_path)} steps", True, PLAYER_COLOR)
    screen.blit(timer_text, (15, 15))
    
    # Draw grid with offset for panel
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            rect = pygame.Rect(c*TILE_SIZE, r*TILE_SIZE + PANEL_HEIGHT, TILE_SIZE, TILE_SIZE)
            if GRID[r][c] == 1:
                pygame.draw.rect(screen, WALL_COLOR, rect)
            pygame.draw.rect(screen, GRID_LINE_COLOR, rect, 1) # Grid lines

    # Draw Goal
    pygame.draw.rect(screen, GOAL_COLOR, (goal_pos[0]*TILE_SIZE, goal_pos[1]*TILE_SIZE + PANEL_HEIGHT, TILE_SIZE, TILE_SIZE))
    
    # Draw Player
    pygame.draw.rect(screen, PLAYER_COLOR, (player_pos[0]*TILE_SIZE, player_pos[1]*TILE_SIZE + PANEL_HEIGHT, TILE_SIZE, TILE_SIZE))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
