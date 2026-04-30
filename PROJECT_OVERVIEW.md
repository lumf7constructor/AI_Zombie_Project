# Project Structure & Documentation

## Game Files (Runnable)

### 1. `test.py`
- **Algorithms**: A* for both prey and monster
- **Type**: Baseline reactive game
- **Result**: Monster wins ~20-30 steps
- **Purpose**: Reference behavior

### 2. `minimax_evasive_prey.py` 
- **Algorithms**: Prey uses Minimax + A*, Monster uses A*
- **Type**: One-sided strategic game
- **Result**: Prey often wins ~40-60+ steps
- **Purpose**: Shows minimax evasion strategy

### 3. `minimax_ambush_monster.py`
- **Algorithms**: Prey uses A*, Monster uses Path Interception (greedy optimization)
- **Type**: One-sided tactical game
- **Result**: Monster catches prey ~27 steps
- **Purpose**: Shows predictive interception advantage

### 4. `minimax_both_players.py` ⭐ NEW
- **Algorithms**: Both prey and monster use adversarial Minimax
- **Type**: True game-theoretic game
- **Result**: Unknown (depends on optimal play)
- **Purpose**: Demonstrates balanced adversarial game theory

---

## Documentation Files

### Quick Learning Path
1. Start here: `GAMES_COMPARISON.md` - See all 4 games side-by-side
2. Then: `MINIMAX_BOTH_PLAYERS_GUIDE.md` - Understand the new game
3. Deep dive: `ALGORITHM_GUIDE.md` - Detailed algorithm breakdown
4. Technical: `COMPLEXITY_ANALYSIS.md` - Time/space analysis

### Reference Documents

#### `GAMES_COMPARISON.md`
- Table comparing all 4 games
- Expected behaviors for each
- Performance trade-offs
- When to use each game

#### `ALGORITHM_GUIDE.md`
- How each algorithm works (with diagrams)
- Detailed game tree examples
- Why each approach is different
- Performance summaries

#### `COMPLEXITY_ANALYSIS.md`
- Time complexity of each algorithm
- Space complexity comparisons
- Memory usage breakdown
- Real-world performance metrics

#### `MINIMAX_BOTH_PLAYERS_GUIDE.md` (NEW)
- What the new game does
- How adversarial minimax works
- Why it's special
- What to expect when running it

---

## Supporting Files

### Code Files
- `config.py` - Grid configuration (30x30 maze)
- `utils.py` - A* pathfinding implementation
- `env_setup.py` - Environment visualization helper
- `env_visuals.py` - Visual rendering utilities

### Documentation
- `README.md` - Project overview
- `requirements.txt` - Python dependencies

---

## Recommended Viewing Order

### First Time?
```
1. Run: python3 test.py
   "See the baseline behavior"
   
2. Run: python3 minimax_evasive_prey.py
   "Watch the prey evade with minimax"
   
3. Run: python3 minimax_ambush_monster.py
   "See the monster intercept with prediction"
   
4. Run: python3 minimax_both_players.py
   "Experience true adversarial game theory"
```

### Want to Understand?
```
1. Read: GAMES_COMPARISON.md (overview)
2. Read: ALGORITHM_GUIDE.md (deep dive)
3. Read: COMPLEXITY_ANALYSIS.md (performance)
4. Read: MINIMAX_BOTH_PLAYERS_GUIDE.md (new game)
```

### Want to Analyze?
```
1. Check: COMPLEXITY_ANALYSIS.md
2. Run: Each game and time them
3. Study: Source code of minimax_both_players.py
4. Modify: Depths, evaluation functions, etc.
```

---

## Key Files to Modify If You Want to Experiment

### To Change Difficulty
- `minimax_evasive_prey.py` line 70: `PREY_MINIMAX_DEPTH = 3` (higher = smarter)
- `minimax_both_players.py` line 77: `PREY_MINIMAX_DEPTH = 3` (higher = smarter)
- `minimax_both_players.py` line 78: `MONSTER_MINIMAX_DEPTH = 3` (higher = smarter)

### To Change Speed
- Any game file, line ~80: `STEPS_PER_FRAME = 1` (lower = faster)

### To Change Evaluation Function
- `minimax_evasive_prey.py` line 191: `evaluate_board()` function
- `minimax_both_players.py` line 166: `evaluate_board()` function

---

## Quick Statistics

### Games
- **Total games created**: 4
- **Games using minimax**: 3 (partially in 1, 2, fully in 1, 4)
- **Games with true adversarial minimax**: 1 (minimax_both_players.py)

### Documentation
- **Guide files**: 5
- **Total explanation**: ~20,000+ words
- **Diagrams**: Multiple in guides

### Code
- **New game**: 400+ lines
- **Total project**: 3,000+ lines

---

## Algorithm Summary

| Algorithm | Where Used | Why | Complexity |
|-----------|-----------|-----|-----------|
| A* | test.py (both), evasive_prey.py (monster), ambush_monster.py (prey) | Efficient pathfinding | O(n log n) |
| Minimax | evasive_prey.py (prey), both_players.py (both) | Strategic game tree | O(b^d × n log n) |
| Path Interception | ambush_monster.py (monster) | Greedy optimization | O(n × n log n) |

---

## Next Steps

**To run the new game:**
```bash
python3 minimax_both_players.py
```

**To understand it:**
Read `MINIMAX_BOTH_PLAYERS_GUIDE.md`

**To go deeper:**
Read `ALGORITHM_GUIDE.md` and `COMPLEXITY_ANALYSIS.md`

**To experiment:**
Modify `PREY_MINIMAX_DEPTH` or `MONSTER_MINIMAX_DEPTH` and see how it changes gameplay!

---

## The Journey

```
Test.py (Simple)
    ↓
Minimax Evasive (Strategy for Prey)
    ↓
Minimax Ambush (Tactics for Monster)
    ↓
Minimax Both (Adversarial Balance) ⭐
    ↓
Game Theory Mastery! 🎓
```

Enjoy! 🚀
