from typing import Dict, List, Tuple
from typing import Optional
from collections import deque

import rubik

Position = rubik.Position
Permutation = rubik.Permutation
ParentMap = Dict[Position, Tuple[Optional[Position], Optional[Permutation]]]

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

    # Parent maps for both directions
    backward_parents:ParentMap = {start: (None, None)}  
    forward_parents: ParentMap = {end: (None, None)}

    # Queues for both directions
    forward_queue = deque([end])
    backward_queue = deque([start]) 
    count = 0
    while forward_queue and backward_queue and count<14:
        count += 1
        if len(forward_queue) <= len(backward_queue):
            meeting_point = step(
    
                backward_parents,
                forward_parents,
                forward_queue,
                moves,
            )    
        else:
            meeting_point = step( 
                forward_parents,
                backward_parents,
                backward_queue,
                moves,
            )

        if meeting_point is not None:
            left = reconstruct_path(meeting_point, backward_parents)
            right = reconstruct_path(meeting_point, forward_parents)
            reversed_right = [rubik.perm_inverse(mv) for mv in reversed(right)]
            return left + reversed_right
    return None

def step(other_side_parents: ParentMap, 
         this_side_parents: ParentMap, 
         this_side_queue: deque, 
         moves: List[rubik.Permutation]
         ) -> Optional[rubik.Position]:
    #expanding one level in the forward direction
    level_size = len(this_side_queue)
    added_positions = []
    for _ in range(level_size):
        current_position = this_side_queue.popleft()
        for move in moves:
            neighbor = rubik.perm_apply(move, current_position)
            if neighbor in this_side_parents:
                continue
            this_side_parents[neighbor] = (current_position, move)
            this_side_queue.append(neighbor)
            added_positions.append(neighbor) 
    #check if meeting point found
    for pos in added_positions:
        if pos in other_side_parents:
            # Found a meeting point
            return pos
    return None
        
def reconstruct_path(meeting_point: rubik.Position,
                    forward_parents: ParentMap) -> List[rubik.Permutation]:
    # Reconstruct the path from start to meeting_point
    path: List[Permutation] = []
    current = meeting_point
    while True:
        parent, mv = forward_parents[current]
        if parent is None:
            break
        path.append(mv)  
        current = parent
    path.reverse()
    return path
