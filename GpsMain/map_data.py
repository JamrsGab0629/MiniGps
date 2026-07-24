import math

# Maximum allowed snapping distance in pixels
MAX_ROAD_SNAP_DISTANCE = 120 


class MapGraph:
    """Manages raw junctions, houses, and the assembled graph network."""

    def __init__(self):
        self.junctions = {}
        self.houses = {}
        self.subdivision_map = {}

    def rebuild(self):
        """Rebuilds full graph connecting houses to their closest junction without mutating base data."""
        # Create a deep copy of junctions so neighbors list isn't mutated in self.junctions
        self.subdivision_map = {}
        for j_name, j_data in self.junctions.items():
            self.subdivision_map[j_name] = {
                "x": j_data["x"],
                "y": j_data["y"],
                "neighbors": list(j_data.get("neighbors", []))  # Fresh copy of neighbors!
            }

        # Snap houses to nearest junction (with maximum distance threshold)
        for h_name, h_data in self.houses.items():
            if not self.junctions:
                continue

            hx, hy = h_data["x"], h_data["y"]
            
            # Find closest junction
            nearest_j = min(
                self.junctions.keys(),
                key=lambda j: math.hypot(self.junctions[j]["x"] - hx, self.junctions[j]["y"] - hy)
            )

            # Calculate actual Euclidean distance to nearest junction
            dist = math.hypot(self.junctions[nearest_j]["x"] - hx, self.junctions[nearest_j]["y"] - hy)

            # -----------------------------------------------------------------
            # DISTANCE THRESHOLD CHECK
            # -----------------------------------------------------------------
            if dist <= MAX_ROAD_SNAP_DISTANCE:
                # Connect house to junction
                self.subdivision_map[h_name] = {"x": hx, "y": hy, "neighbors": [nearest_j]}

                # Connect junction back to house (avoid duplicates)
                if h_name not in self.subdivision_map[nearest_j]["neighbors"]:
                    self.subdivision_map[nearest_j]["neighbors"].append(h_name)
            else:
                # House is isolated (too far from any road)
                self.subdivision_map[h_name] = {"x": hx, "y": hy, "neighbors": []}
                print(f"Warning: '{h_name}' is {dist:.1f}px away from '{nearest_j}' (exceeds limit of {MAX_ROAD_SNAP_DISTANCE}px). Connection omitted.")

    def find_node_near_click(self, x, y, max_dist=15):
        """Finds any junction or house within threshold distance of a click."""
        for node, data in self.junctions.items():
            if math.hypot(data["x"] - x, data["y"] - y) <= max_dist:
                return node, "junction"
        for name, data in self.houses.items():
            if math.hypot(data["x"] - x, data["y"] - y) <= max_dist:
                return name, "house"
        return None, None