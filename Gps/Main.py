import tkinter as tk
from collections import deque
import math

# =====================================================================
# 1. MAP GEOMETRY & ROAD NETWORK (Earth and Homes Subdivision)
# =====================================================================
JUNCTION_GRAPH = {
    # === ENTRANCE GATE ===
    "Entrance_Gate_J1": {"x": 131, "y": 86, "neighbors": ["Junction_2"]},
    "Junction_2": {"x": 191, "y": 188, "neighbors": ["Entrance_Gate_J1", "Junction_3"]},
    
    # West Grid Row 1
    "Junction_3": {"x": 144, "y": 205, "neighbors": ["Junction_2", "Junction_4", "Junction_9"]},
    "Junction_4": {"x": 99,  "y": 232, "neighbors": ["Junction_3", "Junction_5", "Junction_8"]},
    "Junction_5": {"x": 60,  "y": 265, "neighbors": ["Junction_4", "Junction_6"]},
    
    # West Grid Row 2
    "Junction_6": {"x": 112, "y": 451, "neighbors": ["Junction_5", "Junction_7", "Junction_10"]},
    "Junction_7": {"x": 182, "y": 451, "neighbors": ["Junction_6", "Junction_8", "Junction_11"]},
    "Junction_8": {"x": 230, "y": 430, "neighbors": ["Junction_7", "Junction_4", "Junction_9", "Junction_12"]},
    "Junction_9": {"x": 284, "y": 392, "neighbors": ["Junction_8", "Junction_3", "Junction_13"]},
    
    # West Grid Row 3
    "Junction_10": {"x": 160, "y": 570, "neighbors": ["Junction_6", "Junction_11"]},
    "Junction_11": {"x": 218, "y": 562, "neighbors": ["Junction_10", "Junction_7", "Junction_12"]},
    "Junction_12": {"x": 252, "y": 562, "neighbors": ["Junction_11", "Junction_8", "Junction_13", "Junction_15"]},
    "Junction_13": {"x": 334, "y": 526, "neighbors": ["Junction_12", "Junction_9", "Junction_14"]},
    
    # Mid-subdivision Transition Junctions
    "Junction_14": {"x": 363, "y": 560, "neighbors": ["Junction_13", "Junction_17"]},
    "Junction_15": {"x": 263, "y": 569, "neighbors": ["Junction_12", "Junction_16"]},
    
    # Western Bends & Central Spine
    "Junction_16": {"x": 349, "y": 620, "neighbors": ["Junction_15", "Junction_18"]},
    "Junction_17": {"x": 357, "y": 568, "neighbors": ["Junction_14", "Junction_18", "Junction_19"]},
    "Junction_18": {"x": 352, "y": 607, "neighbors": ["Junction_16", "Junction_17", "Junction_20"]},
    
    # Central Main Avenue
    "Junction_19": {"x": 419, "y": 560, "neighbors": ["Junction_17", "Junction_21"]},
    "Junction_21": {"x": 422, "y": 574, "neighbors": ["Junction_19", "Junction_25"]},
    "Junction_25": {"x": 649, "y": 474, "neighbors": ["Junction_21", "Junction_23"]},
    "Junction_23": {"x": 642, "y": 466, "neighbors": ["Junction_25", "Junction_31"]},
    
    "Junction_20": {"x": 416, "y": 628, "neighbors": ["Junction_18", "Junction_22"]},
    "Junction_22": {"x": 424, "y": 618, "neighbors": ["Junction_20", "Junction_26"]},
    "Junction_26": {"x": 725, "y": 539, "neighbors": ["Junction_22", "Junction_24"]},
    "Junction_24": {"x": 728, "y": 553, "neighbors": ["Junction_26", "Junction_28"]},
    
    # === CURVED EASTERN SECTION ===
    "Junction_28": {"x": 816, "y": 544, "neighbors": ["Junction_24", "Junction_30", "Junction_35"]},
    "Junction_30": {"x": 824, "y": 531, "neighbors": ["Junction_28", "Junction_29"]},
    "Junction_29": {"x": 838, "y": 484, "neighbors": ["Junction_30", "Junction_27"]},
    "Junction_27": {"x": 840, "y": 476, "neighbors": ["Junction_29", "Junction_31"]},
    
    "Junction_31": {"x": 900, "y": 480, "neighbors": ["Junction_23", "Junction_27", "Curve_31_32_1", "Junction_35"]},
    
    # Top Curved Cul-de-sac Loop
    "Curve_31_32_1": {"x": 950, "y": 472, "neighbors": ["Junction_31", "Curve_31_32_2"]},
    "Curve_31_32_2": {"x": 1000, "y": 475, "neighbors": ["Curve_31_32_1", "Junction_32"]},
    "Junction_32":    {"x": 1050, "y": 490, "neighbors": ["Curve_31_32_2"]},
    
    # Mid Vertical Connector
    "Junction_35": {"x": 900, "y": 550, "neighbors": ["Junction_31", "Junction_28", "Curve_35_34_1", "Curve_35_37_1"]},
    
    # Center Curved Connector
    "Curve_35_34_1": {"x": 965, "y": 542, "neighbors": ["Junction_35", "Curve_35_34_2"]},
    "Curve_35_34_2": {"x": 1015, "y": 548, "neighbors": ["Curve_35_34_1", "Junction_34"]},
    "Junction_34":    {"x": 1060, "y": 565, "neighbors": ["Curve_35_34_2", "Curve_34_36_1"]},
    
    # Right Curved Bend
    "Curve_34_36_1": {"x": 1070, "y": 615, "neighbors": ["Junction_34", "Junction_36"]},
    "Junction_36":    {"x": 1045, "y": 665, "neighbors": ["Curve_34_36_1", "Curve_36_37_1"]},
    
    # Bottom Curved Loop
    "Curve_36_37_1": {"x": 975, "y": 675, "neighbors": ["Junction_36", "Junction_37"]},
    "Junction_37":    {"x": 905, "y": 655, "neighbors": ["Curve_36_37_1", "Curve_35_37_1"]},
    "Curve_35_37_1": {"x": 895, "y": 600, "neighbors": ["Junction_37", "Junction_35"]}
}

