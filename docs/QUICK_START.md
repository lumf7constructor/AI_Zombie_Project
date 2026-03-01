# Quick Reference: Available Visualization Scripts

## Animation + Metrics Generation (Run these to see both Pygame + PNG output)

### Phase 1 (10×10 Small Grid)
```bash
python phase1_search.py      # BFS animation + footprint PNG + metrics
python phase1_astar.py       # A* animation + footprint PNG + metrics
```

### Phase 2 (30×30 Medium Grid)
```bash
python phase2_search.py      # BFS animation + footprint PNG + metrics
python phase2_astar.py       # A* animation + footprint PNG + metrics
```

### Phase 3 (50×40 Large Grid)
```bash
python phase3_search.py      # BFS animation + footprint PNG + metrics
python phase3_astar.py       # A* animation + footprint PNG + metrics
```

---

## Discovery Time Heatmaps (Color gradient: dark=early, bright=late)

### Phase 1 (10×10)
```bash
python phase1_heatmaps.py    # Side-by-side viridis gradient
# Output: phase1_discovery_heatmap.png
```

### Phase 2 (30×30)
```bash
python phase2_heatmaps.py    # Shows BFS radial vs A* focused beam
# Output: phase2_discovery_heatmap.png
```

### Phase 3 (50×40)
```bash
python phase3_heatmaps.py    # Large-scale comparison
# Output: phase3_discovery_heatmap.png
```

---

## Side-by-Side Comparison with Frontier Overlay

### Phase 2 (30×30)
```bash
python phase2_compare.py
# Controls: F=toggle frontier overlay, ESC=quit
# Shows: BFS-only (blue), A*-only (green), common path (yellow)
```

### Phase 3 (50×40)
```bash
python phase3_compare.py
# Same controls as Phase2 but on larger grid
```

---

## All Benchmark Results

```bash
python benchmarks/run_benchmarks.py
# Generates: benchmarks/results.csv (50 trials per algorithm per phase)
# Prints summary statistics to console
```

---

## Generated Output Files

### Footprint PNG Files (Static)
- `phase1_bfs_footprint.png` — BFS exploration vs final path
- `phase1_astar_footprint.png` — A* exploration vs final path
- `phase2_bfs_footprint.png`
- `phase2_astar_footprint.png`
- `phase3_bfs_footprint.png`
- `phase3_astar_footprint.png`

### Heatmap PNG Files (Discovery Order)
- `phase1_discovery_heatmap.png` — Color gradient over time
- `phase2_discovery_heatmap.png` — Concentric circles (BFS) vs beam (A*)
- `phase3_discovery_heatmap.png` — Large-scale pattern comparison

### CSV Results
- `benchmarks/results.csv` — 150 trial results (50 each: BFS, A*, A* fast)

---

## Quick Demo (5 minutes)

```bash
# 1. See BFS vs A* on a small grid (instant)
python phase1_search.py
python phase1_astar.py
# Look at: phase1_bfs_footprint.png and phase1_astar_footprint.png

# 2. Watch them explore in real-time (30 seconds each)
python phase1_animation.py    # Press SPACE, watch circles form
# Then Ctrl+C

python phase1_heatmaps.py     # Shows color gradient
# Look at: phase1_discovery_heatmap.png

# 3. See metrics printed to console for all phases
python benchmarks/run_benchmarks.py
```

---

## File Sizes & Execution Times (Approximate)

| Script | Grid | Pygame Window | PNG Gen | Total Time |
|--------|------|---------------|---------|------------|
| phase1_search.py | 10×10 | Instant | <1s | <2s |
| phase1_astar.py | 10×10 | Instant | <1s | <2s |
| phase1_heatmaps.py | 10×10 | N/A | <1s | <1s |
| phase1_animation.py | 10×10 | ~5s (interactive) | N/A | Varies |
| phase2_search.py | 30×30 | ~2s | <1s | <3s |
| phase2_animation.py | 30×30 | ~15s (interactive) | N/A | Varies |
| phase3_search.py | 50×40 | ~1s | <1s | <2s |
| phase3_animation.py | 50×40 | ~20s (interactive) | N/A | Varies |

---

## Troubleshooting

### "Matplotlib not available" or no PNG files generated
```bash
pip install matplotlib
```

### Pygame window doesn't appear
- Check you're not on a headless system
- Try heatmap scripts instead (no GUI required)

### Animation runs too fast
Edit `config.py` and lower `FPS`:
```python
FPS = 15  # Instead of 30
```

### Large grid animations lag
- Use Phase 1 (10×10) for smooth animation
- Or reduce `TILE_SIZE_LARGE` in `config.py`

---

## Key Insights from Visualizations

1. **Footprints:** BFS explores a huge circle; A* explores a narrow beam
2. **Heatmaps:** BFS is concentric circles; A* gradients toward goal
3. **Animations:** BFS is methodical; A* is focused
4. **Metrics:** A* explores 5-10× fewer nodes with same path length

---

See `VISUALIZATIONS.md` for detailed documentation.
