#
# Dominic Tucchio [dtucchio@uri.edu]
# Maya Geva [maya.geva@uri.edu]
# CSC 440 - Design and Analysis of Algorithms
# Assignment 2
#

import math
import sys
from typing import List
from typing import Tuple

EPSILON = sys.float_info.epsilon
Point = Tuple[int, int]

## Helper Functions
#
def y_intercept(p1: Point, p2: Point, x: int) -> float:
    """
    Given two points, p1 and p2, an x coordinate from a vertical line,
    compute and return the the y-intercept of the line segment p1->p2
    with the vertical line passing through x.
    """
    x1, y1 = p1
    x2, y2 = p2
    slope = (y2 - y1) / (x2 - x1)
    return y1 + (x - x1) * slope


def triangle_area(a: Point, b: Point, c: Point) -> float:
    """
    Given three points a,b,c,
    computes and returns the area defined by the triangle a,b,c.
    Note that this area will be negative if a,b,c represents a clockwise sequence,
    positive if it is counter-clockwise,
    and zero if the points are collinear.
    """
    ax, ay = a
    bx, by = b
    cx, cy = c
    return ((cx - bx) * (by - ay) - (bx - ax) * (cy - by)) / 2


def is_clockwise(a: Point, b: Point, c: Point) -> bool:
    """
    Given three points a,b,c,
    returns True if and only if a,b,c represents a clockwise sequence
    (subject to floating-point precision)
    """
    return triangle_area(a, b, c) < -EPSILON


def is_counter_clockwise(a: Point, b: Point, c: Point) -> bool:
    """
    Given three points a,b,c,
    returns True if and only if a,b,c represents a counter-clockwise sequence
    (subject to floating-point precision)
    """
    return triangle_area(a, b, c) > EPSILON


def collinear(a: Point, b: Point, c: Point) -> bool:
    """
    Given three points a,b,c,
    returns True if and only if a,b,c are collinear
    (subject to floating-point precision)
    """
    return abs(triangle_area(a, b, c)) <= EPSILON

def hull_collinear(hull):
    for i in range(2, len(hull)):
        if not collinear(hull[0], hull[1], hull[i]):
            return False
        
    return True

def sort_clockwise(points: List[Point]):
    """
    Sorts `points` by ascending clockwise angle from +x about the centroid,
    breaking ties first by ascending x value and then by ascending y value.

    The order of equal points is not modified

    Note: This function modifies its argument
    """
    # Trivial cases don't need sorting, and this dodges divide-by-zero errors
    if len(points) < 2:
        return

    # Compute the centroid
    centroid_x = sum(p[0] for p in points) / len(points)
    centroid_y = sum(p[1] for p in points) / len(points)

    # Sort by ascending clockwise angle from +x, breaking ties with ^x then ^y
    def sort_key(point: Point):
        angle = math.atan2(point[1] - centroid_y, point[0] - centroid_x)
        normalized_angle = (angle + math.tau) % math.tau
        return (normalized_angle, point[0], point[1])

    # Sort the points
    points.sort(key=sort_key)

# Convex Hull Algorithms
#
def base_case_hull(points: List[Point]) -> List[Point]:
    """ Base case of the recursive algorithm. Used when there are 6 or fewer points.
    """
    # Handle trivial cases
    if len(points) <= 2:
        return points 
    
    # INVARIANT: At the initialization of the outer loop, points is a sorted list of points by x-coordinate
    points = sorted(points, key=lambda p: (p[0], p[1]))
    hull = []

    # INVARIANT: The hull's points (if any) are part of the convex hull
        # Initialization: Hull is empty, so it contains only points that are part of the convex hull
        # Maintenance: If we find two points that are part of the convex hull, we add them to hull
        # Termination: We have checked all pairs of points, and added all points that are part of the convex hull to hull
    for i in range(len(points)):
        for j in range(len(points)):
            if i == j:
                continue

            pt_a = points[i]
            pt_b = points[j]

            right_side = left_side = False
            for k in range(len(points)):
                # INVARIANT: pt_a and pt_b are fixed points
                    # Initialization: pt_a and pt_b are fixed, and we have not yet checked any other points
                    # Maintenance: We check the position of pt_c relative to the line segment pt_a -> pt_b
                        # if pt_c is to the right of the line segment, we set right_side to True
                        # if pt_c is to the left of the line segment, we set left_side to True
                        # if pt_c is collinear with the line segment, we do nothing
                    # Termination: We have checked all points, and determined if there are points on both sides of the line segment pt_a -> pt_b
                
                if k == i or k == j:
                    continue

                pt_c = points[k]
                area = triangle_area(pt_a, pt_b, pt_c)

                if area > 0:
                    right_side = True
                elif area < 0:
                    left_side = True

            if not (right_side and left_side):
                if (pt_a not in hull): hull.append(pt_a)
                if (pt_b not in hull): hull.append(pt_b)

    sort_clockwise(hull)
    return hull
    
