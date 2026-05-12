"""
GRID3_REASONING.PY - Phase 3 Reasoning Agent
============================================================================
Demonstrates an agent using Prolog for logical reasoning about the
environment, its actions, and their effects.

The agent:
1. Builds an environment model in Prolog
2. Reasons about safe moves and distances
3. Greedily navigates to goal using Prolog queries
4. Visualizes decisions and path in real-time

Key Features:
- Prolog dynamic facts: walls, goal, agent position, grid bounds
- Prolog rules: spatial reasoning, distance calculations, movement validation
- Greedy strategy with fallback: minimize Manhattan distance to goal
- Pygame visualization with step-by-step playback
- Console logging of Prolog queries and results

Dependencies:
    pip install pyswip pygame

System Requirements:
    SWI-Prolog 8.0+ installed and on system PATH
    https://www.swi-prolog.org/download/stable
"""
import os
import sys
import random
import pygame
from typing import List, Tuple, Set, Dict, Optional

try:
    from pyswip import Prolog
    # PrologError location differs by pyswip version
    try:
        from pyswip.core import PrologError
    except ImportError:
        try:
            from pyswip import PrologError
        except ImportError:
            # Fallback: use generic Exception if PrologError not found
            PrologError = Exception
except ImportError:
    print("ERROR: pyswip not installed.")
    print("Install with: pip install pyswip")
    print("Also ensure SWI-Prolog is installed: https://www.swi-prolog.org/download/stable")
    sys.exit(1)

# ============================================================================
# CONFIGURATION
# ============================================================================
GRID_WIDTH  = 15
GRID_HEIGHT = 10
TILE_SIZE   = 60
SIDEBAR_W   = 260
WINDOW_WIDTH  = GRID_WIDTH  * TILE_SIZE + SIDEBAR_W
WINDOW_HEIGHT = GRID_HEIGHT * TILE_SIZE
FPS = 3 

# Colors
COLOR_WALL        = (45,  45,  45)
COLOR_FLOOR       = (245, 245, 240)
COLOR_GOAL        = (34,  197, 94)
COLOR_AGENT       = (239, 68,  68)
COLOR_PATH        = (147, 197, 253)  
COLOR_START       = (251, 191, 36)    
COLOR_BORDER      = (200, 200, 200)
COLOR_SIDEBAR_BG  = (30,  30,  30)
COLOR_SIDEBAR_ACC = (55,  55,  55)
COLOR_TEXT        = (240, 240, 240)
COLOR_TEXT_DIM    = (150, 150, 150)
COLOR_SUCCESS     = (34,  197, 94)
COLOR_FAIL        = (239, 68,  68)
COLOR_QUERY_BG    = (20,  20,  20)

