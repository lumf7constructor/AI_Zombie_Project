# AI Zombie Project: Complete Feature Summary

## Project Overview

This is a comprehensive pathfinding visualization and analysis project comparing **BFS (Breadth-First Search)** and **A* (A-Star)** algorithms across three grid scales with four distinct visualization methods.

---

## Architecture

```
AI_Zombie_Project/
├── config.py                          # Centralized config: grids, sizes, colors
├── utils.py                           # Core algorithms: BFS, A*, A* fast
│
├── PHASE 1 (10×10 Small Grid)
│   ├── phase1_search.py              # BFS: animation + footprint PNG + metrics
│   ├── phase1_astar.py               # A*:  animation + footprint PNG + metrics
│   ├── phase1_heatmaps.py            # Discovery time gradient visualization
│   ├── phase1_animation.py           # Interactive step-by-step explorer
│   ├── phase1_search_visual.py       # (legacy animation)
│   └── phase1_astar_visual.py        # (legacy animation)
│
├── PHASE 2 (30×30 Medium Grid)
│   ├── phase2_search.py              # BFS + footprint + metrics
│   ├── phase2_astar.py               # A*  + footprint + metrics
│   ├── phase2_heatmaps.py            # Discovery time gradient
│   ├── phase2_animation.py           # Interactive explorer
│   ├── phase2_compare.py             # Visual comparison with frontier overlay
│   ├── phase2_search_visual.py       # (legacy)
│   └── phase2_astar_visual.py        # (legacy)
│
├── PHASE 3 (50×40 Large Grid)
│   ├── phase3_search.py              # BFS + footprint + metrics
│   ├── phase3_astar.py               # A*  + footprint + metrics
│   ├── phase3_heatmaps.py            # Discovery time gradient
│   ├── phase3_animation.py           # Interactive explorer
│   ├── phase3_compare.py             # Visual comparison with frontier overlay
│   ├── phase3_search_visual.py       # (legacy)
│   └── phase3_astar_visual.py        # (legacy)
│
├── BENCHMARKS
│   ├── benchmarks/run_benchmarks.py  # Multi-trial performance analysis
│   └── benchmarks/results.csv        # 150 trial results (BFS, A*, A* fast)
│
└── DOCUMENTATION
    ├── README.md                      # Original project README
    ├── VISUALIZATIONS.md              # Detailed visualization guide
    ├── QUICK_START.md                 # Quick reference for running scripts
    └── PROJECT_SUMMARY.md             # This file
```

---

## Core Features

### 1. **Four Visualization Methods**

#### A) Search Footprint (Static PNG + Metrics)
- **What:** Side-by-side grid comparison
- **Shows:** Explored nodes (color) vs final path (yellow)
- **Output:** PNG image + metrics scorecard
- **Files:** `phase*_search.py`, `phase*_astar.py`
- **Best for:** Academic papers, static analysis

#### B) Discovery Time Heatmaps (Viridis Gradient)
- **What:** Color gradient showing when nodes were discovered
- **Shows:** BFS = concentric circles, A* = focused beam
- **Output:** PNG image with colorbar
- **Files:** `phase*_heatmaps.py`
- **Best for:** Understanding algorithm bias

#### C) Step-by-Step Animation (Interactive Pygame)
- **What:** Real-time side-by-side exploration
- **Controls:** SPACE=play/pause, LEFT/RIGHT=step, ESC=quit
- **Shows:** Exploration expanding in real-time
- **Output:** Interactive window
- **Files:** `phase*_animation.py`
- **Best for:** Teaching, intuitive understanding

#### D) Comparison with Frontier Overlay (Real-time Pygame)
- **What:** Visual comparison with optional frontier visualization
- **Controls:** F=toggle frontier, ESC=quit
- **Shows:** BFS-only, A*-only, common path, and frontier overlap
- **Output:** Real-time visualization
- **Files:** `phase*_compare.py`
- **Best for:** Advanced analysis

### 2. **Metrics Collection**

