import pygame
import sys
import os
import time
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    TILE_SIZE_XLARGE, GRID_WIDTH_XLARGE, GRID_HEIGHT_XLARGE, FPS,
    BG_COLOR, WALL_COLOR, PLAYER_COLOR, GOAL_COLOR, GRID_LINE_COLOR,
    GRID_XLARGE, PLAYER_START_POS_XLARGE, GOAL_POS_XLARGE
)
from utils import get_astar_path

# Try to import matplotlib for static visualization
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# --- Configuration ---
# (All imported from config.py for extra large grid)

# Positions [x, y]
player_pos = PLAYER_START_POS_XLARGE.copy()
goal_pos = GOAL_POS_XLARGE.copy()

# --- Pygame Setup ---
pygame.init()
PANEL_HEIGHT = 60  # Space for UI panel at the top
screen = pygame.display.set_mode((GRID_WIDTH_XLARGE * TILE_SIZE_XLARGE, GRID_HEIGHT_XLARGE * TILE_SIZE_XLARGE + PANEL_HEIGHT))
pygame.display.set_caption("AI Grid 3: A* Search on Extra Large Grid (50x40)")
clock = pygame.time.Clock()

# Calculate the path once at the beginning, with exploration info
start_time = time.time()
calculated_path, astar_info = get_astar_path(player_pos, goal_pos, GRID_XLARGE, return_info=True)
end_time = time.time()
algorithm_time = end_time - start_time
path_index = 0

# Extract metrics
path_length = len(calculated_path)
nodes_explored = astar_info.get('nodes_expanded', 0)
visited_set = set(astar_info.get('visited', set()))

# Debug: Print path info
print(f"Start position: {player_pos}")
print(f"Goal position: {goal_pos}")
print(f"Path found: {path_length} steps")
print(f"Nodes explored: {nodes_explored}")
print(f"Algorithm time: {algorithm_time:.4f} seconds")

# --- Main Loop ---
running = True
animation_complete = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move the agent automatically along the calculated path
    if path_index < len(calculated_path):
        player_pos = list(calculated_path[path_index])
        path_index += 1
    else:
        # Animation finished - wait 2 seconds then auto-close
        if not animation_complete:
            animation_complete = True
            animation_end_time = time.time()
        elif time.time() - animation_end_time > 2:
            running = False

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

# --- Save Static Search Footprint Visualization ---
if MATPLOTLIB_AVAILABLE:
    try:
        # Create side-by-side visualization: left = explored, right = metrics
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Left: Explored nodes visualization
        explored_grid = np.zeros((GRID_HEIGHT_XLARGE, GRID_WIDTH_XLARGE, 3), dtype=np.uint8)
        # Start with grid (black for empty, dark gray for walls)
        for r in range(GRID_HEIGHT_XLARGE):
            for c in range(GRID_WIDTH_XLARGE):
                if GRID_XLARGE[r][c] == 1:
                    explored_grid[r, c] = [50, 50, 50]  # Dark gray for walls
                else:
                    explored_grid[r, c] = [255, 255, 255]  # White for empty
        
        # Color explored nodes light green
        for (x, y) in visited_set:
            if 0 <= x < GRID_WIDTH_XLARGE and 0 <= y < GRID_HEIGHT_XLARGE:
                explored_grid[y, x] = [200, 230, 180]  # Light green
        
        # Highlight path in bright yellow
        path_set = set(calculated_path)
        for (x, y) in path_set:
            if 0 <= x < GRID_WIDTH_XLARGE and 0 <= y < GRID_HEIGHT_XLARGE:
                explored_grid[y, x] = [255, 255, 0]  # Bright yellow
        
        # Mark start and goal
        sx, sy = int(player_pos[0]), int(player_pos[1])
        gx, gy = int(goal_pos[0]), int(goal_pos[1])
        if 0 <= sx < GRID_WIDTH_XLARGE and 0 <= sy < GRID_HEIGHT_XLARGE:
            explored_grid[sy, sx] = [0, 255, 0]  # Green for start
        if 0 <= gx < GRID_WIDTH_XLARGE and 0 <= gy < GRID_HEIGHT_XLARGE:
            explored_grid[gy, gx] = [255, 0, 0]  # Red for goal
        
        ax1.imshow(explored_grid)
        ax1.set_title("A* (Grid 3): Explored Nodes (Light Green) & Path (Yellow)")
        ax1.axis('off')
        
        # Right: Metrics scorecard
        ax2.axis('off')
        metrics_text = f"""
A* Search Metrics (50x40 Grid)
{'='*40}

Path Length: {path_length} steps
Nodes Explored: {nodes_explored}
Execution Time: {algorithm_time:.6f} seconds

Efficiency: {(path_length / max(1, nodes_explored) * 100):.2f}%
        """
        ax2.text(0.1, 0.5, metrics_text, fontsize=10, family='monospace',
                verticalalignment='center', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig('/home/lum/AI_Zombie_Project/grid3_astar_footprint.png', dpi=100, bbox_inches='tight')
        print("Saved: grid3_astar_footprint.png")
        plt.close()
    except Exception as e:
        print(f"Could not save matplotlib visualization: {e}")
else:
    print("Matplotlib not available - skipping static visualization")
