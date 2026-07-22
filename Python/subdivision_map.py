import tkinter as tk
from collections import deque
import math

# =====================================================================
# 1. EARTH AND HOMES (BALAGTAS) MAP GEOMETRY & CONNECTIONS
# =====================================================================
JUNCTION_GRAPH = {
    # === ENTRANCE GATE (Located at Balagtas Text on Map) ===
    "Entrance_Gate_J1": {"x": 131, "y": 86, "neighbors": ["Junction_2"]},
    "Junction_2": {"x": 191, "y": 188, "neighbors": ["Entrance_Gate_J1", "Junction_3"]},
    
    # West Grid Row 1 (Top Intersections near Gate)
    "Junction_3": {"x": 144, "y": 205, "neighbors": ["Junction_2", "Junction_4", "Junction_9"]},
    "Junction_4": {"x": 99,  "y": 232, "neighbors": ["Junction_3", "Junction_5", "Junction_8"]},
    "Junction_5": {"x": 60,  "y": 265, "neighbors": ["Junction_4", "Junction_6"]},
    
    # West Grid Row 2 (Middle Crossroad Row)
    "Junction_6": {"x": 112, "y": 451, "neighbors": ["Junction_5", "Junction_7", "Junction_10"]},
    "Junction_7": {"x": 182, "y": 451, "neighbors": ["Junction_6", "Junction_8", "Junction_11"]},
    "Junction_8": {"x": 230, "y": 430, "neighbors": ["Junction_7", "Junction_4", "Junction_9", "Junction_12"]},
    "Junction_9": {"x": 284, "y": 392, "neighbors": ["Junction_8", "Junction_3", "Junction_13"]},
    
    # West Grid Row 3 (Lower Crossroad Row)
    "Junction_10": {"x": 160, "y": 570, "neighbors": ["Junction_6", "Junction_11"]},
    "Junction_11": {"x": 218, "y": 562, "neighbors": ["Junction_10", "Junction_7", "Junction_12"]},
    "Junction_12": {"x": 252, "y": 562, "neighbors": ["Junction_11", "Junction_8", "Junction_13", "Junction_15"]},
    "Junction_13": {"x": 334, "y": 526, "neighbors": ["Junction_12", "Junction_9", "Junction_14"]},
    
    # Mid-subdivision Transition Junctions
    "Junction_14": {"x": 363, "y": 560, "neighbors": ["Junction_13", "Junction_17"]},
    "Junction_15": {"x": 263, "y": 569, "neighbors": ["Junction_12", "Junction_16"]},
    
    # === WESTERN ROUNDABOUT / BEND ===
    "Junction_16": {"x": 349, "y": 620, "neighbors": ["Junction_15", "Junction_18"]},
    "Junction_17": {"x": 357, "y": 568, "neighbors": ["Junction_14", "Junction_18", "Junction_19"]},
    "Junction_18": {"x": 352, "y": 607, "neighbors": ["Junction_16", "Junction_17", "Junction_20"]},
    
    # === MAIN CENTRAL AVENUE (Passing Earth & Homes / Coco House) ===
    "Junction_19": {"x": 419, "y": 560, "neighbors": ["Junction_17", "Junction_21"]},
    "Junction_21": {"x": 422, "y": 574, "neighbors": ["Junction_19", "Junction_25"]},
    "Junction_25": {"x": 649, "y": 474, "neighbors": ["Junction_21", "Junction_23"]},
    "Junction_23": {"x": 642, "y": 466, "neighbors": ["Junction_25", "Junction_31"]},
    
    "Junction_20": {"x": 416, "y": 628, "neighbors": ["Junction_18", "Junction_22"]},
    "Junction_22": {"x": 424, "y": 618, "neighbors": ["Junction_20", "Junction_26"]},
    "Junction_26": {"x": 725, "y": 539, "neighbors": ["Junction_22", "Junction_24"]},
    "Junction_24": {"x": 728, "y": 553, "neighbors": ["Junction_26", "Junction_28"]},
    
    # === EASTERN SECTION & EAST LOOP (Dolindo / Tats San Juan / Block 1) ===
    "Junction_28": {"x": 816, "y": 544, "neighbors": ["Junction_24", "Junction_30", "Junction_35"]},
    "Junction_30": {"x": 824, "y": 531, "neighbors": ["Junction_28", "Junction_29"]},
    "Junction_29": {"x": 838, "y": 484, "neighbors": ["Junction_30", "Junction_27"]},
    "Junction_27": {"x": 840, "y": 476, "neighbors": ["Junction_29", "Junction_31"]},
    
    "Junction_31": {"x": 903, "y": 500, "neighbors": ["Junction_23", "Junction_27", "Junction_32", "Junction_35"]},
    "Junction_32": {"x": 1063, "y": 431, "neighbors": ["Junction_31"]},
    "Junction_33": {"x": 946, "y": 650, "neighbors": ["Junction_35"]},
    
    "Junction_35": {"x": 912, "y": 511, "neighbors": ["Junction_31", "Junction_28", "Junction_33", "Junction_34", "Junction_36"]},
    "Junction_34": {"x": 1026, "y": 554, "neighbors": ["Junction_35", "Junction_36", "Junction_41"]},
    "Junction_36": {"x": 1071, "y": 563, "neighbors": ["Junction_35", "Junction_34", "Junction_37"]},
    
    "Junction_37": {"x": 1173, "y": 554, "neighbors": ["Junction_36", "Junction_38"]},
    "Junction_38": {"x": 1167, "y": 695, "neighbors": ["Junction_37", "Junction_39"]},
    "Junction_39": {"x": 1094, "y": 701, "neighbors": ["Junction_38", "Junction_40"]},
    "Junction_40": {"x": 1096, "y": 685, "neighbors": ["Junction_39", "Junction_41"]},
    "Junction_41": {"x": 1025, "y": 689, "neighbors": ["Junction_40", "Junction_34"]}
}