Every run captures and displays:
- **Path Length** — Number of steps in final path (same for both algorithms)
- **Nodes Explored** — Size of closed set (A* much smaller)
- **Execution Time** — Milliseconds to compute path
- **Efficiency %** — (path_length / nodes_explored) × 100

**Example:**
```
BFS: Path=55, Explored=820, Time=0.00354s, Efficiency=6.71%
A*:  Path=55, Explored=115, Time=0.00189s, Efficiency=47.83%
```

### 3. **Benchmarking Harness**

- **Script:** `benchmarks/run_benchmarks.py`
- **Trials:** 50 runs per algorithm per phase
- **Algorithms:** BFS, A* (standard), A* (fast/optimized)
- **Output:** CSV with detailed metrics + console summary
- **Optional:** Matplotlib plots (if available)

---

## Algorithm Implementations

### Core Algorithms (in `utils.py`)

#### BFS (Breadth-First Search)
```python
get_bfs_path(start, goal, grid, return_info=False)
```
- **Time:** O(V + E)
- **Space:** O(V)
- **Characteristic:** Explores uniformly in all directions
- **Optimal:** Yes (finds shortest path)
- **Heuristic:** No

#### A* (A-Star)
```python
get_astar_path(start, goal, grid, return_info=False)
```
- **Time:** O(E) in best case, O(V × log V) in worst
- **Space:** O(V)
- **Characteristic:** Guided by heuristic (Manhattan distance)
- **Optimal:** Yes (finds shortest path)
- **Heuristic:** Yes

#### A* Fast (Optimized)
```python
get_astar_path_fast(start, goal, grid, return_info=False)
```
- **Optimization:** Integer node encoding, preallocated arrays
- **Benefit:** Reduced Python overhead
- **Performance:** 2-3× faster than standard A* in practice

### Return Information

All algorithms support `return_info=True` to get:
```python
{
    'nodes_expanded': int,        # Number of nodes in closed set
    'visited': set,               # All explored nodes (x, y) tuples
    'heap_ops': int               # Number of heap operations (A* only)
}
```

---

## Grid Configurations (config.py)

### Phase 1: Small Grid
- **Size:** 10×10 (100 nodes)
- **Tile Size:** 64 pixels
- **Generation:** Hardcoded maze
- **Use:** Quick tests, instant execution

### Phase 2: Medium Grid
- **Size:** 30×30 (900 nodes)
- **Tile Size:** 20 pixels
- **Generation:** Procedural DFS maze
- **Use:** Realistic benchmarks, visible difference

### Phase 3: Large Grid
- **Size:** 50×40 (2000 nodes)
- **Tile Size:** 16 pixels
- **Generation:** Procedural DFS maze
- **Use:** Performance analysis, A* superiority evident

---

## Key Results & Insights

### Typical Performance (Phase 2: 30×30)

| Metric | BFS | A* | A* Fast | Speedup |
|--------|-----|-----|---------|---------|
| Nodes Explored | 820 | 115 | 115 | **7.1×** |
| Execution Time | 3.54ms | 1.89ms | 1.75ms | **2.0×** |
| Efficiency % | 6.71% | 47.83% | 47.83% | **7.1×** |

### Visualization Insights

1. **Footprints:** BFS = large circle, A* = narrow beam
2. **Heatmaps:** BFS = concentric rings, A* = elongated focus
3. **Animations:** BFS explores methodically, A* ignores dead ends
4. **Metrics:** A* consistent across grids; BFS scales poorly

---

## Running the Full Suite

### Generate All Phase 1 Outputs
```bash
python phase1_search.py        # Generates phase1_bfs_footprint.png
python phase1_astar.py         # Generates phase1_astar_footprint.png
python phase1_heatmaps.py      # Generates phase1_discovery_heatmap.png
python phase1_animation.py     # Interactive window (press SPACE to start)
```

### Generate All Phase 2 Outputs
```bash
python phase2_search.py        # BFS + footprint
python phase2_astar.py         # A* + footprint
python phase2_heatmaps.py      # Heatmap
python phase2_animation.py     # Animation
python phase2_compare.py       # Comparison with frontier overlay
```

