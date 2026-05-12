"""
GRID3_REASONING_FLEEING.PY - Phase 3 Fleeing Reasoning Agent
Zombie starts near the goal to create a real fleeing scenario!
"""
import os
import sys
import random
import pygame
from collections import Counter
from typing import List, Tuple, Set

# ============================================================================
# PYSWIP IMPORT
# ============================================================================
try:
    from pyswip import Prolog
except ImportError:
    print("ERROR: pyswip not installed. pip install pyswip")
    print("SWI-Prolog: https://www.swi-prolog.org/download/stable")
    sys.exit(1)

# ============================================================================
# CONFIGURATION
# ============================================================================
GRID_W    = 30
GRID_H    = 30
TILE      = 26
SIDEBAR_W = 280
WIN_W     = GRID_W * TILE + SIDEBAR_W
WIN_H     = GRID_H * TILE
FPS       = 4

AGENT_START  = (0, 0)
ZOMBIE_START = (25, 25)
GOAL_POS     = (29, 29)

C_WALL       = (40, 40, 40)
C_FLOOR      = (248, 248, 242)
C_GOAL       = (34, 197, 94)
C_AGENT      = (59, 130, 246)
C_ZOMBIE     = (220, 38, 38)
C_PATH       = (186, 220, 254)
C_DANGER     = (255, 230, 200)
C_BORDER     = (210, 210, 210)
C_SIDEBAR    = (18, 18, 18)
C_TEXT       = (230, 230, 230)
C_DIM        = (120, 120, 120)
C_SUCCESS    = (34, 197, 94)
C_FAIL       = (220, 38, 38)
C_ACCENT     = (99, 102, 241)

