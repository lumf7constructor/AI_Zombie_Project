"""
Shared utility functions for the AI Zombie Project.
Includes pathfinding algorithms and helper functions.
"""

import collections
from config import GRID, GRID_WIDTH, GRID_HEIGHT


def get_bfs_path(start, goal, grid=None, return_info=False):
    """
    Finds the shortest path from start to goal using BFS.
    Avoids walls (grid value 1).
    
    Args:
        start: [x, y] starting position
        goal: [x, y] goal position
        grid: Grid to use (defaults to GRID if not provided)
        
    Returns:
        List of tuples representing the path from start to goal.
        Returns empty list if no path exists.
    """
    # Parent-pointer BFS to avoid copying paths for every queue entry.
    if grid is None:
        grid = GRID

    grid_width = len(grid[0]) if grid else GRID_WIDTH
    grid_height = len(grid) if grid else GRID_HEIGHT

    start_t = tuple(start)
    goal_t = tuple(goal)

    from collections import deque
    q = deque([start_t])
    visited = {start_t}
    parent = {start_t: None}
    nodes_expanded = 0

    while q:
        x, y = q.popleft()
        nodes_expanded += 1

        if (x, y) == goal_t:
            # reconstruct path
            path = []
            cur = goal_t
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            path.reverse()
            if return_info:
                return path, {"visited": visited, "nodes_expanded": nodes_expanded}
            return path

        # neighbor order: Down, Up, Right, Left (keeps old behavior)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid_width and 0 <= ny < grid_height:
                if grid[ny][nx] != 1 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    parent[(nx, ny)] = (x, y)
                    q.append((nx, ny))

    if return_info:
        return [], {"visited": visited, "nodes_expanded": nodes_expanded}
    return []


