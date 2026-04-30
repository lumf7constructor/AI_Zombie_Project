"""
Comprehensive comparison of Phase 2 minimax algorithms.
Runs all 4 scenarios and generates metrics/visualizations.
"""

import sys
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    GRID_LARGE,
    GRID_WIDTH_LARGE,
    GRID_HEIGHT_LARGE,
    PLAYER_START_POS_LARGE,
    GOAL_POS_LARGE,
)
from utils import get_minimax_path, get_astar_path


@dataclass
class GameMetrics:
    """Stores metrics from a single game scenario."""
    scenario_name: str
    winner: Optional[str]  # "prey", "monster", or None if timeout
    steps_to_end: int
    computation_time: float
    prey_path_length: int
    monster_path_length: int
    total_nodes_evaluated: int
    prey_nodes_expanded: int  # actual nodes expanded by prey's algorithm
    monster_nodes_expanded: int  # actual nodes expanded by monster's algorithm
    total_path_calls: int  # total number of times pathfinding was called


class GameSimulator:
    """Simulates a game scenario without pygame visualization."""

    def __init__(
        self,
        scenario_name: str,
        prey_algorithm,
        monster_algorithm,
        prey_depth=None,
        monster_depth=None,
        prey_lookahead=None,
        max_steps=1000,
    ):
        self.scenario_name = scenario_name
        self.prey_algorithm = prey_algorithm
        self.monster_algorithm = monster_algorithm
        self.prey_depth = prey_depth
        self.monster_depth = monster_depth
        self.prey_lookahead = prey_lookahead
        self.max_steps = max_steps

        # Game state
        self.prey_pos = list(PLAYER_START_POS_LARGE)
        self.monster_pos = [GRID_WIDTH_LARGE - 2, GRID_HEIGHT_LARGE - 2]
        self.reward_pos = list(GOAL_POS_LARGE)

        self.step_count = 0
        self.result = None
        self.metrics = None
        
        # Track nodes expanded per agent
        self.prey_nodes_expanded = []
        self.monster_nodes_expanded = []

    def _get_prey_path(self) -> List[Tuple[int, int]]:
        """Get prey's next path based on algorithm."""
        if self.prey_algorithm == "minimax":
            path, info = get_minimax_path(
                tuple(self.prey_pos),
                tuple(self.reward_pos),
                GRID_LARGE,
                depth=self.prey_depth,
                return_info=True,  # Get detailed metrics
            )
            self.prey_nodes_expanded.append(info.get("nodes_expanded", 0))
            return path
        elif self.prey_algorithm == "astar":
            path = get_astar_path(
                tuple(self.prey_pos),
                tuple(self.reward_pos),
                GRID_LARGE,
            )
            self.prey_nodes_expanded.append(len(path))  # A* path length as proxy
            return path
        return []

    def _get_monster_path(self) -> List[Tuple[int, int]]:
        """Get monster's next path based on algorithm."""
        if self.monster_algorithm == "minimax":
            path, info = get_minimax_path(
                tuple(self.monster_pos),
                tuple(self.prey_pos),
                GRID_LARGE,
                depth=self.monster_depth,
                return_info=True,  # Get detailed metrics
            )
            self.monster_nodes_expanded.append(info.get("nodes_expanded", 0))
            return path
        elif self.monster_algorithm == "astar":
            path = get_astar_path(
                tuple(self.monster_pos),
                tuple(self.prey_pos),
                GRID_LARGE,
            )
            self.monster_nodes_expanded.append(len(path))  # A* path length as proxy
            return path
        return []

    def run(self) -> GameMetrics:
        """Run the simulation and collect metrics."""
        start_time = time.time()
        prey_paths_computed = []
        monster_paths_computed = []
        
        try:
            while self.step_count < self.max_steps:
                # Get paths (now tracking nodes expanded)
                prey_path = self._get_prey_path()
                monster_path = self._get_monster_path()

                if prey_path:
                    prey_paths_computed.append(len(prey_path))
                if monster_path:
                    monster_paths_computed.append(len(monster_path))

                # Move agents
                if len(prey_path) > 1:
                    self.prey_pos = list(prey_path[1])
                if len(monster_path) > 1:
                    self.monster_pos = list(monster_path[1])

                self.step_count += 1

                # Check conditions
                if self.prey_pos == self.reward_pos:
                    self.result = "prey"
                    break
                if self.monster_pos == self.prey_pos:
                    self.result = "monster"
                    break
        except Exception as e:
            print(f"  ⚠️  Error in {self.scenario_name}: {e}")
            self.result = None

        computation_time = time.time() - start_time

        # Create metrics
        self.metrics = GameMetrics(
            scenario_name=self.scenario_name,
            winner=self.result,
            steps_to_end=self.step_count,
            computation_time=computation_time,
            prey_path_length=sum(prey_paths_computed) if prey_paths_computed else 0,
            monster_path_length=sum(monster_paths_computed) if monster_paths_computed else 0,
            total_nodes_evaluated=sum(prey_paths_computed) + sum(monster_paths_computed),
            prey_nodes_expanded=sum(self.prey_nodes_expanded) if self.prey_nodes_expanded else 0,
            monster_nodes_expanded=sum(self.monster_nodes_expanded) if self.monster_nodes_expanded else 0,
            total_path_calls=len(self.prey_nodes_expanded) + len(self.monster_nodes_expanded),
        )

        return self.metrics