# Explicitly positioned purple landmarks to prevent label collision
CUSTOM_PURPLE_LANDMARKS = {
    "Coco House": {"x": 515, "y": 515, "align": "above", "text_offset": (0, -10)},
    "Claros Residence": {"x": 590, "y": 470, "align": "above", "text_offset": (-20, -10)},
    "Tats San Juan": {"x": 670, "y": 450, "align": "below", "text_offset": (20, 10)},
    "Dolindo Residence": {"x": 480, "y": 620, "align": "below", "text_offset": (0, 10)},
    "Block 1 Lot A45": {"x": 1030, "y": 480, "align": "above", "text_offset": (0, -10)}
}

HOUSES = {
    "My House": {"x": 210, "y": 180},
    "Guard House": {"x": 230, "y": 180},
    "Gazebo": {"x": 240, "y": 580},
    "Community Center": {"x": 370, "y": 530},

   
    "House 4": {"x": 210, "y": 410},
   
    "House 6": {"x": 90,  "y": 450},
    "House 7": {"x": 80,  "y": 220},
    "House 8": {"x": 210, "y": 450},
    "House 9": {"x": 300, "y": 380},
    "House 10": {"x": 250, "y": 410},
  
    "House 13": {"x": 100, "y": 500},
    "House 14": {"x": 170, "y": 430},
    "House 15": {"x": 200, "y": 580},
    
    "House 18": {"x": 330, "y": 640},
    "House 19": {"x": 330, "y": 600},
    "House 20": {"x": 430, "y": 650},
    "House 21": {"x": 440, "y": 600},
    "House 22": {"x": 630, "y": 520},
    "House 23": {"x": 660, "y": 500},
    "House 24": {"x": 740, "y": 530},
   
    "House 26": {"x": 800, "y": 520},
    "House 27": {"x": 820, "y": 460},
    "House 28": {"x": 860, "y": 460},
    
    "House 30": {"x": 920, "y": 460},
   
    "House 34": {"x": 1030, "y": 540},
    "House 35": {"x": 1080, "y": 580},
    "House 36": {"x": 1060, "y": 680},
    "House 37": {"x": 920, "y": 670},
    "House 38": {"x": 980, "y": 690},
    "House 39": {"x": 880, "y": 620}
}