# ============================================================================
# MAZE GENERATION
# ============================================================================
def generate_maze(width: int, height: int, seed: int = 42) -> Set[Tuple[int, int]]:
    """
    Generate a solvable maze using recursive DFS backtracking.
    Guarantees a path exists from (0,0) to (width-1, height-1).

    Args:
        width:  Grid width
        height: Grid height
        seed:   Random seed for reproducibility

    Returns:
        Set of (x, y) wall coordinates
    """
    random.seed(seed)

    # Start with every cell walled
    walls: Set[Tuple[int, int]] = set()
    for x in range(width):
        for y in range(height):
            walls.add((x, y))

    def carve(x: int, y: int):
        walls.discard((x, y))
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) in walls:
                walls.discard((x + dx // 2, y + dy // 2))
                carve(nx, ny)

    carve(1, 1)

    # Ensure start and goal are always open
    walls.discard((0, 0))
    walls.discard((1, 0))
    walls.discard((0, 1))
    walls.discard((width - 1, height - 1))
    walls.discard((width - 2, height - 1))
    walls.discard((width - 1, height - 2))

    return walls

# ============================================================================
# PROLOG INITIALIZATION
# ============================================================================
def init_prolog(
    walls: Set[Tuple[int, int]]
) -> Tuple["Prolog", Tuple[int, int], Tuple[int, int]]:
    """
    Initialize Prolog engine and assert all world facts.

    Args:
        walls: Set of wall (x, y) coordinates

    Returns:
        (prolog engine, start position, goal position)
    """
    print("\n" + "=" * 65)
    print("  INITIALIZING PROLOG REASONING ENGINE")
    print("=" * 65)

    try:
        prolog = Prolog()
    except Exception as e:
        print(f"ERROR: Failed to initialize Prolog: {e}")
        print("Make sure SWI-Prolog is installed and on your system PATH")
        sys.exit(1)

    # Load knowledge base
    prolog_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reasoning.pl")
    if not os.path.exists(prolog_file):
        prolog_file = "reasoning.pl"
    if not os.path.exists(prolog_file):
        print(f"ERROR: reasoning.pl not found")
        sys.exit(1)

    print(f"  Loading: {prolog_file}")
    try:
        prolog.consult(prolog_file)
        print("  Knowledge base loaded OK")
    except Exception as e:
        print(f"ERROR: Failed to load reasoning.pl: {e}")
        sys.exit(1)

    # Assert grid dimensions
    prolog.assertz(f"grid_size({GRID_WIDTH}, {GRID_HEIGHT})")
    print(f"  grid_size({GRID_WIDTH}, {GRID_HEIGHT}) asserted")

    # Assert all walls
    for x, y in walls:
        prolog.assertz(f"wall({x}, {y})")
    print(f"  {len(walls)} wall facts asserted")

    # Assert goal
    goal = (GRID_WIDTH - 1, GRID_HEIGHT - 1)
    prolog.assertz(f"goal({goal[0]}, {goal[1]})")
    print(f"  goal({goal[0]}, {goal[1]}) asserted")

    # Assert start
    start = (0, 0)
    prolog.assertz(f"agent({start[0]}, {start[1]})")
    print(f"  agent({start[0]}, {start[1]}) asserted")

    print("=" * 65 + "\n")
    return prolog, start, goal

# ============================================================================
# REASONING AGENT
# ============================================================================
class ReasoningAgent:
    """
    Agent that delegates every movement decision to Prolog.
    Python only drives the loop and tracks state.
    No pathfinding algorithm lives in Python — all logic is in reasoning.pl.
    """

    def __init__(self, prolog: "Prolog", start: Tuple[int, int],
                 goal: Tuple[int, int], walls: Set[Tuple[int, int]]):
        self.prolog    = prolog
        self.x, self.y = start
        self.goal_x, self.goal_y = goal
        self.walls     = walls
        self.path: List[Tuple[int, int]] = [start]
        self.visited: Set[Tuple[int, int]] = {start}
        self.step_count = 0
        self.is_done    = False
        self.is_stuck   = False
        self.last_query  = "—"
        self.last_result = "—"

    def _query(self, q: str) -> list:
        """Safe Prolog query wrapper."""
        try:
            return list(self.prolog.query(q))
        except Exception as e:
            print(f"  [Prolog error] {q} → {e}")
            return []

    def step(self) -> bool:
        """
        One reasoning step:
          1. Query reached_goal?
          2. Query next_step (greedy — closest to goal)
          3. Fallback: any unvisited safe neighbor
          4. Update Prolog facts and local state
        """
        self.step_count += 1

        # ── 1. Goal check ──────────────────────────────────────────────────
        self.last_query = f"reached_goal({self.x}, {self.y})"
        if self._query(f"reached_goal({self.x}, {self.y})"):
            self.is_done     = True
            self.last_result = "YES — Goal reached!"
            print(f"\n{'='*65}")
            print(f"  SUCCESS: Goal reached in {self.step_count - 1} steps!")
            print(f"{'='*65}\n")
            return False

        # ── 2. Greedy next step via Prolog ─────────────────────────────────
        self.last_query = f"next_step({self.x}, {self.y}, NX, NY)"
        results = self._query(f"next_step({self.x}, {self.y}, NX, NY)")

        nx, ny = None, None

        if results:
            # Filter out already-visited cells to avoid greedy loops
            for r in results:
                cx, cy = int(r['NX']), int(r['NY'])
                if (cx, cy) not in self.visited:
                    nx, ny = cx, cy
                    break

        # ── 3. Fallback: any unvisited safe neighbor ───────────────────────
        if nx is None:
            self.last_query = f"can_move({self.x}, {self.y}, NX, NY)"
            fallback = self._query(f"can_move({self.x}, {self.y}, NX, NY)")
            for r in fallback:
                cx, cy = int(r['NX']), int(r['NY'])
                if (cx, cy) not in self.visited:
                    nx, ny = cx, cy
                    self.last_query += " [fallback]"
                    break

        # ── 4. Truly stuck ─────────────────────────────────────────────────
        if nx is None:
            self.is_stuck    = True
            self.last_result = "FAILED — No valid moves"
            print(f"  STUCK at ({self.x}, {self.y}) — no unvisited neighbors")
            return False

        self.last_result = f"→ ({nx}, {ny})"

        # Update Prolog facts
        try:
            self.prolog.retract(f"agent({self.x}, {self.y})")
        except Exception:
            pass
        try:
            self.prolog.assertz(f"agent({nx}, {ny})")
        except Exception:
            pass

        # Update local state
        self.x, self.y = nx, ny
        self.path.append((nx, ny))
        self.visited.add((nx, ny))

        print(f"  Step {self.step_count:>3}: {self.last_query}  →  ({nx}, {ny})")
        return True

# ============================================================================
# PYGAME VISUALIZER
# ============================================================================
class GridVisualizer:
    """Renders the grid, agent trail, and Prolog reasoning sidebar."""

    def __init__(self, walls: Set[Tuple[int, int]], goal: Tuple[int, int]):
        pygame.init()
        self.walls  = walls
        self.goal   = goal
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Phase 3 — Reasoning Agent with Prolog")
        self.clock  = pygame.time.Clock()

        # Fonts initialised after pygame.init()
        self.f_tiny  = pygame.font.SysFont("Consolas", 13)
        self.f_small = pygame.font.SysFont("Consolas", 15)
        self.f_med   = pygame.font.SysFont("Consolas", 18, bold=True)
        self.f_big   = pygame.font.SysFont("Consolas", 22, bold=True)

    def _cell(self, x: int, y: int) -> pygame.Rect:
        return pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def _text(self, surface, txt: str, font, color, x: int, y: int):
        surface.blit(font.render(txt, True, color), (x, y))

    def _wrap(self, text: str, max_chars: int) -> List[str]:
        if len(text) <= max_chars:
            return [text]
        lines, cur = [], ""
        for word in text.split():
            if cur and len(cur) + 1 + len(word) > max_chars:
                lines.append(cur)
                cur = word
            else:
                cur = (cur + " " + word).strip()
        if cur:
            lines.append(cur)
        return lines or [text[:max_chars]]

    def draw(self, agent: ReasoningAgent):
        self.screen.fill((20, 20, 20))
        grid_surf = pygame.Surface((GRID_WIDTH * TILE_SIZE, GRID_HEIGHT * TILE_SIZE))
        grid_surf.fill(COLOR_FLOOR)

        # Path trail
        for pos in agent.path[:-1]:
            pygame.draw.rect(grid_surf, COLOR_PATH, self._cell(*pos))

        # Walls
        for wx, wy in self.walls:
            pygame.draw.rect(grid_surf, COLOR_WALL, self._cell(wx, wy))

        # Start marker
        pygame.draw.rect(grid_surf, COLOR_START, self._cell(0, 0))
        lbl = self.f_small.render("S", True, (30, 30, 30))
        grid_surf.blit(lbl, (0 * TILE_SIZE + TILE_SIZE//2 - 5,
                              0 * TILE_SIZE + TILE_SIZE//2 - 8))

        # Goal
        gx, gy = self.goal
        pygame.draw.rect(grid_surf, COLOR_GOAL, self._cell(gx, gy))
        lbl = self.f_small.render("G", True, (255, 255, 255))
        grid_surf.blit(lbl, (gx * TILE_SIZE + TILE_SIZE//2 - 5,
                              gy * TILE_SIZE + TILE_SIZE//2 - 8))

        # Agent
        cx = agent.x * TILE_SIZE + TILE_SIZE // 2
        cy = agent.y * TILE_SIZE + TILE_SIZE // 2
        pygame.draw.circle(grid_surf, COLOR_AGENT, (cx, cy), TILE_SIZE // 3)
        pygame.draw.circle(grid_surf, (255, 255, 255), (cx, cy), TILE_SIZE // 3, 2)

        # Grid lines
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(grid_surf, COLOR_BORDER,
                             (x * TILE_SIZE, 0),
                             (x * TILE_SIZE, GRID_HEIGHT * TILE_SIZE))
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(grid_surf, COLOR_BORDER,
                             (0, y * TILE_SIZE),
                             (GRID_WIDTH * TILE_SIZE, y * TILE_SIZE))

        self.screen.blit(grid_surf, (0, 0))

        # ── Sidebar ────────────────────────────────────────────────────────
        sx = GRID_WIDTH * TILE_SIZE
        pygame.draw.rect(self.screen, COLOR_SIDEBAR_BG,
                         (sx, 0, SIDEBAR_W, WINDOW_HEIGHT))
        pygame.draw.line(self.screen, (80, 80, 80), (sx, 0), (sx, WINDOW_HEIGHT), 2)

        pad  = sx + 14
        yo   = 18
        lh   = 22

        self._text(self.screen, "PROLOG AGENT", self.f_big, COLOR_TEXT, pad, yo)
        yo += 30
        pygame.draw.line(self.screen, (80, 80, 80), (sx + 10, yo), (sx + SIDEBAR_W - 10, yo))
        yo += 12

        # Stats
        self._text(self.screen, f"Step   : {agent.step_count}", self.f_small, COLOR_TEXT, pad, yo); yo += lh
        self._text(self.screen, f"Pos    : ({agent.x}, {agent.y})", self.f_small, COLOR_TEXT, pad, yo); yo += lh
        self._text(self.screen, f"Goal   : ({agent.goal_x}, {agent.goal_y})", self.f_small, COLOR_TEXT, pad, yo); yo += lh

        # Manhattan distance
        dist = abs(agent.x - agent.goal_x) + abs(agent.y - agent.goal_y)
        self._text(self.screen, f"Dist   : {dist}", self.f_small, COLOR_TEXT, pad, yo); yo += lh
        self._text(self.screen, f"Visited: {len(agent.visited)}", self.f_small, COLOR_TEXT, pad, yo); yo += lh + 8

        pygame.draw.line(self.screen, (80, 80, 80), (sx + 10, yo), (sx + SIDEBAR_W - 10, yo))
        yo += 12

        # Query block
        self._text(self.screen, "LAST QUERY:", self.f_small, COLOR_TEXT_DIM, pad, yo); yo += lh
        qbg = pygame.Rect(sx + 8, yo - 2, SIDEBAR_W - 16, 58)
        pygame.draw.rect(self.screen, COLOR_QUERY_BG, qbg, border_radius=4)
        for line in self._wrap(agent.last_query, 28):
            self._text(self.screen, line, self.f_tiny, (100, 200, 255), pad, yo)
            yo += 17
        yo += 6

        # Result
        self._text(self.screen, "RESULT:", self.f_small, COLOR_TEXT_DIM, pad, yo); yo += lh
        r_color = COLOR_SUCCESS if not agent.is_stuck else COLOR_FAIL
        for line in self._wrap(agent.last_result, 28):
            self._text(self.screen, line, self.f_small, r_color, pad, yo)
            yo += lh
        yo += 8

        pygame.draw.line(self.screen, (80, 80, 80), (sx + 10, yo), (sx + SIDEBAR_W - 10, yo))
        yo += 12

        # Controls hint
        self._text(self.screen, "SPACE  pause / resume", self.f_tiny, COLOR_TEXT_DIM, pad, yo); yo += 18
        self._text(self.screen, "ESC    quit",           self.f_tiny, COLOR_TEXT_DIM, pad, yo); yo += 18

        # Status banner at bottom
        if agent.is_done:
            banner = pygame.Rect(sx, WINDOW_HEIGHT - 44, SIDEBAR_W, 44)
            pygame.draw.rect(self.screen, (20, 80, 40), banner)
            msg = f"GOAL REACHED  ({agent.step_count - 1} steps)"
            self._text(self.screen, msg, self.f_med, COLOR_SUCCESS,
                       pad, WINDOW_HEIGHT - 30)
        elif agent.is_stuck:
            banner = pygame.Rect(sx, WINDOW_HEIGHT - 44, SIDEBAR_W, 44)
            pygame.draw.rect(self.screen, (80, 20, 20), banner)
            self._text(self.screen, "AGENT STUCK", self.f_med, COLOR_FAIL,
                       pad, WINDOW_HEIGHT - 30)

        pygame.display.flip()

# ============================================================================
# MAIN
# ============================================================================
def main():
    print("\n" + "=" * 65)
    print("  PHASE 3: REASONING AGENT WITH PROLOG")
    print("=" * 65)
    print(f"  Grid  : {GRID_WIDTH} x {GRID_HEIGHT}")
    print(f"  Start : (0, 0)  →  Goal: ({GRID_WIDTH-1}, {GRID_HEIGHT-1})")
    print(f"  FPS   : {FPS}")
    print("=" * 65)

    # Generate maze
    walls = generate_maze(GRID_WIDTH, GRID_HEIGHT, seed=42)
    print(f"\n  Maze generated — {len(walls)} wall cells")

    # Init Prolog
    prolog, start, goal = init_prolog(walls)

    # Create agent and visualizer
    agent = ReasoningAgent(prolog, start, goal, walls)
    vis   = GridVisualizer(walls, goal)

    print("  Controls: SPACE = pause/resume   ESC = quit\n")

    running = True
    paused  = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    print(f"  {'Paused' if paused else 'Resumed'}")

        if not paused and not agent.is_done and not agent.is_stuck:
            agent.step()

        vis.draw(agent)
        vis.clock.tick(FPS)

    # Final summary
    print("\n" + "=" * 65)
    print("  SIMULATION COMPLETE")
    print("=" * 65)
    print(f"  Steps taken : {agent.step_count}")
    print(f"  Path length : {len(agent.path)}")
    print(f"  Cells visited: {len(agent.visited)}")
    print(f"  Success     : {agent.is_done}")
    print(f"  Stuck       : {agent.is_stuck}")
    if agent.path:
        path_str = " → ".join(f"({x},{y})" for x, y in agent.path)
        print(f"  Full path   : {path_str}")
    print("=" * 65 + "\n")

    # Cleanup
    try:
        del prolog
    except Exception:
        pass
    pygame.quit()

if __name__ == "__main__":
    main()