HOUSES = {
    "House 1": {"x": 184, "y": 169}, "House 2": {"x": 212, "y": 240},
    "House 3": {"x": 159, "y": 252}, "House 4": {"x": 202, "y": 356},
    "House 5": {"x": 142, "y": 343}, "House 6": {"x": 169, "y": 418},
    "House 7": {"x": 68, "y": 313},  "House 8": {"x": 69, "y": 335},
    "House 9": {"x": 322, "y": 479}, "House 10": {"x": 322, "y": 489},
    "House 11": {"x": 167, "y": 572}, "House 12": {"x": 287, "y": 614},
    "House 13": {"x": 122, "y": 506}, "House 14": {"x": 151, "y": 546},
    "House 15": {"x": 216, "y": 547}, "House 16": {"x": 198, "y": 515},
    "House 17": {"x": 531, "y": 521}, "House 18": {"x": 506, "y": 538},
    "House 19": {"x": 455, "y": 628}, "House 20": {"x": 494, "y": 623},
    "House 21": {"x": 578, "y": 596}, "House 22": {"x": 621, "y": 579},
    "House 23": {"x": 668, "y": 562}, "House 24": {"x": 714, "y": 552},
    "House 25": {"x": 677, "y": 489}, "House 26": {"x": 689, "y": 445},
    "House 27": {"x": 751, "y": 454}, "House 28": {"x": 800, "y": 452},
    "House 29": {"x": 719, "y": 454}, "House 30": {"x": 870, "y": 478},
    "House 31": {"x": 822, "y": 540}, "House 32": {"x": 831, "y": 489},
    "House 33": {"x": 900, "y": 498}, "House 34": {"x": 833, "y": 606},
    "House 35": {"x": 986, "y": 574}, "House 36": {"x": 959, "y": 640},
    "House 37": {"x": 1098, "y": 615}, "House 38": {"x": 1070, "y": 693},
    "House 39": {"x": 1062, "y": 424}
}

# How far (in pixels) a house is allowed to sit from its connecting road
# before it gets pulled in to hug the street. Houses already closer than
# this are left exactly where they are.
HOUSE_ROAD_HUG_DISTANCE = 16


def assemble_full_map():
    """Combines junction network and attaches each house to its nearest
    street driveway, pulling any house that floats far from the road
    inward so it visually sits right beside its street."""
    full_map = {node: dict(data) for node, data in JUNCTION_GRAPH.items()}
    junction_keys = list(JUNCTION_GRAPH.keys())

    for house_name, h_data in HOUSES.items():
        hx, hy = h_data["x"], h_data["y"]
        closest_j = min(
            junction_keys,
            key=lambda j: math.hypot(JUNCTION_GRAPH[j]["x"] - hx, JUNCTION_GRAPH[j]["y"] - hy)
        )
        jx, jy = JUNCTION_GRAPH[closest_j]["x"], JUNCTION_GRAPH[closest_j]["y"]
        dist_to_road = math.hypot(jx - hx, jy - hy)

        if dist_to_road > HOUSE_ROAD_HUG_DISTANCE:
            # Pull the house in along the same direction, so it hugs the
            # road instead of floating far away from it.
            ratio = HOUSE_ROAD_HUG_DISTANCE / dist_to_road
            draw_x = jx + (hx - jx) * ratio
            draw_y = jy + (hy - jy) * ratio
        else:
            draw_x, draw_y = hx, hy

        full_map[house_name] = {"x": draw_x, "y": draw_y, "neighbors": [closest_j]}
        full_map[closest_j]["neighbors"].append(house_name)

    return full_map

SUBDIVISION_MAP = assemble_full_map()

# =====================================================================
# 2. PATHFINDING ENGINE (BFS)
# =====================================================================
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