def run_all_scenarios() -> List[GameMetrics]:
    """Run all 4 phase2 scenarios and collect metrics."""
    scenarios = []

    # Scenario 1: minimax_game.py - Both players use MINIMAX with depth 60
    print("Running: minimax_game (Both MINIMAX, depth 60)...")
    sim1 = GameSimulator(
        scenario_name="Both MINIMAX (d=60)",
        prey_algorithm="minimax",
        monster_algorithm="minimax",
        prey_depth=60,
        monster_depth=60,
        max_steps=500,
    )
    scenarios.append(sim1.run())

    # Scenario 2: minimax_ambush_monster.py - Monster uses MINIMAX with lookahead on prey
    print("Running: minimax_ambush_monster (Monster strategic, Prey A*)...")
    sim2 = GameSimulator(
        scenario_name="Ambush Monster",
        prey_algorithm="astar",
        monster_algorithm="minimax",
        monster_depth=8,
        max_steps=500,
    )
    scenarios.append(sim2.run())

    # Scenario 3: minimax_both_players.py - Both use MINIMAX with shallow depth
    print("Running: minimax_both_players (Both MINIMAX, d=3)...")
    sim3 = GameSimulator(
        scenario_name="Both MINIMAX (d=3)",
        prey_algorithm="minimax",
        monster_algorithm="minimax",
        prey_depth=3,
        monster_depth=3,
        max_steps=500,
    )
    scenarios.append(sim3.run())

    # Scenario 4: minimax_evasive_prey.py - Prey uses MINIMAX, monster uses A*
    print("Running: minimax_evasive_prey (Prey MINIMAX, Monster A*)...")
    sim4 = GameSimulator(
        scenario_name="Evasive Prey",
        prey_algorithm="minimax",
        monster_algorithm="astar",
        prey_depth=2,
        max_steps=500,
    )
    scenarios.append(sim4.run())

    return scenarios


def print_comparison_table(metrics_list: List[GameMetrics]):
    """Print a formatted comparison table."""
    print("\n" + "=" * 140)
    print("ALGORITHM COMPARISON METRICS")
    print("=" * 140)
    print(
        f"{'Scenario':<25} | {'Result':<10} | {'Steps':<6} | {'Time':<8} | {'Prey Path':<10} | {'Monster Path':<12} | {'Prey Nodes':<12} | {'Monster Nodes':<14} | {'Total Calls':<11}"
    )
    print("-" * 140)

    for m in metrics_list:
        result_str = m.winner.upper() if m.winner else "TIMEOUT"
        print(
            f"{m.scenario_name:<25} | {result_str:<10} | {m.steps_to_end:<6} | {m.computation_time:<8.4f} | {m.prey_path_length:<10} | {m.monster_path_length:<12} | {m.prey_nodes_expanded:<12} | {m.monster_nodes_expanded:<14} | {m.total_path_calls:<11}"
        )

    print("=" * 140)
    print("\n📊 METRIC DEFINITIONS:")
    print("  • Steps: Number of game turns until outcome")
    print("  • Time: Total simulation time (seconds)")
    print("  • Prey/Monster Path: Sum of path lengths computed during game")
    print("  • Prey/Monster Nodes: Actual nodes expanded by each algorithm during all pathfinding calls")
    print("  • Total Calls: Total number of pathfinding function calls (Prey + Monster)")
    print()



