# AI Zombie Project: Complete Visualization & Metrics Guide

## Overview

This project now includes **four complementary visualization types** to understand and compare BFS (Breadth-First Search) and A* pathfinding algorithms:

1. **Search Footprint (Static Plots)** — Side-by-side comparison of explored vs. final paths
2. **Discovery Time Heatmaps** — Color gradients showing the order of node exploration
3. **Step-by-Step Animation** — Interactive side-by-side animated exploration
4. **Metrics Overlay (Scorecard)** — Performance statistics on all visualizations

---

## File Organization

### Phase Scripts (Animated + Static Output)

Each phase has **6 core files**:

- `phase{N}_search.py` — BFS with Pygame animation + matplotlib static footprint + metrics
- `phase{N}_astar.py` — A* with Pygame animation + matplotlib static footprint + metrics
- `phase{N}_heatmaps.py` — Discovery time heatmaps (BFS vs A* side-by-side)
- `phase{N}_animation.py` — Step-by-step interactive animation (SPACE=play/pause)
- `phase{N}_compare.py` — Visual comparison with optional frontier overlay (F=toggle)

### Phase Sizes

| Phase | Grid Size | Tile Size | Description |
|-------|-----------|-----------|-------------|
| Phase 1 | 10×10 | 64px | Small grid, quick execution |
| Phase 2 | 30×30 | 20px | Medium grid, realistic maze |
| Phase 3 | 50×40 | 16px | Large grid, performance focus |

---

## 1. Search Footprint (Static Plots)

### What It Shows

**Left side:** Grid visualization
- **Light Blue** — BFS explored nodes (visited set)
- **Light Green** — A* explored nodes (more selective)
- **Bright Yellow** — Final shortest path
- **Green square** — Start position
- **Red square** — Goal position
- **Dark gray** — Walls

**Right side:** Metrics scorecard
- Path Length (steps)
- Nodes Explored (efficiency metric)
- Execution Time
- Efficiency % = (path_length / nodes_explored × 100)

### Files Generated

- `phase1_bfs_footprint.png` / `phase1_astar_footprint.png`
- `phase2_bfs_footprint.png` / `phase2_astar_footprint.png`
- `phase3_bfs_footprint.png` / `phase3_astar_footprint.png`

### How to Use

Run each phase script to automatically generate the footprint:

```bash
python phase1_search.py    # Generates phase1_bfs_footprint.png
python phase1_astar.py     # Generates phase1_astar_footprint.png
```

### Academic Use Case

This is the most common visualization in pathfinding papers. **BFS will show a large circular explored area** (explores evenly in all directions), while **A* will show a narrow beam toward the goal**.

---

## 2. Discovery Time Heatmaps

### What It Shows

**Viridis color gradient** (dark = early discovery, bright = late discovery)

- **BFS:** Perfect concentric circles expanding from start
- **A*:** Elongated beam stretching toward goal

This directly visualizes the **priority function** $f(n) = g(n) + h(n)$:
- **BFS**: $h(n) ≈ 0$, so $f(n) = g(n)$ (distance from start only)
- **A***: $h(n)$ = heuristic distance to goal, guides search efficiently

### Files Generated

- `phase1_discovery_heatmap.png`
- `phase2_discovery_heatmap.png`
- `phase3_discovery_heatmap.png`

### How to Use

```bash
python phase1_heatmaps.py   # Side-by-side discovery gradient
python phase2_heatmaps.py
python phase3_heatmaps.py
```

### Academic Use Case

This visualization is powerful for explaining **why A* is faster**: it shows the exploration pattern is strategically biased toward the goal.

---

## 3. Step-by-Step Animation

### What It Shows

**Interactive Pygame window** with side-by-side BFS vs A* exploration:
- **Light Blue** (BFS side) — Explored nodes
- **Light Green** (A* side) — Explored nodes
- **Cyan** — Final shortest path (overlaid)

### Controls

| Key | Action |
|-----|--------|
| **SPACE** | Play/Pause animation |
| **LEFT** | Step backward (when paused) |
| **RIGHT** | Step forward (when paused) |
| **ESC** | Quit |

### Files

- `phase1_animation.py` (10×10, fast)
- `phase2_animation.py` (30×30, medium)
- `phase3_animation.py` (50×40, large)

### How to Use

```bash
python phase1_animation.py
# Window opens; press SPACE to start animation
# Watch how BFS fills uniformly while A* focuses on the goal direction
```

### Academic Use Case

**The "aha moment!"** — Watching BFS slowly crawl through every corridor while A* ignores dead ends is the most convincing demonstration of algorithmic efficiency.

---

## 4. Metrics Overlay (Scorecard)

### Data Captured

All visualizations include a **metrics scorecard**:

```
Path Length:      [number of steps in final path]
Nodes Explored:   [size of closed set]
Execution Time:   [milliseconds to run]
Efficiency %:     [path_length / nodes_explored × 100]
```

### Interpretation

