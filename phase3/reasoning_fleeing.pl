% ============================================================================
% REASONING_FLEEING.PL - Prolog Knowledge Base for Fleeing Agent
% ============================================================================
:- use_module(library(lists)).

% Dynamic facts
:- dynamic wall/2.
:- dynamic goal/2.
:- dynamic agent/2.
:- dynamic zombie/2.
:- dynamic grid_size/2.
:- dynamic visit_count/3.
:- dynamic visit_step/3.
:- dynamic current_step/1.

% ============================================================================
% SPATIAL REASONING
% ============================================================================
is_within_bounds(X, Y) :-
    grid_size(W, H),
    X >= 0, X < W,
    Y >= 0, Y < H.

is_safe(X, Y) :-
    is_within_bounds(X, Y),
    \+ wall(X, Y).

% ============================================================================
% MOVEMENT
% ============================================================================
neighbor(X, Y, NX, Y)  :- NX is X + 1, is_safe(NX, Y).
neighbor(X, Y, NX, Y)  :- NX is X - 1, is_safe(NX, Y).
neighbor(X, Y, X, NY)  :- NY is Y + 1, is_safe(X, NY).
neighbor(X, Y, X, NY)  :- NY is Y - 1, is_safe(X, NY).

can_move(X, Y, NX, NY) :- neighbor(X, Y, NX, NY).

% ============================================================================
% DISTANCE
% ============================================================================
manhattan(X1, Y1, X2, Y2, D) :-
    D is abs(X1 - X2) + abs(Y1 - Y2).

distance_to_goal(X, Y, D) :-
    goal(GX, GY),
    manhattan(X, Y, GX, GY, D).

distance_to_zombie(X, Y, D) :-
    zombie(ZX, ZY),
    manhattan(X, Y, ZX, ZY, D).

% ============================================================================
% ZOMBIE PREDICTION
% ============================================================================
zombie_next_cells(Cells) :-
    zombie(ZX, ZY),
    agent(AX, AY),
    findall(
        NX-NY,
        (   neighbor(ZX, ZY, NX, NY),
            manhattan(NX, NY, AX, AY, D1),
            manhattan(ZX, ZY, AX, AY, D2),
            D1 =< D2
        ),
        Cells
    ).

zombie_will_be_at(X, Y) :-
    zombie_next_cells(Cells),
    member(X-Y, Cells).

% ============================================================================
% DANGER LEVELS
% ============================================================================
danger_level(X, Y, 0) :- zombie(X, Y), !.
danger_level(X, Y, 1) :- zombie_will_be_at(X, Y), !.
danger_level(_, _, 2).

% ============================================================================
% RECENCY-WEIGHTED VISIT PENALTY
% ============================================================================
visit_penalty(X, Y, Penalty) :-
    visit_count(X, Y, Count),
    !,
    (   current_step(Step),
        visit_step(X, Y, LastStep),
        Recency is Step - LastStep,
        (   Recency > 10
        ->  Penalty is -(Count * 4)
        ;   Penalty is -(Count * 8)
        )
    ;   Penalty is -(Count * 8)
    ).
visit_penalty(_, _, 0).

% ============================================================================
% 2-STEP LOOKAHEAD BONUS
% Rewards cells with more unvisited safe escape routes
% ============================================================================
lookahead_bonus(X, Y, Bonus) :-
    findall(
        1,
        (   can_move(X, Y, NX, NY),
            danger_level(NX, NY, 2),
            \+ visit_count(NX, NY, _)
        ),
        FreeNeighbors
    ),
    length(FreeNeighbors, N),
    Bonus is N * 2.

% ============================================================================
% SCORING
% Score = (DZ * 3) - DG + visit_penalty + lookahead + step-seeded tie-break
% ============================================================================
score_cell(X, Y, Score) :-
    distance_to_zombie(X, Y, DZ),
    distance_to_goal(X, Y, DG),
    visit_penalty(X, Y, VP),
    lookahead_bonus(X, Y, LB),
    (current_step(Step) -> true ; Step = 0),
    TieBreak is ((X * 31 + Y * 17 + Step) mod 100) * 0.001,
    Score is (DZ * 3) - DG + VP + LB + TieBreak.

% ============================================================================
% FLEE STEP - safe > warning > deadly
% ============================================================================
flee_step(X, Y, NX, NY) :-
    agent(X, Y),
    best_move(X, Y, 2, NX, NY), !,
    record_move(NX, NY).

flee_step(X, Y, NX, NY) :-
    agent(X, Y),
    best_move(X, Y, 1, NX, NY), !,
    record_move(NX, NY).

flee_step(X, Y, NX, NY) :-
    agent(X, Y),
    best_move(X, Y, 0, NX, NY), !,
    record_move(NX, NY).

best_move(X, Y, DangerLevel, BestX, BestY) :-
    findall(
        Score-NX0-NY0,
        (   can_move(X, Y, NX0, NY0),
            danger_level(NX0, NY0, DangerLevel),
            score_cell(NX0, NY0, Score)
        ),
        Moves
    ),
    Moves \= [],
    sort(Moves, SortedAsc),
    reverse(SortedAsc, [_-BestX-BestY|_]).

% ============================================================================
% VISIT TRACKING
% ============================================================================
record_move(X, Y) :-
    (current_step(Step) -> true ; Step = 0),
    (   retract(visit_count(X, Y, OldCount))
    ->  NewCount is OldCount + 1
    ;   NewCount = 1
    ),
    assertz(visit_count(X, Y, NewCount)),
    retractall(visit_step(X, Y, _)),
    assertz(visit_step(X, Y, Step)).

clear_old_visited :-
    current_step(Step),
    Cutoff is Step - 20,
    forall(
        (visit_step(X, Y, S), S < Cutoff),
        (   retract(visit_count(X, Y, _)),
            retract(visit_step(X, Y, _))
        )
    ).

clear_visited :-
    retractall(visit_count(_, _, _)),
    retractall(visit_step(_, _, _)).

set_step(S) :-
    retractall(current_step(_)),
    assertz(current_step(S)).

% ============================================================================
% STATUS
% ============================================================================
reached_goal(X, Y)     :- goal(X, Y).
caught_by_zombie(X, Y) :- zombie(X, Y).

agent_status(at_goal)  :- agent(X, Y), reached_goal(X, Y), !.
agent_status(caught)   :- agent(X, Y), caught_by_zombie(X, Y), !.
agent_status(fleeing)  :-
    agent(AX, AY), zombie(ZX, ZY),
    manhattan(AX, AY, ZX, ZY, D), D < 5, !.
agent_status(navigating).