def generate_visualizations(metrics_list: List[GameMetrics]):
    """Generate simple matplotlib visualizations."""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("⚠️  matplotlib not installed. Skipping visualizations.")
        return

    scenarios = [m.scenario_name for m in metrics_list]
    steps = [m.steps_to_end for m in metrics_list]
    times = [m.computation_time for m in metrics_list]
    prey_nodes = [m.prey_nodes_expanded for m in metrics_list]
    monster_nodes = [m.monster_nodes_expanded for m in metrics_list]
    winners = [m.winner for m in metrics_list]

    # Create figure with 3 subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Phase 2: Minimax Algorithm Comparison", fontsize=16, fontweight="bold")

    # 1. Steps to completion
    ax = axes[0, 0]
    colors = ["green" if w == "prey" else "red" for w in winners]
    ax.bar(scenarios, steps, color=colors, alpha=0.7, edgecolor="black")
    ax.set_ylabel("Steps to Completion", fontweight="bold")
    ax.set_title("Game Duration (Steps)")
    ax.grid(axis="y", alpha=0.3)
    for i, (s, v) in enumerate(zip(scenarios, steps)):
        ax.text(i, v + 2, str(v), ha="center", fontweight="bold")

    # 2. Computation time
    ax = axes[0, 1]
    ax.bar(scenarios, times, color="steelblue", alpha=0.7, edgecolor="black")
    ax.set_ylabel("Time (seconds)", fontweight="bold")
    ax.set_title("Computational Time")
    ax.grid(axis="y", alpha=0.3)
    for i, (s, v) in enumerate(zip(scenarios, times)):
        ax.text(i, v + 0.001, f"{v:.4f}s", ha="center", fontweight="bold", fontsize=9)

    # 3. Nodes expanded per agent
    ax = axes[1, 0]
    x = np.arange(len(scenarios))
    width = 0.35
    ax.bar(x - width/2, prey_nodes, width, label="Prey Nodes Expanded", alpha=0.7, edgecolor="black")
    ax.bar(x + width/2, monster_nodes, width, label="Monster Nodes Expanded", alpha=0.7, edgecolor="black")
    ax.set_ylabel("Nodes Expanded", fontweight="bold")
    ax.set_title("Algorithm Complexity (Nodes Expanded)")
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, rotation=15, ha='right')
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # 4. Summary text
    ax = axes[1, 1]
    ax.axis("off")
    summary_text = "COMPARISON SUMMARY:\n" + "-" * 40 + "\n"
    for scenario, winner, calls in zip(scenarios, winners, [m.total_path_calls for m in metrics_list]):
        emoji = "✓ PREY" if winner == "prey" else "✗ MONSTER" if winner == "monster" else "⏱️ TIMEOUT"
        summary_text += f"{scenario}: {emoji}\n  ({calls} pathfinding calls)\n"
    summary_text += "\n" + "-" * 40 + "\n"
    summary_text += f"Avg Time: {np.mean(times):.4f}s\n"
    summary_text += f"Avg Steps: {np.mean(steps):.1f}\n"
    summary_text += f"Total Pathfinding Calls: {sum(m.total_path_calls for m in metrics_list)}\n"

    ax.text(
        0.1,
        0.95,
        summary_text,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        fontfamily="monospace",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )

    plt.tight_layout()
    plt.savefig("/home/lum/AI_Zombie_Project/phase2/comparison_metrics.png", dpi=100)
    print("✓ Saved visualization: comparison_metrics.png")
    plt.close()

    # Create detailed nodes comparison chart
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(scenarios))
    width = 0.25

    bars1 = ax.bar(x - width, prey_nodes, width, label="Prey Nodes Expanded", alpha=0.8, edgecolor="blue")
    bars2 = ax.bar(x, monster_nodes, width, label="Monster Nodes Expanded", alpha=0.8, edgecolor="red")
    total_nodes = [p + m for p, m in zip(prey_nodes, monster_nodes)]
    bars3 = ax.bar(x + width, total_nodes, width, label="Total Nodes", alpha=0.8, edgecolor="black")

    ax.set_xlabel("Scenario", fontweight="bold")
    ax.set_ylabel("Nodes Expanded", fontweight="bold")
    ax.set_title("Algorithm Complexity Comparison (Actual Nodes Expanded)", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, rotation=15, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # Add value labels on bars
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    plt.savefig("/home/lum/AI_Zombie_Project/phase2/nodes_complexity.png", dpi=100)
    print("✓ Saved visualization: nodes_complexity.png")
    plt.close()


def main():
    print("\n" + "=" * 100)
    print("PHASE 2: MINIMAX ALGORITHM COMPARISON")
    print("=" * 100 + "\n")

    # Run all scenarios
    metrics_list = run_all_scenarios()

    # Print table
    print_comparison_table(metrics_list)

    # Generate visualizations
    print("Generating visualizations...")
    generate_visualizations(metrics_list)

    print("\n✓ Comparison complete!")
    print("  - Metrics table printed above")
    print("  - Visualizations saved to phase2/ folder")


if __name__ == "__main__":
    main()
