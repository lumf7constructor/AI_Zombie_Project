"""
Simple text-based and visual summary of Phase 2 algorithm comparison.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phase2.compare_algorithms import run_all_scenarios, print_comparison_table


def create_summary_report(metrics_list):
    """Create a detailed summary report."""
    
    report = "\n" + "=" * 100 + "\n"
    report += "PHASE 2 ALGORITHM COMPARISON - SUMMARY REPORT\n"
    report += "=" * 100 + "\n\n"

    # Key findings
    report += "📊 KEY FINDINGS:\n"
    report += "-" * 100 + "\n"

    prey_wins = sum(1 for m in metrics_list if m.winner == "prey")
    monster_wins = sum(1 for m in metrics_list if m.winner == "monster")
    
    report += f"✓ Prey Victories: {prey_wins}/4\n"
    report += f"✗ Monster Victories: {monster_wins}/4\n\n"

    # Fastest computation
    fastest = min(metrics_list, key=lambda m: m.computation_time)
    report += f"⚡ Fastest: {fastest.scenario_name} ({fastest.computation_time:.4f}s)\n"
    
    # Most efficient (fewest steps)
    shortest = min(metrics_list, key=lambda m: m.steps_to_end)
    report += f"📍 Shortest Game: {shortest.scenario_name} ({shortest.steps_to_end} steps)\n\n"

    # Scenario breakdown
    report += "\n📋 DETAILED BREAKDOWN:\n"
    report += "-" * 100 + "\n\n"

    scenarios_info = {
        "Both MINIMAX (d=60)": {
            "description": "Both agents use MINIMAX with depth 60 (deep lookahead)",
            "strategy": "Symmetrical AI competition - both players play optimally far ahead",
            "expected": "Balanced, but monster usually wins (better positioned)",
        },
        "Ambush Monster": {
            "description": "Monster uses MINIMAX depth 8, Prey uses A*",
            "strategy": "Monster strategically predicts prey behavior, prey uses simple pathfinding",
            "expected": "Monster has advantage due to strategic lookahead",
        },
        "Both MINIMAX (d=3)": {
            "description": "Both agents use MINIMAX with shallow depth 3",
            "strategy": "Limited lookahead - myopic decision making",
            "expected": "Unpredictable, shorter computation times",
        },
        "Evasive Prey": {
            "description": "Prey uses MINIMAX depth 2, Monster uses A*",
            "strategy": "Prey tries to evade, monster uses simple pathfinding",
            "expected": "Monster might catch prey as monster doesn't plan ahead",
        },
    }

    for m in metrics_list:
        info = scenarios_info.get(m.scenario_name, {})
        report += f"🎮 {m.scenario_name}\n"
        report += f"   Description: {info.get('description', 'N/A')}\n"
        report += f"   Strategy: {info.get('strategy', 'N/A')}\n"
        report += f"   Result: {m.winner.upper() if m.winner else 'TIMEOUT'}\n"
        report += f"   Steps: {m.steps_to_end} | Time: {m.computation_time:.4f}s\n"
        report += f"   Nodes Evaluated: {m.total_nodes_evaluated}\n\n"

    report += "\n" + "=" * 100 + "\n"
    return report


def save_summary(metrics_list):
    """Save summary to file."""
    report = create_summary_report(metrics_list)
    
    report_path = "/home/lum/AI_Zombie_Project/phase2/COMPARISON_RESULTS.txt"
    with open(report_path, "w") as f:
        f.write(report)
    
    print(report)
    print(f"\n✓ Summary saved to: {report_path}")


if __name__ == "__main__":
    print("Gathering metrics...\n")
    metrics = run_all_scenarios()
    print_comparison_table(metrics)
    save_summary(metrics)
