import pygame
import sys
import time
from config import (
    TILE_SIZE_XLARGE, GRID_WIDTH_XLARGE, GRID_HEIGHT_XLARGE, FPS,
    BG_COLOR, WALL_COLOR, PLAYER_COLOR, GOAL_COLOR, GRID_LINE_COLOR,
    GRID_XLARGE, PLAYER_START_POS_XLARGE, GOAL_POS_XLARGE
)
from utils import get_astar_path

# --- Configuration ---
# (All imported from config.py for extra large grid)

# Positions [x, y]
player_pos = PLAYER_START_POS_XLARGE.copy()
goal_pos = GOAL_POS_XLARGE.copy()

# --- Pygame Setup ---
pygame.init()
PANEL_HEIGHT = 60  # Space for UI panel at the top
screen = pygame.display.set_mode((GRID_WIDTH_XLARGE * TILE_SIZE_XLARGE, GRID_HEIGHT_XLARGE * TILE_SIZE_XLARGE + PANEL_HEIGHT))
pygame.display.set_caption("AI Phase 3: A* Search on Extra Large Grid (50x40)")
clock = pygame.time.Clock()

# Calculate the path once at the beginning
start_time = time.time()
calculated_path = get_astar_path(player_pos, goal_pos, GRID_XLARGE)
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
    pygame.draw.rect(screen, (50, 50, 50), (0, 0, GRID_WIDTH_XLARGE * TILE_SIZE_XLARGE, PANEL_HEIGHT))
    pygame.draw.line(screen, GRID_LINE_COLOR, (0, PANEL_HEIGHT), (GRID_WIDTH_XLARGE * TILE_SIZE_XLARGE, PANEL_HEIGHT), 2)
    
    # Display timing info in the panel
    font = pygame.font.Font(None, 28)
    timer_text = font.render(f"A* Time: {algorithm_time:.4f}s | Path: {len(calculated_path)} steps", True, PLAYER_COLOR)
    screen.blit(timer_text, (15, 15))
    
    # Draw grid with offset for panel
    for r in range(GRID_HEIGHT_XLARGE):
        for c in range(GRID_WIDTH_XLARGE):
            rect = pygame.Rect(c*TILE_SIZE_XLARGE, r*TILE_SIZE_XLARGE + PANEL_HEIGHT, TILE_SIZE_XLARGE, TILE_SIZE_XLARGE)
            if GRID_XLARGE[r][c] == 1:
                pygame.draw.rect(screen, WALL_COLOR, rect)
            pygame.draw.rect(screen, GRID_LINE_COLOR, rect, 1) # Grid lines

    # Draw Goal
    pygame.draw.rect(screen, GOAL_COLOR, (goal_pos[0]*TILE_SIZE_XLARGE, goal_pos[1]*TILE_SIZE_XLARGE + PANEL_HEIGHT, TILE_SIZE_XLARGE, TILE_SIZE_XLARGE))
    
    # Draw Player
    pygame.draw.rect(screen, PLAYER_COLOR, (player_pos[0]*TILE_SIZE_XLARGE, player_pos[1]*TILE_SIZE_XLARGE + PANEL_HEIGHT, TILE_SIZE_XLARGE, TILE_SIZE_XLARGE))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