# =====================================================================
# 3. UI PRESENTATION ENGINE (Tkinter)
# =====================================================================
class SubdivisionMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Earth and Homes Subdivision (Balagtas) - Navigation System")
        self.root.configure(bg="#0f141c")

        sorted_keys = sorted(SUBDIVISION_MAP.keys())

        control_frame = tk.Frame(root, padx=15, pady=12, bg="#161c26")
        control_frame.pack(side=tk.TOP, fill=tk.X)

        lbl_style = {"bg": "#161c26", "fg": "#ffffff", "font": ("Arial", 10, "bold")}

        tk.Label(control_frame, text="Start Point:", **lbl_style).pack(side=tk.LEFT, padx=5)
        self.start_var = tk.StringVar(value="Entrance_Gate_J1")
        self.start_menu = tk.OptionMenu(control_frame, self.start_var, *sorted_keys)
        self.start_menu.config(bg="#242e3e", fg="white", highlightthickness=0, borderwidth=0, font=("Arial", 9))
        self.start_menu.pack(side=tk.LEFT, padx=5)

        tk.Label(control_frame, text="Destination:", **lbl_style).pack(side=tk.LEFT, padx=15)
        self.target_var = tk.StringVar(value="House 38")
        self.target_menu = tk.OptionMenu(control_frame, self.target_var, *sorted_keys)
        self.target_menu.config(bg="#242e3e", fg="white", highlightthickness=0, borderwidth=0, font=("Arial", 9))
        self.target_menu.pack(side=tk.LEFT, padx=5)

        btn_find = tk.Button(
            control_frame, text="🎯 Find Route from Gate", command=self.update_map,
            bg="#00b4d8", fg="white", font=("Arial", 10, "bold"), padx=12, relief=tk.FLAT, cursor="hand2"
        )
        btn_find.pack(side=tk.LEFT, padx=20)

        self.lbl_status = tk.Label(control_frame, text="Ready.", bg="#161c26", fg="#00b4d8", font=("Arial", 10))
        self.lbl_status.pack(side=tk.LEFT, padx=10)

        self.canvas = tk.Canvas(root, width=1220, height=750, bg="#0f141c", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.draw_base_graph()

    def draw_base_graph(self):
        self.canvas.delete("all")
        drawn_edges = set()

        # 1. Draw Road Lanes (junctions are used here only as invisible
        #    geometry to route the road lines and house driveways through)
        for node, data in SUBDIVISION_MAP.items():
            for neighbor in data["neighbors"]:
                edge_id = tuple(sorted((node, neighbor)))
                if edge_id not in drawn_edges and neighbor in SUBDIVISION_MAP:
                    x1, y1 = data["x"], data["y"]
                    x2, y2 = SUBDIVISION_MAP[neighbor]["x"], SUBDIVISION_MAP[neighbor]["y"]

                    is_house_driveway = "House" in node or "House" in neighbor
                    line_color = "#2a374a" if is_house_driveway else "#1c2536"
                    lane_color = "#3a4b6e" if not is_house_driveway else "#2e3d59"

                    self.canvas.create_line(x1, y1, x2, y2, fill=line_color, width=8, capstyle=tk.ROUND)
                    self.canvas.create_line(x1, y1, x2, y2, fill=lane_color, width=3, capstyle=tk.ROUND)
                    drawn_edges.add(edge_id)

        # 2. Draw only the Entrance Gate and the Houses.
        #    Junction_* nodes are intentionally NOT drawn - they exist purely
        #    as invisible road geometry for pathfinding, not as visible markers.
        for node, data in SUBDIVISION_MAP.items():
            if "Junction_" in node:
                continue  # keep junctions invisible - they're road scaffolding only

            x, y = data["x"], data["y"]

            if "Entrance_Gate" in node:
                color = "#2ec4b6"  # Bright Teal for Main Gate
                r = 7
                lbl = "GATE (Balagtas Entrance)"
            elif "House" in node:
                color = "#ffb703"  # Gold for Houses
                r = 4
                lbl = node.replace("House ", "H")
            else:
                continue

            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="#0f141c", width=1)
            self.canvas.create_text(x, y - 11, text=lbl, fill=color, font=("Arial", 7, "bold"))

    def draw_highlighted_path(self, path, color, offset=0):
        for i in range(len(path) - 1):
            n1, n2 = path[i], path[i + 1]
            x1, y1 = SUBDIVISION_MAP[n1]["x"] + offset, SUBDIVISION_MAP[n1]["y"] + offset
            x2, y2 = SUBDIVISION_MAP[n2]["x"] + offset, SUBDIVISION_MAP[n2]["y"] + offset
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=5, capstyle=tk.ROUND)

    def update_map(self):
        start = self.start_var.get()
        target = self.target_var.get()

        self.draw_base_graph()

        if start == target:
            self.lbl_status.config(text="Start and Destination match!", fg="#ffb703")
            return

        path1, path2 = calculate_paths(SUBDIVISION_MAP, start, target)

        if not path1:
            self.lbl_status.config(text="No path connections found.", fg="#ff4d6d")
            return

        self.draw_highlighted_path(path1, "#00f5d4")  # Primary route (Cyan)

        if path2:
            self.draw_highlighted_path(path2, "#ffb703", offset=3)  # Alt route (Gold)
            self.lbl_status.config(text=f"Primary (Cyan: {len(path1)-1} stops) & Alt (Gold) mapped from Gate.", fg="#00f5d4")
        else:
            self.lbl_status.config(text=f"Optimal route mapped ({len(path1)-1} stops from Gate).", fg="#90e0ef")

if __name__ == "__main__":
    root = tk.Tk()
    app = SubdivisionMapApp(root)
    root.mainloop()