| Metric | Meaning |
|--------|---------|
| **Path Length** | Same for BFS & A* (both find shortest path) |
| **Nodes Explored** | Efficiency measure; A* should be much lower |
| **Execution Time** | Wall-clock performance (varies by system) |
| **Efficiency %** | Higher is better (tight path relative to exploration) |

### Example Output

```
BFS Search Metrics (30x30 Grid)
=====================================
Path Length:      55 steps
Nodes Explored:   820
Execution Time:   0.003542 seconds
Efficiency:       6.71%

A* Search Metrics (30x30 Grid)
=====================================
Path Length:      55 steps
Nodes Explored:   115
Execution Time:   0.001890 seconds
Efficiency:       47.83%
```

---

## Running All Visualizations for a Phase

### Quick Script: Generate All Phase 2 Visualizations

```bash
#!/bin/bash
echo "=== Phase 2 Footprints ==="
python phase2_search.py
python phase2_astar.py

echo "=== Phase 2 Heatmaps ==="
python phase2_heatmaps.py

echo "=== Phase 2 Animation ==="
# Run with -i flag or in IDE so window stays open
python phase2_animation.py
```

### Output Files

After running all scripts:
- `phase2_bfs_footprint.png` — Static BFS comparison
- `phase2_astar_footprint.png` — Static A* comparison
- `phase2_discovery_heatmap.png` — Discovery time gradient

---

## Detailed Feature Comparison

| Feature | Footprint | Heatmap | Animation | Compare |
|---------|-----------|---------|-----------|---------|
| Static plot | ✓ | ✓ | ✗ | ✓ |
| Interactive | ✗ | ✗ | ✓ | ✓ |
| Metrics overlay | ✓ | ✗ | ✗ | ✓ |
| Frontier visualization | ✗ | ✗ | ✗ | ✓ (F key) |
| Discovery order | ✗ | ✓ | ✗ | ✗ |
| Real-time animation | ✗ | ✗ | ✓ | ✓ |

---

## Performance Tuning

### Matplotlib Performance Issues?

If heatmaps or footprints are slow on your system:

1. **Install Matplotlib Optimally:**
   ```bash
   pip install --upgrade matplotlib
   ```

2. **Use a Faster Backend:**
   Edit the top of heatmap/footprint files:
   ```python
   import matplotlib
   matplotlib.use('Agg')  # Non-interactive backend
   import matplotlib.pyplot as plt
   ```

3. **Reduce DPI** (trades quality for speed):
   ```python
   plt.savefig('output.png', dpi=72)  # Default is 100
   ```

### Pygame Window Too Large?

Modify `TILE_SIZE` in `config.py`:
- Phase 1: `TILE_SIZE = 32` (instead of 64) makes 10×10 fit smaller screen
- Phase 2: `TILE_SIZE_LARGE = 10` (instead of 20) makes 30×30 more compact
- Phase 3: `TILE_SIZE_XLARGE = 8` (instead of 16) makes 50×40 fit standard 1080p

---

## Math Behind the Visualizations

### BFS Cost Function
$$f(n) = g(n)$$

Where $g(n)$ is the distance from start. Explores uniformly in all directions.

### A* Cost Function
$$f(n) = g(n) + h(n)$$

Where:
- $g(n)$ = distance from start (same as BFS)
- $h(n)$ = heuristic estimate to goal (Manhattan distance)

**A* advantage:** The heuristic $h(n)$ biases exploration toward the goal.

### Efficiency Metric
$$\text{Efficiency \%} = \frac{\text{Path Length}}{\text{Nodes Explored}} \times 100$$

Higher is better. A* typically achieves 40-80%, while BFS struggles at 5-15%.

---

## Troubleshooting

### "Matplotlib not available"
Install it:
```bash
pip install matplotlib
```

### "pygame.error: No available video device"
You're on a headless system. Use only heatmap/footprint scripts (no Pygame animations):
```bash
python phase1_heatmaps.py     # Works on headless
python phase1_animation.py    # Will fail
```

### Animations run too fast
Reduce FPS in `config.py`:
```python
FPS = 15  # Default is 30
```

### Grid coordinates seem inverted
The code uses **(x, y)** where **x = column, y = row**. Arrays are indexed as `grid[row][col]`.

---

## Summary of Visualizations

| Goal | Visualization | File | Best For |
|------|---------------|------|----------|
| Compare BFS vs A* | Footprint + Metrics | `phase*_search.py` | Static analysis, papers |
| See exploration pattern | Heatmap | `phase*_heatmaps.py` | Understanding algorithm bias |
| Watch it in action | Animation | `phase*_animation.py` | Teaching, intuition |
| Overlay frontiers | Compare | `phase*_compare.py` | Advanced analysis |

---

## Next Steps

1. **Run Phase 1** to see the difference on a small grid:
   ```bash
   python phase1_search.py
   python phase1_astar.py
   python phase1_heatmaps.py
   ```

2. **Examine the PNG files** generated in your project directory.

3. **Launch animations** to watch BFS vs A* in real-time:
   ```bash
   python phase2_animation.py
   ```

4. **Use metrics** to quantify efficiency gains of A* over BFS.

---

**Happy pathfinding!**
