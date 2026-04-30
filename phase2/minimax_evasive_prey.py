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
#  GAME-SPECIFIC COLOURS
# ==============================================================================
PREY_COLOR     = (30,  144, 255)   # dodger-blue
MONSTER_COLOR  = (220,  20,  60)   # crimson red
REWARD_COLOR   = (255, 215,   0)   # gold
PANEL_BG       = ( 30,  30,  30)
TEXT_COLOR     = (230, 230, 230)
WIN_COLOR      = ( 50, 205,  50)   # lime green  -> prey wins
LOSE_COLOR     = (220,  20,  60)   # crimson      -> monster wins

# ==============================================================================
#  AGENT POSITIONS
# ==============================================================================
prey_start   = list(PLAYER_START_POS_LARGE)
monster_start = [GRID_WIDTH_LARGE - 2, GRID_HEIGHT_LARGE - 2]
reward_pos   = list(GOAL_POS_LARGE)

# ==============================================================================
#  MINIMAX PARAMETERS
# ==============================================================================
PREY_MINIMAX_DEPTH = 2  # How many moves ahead prey looks (deeper = smarter but slower)
PREY_LOOKAHEAD_MOVES = 3  # Monster looks 3 moves ahead in prey's simulation

# ==============================================================================
#  SPEED CONTROLS
# ==============================================================================
STEPS_PER_FRAME = 2

PANEL_HEIGHT = 95

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
    """Draw a path as connected line segments."""
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


