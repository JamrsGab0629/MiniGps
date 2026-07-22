# =====================================================================
# PATHFINDING ENGINE (BFS)
#
# NOTE: this is breadth-first search (fewest ROAD SEGMENTS), not
# Dijkstra/Yen's. Since segment lengths vary a lot on this map, BFS can
# pick a path that's lighter on turns but longer in actual meters.
# Kept as-is; flag if you'd like a true weighted-shortest-path swap.
# =====================================================================
import math
from collections import deque

from map_data import METERS_PER_PIXEL


def find_path_bfs(graph, start, target, blocked_edge=None):
    queue = deque([start])
    visited = {start}
    parent_map = {}

    while queue:
        current = queue.popleft()
        if current == target:
            path = []
            step = target
            while step:
                path.append(step)
                step = parent_map.get(step)
            return path[::-1]

        for neighbor in graph[current]["neighbors"]:
            if blocked_edge:
                u, v = blocked_edge
                if (current == u and neighbor == v) or (current == v and neighbor == u):
                    continue
            if neighbor not in visited:
                visited.add(neighbor)
                parent_map[neighbor] = current
                queue.append(neighbor)
    return None


def calculate_paths(graph, start, target):
    path1 = find_path_bfs(graph, start, target)
    if not path1:
        return None, None

    alternative_paths = []
    for i in range(len(path1) - 1):
        edge_to_block = (path1[i], path1[i + 1])
        alt_path = find_path_bfs(graph, start, target, blocked_edge=edge_to_block)
        if alt_path:
            alternative_paths.append(alt_path)

    path2 = None
    if alternative_paths:
        alternative_paths.sort(key=len)
        best_alt = alternative_paths[0]
        if len(best_alt) <= len(path1) + 6:
            path2 = best_alt

    return path1, path2


def calculate_path_distance_meters(graph, path):
    """
    Takes `graph` explicitly (instead of reaching for a module-level
    SUBDIVISION_MAP) so this module doesn't need to import geometry.py --
    avoids a circular import and keeps this file testable on its own.
    Math is identical to the original.
    """
    if not path or len(path) < 2:
        return 0.0
    total_pixels = 0.0
    for i in range(len(path) - 1):
        n1, n2 = path[i], path[i + 1]
        x1, y1 = graph[n1]["x"], graph[n1]["y"]
        x2, y2 = graph[n2]["x"], graph[n2]["y"]
        total_pixels += math.hypot(x2 - x1, y2 - y1)
    return total_pixels * METERS_PER_PIXEL
