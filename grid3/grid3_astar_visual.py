import pygame
import random
import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    TILE_SIZE_XLARGE, GRID_WIDTH_XLARGE, GRID_HEIGHT_XLARGE, FPS,
    GRID_XLARGE, PLAYER_START_POS_XLARGE, GOAL_POS_XLARGE,
    BLACK, DARK_GRAY, MED_GRAY, LIGHT_GRAY,
    RED, DARK_RED, PURPLE, DARK_PURPLE,
    PRIZE_GOLD, DARK_GOLD
)
from utils import get_astar_path

pygame.init()

# Setup Screen
SCREEN_WIDTH = GRID_WIDTH_XLARGE * TILE_SIZE_XLARGE
SCREEN_HEIGHT = GRID_HEIGHT_XLARGE * TILE_SIZE_XLARGE
PANEL_HEIGHT = 60 

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + PANEL_HEIGHT))
pygame.display.set_caption("AI Grid 3: A* Search - Visual Edition (XL)")
clock = pygame.time.Clock()

# Grid (create mutable copy)
grid = [row[:] for row in GRID_XLARGE]

# Find prize position (3) in grid
prize_pos = None
for row in range(GRID_HEIGHT_XLARGE):
    for col in range(GRID_WIDTH_XLARGE):
        if grid[row][col] == 3:
            prize_pos = (col, row)
            break
    if prize_pos:
        break

# Target logic: If no '3' exists, use the default GOAL_POS
target_pos = list(prize_pos) if prize_pos else GOAL_POS_XLARGE.copy()
player_pos = PLAYER_START_POS_XLARGE.copy()
prize_found = False

# STARS for background
stars = []
for _ in range(300):
    stars.append({
        'x': random.randint(0, SCREEN_WIDTH),
        'y': random.randint(0, SCREEN_HEIGHT),
        'size': random.choice([1, 2]),
        'brightness': random.randint(60, 120)
    })

# --- RENDER FUNCTIONS ---

def draw_meteor(x, y):
    scale = TILE_SIZE_XLARGE / 40
    points = [
        (x + int(4*scale), y + int(4*scale)),
        (x + TILE_SIZE_XLARGE - int(4*scale), y + int(6*scale)),
        (x + TILE_SIZE_XLARGE - int(2*scale), y + TILE_SIZE_XLARGE - int(8*scale)),
        (x + int(8*scale), y + TILE_SIZE_XLARGE - int(4*scale)),
    ]
    pygame.draw.polygon(screen, DARK_GRAY, points)
    pygame.draw.polygon(screen, MED_GRAY, points, 1)

def draw_player(x, y):
    scale = TILE_SIZE_XLARGE / 40
    center = (x + TILE_SIZE_XLARGE//2, y + TILE_SIZE_XLARGE//2)
    
    # Body (Blue Monster)
    body_rect = (center[0] - int(8*scale), center[1] - int(6*scale), int(16*scale), int(14*scale))
    pygame.draw.ellipse(screen, (0, 150, 255), body_rect)
    
    # Eyes
    eye_size = max(1, int(2*scale))
    pygame.draw.circle(screen, (255, 255, 255), (center[0] - int(4*scale), center[1] - int(2*scale)), eye_size)
    pygame.draw.circle(screen, (255, 255, 255), (center[0] + int(4*scale), center[1] - int(2*scale)), eye_size)

def draw_prize(x, y):
    scale = TILE_SIZE_XLARGE / 40
    center = (x + TILE_SIZE_XLARGE//2, y + TILE_SIZE_XLARGE//2)
    
    # Make it a bright glowing diamond
    points = [
        (center[0], y + int(2*scale)),                      # Top
        (x + TILE_SIZE_XLARGE - int(2*scale), center[1]),   # Right
        (center[0], y + TILE_SIZE_XLARGE - int(2*scale)),   # Bottom
        (x + int(2*scale), center[1])                       # Left
    ]
    # Inner glow
    pygame.draw.polygon(screen, (255, 255, 150), points)
    # Main color
    pygame.draw.polygon(screen, PRIZE_GOLD, points, 2)

# --- INITIALIZATION ---

start_time = time.time()
calculated_path = get_astar_path(player_pos, target_pos, GRID_XLARGE)
end_time = time.time()
algorithm_time = end_time - start_time
path_index = 0

# --- MAIN LOOP ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Path following logic
    if path_index < len(calculated_path):
        player_pos = list(calculated_path[path_index])
        path_index += 1
    elif not prize_found:
        prize_found = True

    # Drawing
    screen.fill(BLACK)

    # Panel
    pygame.draw.rect(screen, (40, 40, 45), (0, 0, SCREEN_WIDTH, PANEL_HEIGHT))
    font = pygame.font.Font(None, 26)
    timer_text = font.render(f"A* XL Time: {algorithm_time:.4f}s | Path: {len(calculated_path)} steps", True, PRIZE_GOLD)
    screen.blit(timer_text, (20, 20))

    # Background Stars
    for s in stars:
        pygame.draw.circle(screen, (s['brightness'], s['brightness'], s['brightness']), 
                          (int(s['x']), int(s['y']) + PANEL_HEIGHT), s['size'])

    # Grid Rendering
    for row in range(GRID_HEIGHT_XLARGE):
        for col in range(GRID_WIDTH_XLARGE):
            x_pos = col * TILE_SIZE_XLARGE
            y_pos = row * TILE_SIZE_XLARGE + PANEL_HEIGHT
            tile = grid[row][col]
            
            # Draw base floor
            pygame.draw.rect(screen, (10, 10, 15), (x_pos, y_pos, TILE_SIZE_XLARGE, TILE_SIZE_XLARGE))
            
            if tile == 1:
                draw_meteor(x_pos, y_pos)
            elif tile == 3:
                draw_prize(x_pos, y_pos)
            
            # Subtle grid lines
            pygame.draw.rect(screen, (25, 25, 30), (x_pos, y_pos, TILE_SIZE_XLARGE, TILE_SIZE_XLARGE), 1)
    
    # Draw Player
    draw_player(player_pos[0] * TILE_SIZE_XLARGE, player_pos[1] * TILE_SIZE_XLARGE + PANEL_HEIGHT)
    
    # End Game Overlay
    if prize_found:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT + PANEL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))
        
        big_font = pygame.font.Font(None, 64)
        msg = big_font.render("PRIZE CLAIMED", True, PRIZE_GOLD)
        msg_rect = msg.get_rect(center=(SCREEN_WIDTH//2, (SCREEN_HEIGHT + PANEL_HEIGHT)//2))
        screen.blit(msg, msg_rect)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()