import math


class MapGraph:
    """Manages raw junctions, houses, and the assembled graph network."""

    def __init__(self):
        self.junctions = {}
        self.houses = {}
        self.subdivision_map = {}

    def rebuild(self):
        """Rebuilds full graph connecting houses to their closest junction."""
        self.subdivision_map = {node: dict(data) for node, data in self.junctions.items()}

        for h_name, h_data in self.houses.items():
            if not self.junctions:
                continue
            hx, hy = h_data["x"], h_data["y"]
            nearest_j = min(
                self.junctions.keys(),
                key=lambda j: math.hypot(self.junctions[j]["x"] - hx, self.junctions[j]["y"] - hy)
            )

            self.subdivision_map[h_name] = {"x": hx, "y": hy, "neighbors": [nearest_j]}
            self.subdivision_map[nearest_j]["neighbors"].append(h_name)

    def find_node_near_click(self, x, y, max_dist=15):
        """Finds any junction or house within threshold distance of a click."""
        for node, data in self.junctions.items():
            if math.hypot(data["x"] - x, data["y"] - y) <= max_dist:
                return node, "junction"
        for name, data in self.houses.items():
            if math.hypot(data["x"] - x, data["y"] - y) <= max_dist:
                return name, "house"
        return None, None