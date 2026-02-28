"""
Benchmark runner for AI_Zombie_Project.
Generates CSV results and PNG summary plots.

Usage: python3 benchmarks/run_benchmarks.py

Outputs:
 - benchmarks/results.csv
 - benchmarks/plots_time.png
 - benchmarks/plots_nodes.png
"""
import time
import csv
import statistics
from pathlib import Path
import sys

# Ensure repository root is on sys.path so we can import config and utils
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import (
    GRID_LARGE, PLAYER_START_POS_LARGE, GOAL_POS_LARGE,
    GRID_XLARGE, PLAYER_START_POS_XLARGE, GOAL_POS_XLARGE,
)
from utils import get_bfs_path, get_astar_path, get_astar_path_fast

try:
    import matplotlib.pyplot as plt
    import pandas as pd
    HAS_PLOTTING = True
except Exception:
    plt = None
    pd = None
    HAS_PLOTTING = False

OUT_DIR = Path(__file__).parent
OUT_DIR.mkdir(parents=True, exist_ok=True)
CSV_PATH = OUT_DIR / "results.csv"
PLOT_TIME = OUT_DIR / "plots_time.png"
PLOT_NODES = OUT_DIR / "plots_nodes.png"

TRIALS = 50

phases = [
    ("phase2", GRID_LARGE, PLAYER_START_POS_LARGE, GOAL_POS_LARGE),
    ("phase3", GRID_XLARGE, PLAYER_START_POS_XLARGE, GOAL_POS_XLARGE),
]

algos = [
    ("bfs", get_bfs_path),
    ("astar", get_astar_path),
    ("astar_fast", get_astar_path_fast),
]

rows = []
print(f"Running {TRIALS} trials per algorithm per phase...")
for phase_name, grid, start, goal in phases:
    for alg_name, func in algos:
        print(f"Phase={phase_name} Alg={alg_name}")
        for i in range(TRIALS):
            s = start.copy(); g = goal.copy()
            t0 = time.time()
            try:
                res = func(s, g, grid, return_info=True)
                if isinstance(res, tuple) and len(res) >= 2:
                    path, info = res
                else:
                    path = res
                    info = {}
            except TypeError:
                path = func(s, g, grid)
                info = {}
            t = time.time() - t0
            rows.append({
                "phase": phase_name,
                "algorithm": alg_name,
                "run": i,
                "time": t,
                "nodes_expanded": info.get("nodes_expanded", 0),
                "heap_ops": info.get("heap_ops", 0),
                "path_len": len(path) if path else 0,
            })

# Write CSV
with open(CSV_PATH, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
print(f"Wrote results to {CSV_PATH}")
if HAS_PLOTTING:
    # Load into pandas and plot summary
    df = pd.DataFrame(rows)

    summary = df.groupby(["phase", "algorithm"]).agg({
        "time": ["mean", "std"],
        "nodes_expanded": ["mean", "std"],
        "path_len": ["mean"],
    }).reset_index()

    # Time plot
    fig, ax = plt.subplots(figsize=(8, 4))
    for phase_name in df['phase'].unique():
        sub = summary[summary['phase'] == phase_name]
        algs = sub['algorithm']
        means = sub[('time', 'mean')]
        errs = sub[('time', 'std')]
        ax.errorbar([f"{phase_name}\n{a}" for a in algs], means, yerr=errs, fmt='o', label=phase_name)
    ax.set_ylabel('time (s)')
    ax.set_title('Mean time per algorithm (with std)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    fig.savefig(PLOT_TIME)
    print(f"Wrote time plot to {PLOT_TIME}")

    # Nodes plot
    fig, ax = plt.subplots(figsize=(8, 4))
    for phase_name in df['phase'].unique():
        sub = summary[summary['phase'] == phase_name]
        algs = sub['algorithm']
        means = sub[('nodes_expanded', 'mean')]
        errs = sub[('nodes_expanded', 'std')]
        ax.errorbar([f"{phase_name}\n{a}" for a in algs], means, yerr=errs, fmt='o', label=phase_name)
    ax.set_ylabel('nodes expanded')
    ax.set_title('Mean nodes expanded per algorithm (with std)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    fig.savefig(PLOT_NODES)
    print(f"Wrote nodes plot to {PLOT_NODES}")
else:
    print("matplotlib / pandas not available: CSV written but plots were skipped. Install requirements from requirements.txt to enable plotting.")

print('Done.')
