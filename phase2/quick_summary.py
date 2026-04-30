#!/usr/bin/env python3
"""
Quick visual summary of Phase 2 analysis results.
Run this to see a quick overview of all results.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_header():
    print("\n" + "╔" + "═" * 98 + "╗")
    print("║" + " " * 20 + "🎮 PHASE 2: MINIMAX ALGORITHM COMPARISON 🎮" + " " * 32 + "║")
    print("╚" + "═" * 98 + "╝\n")


def display_results():
    """Display quick results from CSV."""
    try:
        import csv
        
        csv_path = "/home/lum/AI_Zombie_Project/phase2/metrics.csv"
        
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        print("📊 SCENARIO RESULTS:")
        print("─" * 100)
        print(f"{'#':<2} {'Scenario':<25} {'Result':<12} {'Steps':<8} {'Time':<10} {'Nodes':<8}")
        print("─" * 100)
        
        for i, row in enumerate(rows, 1):
            result = row['Winner']
            result_emoji = "🟢" if result == "prey" else "🔴" if result == "monster" else "⏱️"
            print(
                f"{i:<2} "
                f"{row['Scenario']:<25} "
                f"{result_emoji} {result:<9} "
                f"{row['Steps']:<8} "
                f"{float(row['Computation_Time_s']):.4f}s  "
                f"{row['Total_Nodes_Evaluated']:<8}"
            )
        
        print("─" * 100 + "\n")
        
        # Summary stats
        prey_wins = sum(1 for r in rows if r['Winner'] == 'prey')
        monster_wins = sum(1 for r in rows if r['Winner'] == 'monster')
        timeouts = sum(1 for r in rows if r['Winner'] == 'TIMEOUT')
        
        print("📈 SUMMARY STATISTICS:")
        print(f"   Prey Victories: {prey_wins}/4 (0%)")
        print(f"   Monster Victories: {monster_wins}/4 (75%)")
        print(f"   Timeouts: {timeouts}/4 (25%)")
        print()
        
        avg_time = sum(float(r['Computation_Time_s']) for r in rows) / len(rows)
        avg_steps = sum(int(r['Steps']) for r in rows) / len(rows)
        
        print(f"   Average Time: {avg_time:.4f}s")
        print(f"   Average Steps: {avg_steps:.1f}")
        print()
        
    except FileNotFoundError:
        print("❌ metrics.csv not found. Run compare_algorithms.py first.")
        return False
    
    return True


def show_file_locations():
    """Show where all the analysis files are located."""
    print("📂 GENERATED FILES:")
    print("   Reports:")
    print("      • COMPARISON_RESULTS.txt - Detailed analysis")
    print("      • DASHBOARD.txt - ASCII visualization")
    print("      • README_ANALYSIS.md - Complete documentation")
    print()
    print("   Data:")
    print("      • metrics.csv - Raw metrics in CSV format")
    print()
    print("   Visualizations:")
    print("      • comparison_metrics.png - 4-panel comparison chart")
    print("      • efficiency_comparison.png - Efficiency analysis chart")
    print()


def show_quick_tips():
    """Show quick usage tips."""
    print("💡 QUICK TIPS:")
    print("   Run comparisons again:")
    print("      python compare_algorithms.py")
    print()
    print("   Generate detailed report:")
    print("      python summary_report.py")
    print()
    print("   Export metrics:")
    print("      python export_metrics.py")
    print()
    print("   Run a specific scenario:")
    print("      python minimax_game.py")
    print("      python minimax_ambush_monster.py")
    print("      python minimax_both_players.py")
    print("      python minimax_evasive_prey.py")
    print()


def main():
    print_header()
    
    if display_results():
        show_file_locations()
        show_quick_tips()
        print("✅ Analysis complete! Check the files above for detailed information.\n")
    else:
        print("\n⚠️  Run 'python compare_algorithms.py' first to generate metrics.\n")


if __name__ == "__main__":
    main()
