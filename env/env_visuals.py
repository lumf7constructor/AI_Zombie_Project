import pygame
import random
from config import (
    TILE_SIZE, GRID_WIDTH, GRID_HEIGHT,
    GRID, PLAYER_START_POS,
    BLACK, DARK_GRAY, MED_GRAY, LIGHT_GRAY,
    RED, DARK_RED, PURPLE, DARK_PURPLE,
    PRIZE_GOLD, DARK_GOLD
)

pygame.init()

SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI Project: Zombie Survival - Phase 0 - Final Environment Setup - Zathura Edition")
clock = pygame.time.Clock()

## Grid (create mutable copy)
grid = [row[:] for row in GRID]

monster_pos = PLAYER_START_POS.copy()
grid[monster_pos[1]][monster_pos[0]] = 2

prize_pos = None
for row in range(GRID_HEIGHT):
    for col in range(GRID_WIDTH):
        if grid[row][col] == 3:
            prize_pos = (col, row)  # Store as [x, y]
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

# MONSTER VISUALS
def draw_monster(x, y):
    center = (x + TILE_SIZE//2, y + TILE_SIZE//2)
    
    # Body
    body_points = [
        (center[0] - 18, center[1] - 10),  
        (center[0] + 18, center[1] - 10),  
        (center[0] + 22, center[1] + 3), 
        (center[0] + 15, center[1] + 14),  
        (center[0] - 15, center[1] + 14),  
        (center[0] - 22, center[1] + 3),   
    ]
    pygame.draw.polygon(screen, PURPLE, body_points)
    pygame.draw.polygon(screen, DARK_PURPLE, body_points, 2)
    
    # Head
    head_points = [
        (center[0] - 11, center[1] - 18),
        (center[0] + 11, center[1] - 18),
        (center[0] + 7, center[1] - 7),
        (center[0] - 7, center[1] - 7),
    ]
    pygame.draw.polygon(screen, (100, 30, 140), head_points)
    
    # Eyes
    pygame.draw.circle(screen, RED, (center[0] - 6, center[1] - 14), 3)
    pygame.draw.circle(screen, RED, (center[0] + 6, center[1] - 14), 3)
    # Pupils
    pygame.draw.circle(screen, (255, 200, 200), (center[0] - 6, center[1] - 14), 1)
    pygame.draw.circle(screen, (255, 200, 200), (center[0] + 6, center[1] - 14), 1)
    
    # Horns
    pygame.draw.polygon(screen, DARK_PURPLE, [
        (center[0] - 9, center[1] - 22),
        (center[0] - 13, center[1] - 28),
        (center[0] - 4, center[1] - 24)
    ])
    pygame.draw.polygon(screen, DARK_PURPLE, [
        (center[0] + 9, center[1] - 22),
        (center[0] + 13, center[1] - 28),
        (center[0] + 4, center[1] - 24)
    ])
    
    # Spikes
    spike_positions = [
        (center[0] - 11, center[1] - 7),
        (center[0] - 4, center[1] - 9),
        (center[0] + 4, center[1] - 9),
        (center[0] + 11, center[1] - 7)
    ]
    for sx, sy in spike_positions:
        pygame.draw.polygon(screen, DARK_PURPLE, [
            (sx, sy),
            (sx - 4, sy + 6),
            (sx + 4, sy + 6)
        ])

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

# GRID
def draw_grid():
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            x = col * TILE_SIZE
            y = row * TILE_SIZE
            tile = grid[row][col]
            
            if tile == 0 or tile == 2:
                pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE))
            
            elif tile == 1:
                draw_meteor(x, y)
            
            elif tile == 3:
                draw_prize(x, y)
            
            pygame.draw.rect(screen, (40, 40, 30), (x, y, TILE_SIZE, TILE_SIZE), 1)


# MAIN
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN and not prize_found:
            target_x, target_y = monster_pos[0], monster_pos[1]
            
            if event.key == pygame.K_UP:
                target_y -= 1
            elif event.key == pygame.K_DOWN:
                target_y += 1
            elif event.key == pygame.K_LEFT:
                target_x -= 1
            elif event.key == pygame.K_RIGHT:
                target_x += 1

            if (0 <= target_x < GRID_WIDTH) and (0 <= target_y < GRID_HEIGHT):
                if grid[target_y][target_x] != 1:

                    if grid[target_y][target_x] == 3:
                        prize_found = True

                    grid[monster_pos[1]][monster_pos[0]] = 0
                    grid[target_y][target_x] = 2
                    monster_pos = [target_x, target_y]

    screen.fill(BLACK)

    for s in stars:
        pygame.draw.circle(screen, (s['brightness'], s['brightness'], s['brightness']), 
                          (int(s['x']), int(s['y'])), s['size'])

    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            x = col * TILE_SIZE
            y = row * TILE_SIZE
            tile = grid[row][col]
            
            if tile == 1:
                draw_meteor(x, y)
            elif tile == 3:
                draw_prize(x, y)
            elif tile == 0:
                pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE))

            pygame.draw.rect(screen, (40, 40, 30), (x, y, TILE_SIZE, TILE_SIZE), 1)
    
    draw_monster(monster_pos[0] * TILE_SIZE, monster_pos[1] * TILE_SIZE)
    
    # Win
    if prize_found:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 48)
        text = font.render("PRIZE CLAIMED", True, PRIZE_GOLD)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(text, text_rect)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
