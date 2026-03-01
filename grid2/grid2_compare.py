import pygame
import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    TILE_SIZE_LARGE, GRID_WIDTH_LARGE, GRID_HEIGHT_LARGE,
    BG_COLOR, GRID_LINE_COLOR, WALL_COLOR, PLAYER_COLOR, GOAL_COLOR,
    GRID_LARGE, PLAYER_START_POS_LARGE, GOAL_POS_LARGE
)
from utils import get_bfs_path, get_astar_path, get_astar_path_fast

# UI
PANEL_HEIGHT = 60
FPS = 30

# Colors for drawing paths
BFS_COLOR = (0, 150, 255)
ASTAR_COLOR = (0, 255, 100)
COMMON_COLOR = (255, 200, 0)

# Setup pygame
pygame.init()
screen = pygame.display.set_mode((GRID_WIDTH_LARGE * TILE_SIZE_LARGE, GRID_HEIGHT_LARGE * TILE_SIZE_LARGE + PANEL_HEIGHT))
pygame.display.set_caption("Phase2 Compare: BFS vs A*")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

# Compute both paths and timings
start = PLAYER_START_POS_LARGE.copy()
goal = GOAL_POS_LARGE.copy()

# Get path + exploration info (visited sets) for frontier visualization
start_t = time.time()
bfs_path, bfs_info = get_bfs_path(start, goal, GRID_LARGE, return_info=True)
end_t = time.time()
bfs_time = end_t - start_t

start_t = time.time()
astar_path, astar_info = get_astar_path(start, goal, GRID_LARGE, return_info=True)
end_t = time.time()
astar_time = end_t - start_t

# Also compute fast A* (same API)
_, astar_fast_info = get_astar_path_fast(start, goal, GRID_LARGE, return_info=True)

# Convert to lists of tuples
bfs_path = [tuple(p) for p in bfs_path]
astar_path = [tuple(p) for p in astar_path]

bfs_set = set(bfs_path)
astar_set = set(astar_path)
common = bfs_set & astar_set
only_bfs = bfs_set - astar_set
only_astar = astar_set - bfs_set

print(f"Start: {start}, Goal: {goal}")
print(f"BFS: {len(bfs_path)} steps, time {bfs_time:.6f}s")
print(f"A*: {len(astar_path)} steps, time {astar_time:.6f}s")
print(f"Common nodes: {len(common)}, only BFS: {len(only_bfs)}, only A*: {len(only_astar)}")