METERS_PER_PIXEL = 0.65 

def point_to_segment_projection(px, py, ax, ay, bx, by):
    abx = bx - ax
    aby = by - ay
    ab_len_sq = abx**2 + aby**2
    if ab_len_sq == 0:
        return ax, ay, 0, 0
    t = max(0, min(1, ((px - ax) * abx + (py - ay) * aby) / ab_len_sq))
    proj_x = ax + t * abx
    proj_y = ay + t * aby
    return proj_x, proj_y, abx, aby

def snap_houses_to_road_edges(houses_dict, junctions_dict, offset_dist=10):
    edges = set()
    for u, u_data in junctions_dict.items():
        for v in u_data["neighbors"]:
            if v in junctions_dict:
                edge = tuple(sorted((u, v)))
                edges.add(edge)

    snapped = {}
    for name, h_data in houses_dict.items():
        hx, hy = h_data["x"], h_data["y"]
        
        best_dist = float("inf")
        best_snapped_pos = (hx, hy)
        best_junction = None

        for u, v in edges:
            ax, ay = junctions_dict[u]["x"], junctions_dict[u]["y"]
            bx, by = junctions_dict[v]["x"], junctions_dict[v]["y"]

            proj_x, proj_y, dx, dy = point_to_segment_projection(hx, hy, ax, ay, bx, by)
            dist = math.hypot(hx - proj_x, hy - proj_y)

            if dist < best_dist:
                best_dist = dist
                
                norm_len = math.hypot(dx, dy)
                if norm_len > 0:
                    nx, ny = -dy / norm_len, dx / norm_len
                    dot = (hx - proj_x) * nx + (hy - proj_y) * ny
                    if dot < 0:
                        nx, ny = -nx, -ny
                    offset_x = proj_x + nx * offset_dist
                    offset_y = proj_y + ny * offset_dist
                else:
                    offset_x, offset_y = proj_x, proj_y

                best_snapped_pos = (int(offset_x), int(offset_y))
                dist_u = math.hypot(proj_x - ax, proj_y - ay)
                dist_v = math.hypot(proj_x - bx, proj_y - by)
                best_junction = u if dist_u < dist_v else v

        snapped[name] = {
            "x": best_snapped_pos[0],
            "y": best_snapped_pos[1],
            "junction": best_junction
        }
    return snapped

def assemble_full_map():
    snapped_houses = snap_houses_to_road_edges(HOUSES, JUNCTION_GRAPH, offset_dist=12)
    snapped_purple = snap_houses_to_road_edges(CUSTOM_PURPLE_LANDMARKS, JUNCTION_GRAPH, offset_dist=8)

    full_map = {node: dict(data) for node, data in JUNCTION_GRAPH.items()}

    for house_name, h_data in snapped_houses.items():
        hx, hy = h_data["x"], h_data["y"]
        target_j = h_data["junction"]
        full_map[house_name] = {"x": hx, "y": hy, "neighbors": [target_j]}
        full_map[target_j]["neighbors"].append(house_name)

    for p_name, p_data in snapped_purple.items():
        px, py = p_data["x"], p_data["y"]
        target_j = p_data["junction"]
        full_map[p_name] = {"x": px, "y": py, "neighbors": [target_j]}
        full_map[target_j]["neighbors"].append(p_name)

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

