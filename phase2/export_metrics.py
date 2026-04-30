"""
Generate CSV data and simple ASCII dashboard for Phase 2 comparison.
"""

import sys
import os
import csv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phase2.compare_algorithms import run_all_scenarios


def create_csv_export(metrics_list):
    """Export metrics to CSV file."""
    csv_path = "/home/lum/AI_Zombie_Project/phase2/metrics.csv"
    
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Scenario",
            "Winner",
            "Steps",
            "Computation_Time_s",
            "Prey_Path_Length",
            "Monster_Path_Length",
            "Prey_Nodes_Expanded",
            "Monster_Nodes_Expanded",
            "Total_Nodes_Expanded",
            "Total_Pathfinding_Calls",
        ])
        
        for m in metrics_list:
            writer.writerow([
                m.scenario_name,
                m.winner or "TIMEOUT",
                m.steps_to_end,
                f"{m.computation_time:.6f}",
                m.prey_path_length,
                m.monster_path_length,
                m.prey_nodes_expanded,
                m.monster_nodes_expanded,
                m.prey_nodes_expanded + m.monster_nodes_expanded,
                m.total_path_calls,
            ])
    
    print(f"✓ CSV exported to: {csv_path}")
    return csv_path


def create_ascii_dashboard(metrics_list):
    """Create ASCII art dashboard."""
    dashboard = "\n"
    dashboard += "╔" + "═" * 98 + "╗\n"
    dashboard += "║" + " " * 20 + "PHASE 2: MINIMAX ALGORITHMS COMPARISON DASHBOARD" + " " * 30 + "║\n"
    dashboard += "╚" + "═" * 98 + "╝\n\n"

    # Stats box
    dashboard += "┌─ RESULTS ─────────────────────────────────────────────────────────────────────────────┐\n"
    for i, m in enumerate(metrics_list, 1):
        winner_emoji = "🟢 PREY" if m.winner == "prey" else "🔴 MONSTER" if m.winner == "monster" else "⏱️  TIMEOUT"
        dashboard += f"│ {i}. {m.scenario_name:<30} {winner_emoji:<30} Steps: {m.steps_to_end:<5} │\n"
    dashboard += "└────────────────────────────────────────────────────────────────────────────────────────┘\n\n"

    # Speed comparison
    dashboard += "┌─ COMPUTATIONAL EFFICIENCY ────────────────────────────────────────────────────────────┐\n"
    max_time = max(m.computation_time for m in metrics_list)
    for m in metrics_list:
        bar_len = int((m.computation_time / max_time) * 40) if max_time > 0 else 0
        bar = "█" * bar_len + "░" * (40 - bar_len)
        dashboard += f"│ {m.scenario_name:<30} {bar} {m.computation_time:.4f}s │\n"
    dashboard += "└────────────────────────────────────────────────────────────────────────────────────────┘\n\n"

    # Game length
    dashboard += "┌─ GAME LENGTH (STEPS) ─────────────────────────────────────────────────────────────────┐\n"
    max_steps = max(m.steps_to_end for m in metrics_list)
    for m in metrics_list:
        bar_len = int((m.steps_to_end / max_steps) * 40) if max_steps > 0 else 0
        bar = "█" * bar_len + "░" * (40 - bar_len)
        dashboard += f"│ {m.scenario_name:<30} {bar} {m.steps_to_end:<3} steps │\n"
    dashboard += "└────────────────────────────────────────────────────────────────────────────────────────┘\n\n"

    # AI complexity
    dashboard += "┌─ AI COMPLEXITY (NODES EVALUATED) ─────────────────────────────────────────────────────┐\n"
    max_nodes = max(m.total_nodes_evaluated for m in metrics_list) if max(m.total_nodes_evaluated for m in metrics_list) > 0 else 1
    for m in metrics_list:
        if m.total_nodes_evaluated > 0:
            bar_len = int((m.total_nodes_evaluated / max_nodes) * 40)
        else:
            bar_len = 0
        bar = "█" * bar_len + "░" * (40 - bar_len)
        dashboard += f"│ {m.scenario_name:<30} {bar} {m.total_nodes_evaluated:<5} │\n"
    dashboard += "└────────────────────────────────────────────────────────────────────────────────────────┘\n\n"

    return dashboard


def save_ascii_dashboard(metrics_list):
    """Save ASCII dashboard to file."""
    dashboard = create_ascii_dashboard(metrics_list)
    
    dashboard_path = "/home/lum/AI_Zombie_Project/phase2/DASHBOARD.txt"
    with open(dashboard_path, "w") as f:
        f.write(dashboard)
    
    print(dashboard)
    print(f"✓ Dashboard saved to: {dashboard_path}")


def main():
    print("\n🔄 Generating comparison metrics...\n")
    metrics_list = run_all_scenarios()
    
    print("\n" + "=" * 100)
    print("EXPORTING DATA AND VISUALIZATIONS")
    print("=" * 100 + "\n")
    
    # Create CSV
    create_csv_export(metrics_list)
    
    # Create ASCII dashboard
    save_ascii_dashboard(metrics_list)
    
    print("\n✅ All exports complete!")
    print("\nGenerated files:")
    print("  • metrics.csv - Raw data in CSV format")
    print("  • DASHBOARD.txt - ASCII visualization")
    print("  • COMPARISON_RESULTS.txt - Detailed report")
    print("  • comparison_metrics.png - Chart 1")
    print("  • efficiency_comparison.png - Chart 2")


if __name__ == "__main__":
    main()