def compute_hull(points: List[Point]) -> List[Point]:
    """
    Given a list of points, computes the convex hull around those points
    and returns only the points that are on the hull in clockwise order.
    """

    # INVARIANT: If there are 6 or fewer points, we use the base case algorithm to compute the hull.
    # INVARIANT: If there are more than 6 points, we use the divide and conquer algorithm to compute the hull.
    if len(points) <= 6:
        return base_case_hull(points)

    # Sort points by the x-coordinate and split in half
    # INVARIANT: Every point in left_half is to the left of every point in right_half.
    sorted_points = sorted(points, key=lambda p:(p[0]))
    mid = len(sorted_points) // 2 
    left_half = sorted_points[:mid]
    right_half = sorted_points[mid:]

    # Recursively compute the hull on both halves
    # INVARIANT: At the end of each recursive call, left_hull and right_hull are valid convex hulls in clockwise order.
    left_hull = compute_hull(left_half)
    right_hull = compute_hull(right_half)

    # Merge the two hulls
    # INVARIANT: After merging, the returned list is a single valid convex hull in clockwise order.
    return merge_hulls(left_hull, right_hull)
 
def merge_hulls(left_hull: List[Point], right_hull: List[Point]) -> List[Point]:

    # INVARIANT: left_hull and right_hull
        # Initialization: left_hull and right_hull are passed in both valid hulls in clockwise order
        # Maintenance: we are not modifying left_hull or right_hull, we are only reading from them
        # Termination: we finish looking for the upper and lower tangents, and construct the merged hull,
        # but left_hull and right_hull remain unchanged
        
    # Check if all points are collinear
    if hull_collinear(left_hull) or hull_collinear(right_hull):
        hull = sorted(left_hull + right_hull, key=lambda p: (p[0], p[1]))
        return [hull[0], hull[-1]]

    # Find the upper tangent of each hull using the rightmost point of the left hull and the leftmost point of the right hull
    rightmost_left = max(range(len(left_hull)), key=lambda i: left_hull[i][0])
    leftmost_right = min(range(len(right_hull)), key=lambda i: right_hull[i][0])

    done = False
    while not done:
        done = True
        while is_counter_clockwise(right_hull[leftmost_right], left_hull[rightmost_left], left_hull[(rightmost_left + 1) % len(left_hull)]) \
            or collinear(right_hull[leftmost_right], left_hull[rightmost_left], left_hull[(rightmost_left + 1) % len(left_hull)]):
            rightmost_left = (rightmost_left + 1) % len(left_hull)
            done = False

        while is_clockwise(left_hull[rightmost_left], right_hull[leftmost_right], right_hull[(leftmost_right - 1) % len(right_hull)]) \
            or collinear(left_hull[rightmost_left], right_hull[leftmost_right], right_hull[(leftmost_right - 1) % len(right_hull)]):
            leftmost_right = (leftmost_right - 1) % len(right_hull)
            done = False

    # Assign upper tangent points
    upper_left, upper_right = rightmost_left, leftmost_right

    # Find the lower tangent of each hull using the rightmost point of the left hull and the leftmost point of the right hull
    rightmost_left = max(range(len(left_hull)), key=lambda i: left_hull[i][0])
    leftmost_right = min(range(len(right_hull)), key=lambda i: right_hull[i][0])

    done = False
    while not done:
        done = True
        while is_clockwise(right_hull[leftmost_right], left_hull[rightmost_left], left_hull[(rightmost_left - 1) % len(left_hull)]) \
            or collinear(right_hull[leftmost_right], left_hull[rightmost_left], left_hull[(rightmost_left - 1) % len(left_hull)]):
            rightmost_left = (rightmost_left - 1) % len(left_hull)
            done = False

        while is_counter_clockwise(left_hull[rightmost_left], right_hull[leftmost_right], right_hull[(leftmost_right + 1) % len(right_hull)]) \
            or collinear(left_hull[rightmost_left], right_hull[leftmost_right], right_hull[(leftmost_right - 1) % len(right_hull)]):
            leftmost_right = (leftmost_right + 1) % len(right_hull)
            done = False

    # Assign lower tangent points
    lower_left, lower_right = rightmost_left, leftmost_right

    hull = [] # Construct the merged hull
    
    i = upper_left # Loop left hull from upper_left to lower_left
    while True:
        hull.append(left_hull[i])
        if i == lower_left:
            break
        i = (i + 1) % len(left_hull)

    i = lower_right # Loop right hull from lower_right to upper_right
    while True:
        hull.append(right_hull[i])
        if i == upper_right:
            break
        i = (i + 1) % len(right_hull)
    
    return hull
