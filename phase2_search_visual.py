import pygame
import random
import sys
import time
from config import (
    TILE_SIZE_LARGE, GRID_WIDTH_LARGE, GRID_HEIGHT_LARGE, FPS,
    GRID_LARGE, PLAYER_START_POS_LARGE, GOAL_POS_LARGE,
    BLACK, DARK_GRAY, MED_GRAY, LIGHT_GRAY,
    RED, DARK_RED, PURPLE, DARK_PURPLE,
    PRIZE_GOLD, DARK_GOLD
)
from utils import get_bfs_path

pygame.init()

SCREEN_WIDTH = GRID_WIDTH_LARGE * TILE_SIZE_LARGE
SCREEN_HEIGHT = GRID_HEIGHT_LARGE * TILE_SIZE_LARGE
PANEL_HEIGHT = 60  # Space for UI panel at the top

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + PANEL_HEIGHT))
pygame.display.set_caption("AI Phase 2: BFS Search on Large Grid (30x30) - Visual Edition")
clock = pygame.time.Clock()

# Grid (create mutable copy)
grid = [row[:] for row in GRID_LARGE]

# Positions [x, y]
player_pos = PLAYER_START_POS_LARGE.copy()
goal_pos = GOAL_POS_LARGE.copy()

# Find prize position in grid
prize_pos = None
for row in range(GRID_HEIGHT_LARGE):
    for col in range(GRID_WIDTH_LARGE):
        if grid[row][col] == 3:
            prize_pos = (col, row)
            break
    if prize_pos:
        break

prize_found = False

# STARS
stars = []
for _ in range(200):
    stars.append({
        'x': random.randint(0, SCREEN_WIDTH),
        'y': random.randint(0, SCREEN_HEIGHT),
        'size': random.choice([1, 2]),
        'brightness': random.randint(60, 120)
    })

# ROUGH METEOR (scaled down for larger grid)
def draw_meteor(x, y):
    scale = TILE_SIZE_LARGE / 40
    points = [
        (x + int(5*scale), y + int(5*scale)),
        (x + TILE_SIZE_LARGE - int(8*scale), y + int(4*scale)),
        (x + TILE_SIZE_LARGE - int(3*scale), y + int(12*scale)),
        (x + TILE_SIZE_LARGE - int(5*scale), y + int(22*scale)),
        (x + int(25*scale), y + TILE_SIZE_LARGE - int(6*scale)),
        (x + int(10*scale), y + TILE_SIZE_LARGE - int(4*scale)),
        (x + int(4*scale), y + int(25*scale)),
        (x + int(6*scale), y + int(12*scale))
    ]
    
    pygame.draw.polygon(screen, DARK_GRAY, points)

    crater_positions = [
        (x + int(12*scale), y + int(10*scale), int(4*scale)),
        (x + int(22*scale), y + int(17*scale), int(5*scale)),
        (x + int(15*scale), y + int(25*scale), int(3*scale)),
        (x + int(7*scale), y + int(20*scale), int(3*scale))
    ]
    
    for cx, cy, cr in crater_positions:
        pygame.draw.circle(screen, (20, 20, 25), (int(cx), int(cy)), max(1, int(cr)))
        pygame.draw.circle(screen, (10, 10, 10), (int(cx-cr/2), int(cy-cr/2)), max(1, int(cr-1)))

    pygame.draw.polygon(screen, MED_GRAY, points, 1)

# PLAYER VISUALS (scaled down)
def draw_player(x, y):
    scale = TILE_SIZE_LARGE / 40
    center = (x + TILE_SIZE_LARGE//2, y + TILE_SIZE_LARGE//2)
    
    # Body (light blue)
    body_points = [
        (center[0] - int(9*scale), center[1] - int(5*scale)),  
        (center[0] + int(9*scale), center[1] - int(5*scale)),  
        (center[0] + int(11*scale), center[1] + int(1*scale)), 
        (center[0] + int(7*scale), center[1] + int(7*scale)),  
        (center[0] - int(7*scale), center[1] + int(7*scale)),  
        (center[0] - int(11*scale), center[1] + int(1*scale)),   
    ]
    pygame.draw.polygon(screen, (0, 150, 255), body_points)
    pygame.draw.polygon(screen, (0, 100, 200), body_points, 1)
    
    # Head
    head_points = [
        (center[0] - int(5*scale), center[1] - int(9*scale)),
        (center[0] + int(5*scale), center[1] - int(9*scale)),
        (center[0] + int(3*scale), center[1] - int(3*scale)),
        (center[0] - int(3*scale), center[1] - int(3*scale)),
    ]
    pygame.draw.polygon(screen, (0, 120, 200), head_points)
    
    # Eyes
    if TILE_SIZE_LARGE > 10:
        pygame.draw.circle(screen, (255, 255, 255), (int(center[0] - 3*scale), int(center[1] - 7*scale)), 1)
        pygame.draw.circle(screen, (255, 255, 255), (int(center[0] + 3*scale), int(center[1] - 7*scale)), 1)

# PRIZE (scaled down)
def draw_prize(x, y):
    scale = TILE_SIZE_LARGE / 40
    center = (x + TILE_SIZE_LARGE//2, y + TILE_SIZE_LARGE//2)
    
    points = [
        (center[0], y + int(10*scale)),
        (x + TILE_SIZE_LARGE - int(10*scale), center[1] - int(2*scale)),
        (center[0] + int(7*scale), y + TILE_SIZE_LARGE - int(12*scale)),
        (x + int(10*scale), center[1] + int(5*scale)),
        (center[0] - int(5*scale), y + TILE_SIZE_LARGE - int(7*scale))
    ]
    
    pygame.draw.polygon(screen, PRIZE_GOLD, points)
    pygame.draw.polygon(screen, DARK_GOLD, points, 1)

# Calculate the path once at the beginning using BFS
start_time = time.time()
calculated_path = get_bfs_path(player_pos, goal_pos, GRID_LARGE)
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
    timer_text = font.render(f"BFS Time: {algorithm_time:.4f}s | Path: {len(calculated_path)} steps", True, PRIZE_GOLD)
    screen.blit(timer_text, (15, 15))

    # Draw stars
    for s in stars:
        pygame.draw.circle(screen, (s['brightness'], s['brightness'], s['brightness']), 
                          (int(s['x']), int(s['y']) + PANEL_HEIGHT), s['size'])

    # Draw grid with offset for panel
    for row in range(GRID_HEIGHT_LARGE):
        for col in range(GRID_WIDTH_LARGE):
            x = col * TILE_SIZE_LARGE
            y = row * TILE_SIZE_LARGE + PANEL_HEIGHT
            tile = grid[row][col]
            
            if tile == 1:
                draw_meteor(x, y)
            elif tile == 3:
                draw_prize(x, y)
            elif tile == 0:
                pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE_LARGE, TILE_SIZE_LARGE))

            pygame.draw.rect(screen, (40, 40, 30), (x, y, TILE_SIZE_LARGE, TILE_SIZE_LARGE), 1)
    
    # Draw Player with offset
    draw_player(player_pos[0] * TILE_SIZE_LARGE, player_pos[1] * TILE_SIZE_LARGE + PANEL_HEIGHT)
    
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