### Generate All Phase 3 Outputs
```bash
python phase3_search.py        # BFS + footprint
python phase3_astar.py         # A* + footprint
python phase3_heatmaps.py      # Heatmap
python phase3_animation.py     # Animation
python phase3_compare.py       # Comparison with frontier overlay
```

### Run Full Benchmark Suite
```bash
python benchmarks/run_benchmarks.py
# Generates: benchmarks/results.csv
```

---

## File I/O Summary

### Generated PNG Files (Static Visualizations)
- `phase1_bfs_footprint.png` — BFS exploration comparison
- `phase1_astar_footprint.png` — A* exploration comparison
- `phase1_discovery_heatmap.png` — BFS vs A* discovery time
- (Similar for Phase 2 & 3)

### Generated CSV Files (Benchmark Data)
- `benchmarks/results.csv` — 150 rows, columns: phase, algorithm, run, time, nodes_expanded, heap_ops, path_len

### Console Output (All Scripts)
- Start/goal positions
- Path length
- Nodes explored
- Execution time
- Efficiency metrics

---

## Dependencies

### Required
- Python 3.6+
- Pygame (for animations)

### Optional
- NumPy (used by matplotlib)
- Matplotlib (for static PNG output)
- Pandas (for benchmark analysis)

### Installation
```bash
pip install pygame numpy matplotlib pandas
```

---

## Performance Characteristics

### Execution Time by Phase (Approximate)

| Phase | Grid | BFS | A* | Heatmap | Animation |
|-------|------|-----|-----|---------|-----------|
| 1 | 10×10 | <0.1ms | <0.1ms | <1s | <5s |
| 2 | 30×30 | ~3ms | ~2ms | <1s | ~15s |
| 3 | 50×40 | ~1ms | ~1ms | <1s | ~20s |

*Times are approximate and system-dependent.*

---

## Customization Guide

### Change Grid Sizes
Edit `config.py`:
```python
GRID_WIDTH = 15  # Instead of 10
GRID_HEIGHT = 15
TILE_SIZE = 48   # Smaller tiles for bigger grid
```

### Change Colors
Edit `config.py`:
```python
BFS_COLOR = (0, 0, 255)      # Blue instead
ASTAR_COLOR = (0, 255, 0)    # Green instead
WALL_COLOR = (50, 50, 50)    # Darker walls
```

### Change Animation Speed
Edit `config.py`:
```python
FPS = 60  # Faster animation (instead of 30)
```

### Use Different Heuristic (A*)
Edit `utils.py`, in `get_astar_path`:
```python
# Euclidean instead of Manhattan
h = ((goal[0] - x) ** 2 + (goal[1] - y) ** 2) ** 0.5
```

---

## Academic Use

### Citation Suggestion
```
AI Zombie Project: A Comparative Visualization and Metrics Framework
for BFS vs A* Pathfinding Algorithms

Features:
- Multi-phase grid analysis (10×10, 30×30, 50×40)
- Four distinct visualization methods
- Comprehensive metrics collection
- Benchmark harness with 50-trial runs
```

### Recommended Reading
1. Hart, Nilsson, Raphael (1968) - "A Formal Basis for the Heuristic Determination of Minimum Cost Paths"
2. Russell & Norvig (2020) - "Artificial Intelligence: A Modern Approach"

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No PNG files generated | Install matplotlib: `pip install matplotlib` |
| Pygame window doesn't appear | Check video device; use heatmap scripts on headless |
| Animation too slow | Increase FPS in config.py |
| Animation too fast | Decrease FPS in config.py |
| Memory issues on Phase 3 | Reduce grid size or use Phase 1 |
| CSV not generated | Install pandas: `pip install pandas` |

---

## Next Steps

1. **Run Phase 1** for a quick demo (instant execution)
2. **View generated PNG files** to see footprints and heatmaps
3. **Launch animations** to watch algorithms in action
4. **Study metrics** to understand efficiency gains
5. **Modify and experiment** with grid sizes, heuristics, colors

---

**For detailed documentation, see `VISUALIZATIONS.md` and `QUICK_START.md`**

Happy pathfinding! 🧟‍♂️✨
