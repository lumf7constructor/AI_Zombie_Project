# AI Zombie Project - Repository Structure

This repository is now organized into clearly separated directories for each grid size and documentation.

## Directory Structure

```
AI_Zombie_Project/
├── config.py              # Shared configuration (grids, colors, sizes)
├── utils.py              # Shared utilities (pathfinding algorithms)
├── requirements.txt      # Python dependencies
│
├── env/                  # Environment setup
│   ├── env_setup.py     # Initial environment configuration
│   └── env_visuals.py   # Visualization utilities
│
├── grid1/               # Grid 1: Small Grid (10×10)
│   ├── grid1_search.py           # BFS algorithm demonstration
│   ├── grid1_astar.py            # A* algorithm demonstration
│   ├── grid1_animation.py        # Interactive side-by-side animation
│   ├── grid1_heatmaps.py         # Discovery time heatmaps
│   ├── grid1_search_visual.py    # Legacy visualization
│   ├── grid1_astar_visual.py     # Legacy visualization
│   └── *.png                     # Generated footprint and heatmap outputs
│
├── grid2/               # Grid 2: Medium Grid (30×30)
│   ├── grid2_search.py           # BFS algorithm demonstration
│   ├── grid2_astar.py            # A* algorithm demonstration
│   ├── grid2_animation.py        # Interactive side-by-side animation
│   ├── grid2_heatmaps.py         # Discovery time heatmaps
│   ├── grid2_compare.py          # Side-by-side BFS vs A* comparison
│   ├── grid2_search_visual.py    # Legacy visualization
│   ├── grid2_astar_visual.py     # Legacy visualization
│   └── *.png                     # Generated outputs
│
├── grid3/               # Grid 3: Large Grid (50×40)
│   ├── grid3_search.py           # BFS algorithm demonstration
│   ├── grid3_astar.py            # A* algorithm demonstration
│   ├── grid3_animation.py        # Interactive side-by-side animation
│   ├── grid3_heatmaps.py         # Discovery time heatmaps
│   ├── grid3_compare.py          # Side-by-side BFS vs A* comparison
│   ├── grid3_search_visual.py    # Legacy visualization
│   ├── grid3_astar_visual.py     # Legacy visualization
│   └── *.png                     # Generated outputs
│
├── docs/                # Documentation
│   ├── README.md                      # Original project README
│   ├── VISUALIZATIONS.md              # Detailed visualization guide
│   ├── QUICK_START.md                 # Quick reference for running scripts
│   ├── PROJECT_SUMMARY.md             # Feature overview and architecture
│   └── IMPLEMENTATION_SUMMARY.md      # Implementation details from last session
│
└── benchmarks/          # Benchmark outputs and results
```
│
└── benchmarks/          # Benchmark outputs and results
```

## Running Scripts

All grid scripts can be run from the project root directory:

```bash
# From project root, run Grid 1 BFS demo
python grid1/grid1_search.py

# Run Grid 1 A* demo
python grid1/grid1_astar.py

# Interactive animation
python grid1/grid1_animation.py

# Generate heatmaps
python grid1/grid1_heatmaps.py

# Same for grid2 and grid3
python grid2/grid2_search.py
python grid3/grid3_astar.py
```

## Key Files

- **config.py** - Contains all grid definitions, sizes, colors, and start/goal positions
- **utils.py** - Implements BFS and A* pathfinding algorithms with metrics capture
- **grid{N}_search.py** - BFS demonstration with automatic PNG output
- **grid{N}_astar.py** - A* demonstration with automatic PNG output
- **grid{N}_animation.py** - Interactive visualization with step-by-step controls
- **grid{N}_heatmaps.py** - Generates discovery time heatmaps

## Documentation

See `docs/` folder for detailed guides:

- **QUICK_START.md** - Get running in 2 minutes
- **VISUALIZATIONS.md** - Understanding the visualization types
- **PROJECT_SUMMARY.md** - Complete feature overview
- **IMPLEMENTATION_SUMMARY.md** - Technical details from implementation

## Grid Specifications

### Grid 1 (Small Grid - 10×10)
- Fast execution for quick testing
- Minimal maze complexity
- Best for learning algorithm behavior

### Grid 2 (Medium Grid - 30×30)
- Realistic maze with visible differences between BFS and A*
- Balance between complexity and execution speed
- Good for performance analysis

### Grid 3 (Large Grid - 50×40)
- Complex maze with many obstacles
- Shows scalability of algorithms
- Demonstrates heuristic benefits at scale

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Run Grid 1 BFS: `python grid1/grid1_search.py`
3. Watch the animation, then PNG saves automatically
4. Generate heatmaps: `python grid1/grid1_heatmaps.py`
5. Check `grid1/` folder for output PNG files

See `docs/QUICK_START.md` for more examples.
