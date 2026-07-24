from collections import deque
import heapq
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
            # Bypass blocked edge
            if blocked_edge and ((curr == blocked_edge[0] and neighbor == blocked_edge[1]) or 
                                 (curr == blocked_edge[1] and neighbor == blocked_edge[0])):
                continue

            # Bypass other houses
            if neighbor in house_names and neighbor != target:
                continue

            if neighbor not in visited and neighbor in graph:
                visited.add(neighbor)
                parent_map[neighbor] = curr
                queue.append(neighbor)
    return None


def find_path_dijkstra(graph, start, target, blocked_edge=None, house_names=None):
    """Shortest Path algorithm based on physical Euclidean distance (meters/pixels)."""
    if house_names is None:
        house_names = set()

    # Priority queue stores: (cumulative_distance, current_node, path_history)
    pq = [(0.0, start, [start])]
    visited = {}

    while pq:
        dist, curr, path = heapq.heappop(pq)

        if curr == target:
            return path

        if curr in visited and visited[curr] <= dist:
            continue
        visited[curr] = dist

        for neighbor in graph[curr].get("neighbors", []):
            # Bypass blocked edge
            if blocked_edge and ((curr == blocked_edge[0] and neighbor == blocked_edge[1]) or 
                                 (curr == blocked_edge[1] and neighbor == blocked_edge[0])):
                continue

            # Bypass other houses
            if neighbor in house_names and neighbor != target:
                continue

            if neighbor in graph:
                # Calculate actual segment distance weight
                x1, y1 = graph[curr]["x"], graph[curr]["y"]
                x2, y2 = graph[neighbor]["x"], graph[neighbor]["y"]
                edge_weight = math.hypot(x2 - x1, y2 - y1)

                heapq.heappush(pq, (dist + edge_weight, neighbor, path + [neighbor]))

    return None


def calculate_paths(graph, start, target, house_names=None, mode="dijkstra"):
    """
    Finds the primary shortest path and second-shortest path by physical distance.
    `mode` can be 'dijkstra' (recommended for exact distance) or 'bfs'.
    """
    search_algo = find_path_dijkstra if mode == "dijkstra" else find_path_bfs

    # 1. Find initial primary path
    p1 = search_algo(graph, start, target, house_names=house_names)
    if not p1:
        return None, None

    # 2. Collect alternative candidate paths using edge-blocking
    candidate_paths = [p1]
    for i in range(len(p1) - 1):
        alt = search_algo(
            graph, start, target, 
            blocked_edge=(p1[i], p1[i + 1]), 
            house_names=house_names
        )
        if alt and alt not in candidate_paths:
            candidate_paths.append(alt)

    # 3. Sort candidate paths strictly by PHYSICAL DISTANCE (meters)
    candidate_paths.sort(key=lambda path: calculate_path_distance(graph, path))

    # 4. Assign true shortest and true second-shortest
    primary_path = candidate_paths[0]
    second_path = candidate_paths[1] if len(candidate_paths) > 1 else None

    return primary_path, second_path


def calculate_path_distance(graph, path):
    """Calculates total Euclidean path distance scaled to meters."""
    if not path or len(path) < 2:
        return 0.0

    total_pixels = 0.0
    for i in range(len(path) - 1):
        n1, n2 = path[i], path[i + 1]
        x1, y1 = graph[n1]["x"], graph[n1]["y"]
        x2, y2 = graph[n2]["x"], graph[n2]["y"]
        total_pixels += math.hypot(x2 - x1, y2 - y1)

    return total_pixels * METERS_PER_PIXEL