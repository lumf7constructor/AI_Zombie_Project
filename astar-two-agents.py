import pygame
import sys
import os
import time

# -- resolve parent directory so we can import config & utils --
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    TILE_SIZE_LARGE,        # pixel size of each tile  (e.g. 20)
    GRID_WIDTH_LARGE,       # number of columns        (e.g. 30)
    GRID_HEIGHT_LARGE,      # number of rows           (e.g. 30)
    FPS,                    # frames per second
    BG_COLOR,               # background colour
    WALL_COLOR,             # wall tile colour
    GRID_LINE_COLOR,        # thin grid-line colour
    GRID_LARGE,             # the 2-D maze  (0=open, 1=wall)
    PLAYER_START_POS_LARGE, # [col, row] start for the prey
    GOAL_POS_LARGE,         # [col, row] for the reward
)
from utils import get_astar_path

# ==============================================================================
#  GAME-SPECIFIC COLOURS  (override / extend the project palette here)
# ==============================================================================
PREY_COLOR     = (30,  144, 255)   # dodger-blue
MONSTER_COLOR  = (220,  20,  60)   # crimson red
REWARD_COLOR   = (255, 215,   0)   # gold
PATH_PREY_COL  = ( 30, 144, 255, 80)   # semi-transparent blue  (prey trail)
PATH_MON_COL   = (220,  20,  60, 80)   # semi-transparent red   (monster trail)
PANEL_BG       = ( 30,  30,  30)
TEXT_COLOR     = (230, 230, 230)
WIN_COLOR      = ( 50, 205,  50)   # lime green  -> prey wins
LOSE_COLOR     = (220,  20,  60)   # crimson      -> monster wins

# ==============================================================================
#  AGENT POSITIONS  (feel free to edit)
# ==============================================================================
# Prey starts at the project's default player start.
prey_start   = list(PLAYER_START_POS_LARGE)   # e.g. [1, 1]

# Monster starts at the opposite corner - far from both prey and reward.
# Change these to any open [col, row] on the grid.
monster_start = [GRID_WIDTH_LARGE - 2, GRID_HEIGHT_LARGE - 2]

# Reward is fixed (the existing goal position).
reward_pos   = list(GOAL_POS_LARGE)

# ==============================================================================
#  SPEED CONTROLS
# ==============================================================================
# How many Pygame frames pass between each game-logic step.
# Lower  -> faster simulation.    Higher -> slower / easier to follow.
STEPS_PER_FRAME = 5   # 1 = every frame,  10 = every 10th frame

# ==============================================================================
#  HELPERS
# ==============================================================================
PANEL_HEIGHT = 95   # pixels reserved at the top for the UI panel

def tile_rect(col: int, row: int) -> pygame.Rect:
    """Return the screen Rect for grid cell (col, row)."""
    return pygame.Rect(
        col * TILE_SIZE_LARGE,
        row * TILE_SIZE_LARGE + PANEL_HEIGHT,
        TILE_SIZE_LARGE,
        TILE_SIZE_LARGE,
    )


def draw_grid(surface, grid):
    """Draw all tiles (walls + empty) with grid-lines."""
    for r in range(GRID_HEIGHT_LARGE):
        for c in range(GRID_WIDTH_LARGE):
            rect = tile_rect(c, r)
            color = WALL_COLOR if grid[r][c] == 1 else BG_COLOR
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, GRID_LINE_COLOR, rect, 1)