# ============================================================================
# MAZE GENERATION
# ============================================================================
def generate_maze(w: int, h: int, seed: int = 7) -> Set[Tuple[int, int]]:
    random.seed(seed)
    walls: Set[Tuple[int, int]] = {(x, y) for x in range(w) for y in range(h)}

    def carve(x: int, y: int):
        walls.discard((x, y))
        dirs = [(0, -2), (2, 0), (0, 2), (-2, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in walls:
                walls.discard((x + dx // 2, y + dy // 2))
                carve(nx, ny)

    carve(1, 1)
    open_cells = [
        AGENT_START, GOAL_POS, ZOMBIE_START,
        (1, 0), (0, 1),
        (28, 29), (29, 28),
        (24, 25), (25, 24), (26, 25), (25, 26)
    ]
    for cx, cy in open_cells:
        if 0 <= cx < w and 0 <= cy < h:
            walls.discard((cx, cy))
    return walls

# ============================================================================
# PROLOG SETUP
# ============================================================================
def init_prolog(walls: Set[Tuple[int, int]]) -> Prolog:
    print("\n" + "=" * 60)
    print("  PROLOG REASONING ENGINE — FLEEING AGENT")
    print("=" * 60)
    prolog = Prolog()
    pl_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reasoning_fleeing.pl")
    if not os.path.exists(pl_file):
        pl_file = "reasoning_fleeing.pl"
    if not os.path.exists(pl_file):
        print("  ERROR: reasoning_fleeing.pl not found")
        sys.exit(1)
    prolog.consult(pl_file)
    print(f"  Loaded: {pl_file}")

    for p in ["wall", "agent", "zombie", "goal", "grid_size", "visit_count", "visit_step", "current_step"]:
        try:
            prolog.retractall(f"{p}(_,_)")
        except:
            pass

    prolog.assertz(f"grid_size({GRID_W}, {GRID_H})")
    for x, y in walls:
        prolog.assertz(f"wall({x},{y})")
    prolog.assertz(f"goal({GOAL_POS[0]},{GOAL_POS[1]})")
    prolog.assertz(f"agent({AGENT_START[0]},{AGENT_START[1]})")
    prolog.assertz(f"zombie({ZOMBIE_START[0]},{ZOMBIE_START[1]})")

    print(f"  {len(walls)} walls")
    print(f"  Agent start: {AGENT_START}")
    print(f"  Zombie start: {ZOMBIE_START} (near goal!)")
    print(f"  Goal: {GOAL_POS}")
    print("=" * 60 + "\n")
    return prolog

# ============================================================================
# ZOMBIE CONTROLLER
# ============================================================================
def zombie_next(zx: int, zy: int, ax: int, ay: int,
                walls: Set[Tuple[int, int]]) -> Tuple[int, int]:
    best, best_d = (zx, zy), abs(zx - ax) + abs(zy - ay)
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = zx + dx, zy + dy
        if 0 <= nx < GRID_W and 0 <= ny < GRID_H and (nx, ny) not in walls:
            d = abs(nx - ax) + abs(ny - ay)
            if d < best_d:
                best_d = d
                best = (nx, ny)
    return best

# ============================================================================
# REASONING AGENT
# ============================================================================
class FleeingAgent:
    def __init__(self, prolog: Prolog, walls: Set[Tuple[int, int]]):
        self.prolog = prolog
        self.walls = walls
        self.ax, self.ay = AGENT_START
        self.zx, self.zy = ZOMBIE_START
        self.agent_path: List[Tuple[int, int]] = [AGENT_START]
        self.zombie_path: List[Tuple[int, int]] = [ZOMBIE_START]
        self.step_count = 0
        self.won = False
        self.lost = False
        self.last_result = "—"
        self.last_status = "navigating"
        self.predicted_zombie_cells: List[Tuple[int, int]] = []
        self.recent_positions: List[Tuple[int, int]] = []

    def _q(self, q: str) -> list:
        try:
            return list(self.prolog.query(q))
        except Exception as e:
            return []

    def _update_prolog(self):
        try:
            self.prolog.retractall("agent(_,_)")
            self.prolog.retractall("zombie(_,_)")
            self.prolog.assertz(f"agent({self.ax},{self.ay})")
            self.prolog.assertz(f"zombie({self.zx},{self.zy})")
        except:
            pass

    def _is_stuck(self) -> bool:
        if len(self.recent_positions) < 6:
            return False
        window = self.recent_positions[-10:]
        counts = Counter(window)
        return any(c >= 3 for c in counts.values())

    def _force_escape(self) -> Tuple[int, int]:
        print(f"  ⚡ STUCK DETECTED at step {self.step_count} — forcing escape move")
        self._q("clear_visited")
        self.recent_positions.clear()

        candidates = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = self.ax + dx, self.ay + dy
            if (0 <= nx < GRID_W and 0 <= ny < GRID_H
                    and (nx, ny) not in self.walls):
                dz = abs(nx - self.zx) + abs(ny - self.zy)
                dg = abs(nx - GOAL_POS[0]) + abs(ny - GOAL_POS[1])
                candidates.append((dz, -dg, nx, ny))

        if not candidates:
            return self.ax, self.ay
        candidates.sort(reverse=True)
        top = candidates[:min(2, len(candidates))]
        chosen = random.choice(top)
        return chosen[2], chosen[3]

    def _get_predicted_zombie_cells(self) -> List[Tuple[int, int]]:
        results = self._q("zombie_next_cells(Cells)")
        cells = []
        if results:
            raw = results[0].get('Cells', [])
            for item in raw:
                try:
                    if hasattr(item, 'args'):
                        x, y = int(item.args[0]), int(item.args[1])
                    else:
                        parts = str(item).replace('(', '').replace(')', '').split('-')
                        if len(parts) == 2:
                            x, y = int(parts[0]), int(parts[1])
                        else:
                            continue
                    cells.append((x, y))
                except:
                    pass
        return cells

    def step(self) -> bool:
        self.step_count += 1

        self._q(f"set_step({self.step_count})")

        if self.step_count % 15 == 0:
            self._q("clear_old_visited")

        # Terminal state checks
        if (self.ax, self.ay) == (self.zx, self.zy):
            self.lost = True
            self.last_result = "CAUGHT by zombie!"
            print(f"\n  💀 GAME OVER — Zombie caught agent at step {self.step_count}")
            return False
        if (self.ax, self.ay) == GOAL_POS:
            self.won = True
            self.last_result = "GOAL REACHED!"
            print(f"\n  🎉 VICTORY! Agent reached goal in {self.step_count} steps!")
            return False

        self.predicted_zombie_cells = self._get_predicted_zombie_cells()

        # Stuck detection — force escape before querying Prolog
        if self._is_stuck():
            new_ax, new_ay = self._force_escape()
            self.last_result = f"ESCAPE→({new_ax},{new_ay})"
        else:
            results = self._q(f"flee_step({self.ax},{self.ay},NX,NY)")
            new_ax, new_ay = self.ax, self.ay

            if results:
                r = results[0]
                if 'NX' in r and 'NY' in r:
                    new_ax, new_ay = int(r['NX']), int(r['NY'])
                    self.last_result = f"→ ({new_ax},{new_ay})"
                else:
                    self.last_result = "Invalid Prolog result"
            else:
                # Python fallback
                self.last_result = "Fallback"
                best_score = -999999
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = self.ax + dx, self.ay + dy
                    if (0 <= nx < GRID_W and 0 <= ny < GRID_H
                            and (nx, ny) not in self.walls):
                        dz = abs(nx - self.zx) + abs(ny - self.zy)
                        dg = abs(nx - GOAL_POS[0]) + abs(ny - GOAL_POS[1])
                        score = (dz * 3) - dg
                        if score > best_score:
                            best_score = score
                            new_ax, new_ay = nx, ny

        # Zombie moves toward agent's new position
        new_zx, new_zy = zombie_next(self.zx, self.zy, new_ax, new_ay, self.walls)

        self.ax, self.ay = new_ax, new_ay
        self.zx, self.zy = new_zx, new_zy
        self._update_prolog()
        self.agent_path.append((self.ax, self.ay))
        self.zombie_path.append((self.zx, self.zy))

        self.recent_positions.append((self.ax, self.ay))
        if len(self.recent_positions) > 10:
            self.recent_positions.pop(0)

        st = self._q("agent_status(S)")
        self.last_status = str(st[0]['S']) if st else "navigating"

        dist_z = abs(self.ax - self.zx) + abs(self.ay - self.zy)
        dist_g = abs(self.ax - GOAL_POS[0]) + abs(self.ay - GOAL_POS[1])
        status_icon = ("🏃" if self.last_status == "fleeing"
                       else "🎯" if self.last_status == "navigating" else "❓")
        print(f"  {self.step_count:>3} | A({self.ax:>2},{self.ay:>2})"
              f" Z({self.zx:>2},{self.zy:>2})"
              f" | DZ={dist_z:>2} DG={dist_g:>2} | {status_icon} {self.last_result}")

        if (self.ax, self.ay) == (self.zx, self.zy):
            self.lost = True
            print(f"\n  💀 GAME OVER — Caught at step {self.step_count}")
            return False
        if (self.ax, self.ay) == GOAL_POS:
            self.won = True
            print(f"\n  🎉 VICTORY! Goal reached at step {self.step_count}!")
            return False

        return True

# ============================================================================
# VISUALISER
# ============================================================================
class FleeVisualizer:
    def __init__(self, walls: Set[Tuple[int, int]]):
        pygame.init()
        self.walls = walls
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Phase 3 — Fleeing Agent vs Zombie")
        self.clock = pygame.time.Clock()
        self.f_tiny  = pygame.font.SysFont("Consolas", 12)
        self.f_small = pygame.font.SysFont("Consolas", 14)
        self.f_med   = pygame.font.SysFont("Consolas", 17, bold=True)
        self.f_big   = pygame.font.SysFont("Consolas", 20, bold=True)

    def _cell_rect(self, x, y) -> pygame.Rect:
        return pygame.Rect(x * TILE, y * TILE, TILE, TILE)

    def _txt(self, text, font, color, x, y):
        self.screen.blit(font.render(text, True, color), (x, y))

    def draw(self, agent: FleeingAgent):
        self.screen.fill((15, 15, 15))
        grid_surf = pygame.Surface((GRID_W * TILE, GRID_H * TILE))
        grid_surf.fill(C_FLOOR)

        for cx, cy in agent.predicted_zombie_cells:
            pygame.draw.rect(grid_surf, C_DANGER, self._cell_rect(cx, cy))

        for pos in agent.agent_path[:-1]:
            pygame.draw.rect(grid_surf, C_PATH, self._cell_rect(*pos))

        for pos in agent.zombie_path[:-1]:
            r = self._cell_rect(*pos)
            s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
            s.fill((220, 38, 38, 60))
            grid_surf.blit(s, r.topleft)

        for wx, wy in self.walls:
            pygame.draw.rect(grid_surf, C_WALL, self._cell_rect(wx, wy))

        gx, gy = GOAL_POS
        pygame.draw.rect(grid_surf, C_GOAL, self._cell_rect(gx, gy))
        lbl = self.f_small.render("G", True, (255, 255, 255))
        grid_surf.blit(lbl, (gx * TILE + TILE // 2 - 4, gy * TILE + TILE // 2 - 7))

        pygame.draw.rect(grid_surf, (251, 191, 36), self._cell_rect(0, 0))
        lbl = self.f_small.render("S", True, (30, 30, 30))
        grid_surf.blit(lbl, (TILE // 2 - 4, TILE // 2 - 7))

        zc = (agent.zx * TILE + TILE // 2, agent.zy * TILE + TILE // 2)
        pygame.draw.circle(grid_surf, C_ZOMBIE, zc, TILE // 2 - 2)
        pygame.draw.circle(grid_surf, (255, 255, 255), zc, TILE // 2 - 2, 2)
        lbl = self.f_tiny.render("Z", True, (255, 255, 255))
        grid_surf.blit(lbl, (agent.zx * TILE + TILE // 2 - 4, agent.zy * TILE + TILE // 2 - 6))

        ac = (agent.ax * TILE + TILE // 2, agent.ay * TILE + TILE // 2)
        pygame.draw.circle(grid_surf, C_AGENT, ac, TILE // 2 - 2)
        pygame.draw.circle(grid_surf, (255, 255, 255), ac, TILE // 2 - 2, 2)
        lbl = self.f_tiny.render("A", True, (255, 255, 255))
        grid_surf.blit(lbl, (agent.ax * TILE + TILE // 2 - 4, agent.ay * TILE + TILE // 2 - 6))

        for x in range(GRID_W + 1):
            pygame.draw.line(grid_surf, C_BORDER, (x * TILE, 0), (x * TILE, GRID_H * TILE))
        for y in range(GRID_H + 1):
            pygame.draw.line(grid_surf, C_BORDER, (0, y * TILE), (GRID_W * TILE, y * TILE))

        self.screen.blit(grid_surf, (0, 0))

        # Sidebar
        sx = GRID_W * TILE
        pygame.draw.rect(self.screen, C_SIDEBAR, (sx, 0, SIDEBAR_W, WIN_H))
        pygame.draw.line(self.screen, (70, 70, 70), (sx, 0), (sx, WIN_H), 2)

        p  = sx + 14
        yo = 16
        lh = 21

        self._txt("FLEEING AGENT", self.f_big, C_TEXT, p, yo)
        yo += 28
        pygame.draw.line(self.screen, (70, 70, 70), (sx + 8, yo), (sx + SIDEBAR_W - 8, yo))
        yo += 10

        dist_az = abs(agent.ax - agent.zx) + abs(agent.ay - agent.zy)
        dist_ag = abs(agent.ax - GOAL_POS[0]) + abs(agent.ay - GOAL_POS[1])

        self._txt(f"Step       : {agent.step_count}",        self.f_small, C_TEXT, p, yo); yo += lh
        self._txt(f"Agent pos  : ({agent.ax},{agent.ay})",   self.f_small, C_TEXT, p, yo); yo += lh
        self._txt(f"Zombie pos : ({agent.zx},{agent.zy})",   self.f_small, C_TEXT, p, yo); yo += lh

        if dist_az < 5:
            zcol, zicon = C_FAIL, "!"
        elif dist_az < 10:
            zcol, zicon = (251, 191, 36), "~"
        else:
            zcol, zicon = C_SUCCESS, "+"
        self._txt(f"{zicon} Dist->zombie: {dist_az}", self.f_small, zcol,   p, yo); yo += lh
        self._txt(f"  Dist->goal : {dist_ag}",        self.f_small, C_TEXT, p, yo); yo += lh

        status_col = {
            "at_goal": C_SUCCESS, "caught": C_FAIL,
            "fleeing": (251, 191, 36), "navigating": C_ACCENT
        }.get(agent.last_status, C_TEXT)
        self._txt(f"Status     : {agent.last_status}", self.f_small, status_col, p, yo)
        yo += lh + 6

        pygame.draw.line(self.screen, (70, 70, 70), (sx + 8, yo), (sx + SIDEBAR_W - 8, yo))
        yo += 10

        self._txt("STRATEGY:",             self.f_small, C_DIM,    p, yo); yo += lh
        self._txt("Score=(DZ*3)-DG+VP+LB", self.f_tiny,  C_ACCENT, p, yo); yo += 16
        self._txt("VP = visit penalty",    self.f_tiny,  C_DIM,    p, yo); yo += 16
        self._txt("LB = lookahead bonus",  self.f_tiny,  C_DIM,    p, yo); yo += 16

        pygame.draw.line(self.screen, (70, 70, 70), (sx + 8, yo), (sx + SIDEBAR_W - 8, yo))
        yo += 10

        self._txt("SPACE  pause/resume", self.f_tiny, C_DIM, p, yo); yo += 17
        self._txt("ESC    quit",         self.f_tiny, C_DIM, p, yo)

        if agent.won or agent.lost:
            banner_h = 52
            banner_c = (15, 60, 30) if agent.won else (60, 15, 15)
            pygame.draw.rect(self.screen, banner_c, (sx, WIN_H - banner_h, SIDEBAR_W, banner_h))
            msg = "AGENT WINS!" if agent.won else "ZOMBIE WINS!"
            sub = (f"Goal reached in {agent.step_count} steps" if agent.won
                   else f"Caught at step {agent.step_count}")
            mcol = C_SUCCESS if agent.won else C_FAIL
            self._txt(msg, self.f_med,   mcol,  p, WIN_H - banner_h + 8)
            self._txt(sub, self.f_small, C_DIM, p, WIN_H - banner_h + 28)

        pygame.display.flip()

# ============================================================================
# MAIN
# ============================================================================
def main():
    print("\n" + "=" * 60)
    print("  PHASE 3 — FLEEING AGENT vs ZOMBIE")
    print("  Zombie starts NEAR THE GOAL for real fleeing behavior!")
    print("=" * 60)
    print(f"  Grid   : {GRID_W}x{GRID_H}")
    print(f"  Agent  : {AGENT_START} -> Goal: {GOAL_POS}")
    print(f"  Zombie : {ZOMBIE_START} (near goal!)")
    print(f"  FPS    : {FPS}")
    print("=" * 60)

    walls  = generate_maze(GRID_W, GRID_H, seed=7)
    prolog = init_prolog(walls)
    agent  = FleeingAgent(prolog, walls)
    vis    = FleeVisualizer(walls)

    print("\n  Controls:")
    print("    SPACE = pause/resume")
    print("    ESC   = quit")
    print("\n" + "=" * 60 + "\n")

    running   = True
    paused    = False
    max_steps = 1000

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    print(f"\n  {'PAUSED' if paused else 'RESUMED'}\n")

        if not paused and not agent.won and not agent.lost:
            if agent.step_count < max_steps:
                agent.step()
            else:
                print(f"\n  Max steps ({max_steps}) reached — simulation ended")
                running = False

        vis.draw(agent)
        vis.clock.tick(FPS)

    print("\n" + "=" * 60)
    print("  SIMULATION COMPLETE")
    print("=" * 60)
    print(f"  Steps      : {agent.step_count}")
    print(f"  Agent won  : {agent.won}")
    print(f"  Zombie won : {agent.lost}")
    if not agent.won and not agent.lost:
        final_dist = abs(agent.ax - GOAL_POS[0]) + abs(agent.ay - GOAL_POS[1])
        print(f"  Final distance to goal: {final_dist}")
    print("=" * 60 + "\n")
    pygame.quit()

if __name__ == "__main__":
    main()