def get_manhattan_distance(pos1, pos2):
    """
    Calculates Manhattan distance between two positions.
    Useful for heuristic-based pathfinding.
    
    Args:
        pos1: [x, y] position 1
        pos2: [x, y] position 2
        
    Returns:
        Integer Manhattan distance
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def is_valid_position(x, y):
    """
    Checks if a position is within grid bounds and not a wall.
    
    Args:
        x: Column coordinate
        y: Row coordinate
        
    Returns:
        True if position is valid, False otherwise
    """
    if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
        return False
    return GRID[y][x] != 1


def get_neighbors(x, y, include_diagonals=False):
    """
    Gets valid neighboring positions from a given position.
    
    Args:
        x: Column coordinate
        y: Row coordinate
        include_diagonals: If True, includes diagonal neighbors
        
    Returns:
        List of valid neighboring [x, y] positions
    """
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    if include_diagonals:
        directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
    
    neighbors = []
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if is_valid_position(nx, ny):
            neighbors.append([nx, ny])
    
    return neighbors


def get_astar_path(start, goal, grid=None, return_info=False):
    """
    Finds the shortest path from start to goal using A* algorithm.
    Uses Manhattan distance as the heuristic.

    Args:
        start: [x, y] starting position
        goal: [x, y] goal position
        grid: Grid to use (defaults to GRID if not provided)
        return_info: if True return (path, info_dict) where info_dict contains stats

    Returns:
        List of tuples representing the path from start to goal.
        If return_info is True, returns (path, info_dict).
    """
    if grid is None:
        grid = GRID

    grid_width = len(grid[0]) if grid else GRID_WIDTH
    grid_height = len(grid) if grid else GRID_HEIGHT

    import heapq
    counter = 0
    start_t = tuple(start)
    goal_t = tuple(goal)

    # A* with parent pointers. Heap stores (f_score, counter, node)
    open_heap = []
    g_score = {start_t: 0}
    h0 = abs(start_t[0] - goal_t[0]) + abs(start_t[1] - goal_t[1])
    heapq.heappush(open_heap, (h0, counter, start_t))

    came_from = {}
    closed = set()
    nodes_expanded = 0
    heap_ops = 1

    while open_heap:
        f, _, current = heapq.heappop(open_heap)
        nodes_expanded += 1
        if current in closed:
            continue
        if current == goal_t:
            # reconstruct path
            path = []
            cur = current
            while cur in came_from:
                path.append(cur)
                cur = came_from[cur]
            path.append(start_t)
            path.reverse()
            if return_info:
                return path, {"visited": closed, "nodes_expanded": nodes_expanded, "heap_ops": heap_ops}
            return path

        closed.add(current)

        x, y = current
        # neighbors: Down, Up, Right, Left (same order as BFS)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            neighbor = (nx, ny)
            if 0 <= nx < grid_width and 0 <= ny < grid_height:
                if grid[ny][nx] == 1:
                    continue
                tentative_g = g_score[current] + 1
                if neighbor in g_score and tentative_g >= g_score.get(neighbor, float('inf')):
                    continue
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current
                h = abs(nx - goal_t[0]) + abs(ny - goal_t[1])
                f_neighbor = tentative_g + h
                counter += 1
                heapq.heappush(open_heap, (f_neighbor, counter, neighbor))
                heap_ops += 1

    if return_info:
        return [], {"visited": closed, "nodes_expanded": nodes_expanded, "heap_ops": heap_ops}
    return []


def get_astar_path_fast(start, goal, grid=None, return_info=False):
    """
    Faster A* variant using integer-encoded nodes and preallocated lists.

    This reduces per-node Python object allocations (no tuple nodes in heap or dict
    keys) and uses lists for g-scores/closed/came_from for lower overhead on large
    numbers of heap operations.

    Signature mirrors get_astar_path.
    """
    if grid is None:
        grid = GRID

    grid_width = len(grid[0]) if grid else GRID_WIDTH
    grid_height = len(grid) if grid else GRID_HEIGHT

    import heapq

    sx, sy = start[0], start[1]
    gx, gy = goal[0], goal[1]
    start_idx = sy * grid_width + sx
    goal_idx = gy * grid_width + gx

    size = grid_width * grid_height
    INF = 10 ** 9

    g_score = [INF] * size
    came_from = [-1] * size
    closed = [False] * size

    g_score[start_idx] = 0

    h0 = abs(sx - gx) + abs(sy - gy)
    open_heap = []
    counter = 0
    heapq.heappush(open_heap, (h0, counter, start_idx))
    heap_ops = 1
    nodes_expanded = 0

    while open_heap:
        f, _, current = heapq.heappop(open_heap)
        if closed[current]:
            continue
        nodes_expanded += 1
        if current == goal_idx:
            # reconstruct path
            path = []
            cur = current
            while cur != -1:
                cx = cur % grid_width
                cy = cur // grid_width
                path.append((cx, cy))
                cur = came_from[cur]
            path.reverse()
            if return_info:
                # convert closed indices to a set of tuples for compatibility
                visited = set()
                for i, v in enumerate(closed):
                    if v:
                        visited.add((i % grid_width, i // grid_width))
                return path, {"visited": visited, "nodes_expanded": nodes_expanded, "heap_ops": heap_ops}
            return path

        closed[current] = True
        x = current % grid_width
        y = current // grid_width

        # neighbors: Down, Up, Right, Left
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid_width and 0 <= ny < grid_height:
                if grid[ny][nx] == 1:
                    continue
                neighbor_idx = ny * grid_width + nx
                tentative_g = g_score[current] + 1
                if tentative_g >= g_score[neighbor_idx]:
                    continue
                g_score[neighbor_idx] = tentative_g
                came_from[neighbor_idx] = current
                h = abs(nx - gx) + abs(ny - gy)
                f_neighbor = tentative_g + h
                counter += 1
                heapq.heappush(open_heap, (f_neighbor, counter, neighbor_idx))
                heap_ops += 1

    if return_info:
        visited = set()
        for i, v in enumerate(closed):
            if v:
                visited.add((i % grid_width, i // grid_width))
        return [], {"visited": visited, "nodes_expanded": nodes_expanded, "heap_ops": heap_ops}
    return []
