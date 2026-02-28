import pygame
import random
import sys
import time
from config import (
    TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, FPS,
    GRID, PLAYER_START_POS, GOAL_POS,
    BLACK, DARK_GRAY, MED_GRAY, LIGHT_GRAY,
    RED, DARK_RED, PURPLE, DARK_PURPLE,
    PRIZE_GOLD, DARK_GOLD
)
from utils import get_astar_path

pygame.init()

SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE
PANEL_HEIGHT = 60  # Space for UI panel at the top

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + PANEL_HEIGHT))
pygame.display.set_caption("AI Phase 1: A* Search - Visual Edition")
clock = pygame.time.Clock()

# Grid (create mutable copy)
grid = [row[:] for row in GRID]

# Positions [x, y]
player_pos = PLAYER_START_POS.copy()
goal_pos = GOAL_POS.copy()

# Find prize position in grid
prize_pos = None
for row in range(GRID_HEIGHT):
    for col in range(GRID_WIDTH):
        if grid[row][col] == 3:
            prize_pos = (col, row)
            break
    if prize_pos:
        break

prize_found = False

# STARS
stars = []
for _ in range(100):
    stars.append({
        'x': random.randint(0, SCREEN_WIDTH),
        'y': random.randint(0, SCREEN_HEIGHT),
        'size': random.choice([1, 2]),
        'brightness': random.randint(60, 120)
    })

# ROUGH METEOR
def draw_meteor(x, y):
    points = [
        (x + 10, y + 10),
        (x + TILE_SIZE - 15, y + 8),
        (x + TILE_SIZE - 5, y + 25),
        (x + TILE_SIZE - 10, y + 45),
        (x + 50, y + TILE_SIZE - 12),
        (x + 20, y + TILE_SIZE - 8),
        (x + 8, y + 50),
        (x + 12, y + 25)
    ]
    
    pygame.draw.polygon(screen, DARK_GRAY, points)

    crater_positions = [
        (x + 25, y + 20, 8),
        (x + 45, y + 35, 10),
        (x + 30, y + 50, 6),
        (x + 15, y + 40, 7)
    ]
    
    for cx, cy, cr in crater_positions:
        pygame.draw.circle(screen, (20, 20, 25), (cx, cy), cr)
        pygame.draw.circle(screen, (10, 10, 10), (cx-2, cy-2), cr-3)

    pygame.draw.polygon(screen, MED_GRAY, points, 2)
    
    pygame.draw.line(screen, (20, 20, 20), (x+35, y+25), (x+45, y+40), 2)
    pygame.draw.line(screen, (20, 20, 20), (x+20, y+45), (x+30, y+55), 2)

# PLAYER VISUALS
def draw_player(x, y):
    center = (x + TILE_SIZE//2, y + TILE_SIZE//2)
    
    # Body (light blue)
    body_points = [
        (center[0] - 18, center[1] - 10),  
        (center[0] + 18, center[1] - 10),  
        (center[0] + 22, center[1] + 3), 
        (center[0] + 15, center[1] + 14),  
        (center[0] - 15, center[1] + 14),  
        (center[0] - 22, center[1] + 3),   
    ]
    pygame.draw.polygon(screen, (0, 150, 255), body_points)
    pygame.draw.polygon(screen, (0, 100, 200), body_points, 2)
    
    # Head
    head_points = [
        (center[0] - 11, center[1] - 18),
        (center[0] + 11, center[1] - 18),
        (center[0] + 7, center[1] - 7),
        (center[0] - 7, center[1] - 7),
    ]
    pygame.draw.polygon(screen, (0, 120, 200), head_points)
    
    # Eyes
    pygame.draw.circle(screen, (255, 255, 255), (center[0] - 6, center[1] - 14), 3)
    pygame.draw.circle(screen, (255, 255, 255), (center[0] + 6, center[1] - 14), 3)
    # Pupils
    pygame.draw.circle(screen, (0, 0, 0), (center[0] - 6, center[1] - 14), 1)
    pygame.draw.circle(screen, (0, 0, 0), (center[0] + 6, center[1] - 14), 1)

# PRIZE
def draw_prize(x, y):
    center = (x + TILE_SIZE//2, y + TILE_SIZE//2)
    
    points = [
        (center[0], y + 20),
        (x + TILE_SIZE - 20, center[1] - 5),
        (center[0] + 15, y + TILE_SIZE - 25),
        (x + 20, center[1] + 10),
        (center[0] - 10, y + TILE_SIZE - 15)
    ]
    
    pygame.draw.polygon(screen, PRIZE_GOLD, points)
    pygame.draw.polygon(screen, DARK_GOLD, points, 2)

# Calculate the path once at the beginning using A*
start_time = time.time()
calculated_path = get_astar_path(player_pos, goal_pos, GRID)
end_time = time.time()
algorithm_time = end_time - start_time
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
        
        # Check if reached prize
        if prize_pos and player_pos == list(prize_pos):
            prize_found = True

    # Drawing
    screen.fill(BLACK)

    # Draw UI panel at the top
    pygame.draw.rect(screen, (50, 50, 50), (0, 0, SCREEN_WIDTH, PANEL_HEIGHT))
    pygame.draw.line(screen, (40, 40, 30), (0, PANEL_HEIGHT), (SCREEN_WIDTH, PANEL_HEIGHT), 2)

    # Display timing info in the panel
    font = pygame.font.Font(None, 32)
    timer_text = font.render(f"A* Time: {algorithm_time:.4f}s | Path: {len(calculated_path)} steps", True, PRIZE_GOLD)
    screen.blit(timer_text, (15, 15))

    # Draw stars
    for s in stars:
        pygame.draw.circle(screen, (s['brightness'], s['brightness'], s['brightness']), 
                          (int(s['x']), int(s['y']) + PANEL_HEIGHT), s['size'])

    # Draw grid with offset for panel
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            x = col * TILE_SIZE
            y = row * TILE_SIZE + PANEL_HEIGHT
            tile = grid[row][col]
            
            if tile == 1:
                draw_meteor(x, y)
            elif tile == 3:
                draw_prize(x, y)
            elif tile == 0:
                pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE))

            pygame.draw.rect(screen, (40, 40, 30), (x, y, TILE_SIZE, TILE_SIZE), 1)
    
    # Draw Player with offset
    draw_player(player_pos[0] * TILE_SIZE, player_pos[1] * TILE_SIZE + PANEL_HEIGHT)
    
    # Win condition
    if prize_found:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT + PANEL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 48)
        text = font.render("PRIZE CLAIMED", True, PRIZE_GOLD)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + PANEL_HEIGHT//2 - 40))
        screen.blit(text, text_rect)
        
        # Show timing in the overlay
        time_text = font.render(f"Time: {algorithm_time:.4f}s", True, PRIZE_GOLD)
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + PANEL_HEIGHT//2 + 40))
        screen.blit(time_text, time_rect)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