# Main draw loop
# Frontier toggle: press F to toggle drawing explored/frontier nodes
show_frontier = False
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_f:
                show_frontier = not show_frontier

    screen.fill(BG_COLOR)

    # Draw UI panel
    pygame.draw.rect(screen, (40, 40, 40), (0, 0, GRID_WIDTH_LARGE * TILE_SIZE_LARGE, PANEL_HEIGHT))
    info = f"BFS {bfs_time:.4f}s | A* {astar_time:.4f}s | BFS steps: {len(bfs_path)} | A* steps: {len(astar_path)} | diff nodes: {len(only_bfs)+len(only_astar)}"
    text = font.render(info, True, (180, 220, 255))
    screen.blit(text, (12, 16))

    # Draw grid
    for r in range(GRID_HEIGHT_LARGE):
        for c in range(GRID_WIDTH_LARGE):
            rect = pygame.Rect(c * TILE_SIZE_LARGE, r * TILE_SIZE_LARGE + PANEL_HEIGHT, TILE_SIZE_LARGE, TILE_SIZE_LARGE)
            if GRID_LARGE[r][c] == 1:
                pygame.draw.rect(screen, WALL_COLOR, rect)
            pygame.draw.rect(screen, GRID_LINE_COLOR, rect, 1)

    # Draw frontiers (optional)
    if show_frontier:
        bfs_visited = set(bfs_info.get('visited', set()))
        astar_visited = set(astar_info.get('visited', set()))

        # Use semi-transparent surfaces so overlaps blend visually when blitted
        blue_a = (40, 80, 160, 110)
        green_a = (60, 160, 80, 110)
        bfs_surf = pygame.Surface((TILE_SIZE_LARGE, TILE_SIZE_LARGE), pygame.SRCALPHA)
        bfs_surf.fill(blue_a)
        astar_surf = pygame.Surface((TILE_SIZE_LARGE, TILE_SIZE_LARGE), pygame.SRCALPHA)
        astar_surf.fill(green_a)

        # Blit BFS visited first, then A* visited so overlaps show blended color
        for (x, y) in bfs_visited:
            screen.blit(bfs_surf, (x * TILE_SIZE_LARGE, y * TILE_SIZE_LARGE + PANEL_HEIGHT))
        for (x, y) in astar_visited:
            screen.blit(astar_surf, (x * TILE_SIZE_LARGE, y * TILE_SIZE_LARGE + PANEL_HEIGHT))

    # Draw BFS-only nodes
    for (x, y) in only_bfs:
        rect = pygame.Rect(x * TILE_SIZE_LARGE, y * TILE_SIZE_LARGE + PANEL_HEIGHT, TILE_SIZE_LARGE, TILE_SIZE_LARGE)
        pygame.draw.rect(screen, BFS_COLOR, rect)

    # Draw A*-only nodes
    for (x, y) in only_astar:
        rect = pygame.Rect(x * TILE_SIZE_LARGE, y * TILE_SIZE_LARGE + PANEL_HEIGHT, TILE_SIZE_LARGE, TILE_SIZE_LARGE)
        pygame.draw.rect(screen, ASTAR_COLOR, rect)

    # Draw common path nodes last (final path shown in yellow) with a dark outline
    for (x, y) in common:
        rect = pygame.Rect(x * TILE_SIZE_LARGE, y * TILE_SIZE_LARGE + PANEL_HEIGHT, TILE_SIZE_LARGE, TILE_SIZE_LARGE)
        pygame.draw.rect(screen, COMMON_COLOR, rect)
        pygame.draw.rect(screen, (50, 40, 0), rect, 2)

    # Draw start and goal
    pygame.draw.rect(screen, PLAYER_COLOR, (start[0] * TILE_SIZE_LARGE, start[1] * TILE_SIZE_LARGE + PANEL_HEIGHT, TILE_SIZE_LARGE, TILE_SIZE_LARGE))
    pygame.draw.rect(screen, GOAL_COLOR, (goal[0] * TILE_SIZE_LARGE, goal[1] * TILE_SIZE_LARGE + PANEL_HEIGHT, TILE_SIZE_LARGE, TILE_SIZE_LARGE))

    # Legend
    legend_x = 12
    legend_y = GRID_HEIGHT_LARGE * TILE_SIZE_LARGE + PANEL_HEIGHT - 26
    # Path legend
    pygame.draw.rect(screen, BFS_COLOR, (legend_x, legend_y, 16, 16))
    screen.blit(font.render("BFS-only", True, (200, 200, 200)), (legend_x + 20, legend_y))
    pygame.draw.rect(screen, ASTAR_COLOR, (legend_x + 140, legend_y, 16, 16))
    screen.blit(font.render("A*-only", True, (200, 200, 200)), (legend_x + 164, legend_y))
    pygame.draw.rect(screen, COMMON_COLOR, (legend_x + 260, legend_y, 16, 16))
    screen.blit(font.render("Final path (common)", True, (200, 200, 200)), (legend_x + 284, legend_y))

    # Frontier legend (semi-transparent previews)
    f_x = legend_x + 520
    bfs_preview = pygame.Surface((12, 12), pygame.SRCALPHA)
    bfs_preview.fill((40, 80, 160, 150))
    screen.blit(bfs_preview, (f_x, legend_y))
    screen.blit(font.render("BFS visited", True, (200, 200, 200)), (f_x + 16, legend_y))

    astar_preview = pygame.Surface((12, 12), pygame.SRCALPHA)
    astar_preview.fill((60, 160, 80, 150))
    screen.blit(astar_preview, (f_x + 160, legend_y))
    screen.blit(font.render("A* visited", True, (200, 200, 200)), (f_x + 176, legend_y))

    both_preview = pygame.Surface((12, 12), pygame.SRCALPHA)
    both_preview.fill((40, 80, 160, 110))
    temp = pygame.Surface((12, 12), pygame.SRCALPHA)
    temp.fill((60, 160, 80, 110))
    both_preview.blit(temp, (0, 0))
    screen.blit(both_preview, (f_x + 320, legend_y))
    screen.blit(font.render("Both visited", True, (200, 200, 200)), (f_x + 336, legend_y))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