def draw_panel(surface, width, step, prey_dist, monster_dist, result=None, strategy=""):
    """Draw the top information panel."""
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

    # ROW 1: Step and distances
    surface.blit(font_med.render(f"Step: {step}", True, TEXT_COLOR), (10, 8))
    dist = font_med.render(
        f"Prey -> Reward: {prey_dist} steps     Monster -> Prey: {monster_dist} steps",
        True, TEXT_COLOR,
    )
    surface.blit(dist, dist.get_rect(center=(width // 2, 16)))

    # ROW 2: Legend
    dot_r = 6
    # Prey
    pygame.draw.circle(surface, PREY_COLOR, (14, 40), dot_r)
    surface.blit(font_med.render("Prey (MINIMAX - evasive)", True, PREY_COLOR), (24, 32))
    # Monster
    pygame.draw.circle(surface, MONSTER_COLOR, (width // 2 - 70, 40), dot_r)
    surface.blit(font_med.render("Monster (A* - chaser)", True, MONSTER_COLOR),
                 (width // 2 - 60, 32))
    # Reward
    rdx = width - 110
    diamond = [(rdx+dot_r, 34), (rdx+dot_r*2, 40), (rdx+dot_r, 46), (rdx, 40)]
    pygame.draw.polygon(surface, REWARD_COLOR, diamond)
    surface.blit(font_med.render("Reward", True, REWARD_COLOR), (rdx + dot_r*2 + 4, 32))

    # ROW 3: Controls
    ctrl = font_sml.render("SPACE = pause     R = restart     ESC = quit", True, (120, 120, 120))
    surface.blit(ctrl, ctrl.get_rect(center=(width // 2, 72)))


# ==============================================================================
#  MINIMAX EVALUATION FUNCTION
# ==============================================================================
def evaluate_board(prey_pos, monster_pos, reward_pos):
    """
    Evaluation function for the prey's minimax search.
    
    Score = (Distance from Prey to Monster) - (Distance from Prey to Reward)
    
    HIGH score = good for prey (far from monster, moving toward reward)
    LOW score = bad for prey (close to monster)
    """
    dist_to_monster = abs(prey_pos[0] - monster_pos[0]) + abs(prey_pos[1] - monster_pos[1])
    dist_to_reward = abs(prey_pos[0] - reward_pos[0]) + abs(prey_pos[1] - reward_pos[1])
    
    score = dist_to_monster - dist_to_reward
    return score


# ==============================================================================
#  MINIMAX SEARCH WITH EVALUATION
# ==============================================================================
_minimax_cache = {}

def minimax_evasive_prey(prey_pos, monster_pos, reward_pos, depth, grid):
    """
    Minimax search for evasive prey with memoization.
    Prey maximizes: (distance to monster) - (distance to reward)
    Monster minimizes (simulated as A* chase)
    """
    # Cache key
    cache_key = (prey_pos, monster_pos, reward_pos, depth)
    if cache_key in _minimax_cache:
        return _minimax_cache[cache_key]
    
    if depth == 0:
        score = evaluate_board(prey_pos, monster_pos, reward_pos)
        result = ([], score)
        _minimax_cache[cache_key] = result
        return result
    
    # Check if prey reached reward
    if prey_pos == tuple(reward_pos):
        result = ([prey_pos], float('inf'))
        _minimax_cache[cache_key] = result
        return result
    
    # Check if caught
    if prey_pos == monster_pos:
        result = ([prey_pos], float('-inf'))
        _minimax_cache[cache_key] = result
        return result
    
    # Generate valid moves for prey
    valid_moves = []
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = prey_pos[0] + dx, prey_pos[1] + dy
        if 0 <= nx < GRID_WIDTH_LARGE and 0 <= ny < GRID_HEIGHT_LARGE:
            if grid[ny][nx] != 1:
                valid_moves.append((nx, ny))
    
    if not valid_moves:
        score = evaluate_board(prey_pos, monster_pos, reward_pos)
        result = ([prey_pos], score)
        _minimax_cache[cache_key] = result
        return result
    
    best_move = None
    best_score = float('-inf')
    
    for move in valid_moves:
        # Simulate monster chasing this move
        simulated_monster = list(monster_pos)
        monster_path = get_astar_path(tuple(monster_pos), tuple(move), grid)
        if len(monster_path) > 1:
            simulated_monster = list(monster_path[1])
        
        # Recursive call
        _, score = minimax_evasive_prey(move, tuple(simulated_monster), reward_pos, depth - 1, grid)
        
        if score > best_score:
            best_score = score
            best_move = move
    
    if best_move is None:
        best_move = valid_moves[0]
    
    result = ([best_move], best_score)
    _minimax_cache[cache_key] = result
    return result


def find_evasive_prey_path(prey_pos, monster_pos, reward_pos, grid):
    """
    Find an evasive path using minimax evaluation.
    
    Strategy:
    1. Use minimax to pick the safest NEXT MOVE (considering monster)
    2. Extend from there using A* to reward
    3. This balances safety (minimax) with efficiency (A*)
    """
    _minimax_cache.clear()  # Clear cache each turn to stay responsive
    
    # Use minimax to pick the safest NEXT MOVE
    path, score = minimax_evasive_prey(tuple(prey_pos), tuple(monster_pos), tuple(reward_pos), 
                                       PREY_MINIMAX_DEPTH, grid)
    
    # If minimax found a move, use it
    if path and len(path) > 0:
        next_pos = path[0]
        # Continue from there to reward using A*
        full_path = get_astar_path(tuple(next_pos), tuple(reward_pos), grid)
        if full_path:
            return [tuple(prey_pos)] + full_path
        else:
            return [tuple(prey_pos), next_pos]
    
    # Fallback: use pure A* if minimax fails
    astar_path = get_astar_path(tuple(prey_pos), tuple(reward_pos), grid)
    return astar_path if astar_path else [tuple(prey_pos)]


# ==============================================================================
#  GAME STATE
# ==============================================================================
class EvativePreyGame:
    """Game with evasive minimax prey and chasing A* monster."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.prey_pos    = list(prey_start)
        self.monster_pos = list(monster_start)
        self.step_count  = 0
        self.result      = None
        self.paused      = False
        self.prey_path   = []
        self.monster_path = []
        self._update_paths()

    def _update_paths(self):
        """Update both agents' paths."""
        # Evasive prey using minimax
        prey_next = find_evasive_prey_path(self.prey_pos, self.monster_pos, reward_pos, GRID_LARGE)
        self.prey_path = prey_next if prey_next else [self.prey_pos]

        # Monster using A*
        self.monster_path = get_astar_path(
            tuple(self.monster_pos), tuple(self.prey_pos), GRID_LARGE
        )

    def tick(self):
        """Advance the game by one step."""
        if self.result or self.paused:
            return

        # Prey moves
        if len(self.prey_path) > 1:
            next_prey = list(self.prey_path[1])
        else:
            next_prey = self.prey_pos

        # Monster moves
        if len(self.monster_path) > 1:
            next_monster = list(self.monster_path[1])
        else:
            next_monster = self.monster_pos

        self.prey_pos    = next_prey
        self.monster_pos = next_monster
        self.step_count += 1

        # Check win conditions
        if self.prey_pos == reward_pos:
            self.result = "prey"
            return

        if self.monster_pos == self.prey_pos:
            self.result = "monster"
            return

        # Recalculate paths
        self._update_paths()

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
    pygame.display.set_caption("Freeze Tag  |  Prey (MINIMAX - Evasive) vs Monster (A*)")
    clock  = pygame.time.Clock()

    game         = EvativePreyGame()
    frame_count  = 0
    end_display  = None

    while True:
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

        # Simulation tick
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

        # Drawing
        screen.fill(BG_COLOR)
        draw_grid(screen, GRID_LARGE)

        draw_path(screen, game.prey_path,    PREY_COLOR,    width=2)
        draw_path(screen, game.monster_path, MONSTER_COLOR, width=2)

        draw_reward(screen, reward_pos)

        draw_agent(screen, game.prey_pos,    PREY_COLOR,    "P")
        draw_agent(screen, game.monster_pos, MONSTER_COLOR, "M")

        draw_panel(screen, W, game.step_count,
                   game.prey_dist, game.monster_dist,
                   result=game.result)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
