import queue
from typing import Dict, List
from typing import Optional
from collections import deque

import rubik


def shortest_path(
        start: rubik.Position,
        end: rubik.Position,
) -> Optional[List[rubik.Permutation]]:
    """
    Using 2-way BFS, finds the shortest path from start to end.
    Returns a list of Permutations representing that shortest path.
    If there is no path to be found, return None instead of a list.

    You can use the rubik.quarter_twists move 6-tuple.
    Each move can be applied using rubik.perm_apply.
    """
    # no moves needed if start is end
    if start == end:
        return []
    
    moves = rubik.quarter_twists
    # queues and visited dictionaries for both directions
    forward_queue = deque()
    backward_queue = deque()
    forward_queue.append(start)
    backward_queue.append(end)
    forward_visited: Dict[rubik.Position, rubik.Permutation] = {}
    backward_visited: Dict[rubik.Position, rubik.Permutation] = {}
    solution: List[rubik.Permutation] = []
    
    while forward_queue and backward_queue:
        if len(forward_queue) <= len(backward_queue):
            meeting_point, solution = step(
                forward_visited,
                forward_queue,
                backward_visited,
                backward_queue,
                moves,
            )
        else:
            meeting_point, solution = step(
                backward_visited,
                backward_queue,
                forward_visited,
                forward_queue,
                moves,
            )
    return solution
    #raise NotImplementedError
    
    
def step(backward_visited: Dict[rubik.Position, rubik.Permutation],
         backward_queue: deque,
         forward_visited: Dict[rubik.Position, rubik.Permutation],
         forward_queue: deque,
         moves: List[rubik.Permutation],
         ) -> Optional[tuple[rubik.Position, List[rubik.Permutation]]]:
    current_position = forward_queue.popleft()
    for move in moves:
        neighbor = rubik.perm_apply(move, current_position)
        if neighbor in forward_visited:
            continue
        forward_visited[neighbor] = move
        forward_queue.append(neighbor)
        if neighbor in backward_visited:
            # Found a meeting point
            solution = reconstruct_path(neighbor, forward_visited, backward_visited)
            return neighbor, solution
    return None, []
        
def reconstruct_path(meeting_point: rubik.Position,
                     forward_visited: Dict[rubik.Position, rubik.Permutation],
                     backward_visited: Dict[rubik.Position, rubik.Permutation],
                     ) -> List[rubik.Permutation]:
    # Reconstruct the path from start to meeting_point
    path = []
    current = meeting_point
    while current in forward_visited:
        path.append(forward_visited[current])
        current = rubik.perm_apply(forward_visited[current], current)
    path.reverse()
    # Append the backward path
    current = meeting_point
    while current in backward_visited:
        path.append(backward_visited[current])
        current = rubik.perm_apply(backward_visited[current], current)
    return path