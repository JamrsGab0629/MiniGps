from collections import deque
import math

METERS_PER_PIXEL = 0.65  # Scale: 1 pixel ≈ 0.65 meters


def find_path_bfs(graph, start, target, blocked_edge=None, house_names=None):
    """Standard Breadth-First Search bypassing other houses."""
    if house_names is None:
        house_names = set()

    queue = deque([start])
    visited = {start}
    parent_map = {}

    while queue:
        curr = queue.popleft()
        if curr == target:
            path, step = [], target
            while step:
                path.append(step)
                step = parent_map.get(step)
            return path[::-1]

        for neighbor in graph[curr].get("neighbors", []):
            if blocked_edge and ((curr == blocked_edge[0] and neighbor == blocked_edge[1]) or 
                                 (curr == blocked_edge[1] and neighbor == blocked_edge[0])):
                continue

            if neighbor in house_names and neighbor != target:
                continue

            if neighbor not in visited and neighbor in graph:
                visited.add(neighbor)
                parent_map[neighbor] = curr
                queue.append(neighbor)
    return None


def calculate_paths(graph, start, target, house_names=None):
    """Finds primary and alternative paths using BFS edge-blocking."""
    path1 = find_path_bfs(graph, start, target, house_names=house_names)
    if not path1:
        return None, None

    alt_paths = []
    for i in range(len(path1) - 1):
        alt = find_path_bfs(
            graph, start, target, 
            blocked_edge=(path1[i], path1[i + 1]), 
            house_names=house_names
        )
        if alt:
            alt_paths.append(alt)

    path2 = None
    if alt_paths:
        alt_paths.sort(key=len)
        if len(alt_paths[0]) <= len(path1) + 6:
            path2 = alt_paths[0]

    return path1, path2


def calculate_path_distance(graph, path):
    """Calculates total Euclidean path distance scaled to meters."""
    total_pixels = 0.0
    for i in range(len(path) - 1):
        n1, n2 = path[i], path[i + 1]
        x1, y1 = graph[n1]["x"], graph[n1]["y"]
        x2, y2 = graph[n2]["x"], graph[n2]["y"]
        total_pixels += math.hypot(x2 - x1, y2 - y1)
    return total_pixels * METERS_PER_PIXEL