def draw_path(surface, path, color_rgb, width=2):
    """Draw a path as connected line segments (no alpha needed)."""
    if len(path) < 2:
        return
    points = [
        (c * TILE_SIZE_LARGE + TILE_SIZE_LARGE // 2,
         r * TILE_SIZE_LARGE + TILE_SIZE_LARGE // 2 + PANEL_HEIGHT)
        for (c, r) in path
    ]
    pygame.draw.lines(surface, color_rgb, False, points, width)


def draw_agent(surface, pos, color, label=""):
    """Draw a filled circle for an agent with an optional letter."""
    cx = pos[0] * TILE_SIZE_LARGE + TILE_SIZE_LARGE // 2
    cy = pos[1] * TILE_SIZE_LARGE + TILE_SIZE_LARGE // 2 + PANEL_HEIGHT
    radius = max(TILE_SIZE_LARGE // 2 - 2, 4)
    pygame.draw.circle(surface, color, (cx, cy), radius)
    if label:
        font = pygame.font.SysFont(None, max(TILE_SIZE_LARGE - 4, 10))
        txt = font.render(label, True, (255, 255, 255))
        surface.blit(txt, txt.get_rect(center=(cx, cy)))


def draw_reward(surface, pos):
    """Draw the reward as a filled gold diamond."""
    cx = pos[0] * TILE_SIZE_LARGE + TILE_SIZE_LARGE // 2
    cy = pos[1] * TILE_SIZE_LARGE + TILE_SIZE_LARGE // 2 + PANEL_HEIGHT
    half = max(TILE_SIZE_LARGE // 2 - 2, 4)
    diamond = [
        (cx,        cy - half),
        (cx + half, cy),
        (cx,        cy + half),
        (cx - half, cy),
    ]
    pygame.draw.polygon(surface, REWARD_COLOR, diamond)
    pygame.draw.polygon(surface, (180, 140, 0), diamond, 2)


def draw_panel(surface, width, step, prey_dist, monster_dist, result=None):
    """Draw the top information panel -- three clean rows, nothing overlaps."""
    pygame.draw.rect(surface, PANEL_BG, (0, 0, width, PANEL_HEIGHT))
    pygame.draw.line(surface, GRID_LINE_COLOR, (0, PANEL_HEIGHT), (width, PANEL_HEIGHT), 2)

    font_big = pygame.font.SysFont(None, 30)
    font_med = pygame.font.SysFont(None, 22)
    font_sml = pygame.font.SysFont(None, 18)

    if result:
        col = WIN_COLOR if result == "prey" else LOSE_COLOR
        msg = "PREY WINS!  Reached the reward!" if result == "prey" else "MONSTER WINS!  Prey was caught!"
        txt = font_big.render(msg, True, col)
        surface.blit(txt, txt.get_rect(center=(width // 2, PANEL_HEIGHT // 2)))
        return

    # -- ROW 1 (y=8):  Step left,  distances centered --
    surface.blit(font_med.render(f"Step: {step}", True, TEXT_COLOR), (10, 8))
    dist = font_med.render(
        f"Prey -> Reward: {prey_dist} steps     Monster -> Prey: {monster_dist} steps",
        True, TEXT_COLOR,
    )
    surface.blit(dist, dist.get_rect(center=(width // 2, 16)))

    # -- ROW 2 (y=36):  Legend dots evenly spaced --
    dot_r = 6
    # Prey
    pygame.draw.circle(surface, PREY_COLOR, (14, 40), dot_r)
    surface.blit(font_med.render("Prey (A* -> reward)", True, PREY_COLOR), (24, 32))
    # Monster
    pygame.draw.circle(surface, MONSTER_COLOR, (width // 2 - 70, 40), dot_r)
    surface.blit(font_med.render("Monster (A* -> prey)", True, MONSTER_COLOR),
                 (width // 2 - 60, 32))
    # Reward diamond
    rdx = width - 110
    diamond = [(rdx+dot_r, 34), (rdx+dot_r*2, 40), (rdx+dot_r, 46), (rdx, 40)]
    pygame.draw.polygon(surface, REWARD_COLOR, diamond)
    surface.blit(font_med.render("Reward", True, REWARD_COLOR), (rdx + dot_r*2 + 4, 32))

    # -- ROW 3 (y=60):  Controls centered --
    ctrl = font_sml.render("SPACE = pause     R = restart     ESC = quit", True, (120, 120, 120))
    surface.blit(ctrl, ctrl.get_rect(center=(width // 2, 72)))


# ==============================================================================
#  GAME STATE
# ==============================================================================
class FreezeTagGame:
    """Encapsulates all mutable state so we can easily restart (R key)."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.prey_pos    = list(prey_start)
        self.monster_pos = list(monster_start)
        self.step_count  = 0
        self.result      = None          # None | "prey" | "monster"
        self.paused      = False

        # Compute initial paths
        self.prey_path    = []
        self.monster_path = []
        self._update_paths()

    # -- path planning --
    def _update_paths(self):
        """Re-run A* for both agents."""
        # Prey heads for the reward (fixed goal)
        self.prey_path = get_astar_path(
            tuple(self.prey_pos), tuple(reward_pos), GRID_LARGE
        )

        # Monster heads for prey's CURRENT position (dynamic goal)
        self.monster_path = get_astar_path(
            tuple(self.monster_pos), tuple(self.prey_pos), GRID_LARGE
        )

    # -- one simulation step --
    def tick(self):
        """Advance the game by one step (both agents move once)."""
        if self.result or self.paused:
            return

        # -- PREY moves one step toward reward --
        if len(self.prey_path) > 1:
            next_prey = list(self.prey_path[1])   # [0] is current pos
        else:
            next_prey = self.prey_pos              # already at goal

        # -- MONSTER moves one step toward prey --
        if len(self.monster_path) > 1:
            next_monster = list(self.monster_path[1])
        else:
            next_monster = self.monster_pos

        # Apply moves
        self.prey_pos    = next_prey
        self.monster_pos = next_monster
        self.step_count += 1

        # -- Check win / lose conditions --
        if self.prey_pos == reward_pos:
            self.result = "prey"
            return

        if self.monster_pos == self.prey_pos:
            self.result = "monster"
            return

        # -- Recalculate paths for next step --
        self._update_paths()

    # -- properties for the UI --
    @property
    def prey_dist(self):
        return max(0, len(self.prey_path) - 1)

    @property
    def monster_dist(self):
        return max(0, len(self.monster_path) - 1)


# ==============================================================================
#  MAIN
# ==============================================================================
def main():
    pygame.init()
    W = GRID_WIDTH_LARGE  * TILE_SIZE_LARGE
    H = GRID_HEIGHT_LARGE * TILE_SIZE_LARGE + PANEL_HEIGHT
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Phase 2 - Freeze Tag  |  Prey (A*) vs Monster (A*)")
    clock  = pygame.time.Clock()

    game         = FreezeTagGame()
    frame_count  = 0
    end_display  = None    # timestamp when game ended (for auto-close)

    while True:
        # -- Event handling --
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_SPACE:
                    game.paused = not game.paused
                if event.key == pygame.K_r:
                    game.reset()
                    frame_count = 0
                    end_display = None

        # -- Simulation tick (throttled by STEPS_PER_FRAME) --
        if not game.result:
            frame_count += 1
            if frame_count % STEPS_PER_FRAME == 0:
                game.tick()
        else:
            # Auto-close 4 s after game ends
            if end_display is None:
                end_display = time.time()
            elif time.time() - end_display > 4:
                pygame.quit(); sys.exit()

        # -- Drawing --
        screen.fill(BG_COLOR)
        draw_grid(screen, GRID_LARGE)

        # Path lines (behind agents)
        draw_path(screen, game.prey_path,    PREY_COLOR,    width=2)
        draw_path(screen, game.monster_path, MONSTER_COLOR, width=2)

        # Reward
        draw_reward(screen, reward_pos)

        # Agents
        draw_agent(screen, game.prey_pos,    PREY_COLOR,    "P")
        draw_agent(screen, game.monster_pos, MONSTER_COLOR, "M")

        # Panel
        draw_panel(screen, W, game.step_count,
                   game.prey_dist, game.monster_dist,
                   result=game.result)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()