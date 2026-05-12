% ============================================================================
% REASONING.PL - Prolog Knowledge Base for Agent Reasoning
% ============================================================================
% Dynamic facts asserted by Python at runtime
:- dynamic wall/2.           % wall(X, Y) - obstacle cells
:- dynamic goal/2.           % goal(X, Y) - target location
:- dynamic agent/2.          % agent(X, Y) - current agent position
:- dynamic grid_size/2.      % grid_size(W, H) - grid dimensions

% ============================================================================
% SPATIAL REASONING - Environment Understanding
% ============================================================================

% is_within_bounds/2: Check if coordinates are within grid bounds
is_within_bounds(X, Y) :-
    grid_size(W, H),
    X >= 0,
    X < W,
    Y >= 0,
    Y < H.

% is_safe/2: Cell is within bounds AND not a wall
is_safe(X, Y) :-
    is_within_bounds(X, Y),
    \+ wall(X, Y).

% ============================================================================
% MOVEMENT REASONING - Valid Actions
% ============================================================================

% get_neighbor/3: Get a valid neighbor in a direction
% Directions: up(0,-1), down(0,1), left(-1,0), right(1,0)
get_neighbor(X, Y, up, NX, NY) :-
    NX is X,
    NY is Y - 1,
    is_safe(NX, NY).

get_neighbor(X, Y, down, NX, NY) :-
    NX is X,
    NY is Y + 1,
    is_safe(NX, NY).

get_neighbor(X, Y, left, NX, NY) :-
    NX is X - 1,
    NY is Y,
    is_safe(NX, NY).

get_neighbor(X, Y, right, NX, NY) :-
    NX is X + 1,
    NY is Y,
    is_safe(NX, NY).

% can_move/4: Determine if agent can move from (X,Y) to (NX,NY)
can_move(X, Y, NX, NY) :-
    get_neighbor(X, Y, _, NX, NY).

% get_all_neighbors/3: Find all safe neighboring cells
get_all_neighbors(X, Y, Neighbors) :-
    findall(
        neighbor(NX, NY),
        can_move(X, Y, NX, NY),
        Neighbors
    ).

% ============================================================================
% DISTANCE REASONING
% ============================================================================

% manhattan/4: Calculate Manhattan distance between two points
% manhattan(X1, Y1, X2, Y2, Distance)
manhattan(X1, Y1, X2, Y2, Distance) :-
    DX is abs(X1 - X2),
    DY is abs(Y1 - Y2),
    Distance is DX + DY.

% euclidean/4: Calculate Euclidean distance (for reference)
euclidean(X1, Y1, X2, Y2, Distance) :-
    DX is X1 - X2,
    DY is Y1 - Y2,
    DistSq is (DX * DX) + (DY * DY),
    Distance is sqrt(DistSq).

% ============================================================================
% GOAL REASONING - Target Achievement
% ============================================================================

% reached_goal/2: Check if agent is at goal position
reached_goal(X, Y) :-
    goal(X, Y),
    agent(X, Y).

% distance_to_goal/2: Get Manhattan distance from current position to goal
distance_to_goal(X, Y, Distance) :-
    agent(X, Y),
    goal(GX, GY),
    manhattan(X, Y, GX, GY, Distance).

% is_closer/4: Check if cell (NX, NY) is closer to goal than (X, Y)
is_closer(X, Y, NX, NY) :-
    goal(GX, GY),
    manhattan(X, Y, GX, GY, OldDist),
    manhattan(NX, NY, GX, GY, NewDist),
    NewDist < OldDist.

% ============================================================================
% DECISION REASONING - Greedy Strategy (Minimize Distance to Goal)
% ============================================================================

% best_next_step/2: Find the neighbor that minimizes distance to goal
best_next_step(X, Y, neighbor(BestX, BestY)) :-
    agent(X, Y),
    goal(GX, GY),
    % Find all valid moves
    findall(
        neighbor(NX, NY) - Dist,
        (can_move(X, Y, NX, NY), manhattan(NX, NY, GX, GY, Dist)),
        Candidates
    ),
    % Check that we have valid candidates
    Candidates \= [],
    % Sort by distance (ascending) and pick the first
    sort(2, @=<, Candidates, Sorted),
    Sorted = [neighbor(BestX, BestY) - _ | _].

% next_step/4: Query-friendly version for Python
next_step(X, Y, NX, NY) :-
    best_next_step(X, Y, neighbor(NX, NY)).

% ============================================================================
% REASONING ABOUT STATE CHANGES - Effects of Actions
% ============================================================================

% can_reach_goal/1: Reasoning about reachability
% (Checks if there exists ANY safe path using BFS logic)
can_reach_goal :-
    agent(X, Y),
    goal(GX, GY),
    bfs_reachable(X, Y, GX, GY, []).

% bfs_reachable/4: BFS-style reachability check
bfs_reachable(X, Y, X, Y, _) :- !.  % Reached goal
bfs_reachable(X, Y, GX, GY, Visited) :-
    findall(
        neighbor(NX, NY),
        (can_move(X, Y, NX, NY), \+ member(neighbor(NX, NY), Visited)),
        Neighbors
    ),
    Neighbors \= [],
    append(Visited, [neighbor(X, Y)], NewVisited),
    bfs_reachable_queue(Neighbors, GX, GY, NewVisited).

% bfs_reachable_queue/4: Process BFS queue
bfs_reachable_queue([neighbor(X, Y) | Rest], GX, GY, Visited) :-
    (   X = GX, Y = GY
    ->  !  % Found goal
    ;   findall(
            neighbor(NX, NY),
            (can_move(X, Y, NX, NY), \+ member(neighbor(NX, NY), Visited)),
            NewNeighbors
        ),
        append(Rest, NewNeighbors, Queue),
        bfs_reachable_queue(Queue, GX, GY, [neighbor(X, Y) | Visited])
    ).

% ============================================================================
% REASONING ABOUT STUCK STATES
% ============================================================================

% is_stuck/0: Check if agent has no valid moves
is_stuck :-
    agent(X, Y),
    \+ can_move(X, Y, _, _).

% safe_cells_nearby/1: Count safe neighbors
safe_cells_nearby(Count) :-
    agent(X, Y),
    findall(1, can_move(X, Y, _, _), List),
    length(List, Count).

% ============================================================================
% LOGGING AND DEBUGGING UTILITIES
% ============================================================================

% describe_state/0: Print current world state
describe_state :-
    agent(X, Y),
    goal(GX, GY),
    distance_to_goal(X, Y, Dist),
    format('~nAgent at (~w, ~w)~n', [X, Y]),
    format('Goal at (~w, ~w)~n', [GX, GY]),
    format('Distance to goal: ~w~n', [Dist]),
    get_all_neighbors(X, Y, Neighbors),
    length(Neighbors, Count),
    format('Safe neighbors: ~w~n~n', [Count]).

% ============================================================================
% END OF REASONING.PL
% ============================================================================
