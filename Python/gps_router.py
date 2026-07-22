"""
GPS Router — loads the road graph JSON exported by road_drawer_tool.py
and finds the shortest path between two points on the map.

Usage:
    python gps_router.py
"""

import json
import math
import heapq


def load_graph(json_path):
    with open(json_path) as f:
        return json.load(f)


def nearest_node(graph, x, y):
    """Find the junction closest to a given (x, y) image coordinate."""
    best_name, best_dist = None, float("inf")
    for name, data in graph.items():
        d = math.hypot(data["x"] - x, data["y"] - y)
        if d < best_dist:
            best_name, best_dist = name, d
    return best_name


def shortest_path(graph, start_name, end_name):
    """
    Dijkstra's algorithm. Edge weight = straight-line pixel distance
    between connected junctions. Returns (path_as_list_of_names, total_distance).
    """
    if start_name not in graph or end_name not in graph:
        return None, float("inf")

    distances = {name: float("inf") for name in graph}
    previous = {name: None for name in graph}
    distances[start_name] = 0
    queue = [(0, start_name)]
    visited = set()

    while queue:
        current_dist, current = heapq.heappop(queue)
        if current in visited:
            continue
        visited.add(current)

        if current == end_name:
            break

        cx, cy = graph[current]["x"], graph[current]["y"]
        for neighbor in graph[current]["neighbors"]:
            if neighbor not in graph:
                continue
            nx, ny = graph[neighbor]["x"], graph[neighbor]["y"]
            weight = math.hypot(nx - cx, ny - cy)
            new_dist = current_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                previous[neighbor] = current
                heapq.heappush(queue, (new_dist, neighbor))

    if distances[end_name] == float("inf"):
        return None, float("inf")  # no route exists between these two points

    # Walk back from end to start using `previous`
    path = []
    node = end_name
    while node is not None:
        path.append(node)
        node = previous[node]
    path.reverse()

    return path, distances[end_name]


def path_to_coordinates(graph, path):
    """Turn a list of junction names into a list of (x, y) points to draw/follow."""
    return [(graph[name]["x"], graph[name]["y"]) for name in path]


if __name__ == "__main__":
    # --- Example usage ---
    GRAPH_FILE = "road_network.json"  # change to your saved file's name

    graph = load_graph(GRAPH_FILE)

    # Example: "I am at pixel (120, 340), I want to go to pixel (900, 610)"
    start_x, start_y = 120, 340
    end_x, end_y = 900, 610

    start_node = nearest_node(graph, start_x, start_y)
    end_node = nearest_node(graph, end_x, end_y)

    print(f"Nearest junction to start: {start_node}")
    print(f"Nearest junction to destination: {end_node}")

    path, distance = shortest_path(graph, start_node, end_node)

    if path is None:
        print("No route found between these two points.")
    else:
        print(f"\nRoute ({len(path)} junctions, {distance:.1f} px total):")
        print(" -> ".join(path))

        coords = path_to_coordinates(graph, path)
        print("\nCoordinates to follow:")
        for x, y in coords:
            print(f"  ({x:.0f}, {y:.0f})")
