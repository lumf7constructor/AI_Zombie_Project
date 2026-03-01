"""
Grid 2 Discovery Time Heatmaps (30x30 Large Grid)
Shows when nodes were discovered using a color gradient (Viridis).
BFS will show concentric circles; A* will show a focused beam toward goal.

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
import numpy as np
import time
from config import (
    GRID_LARGE, GRID_WIDTH_LARGE, GRID_HEIGHT_LARGE,
    PLAYER_START_POS_LARGE, GOAL_POS_LARGE
)
from utils import get_bfs_path, get_astar_path

# Try to import matplotlib for heatmap visualization
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Matplotlib not available - skipping heatmap visualization")
    exit(1)

# Define color maps
CMAP = 'viridis'  # Can also use 'plasma', 'hot', 'cool', etc.

def get_visitation_order(path_info):
    """Extract visitation order from path info if available."""
    visited = path_info.get('visited', set())
    # If we have order info, use it; otherwise just return visited set with default order
    return list(visited) if visited else []

def create_heatmap_comparison(title_prefix, bfs_info, astar_info, grid_w, grid_h, grid):
    """Create side-by-side heatmap visualization."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # BFS heatmap
    bfs_grid = np.ones((grid_h, grid_w)) * -1  # -1 for unexplored
    bfs_visited = bfs_info.get('visited', set())
    for i, (x, y) in enumerate(sorted(bfs_visited)):
        if 0 <= x < grid_w and 0 <= y < grid_h:
            bfs_grid[y, x] = i / max(1, len(bfs_visited))  # Normalize to [0, 1]
    
    # Mark walls as -2
    for r in range(grid_h):
        for c in range(grid_w):
            if grid[r][c] == 1:
                bfs_grid[r, c] = -2
    
    im1 = ax1.imshow(bfs_grid, cmap=CMAP, vmin=0, vmax=1)
    ax1.scatter(*PLAYER_START_POS_LARGE, color='green', s=100, marker='s', label='Start', zorder=5)
    ax1.scatter(*GOAL_POS_LARGE, color='red', s=100, marker='*', label='Goal', zorder=5)
    ax1.set_title(f"{title_prefix} - BFS Discovery Time\n(Radial expansion pattern)")
    ax1.legend()
    plt.colorbar(im1, ax=ax1, label='Discovery Time')
    ax1.axis('off')
    
    # A* heatmap
    astar_grid = np.ones((grid_h, grid_w)) * -1  # -1 for unexplored
    astar_visited = astar_info.get('visited', set())
    for i, (x, y) in enumerate(sorted(astar_visited)):
        if 0 <= x < grid_w and 0 <= y < grid_h:
            astar_grid[y, x] = i / max(1, len(astar_visited))  # Normalize to [0, 1]
    
    # Mark walls as -2
    for r in range(grid_h):
        for c in range(grid_w):
            if grid[r][c] == 1:
                astar_grid[r, c] = -2
    
    im2 = ax2.imshow(astar_grid, cmap=CMAP, vmin=0, vmax=1)
    ax2.scatter(*PLAYER_START_POS_LARGE, color='green', s=100, marker='s', label='Start', zorder=5)
    ax2.scatter(*GOAL_POS_LARGE, color='red', s=100, marker='*', label='Goal', zorder=5)
    ax2.set_title(f"{title_prefix} - A* Discovery Time\n(Focused beam toward goal)")
    ax2.legend()
    plt.colorbar(im2, ax=ax2, label='Discovery Time')
    ax2.axis('off')
    
    plt.tight_layout()
    return fig

# Run both algorithms and capture exploration info
print("Computing BFS discovery times (Grid 2)...")
start = PLAYER_START_POS_LARGE.copy()
goal = GOAL_POS_LARGE.copy()
bfs_path, bfs_info = get_bfs_path(start, goal, GRID_LARGE, return_info=True)

print("Computing A* discovery times (Grid 2)...")
astar_path, astar_info = get_astar_path(start, goal, GRID_LARGE, return_info=True)

# Create and save heatmap
print("Creating heatmap visualization...")
fig = create_heatmap_comparison("Grid 2 (30x30)", bfs_info, astar_info, GRID_WIDTH_LARGE, GRID_HEIGHT_LARGE, GRID_LARGE)
plt.savefig('/home/lum/AI_Zombie_Project/grid2_discovery_heatmap.png', dpi=100, bbox_inches='tight')
print("Saved: grid2_discovery_heatmap.png")
plt.close()

print(f"BFS nodes explored: {len(bfs_info.get('visited', set()))}")
print(f"A* nodes explored: {len(astar_info.get('visited', set()))}")
