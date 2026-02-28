import pygame
import sys
import time
from config import (
    TILE_SIZE_XLARGE, GRID_WIDTH_XLARGE, GRID_HEIGHT_XLARGE,
    BG_COLOR, GRID_LINE_COLOR, WALL_COLOR, PLAYER_COLOR, GOAL_COLOR,
    GRID_XLARGE, PLAYER_START_POS_XLARGE, GOAL_POS_XLARGE
)
from utils import get_bfs_path, get_astar_path, get_astar_path_fast

# UI
PANEL_HEIGHT = 60
FPS = 30

# Colors for drawing paths
BFS_COLOR = (0, 150, 255)
ASTAR_COLOR = (0, 255, 100)
COMMON_COLOR = (255, 200, 0)
DIFF_COLOR = (200, 50, 200)

# Setup pygame
pygame.init()
screen = pygame.display.set_mode((GRID_WIDTH_XLARGE * TILE_SIZE_XLARGE, GRID_HEIGHT_XLARGE * TILE_SIZE_XLARGE + PANEL_HEIGHT))
pygame.display.set_caption("Phase3 Compare: BFS vs A*")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 26)

# Compute both paths and timings
start = PLAYER_START_POS_XLARGE.copy()
goal = GOAL_POS_XLARGE.copy()

# Get path + exploration info (visited sets) for frontier visualization
start_t = time.time()
bfs_path, bfs_info = get_bfs_path(start, goal, GRID_XLARGE, return_info=True)
end_t = time.time()
bfs_time = end_t - start_t

start_t = time.time()
astar_path, astar_info = get_astar_path(start, goal, GRID_XLARGE, return_info=True)
end_t = time.time()
astar_time = end_t - start_t

# Also compute fast A* (info only)
_, astar_fast_info = get_astar_path_fast(start, goal, GRID_XLARGE, return_info=True)

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
    pygame.draw.rect(screen, (40, 40, 40), (0, 0, GRID_WIDTH_XLARGE * TILE_SIZE_XLARGE, PANEL_HEIGHT))
    info = f"BFS {bfs_time:.4f}s | A* {astar_time:.4f}s | BFS steps: {len(bfs_path)} | A* steps: {len(astar_path)} | diff nodes: {len(only_bfs)+len(only_astar)}"
    text = font.render(info, True, (180, 220, 255))
    screen.blit(text, (12, 16))

    # Draw grid
    for r in range(GRID_HEIGHT_XLARGE):
        for c in range(GRID_WIDTH_XLARGE):
            rect = pygame.Rect(c * TILE_SIZE_XLARGE, r * TILE_SIZE_XLARGE + PANEL_HEIGHT, TILE_SIZE_XLARGE, TILE_SIZE_XLARGE)
            if GRID_XLARGE[r][c] == 1:
                pygame.draw.rect(screen, WALL_COLOR, rect)
            pygame.draw.rect(screen, GRID_LINE_COLOR, rect, 1)

    # Draw frontiers (optional)
    if show_frontier:
        bfs_visited = bfs_info.get('visited', set())
        astar_visited = astar_info.get('visited', set())
        for (x, y) in bfs_visited:
            rect = pygame.Rect(x * TILE_SIZE_XLARGE, y * TILE_SIZE_XLARGE + PANEL_HEIGHT, TILE_SIZE_XLARGE, TILE_SIZE_XLARGE)
            pygame.draw.rect(screen, (40, 80, 160), rect)
        for (x, y) in astar_visited:
            rect = pygame.Rect(x * TILE_SIZE_XLARGE, y * TILE_SIZE_XLARGE + PANEL_HEIGHT, TILE_SIZE_XLARGE, TILE_SIZE_XLARGE)
            pygame.draw.rect(screen, (60, 160, 80), rect)

    # Draw common path nodes first (so they show up as common)
    for (x, y) in common:
        rect = pygame.Rect(x * TILE_SIZE_XLARGE, y * TILE_SIZE_XLARGE + PANEL_HEIGHT, TILE_SIZE_XLARGE, TILE_SIZE_XLARGE)
        pygame.draw.rect(screen, COMMON_COLOR, rect)

    # Draw BFS-only nodes
    for (x, y) in only_bfs:
        rect = pygame.Rect(x * TILE_SIZE_XLARGE, y * TILE_SIZE_XLARGE + PANEL_HEIGHT, TILE_SIZE_XLARGE, TILE_SIZE_XLARGE)
        pygame.draw.rect(screen, BFS_COLOR, rect)

    # Draw A*-only nodes
    for (x, y) in only_astar:
        rect = pygame.Rect(x * TILE_SIZE_XLARGE, y * TILE_SIZE_XLARGE + PANEL_HEIGHT, TILE_SIZE_XLARGE, TILE_SIZE_XLARGE)
        pygame.draw.rect(screen, ASTAR_COLOR, rect)

    # Draw start and goal
    pygame.draw.rect(screen, PLAYER_COLOR, (start[0] * TILE_SIZE_XLARGE, start[1] * TILE_SIZE_XLARGE + PANEL_HEIGHT, TILE_SIZE_XLARGE, TILE_SIZE_XLARGE))
    pygame.draw.rect(screen, GOAL_COLOR, (goal[0] * TILE_SIZE_XLARGE, goal[1] * TILE_SIZE_XLARGE + PANEL_HEIGHT, TILE_SIZE_XLARGE, TILE_SIZE_XLARGE))

    # Legend
    legend_x = 12
    legend_y = GRID_HEIGHT_XLARGE * TILE_SIZE_XLARGE + PANEL_HEIGHT - 26
    # (draw small boxes)
    pygame.draw.rect(screen, BFS_COLOR, (legend_x, legend_y, 16, 16))
    screen.blit(font.render("BFS-only", True, (200, 200, 200)), (legend_x + 20, legend_y))
    pygame.draw.rect(screen, ASTAR_COLOR, (legend_x + 140, legend_y, 16, 16))
    screen.blit(font.render("A*-only", True, (200, 200, 200)), (legend_x + 164, legend_y))
    pygame.draw.rect(screen, COMMON_COLOR, (legend_x + 260, legend_y, 16, 16))
    screen.blit(font.render("Common", True, (200, 200, 200)), (legend_x + 284, legend_y))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