def calculate_path_distance_meters(path):
    if not path or len(path) < 2:
        return 0.0
    total_pixels = 0.0
    for i in range(len(path) - 1):
        n1, n2 = path[i], path[i + 1]
        x1, y1 = SUBDIVISION_MAP[n1]["x"], SUBDIVISION_MAP[n1]["y"]
        x2, y2 = SUBDIVISION_MAP[n2]["x"], SUBDIVISION_MAP[n2]["y"]
        total_pixels += math.hypot(x2 - x1, y2 - y1)
    return total_pixels * METERS_PER_PIXEL

# =====================================================================
# 3. UI PRESENTATION ENGINE (Tkinter)
# =====================================================================
class SubdivisionMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Earth and Homes Subdivision (Balagtas) - Navigation System")
        self.root.configure(bg="#0f141c")

        selectable_nodes = [
            node for node in SUBDIVISION_MAP.keys() 
            if "Junction" not in node and "Curve" not in node
        ]
        selectable_nodes.sort()

        control_frame = tk.Frame(root, padx=15, pady=12, bg="#161c26")
        control_frame.pack(side=tk.TOP, fill=tk.X)

        lbl_style = {"bg": "#161c26", "fg": "#ffffff", "font": ("Arial", 10, "bold")}

        tk.Label(control_frame, text="Start Point:", **lbl_style).pack(side=tk.LEFT, padx=5)
        self.start_var = tk.StringVar(value="My House")
        self.start_menu = tk.OptionMenu(control_frame, self.start_var, *selectable_nodes)
        self.start_menu.config(bg="#242e3e", fg="white", highlightthickness=0, borderwidth=0, font=("Arial", 9))
        self.start_menu.pack(side=tk.LEFT, padx=5)

        tk.Label(control_frame, text="Destination:", **lbl_style).pack(side=tk.LEFT, padx=15)
        self.target_var = tk.StringVar(value="Community Center")
        self.target_menu = tk.OptionMenu(control_frame, self.target_var, *selectable_nodes)
        self.target_menu.config(bg="#242e3e", fg="white", highlightthickness=0, borderwidth=0, font=("Arial", 9))
        self.target_menu.pack(side=tk.LEFT, padx=5)

        btn_find = tk.Button(
            control_frame, text="🎯 Find Route", command=self.update_map,
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

        non_road_nodes = list(HOUSES.keys()) + list(CUSTOM_PURPLE_LANDMARKS.keys())
        for node, data in SUBDIVISION_MAP.items():
            if node in non_road_nodes:
                continue
            for neighbor in data["neighbors"]:
                if neighbor in non_road_nodes:
                    continue
                
                edge_id = tuple(sorted((node, neighbor)))
                if edge_id not in drawn_edges and neighbor in SUBDIVISION_MAP:
                    x1, y1 = data["x"], data["y"]
                    x2, y2 = SUBDIVISION_MAP[neighbor]["x"], SUBDIVISION_MAP[neighbor]["y"]
                    
                    self.canvas.create_line(x1, y1, x2, y2, fill="#1c2536", width=8, capstyle=tk.ROUND, joinstyle=tk.ROUND)
                    self.canvas.create_line(x1, y1, x2, y2, fill="#3a4b6e", width=3, capstyle=tk.ROUND, joinstyle=tk.ROUND)
                    drawn_edges.add(edge_id)

        for node, data in SUBDIVISION_MAP.items():
            x, y = data["x"], data["y"]

            if "Entrance_Gate" in node:
                self.canvas.create_rectangle(x - 12, y - 8, x + 12, y + 8, fill="#1e3a5f", outline="#2ec4b6", width=2)
                self.canvas.create_line(x - 14, y, x + 14, y, fill="#ff4d6d", width=3)
                self.canvas.create_text(x, y - 18, text="MAIN GATE", fill="#2ec4b6", font=("Arial", 9, "bold"))

            elif node == "Guard House":
                self.canvas.create_rectangle(x - 8, y - 6, x + 8, y + 6, fill="#e63946", outline="#f1faee", width=2)
                self.canvas.create_text(x + 12, y, text="🛡️ GUARD HOUSE", fill="#ff758f", font=("Arial", 8, "bold"), anchor="w")

            elif node == "My House":
                self.canvas.create_polygon(x, y - 9, x - 8, y - 1, x + 8, y - 1, fill="#2a9d8f", outline="")
                self.canvas.create_rectangle(x - 6, y - 1, x + 6, y + 6, fill="#e9c46a", outline="#264653", width=1)
                self.canvas.create_text(x - 10, y, text="🏠 MY HOUSE", fill="#52b788", font=("Arial", 8, "bold"), anchor="e")

            elif node == "Community Center":
                self.canvas.create_oval(x - 8, y - 8, x + 8, y + 8, fill="#e63946", outline="#ffffff", width=2)
                self.canvas.create_text(x, y - 16, text="📍 COMMUNITY CENTER", fill="#ff4d6d", font=("Arial", 8, "bold"))

            elif node == "Gazebo":
                r = 8
                self.canvas.create_polygon(
                    x, y - r, x + r*0.7, y - r*0.7, x + r, y, x + r*0.7, y + r*0.7,
                    x, y + r, x - r*0.7, y + r*0.7, x - r, y, x - r*0.7, y - r*0.7,
                    fill="#7209b7", outline="#4cc9f0", width=2
                )
                self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="#f72585", outline="")
                self.canvas.create_text(x, y + 14, text="🏛️ GAZEBO", fill="#4cc9f0", font=("Arial", 8, "bold"))

            elif node in CUSTOM_PURPLE_LANDMARKS:
                self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="#a855f7", outline="#ffffff", width=1.5)
                
                # Apply custom offsets to labels so they don't overlap each other
                off_x, off_y = CUSTOM_PURPLE_LANDMARKS[node].get("text_offset", (0, 0))
                align = CUSTOM_PURPLE_LANDMARKS[node].get("align", "above")
                
                anchor_style = "s" if align == "above" else "n"
                self.canvas.create_text(
                    x + off_x, y + off_y, 
                    text=f"📍 {node}", 
                    fill="#d8b4fe", 
                    font=("Arial", 8, "bold"), 
                    anchor=anchor_style
                )

            elif "House" in node:
                h_num = node.replace("House ", "")
                self.canvas.create_polygon(x, y - 5, x - 5, y - 1, x + 5, y - 1, fill="#e76f51", outline="")
                self.canvas.create_rectangle(x - 4, y - 1, x + 4, y + 4, fill="#e9c46a", outline="#264653", width=1)
                self.canvas.create_text(x, y + 10, text=h_num, fill="#f4a261", font=("Arial", 6, "bold"))

    def draw_highlighted_path(self, path, color, offset=0):
        for i in range(len(path) - 1):
            n1, n2 = path[i], path[i + 1]
            x1, y1 = SUBDIVISION_MAP[n1]["x"] + offset, SUBDIVISION_MAP[n1]["y"] + offset
            x2, y2 = SUBDIVISION_MAP[n2]["x"] + offset, SUBDIVISION_MAP[n2]["y"] + offset
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=5, capstyle=tk.ROUND, joinstyle=tk.ROUND)

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

        self.draw_highlighted_path(path1, "#00f5d4")

        distance_meters = calculate_path_distance_meters(path1)
        walk_time_mins = math.ceil(distance_meters / (4.5 * 1000 / 60))
        drive_time_mins = math.ceil(distance_meters / (20.0 * 1000 / 60))

        status_txt = f"Distance: {int(distance_meters)}m | 🚶 Walk: ~{walk_time_mins} min | 🚗 Drive: ~{drive_time_mins} min"

        if path2:
            self.draw_highlighted_path(path2, "#ffb703", offset=3)
            self.lbl_status.config(text=f"{status_txt} (Alt Route in Gold)", fg="#00f5d4")
        else:
            self.lbl_status.config(text=status_txt, fg="#90e0ef")

if __name__ == "__main__":
    root = tk.Tk()
    app = SubdivisionMapApp(root)
    root.mainloop()