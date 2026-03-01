import pygame
import sys
from config import (
    TILE_SIZE, GRID_WIDTH, GRID_HEIGHT,
    BG_COLOR, WALL_COLOR, PLAYER_COLOR,
    GRID, PLAYER_START_POS, GRID_LINE_COLOR
)

# --- 1. Settings & Configuration ---
# (All imported from config.py)

# --- 2. The Logic Grid (The Brain) ---
# (Shared grid is now in config.py)
grid = [row[:] for row in GRID]  # Create a mutable copy

# Player starting position [X (Column), Y (Row)]
player_pos = PLAYER_START_POS.copy()

# --- 3. Pygame Setup (The Eyes) ---
pygame.init()
screen = pygame.display.set_mode((GRID_WIDTH * TILE_SIZE, GRID_HEIGHT * TILE_SIZE))
pygame.display.set_caption("AI Project: Zombie Survival - Phase 0 - Initial Environment Setup")
clock = pygame.time.Clock()

# --- 4. Main Game Loop ---
running = True
while running:
    # Handle Events (Keystrokes & Quitting)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # Manual movement for testing the environment
        elif event.type == pygame.KEYDOWN:
            target_x, target_y = player_pos[0], player_pos[1]
            
            if event.key == pygame.K_UP:
                target_y -= 1
            elif event.key == pygame.K_DOWN:
                target_y += 1
            elif event.key == pygame.K_LEFT:
                target_x -= 1
            elif event.key == pygame.K_RIGHT:
                target_x += 1

            # Grid Boundary & Wall Collision Check
            if (0 <= target_x < GRID_WIDTH) and (0 <= target_y < GRID_HEIGHT):
                if grid[target_y][target_x] != 1: # If it's not a wall
                    player_pos = [target_x, target_y]

    # Draw Background
    screen.fill(BG_COLOR)

    # Draw the Grid and Walls
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            if grid[row][col] == 1:
                # Draw Wall
                rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, WALL_COLOR, rect)
            
            # Optional: Draw faint grid lines to see the cells clearly
            line_rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, GRID_LINE_COLOR, line_rect, 1)

    # Draw the Player
    player_rect = pygame.Rect(player_pos[0] * TILE_SIZE, player_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    pygame.draw.rect(screen, PLAYER_COLOR, player_rect)

    # Update screen and lock frame rate
    pygame.display.flip()
    clock.tick(15) # 15 frames per second is plenty for a grid game

pygame.quit()
sys.exit()
