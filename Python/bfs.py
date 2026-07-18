import tkinter as tk
from collections import deque

# =====================================================================
# 1. 100% CORRECTED GEOMETRY (4-Lane Left Grid & Dual Center Roads)
# =====================================================================
SUBDIVISION_MAP = {
    # === ENTRANCE STEM & LEFT 4-LANE GRID SYSTEM ===
    "Junction_1": {"x": 131, "y": 86, "neighbors": ["Junction_2"]},
    "Junction_2": {"x": 191, "y": 188, "neighbors": ["Junction_1", "Junction_3"]},
    
    # Grid Row 1 (Top Intersections)
    "Junction_3": {"x": 144, "y": 205, "neighbors": ["Junction_2", "Junction_4", "Junction_9"]},
    "Junction_4": {"x": 99,  "y": 232, "neighbors": ["Junction_3", "Junction_5", "Junction_8"]},
    "Junction_5": {"x": 60,  "y": 265, "neighbors": ["Junction_4", "Junction_6"]},
    
    # Grid Row 2 (Middle Crossroad Row)
    "Junction_6": {"x": 112, "y": 451, "neighbors": ["Junction_5", "Junction_7", "Junction_10"]},
    "Junction_7": {"x": 182, "y": 451, "neighbors": ["Junction_6", "Junction_8", "Junction_11"]},
    "Junction_8": {"x": 230, "y": 430, "neighbors": ["Junction_7", "Junction_4", "Junction_9", "Junction_12"]},
    "Junction_9": {"x": 284, "y": 392, "neighbors": ["Junction_8", "Junction_3", "Junction_13"]},
    
    # Grid Row 3 (Lower Crossroad Row)
    "Junction_10": {"x": 160, "y": 570, "neighbors": ["Junction_6", "Junction_11"]},
    "Junction_11": {"x": 218, "y": 562, "neighbors": ["Junction_10", "Junction_7", "Junction_12"]},
    "Junction_12": {"x": 252, "y": 562, "neighbors": ["Junction_11", "Junction_8", "Junction_13", "Junction_15"]},
    "Junction_13": {"x": 334, "y": 526, "neighbors": ["Junction_12", "Junction_9", "Junction_14"]},
    
    # Connecting entry to Roundabout 1
    "Junction_14": {"x": 363, "y": 560, "neighbors": ["Junction_13", "Junction_17"]},
    "Junction_15": {"x": 263, "y": 569, "neighbors": ["Junction_12", "Junction_16"]},
    
    # === ROUNDABOUT 1 (Interconnected Ring) ===
    "Junction_16": {"x": 349, "y": 620, "neighbors": ["Junction_15", "Junction_18"]},
    "Junction_17": {"x": 357, "y": 568, "neighbors": ["Junction_14", "Junction_18", "Junction_19"]},
    "Junction_18": {"x": 352, "y": 607, "neighbors": ["Junction_16", "Junction_17", "Junction_20"]},
    
    # === DUAL SPINE HIGHWAY (Parallel Tracks) ===
    # Upper Spine Channel
    "Junction_19": {"x": 419, "y": 560, "neighbors": ["Junction_17", "Junction_21"]},
    "Junction_21": {"x": 422, "y": 574, "neighbors": ["Junction_19", "Junction_25"]},
    "Junction_25": {"x": 649, "y": 474, "neighbors": ["Junction_21", "Junction_23"]},
    "Junction_23": {"x": 642, "y": 466, "neighbors": ["Junction_25", "Junction_31"]}, # Connects to Right Hub
    
    # Lower Spine Channel
    "Junction_20": {"x": 416, "y": 628, "neighbors": ["Junction_18", "Junction_22"]},
    "Junction_22": {"x": 424, "y": 618, "neighbors": ["Junction_20", "Junction_26"]},
    "Junction_26": {"x": 725, "y": 539, "neighbors": ["Junction_22", "Junction_24"]},
    "Junction_24": {"x": 728, "y": 553, "neighbors": ["Junction_26", "Junction_28"]}, # Feeds Roundabout 2 Area
    
    # === ROUNDABOUT 2 AREA & EASTERN JUNCTIONS ===
    "Junction_28": {"x": 816, "y": 544, "neighbors": ["Junction_24", "Junction_30", "Junction_35"]},
    "Junction_30": {"x": 824, "y": 531, "neighbors": ["Junction_28", "Junction_29"]},
    "Junction_29": {"x": 838, "y": 484, "neighbors": ["Junction_30", "Junction_27"]},
    "Junction_27": {"x": 840, "y": 476, "neighbors": ["Junction_29", "Junction_31"]},
    
    # Right-side distribution hub
    "Junction_31": {"x": 903, "y": 500, "neighbors": ["Junction_23", "Junction_27", "Junction_32", "Junction_35"]},
    
    # Branching Spurs
    "Junction_32": {"x": 1063, "y": 431, "neighbors": ["Junction_31"]}, # Upper outer spur
    "Junction_33": {"x": 946, "y": 650, "neighbors": ["Junction_35"]},  # South spur
    
    # === INTERCONNECTED RIGHT-SIDE LOOP SYSTEM ===
    "Junction_35": {"x": 912, "y": 511, "neighbors": ["Junction_31", "Junction_28", "Junction_33", "Junction_34", "Junction_36"]},
    "Junction_34": {"x": 1026, "y": 554, "neighbors": ["Junction_35", "Junction_36", "Junction_41"]},
    "Junction_36": {"x": 1071, "y": 563, "neighbors": ["Junction_35", "Junction_34", "Junction_37"]},
    
    # Outer Loop Perimeter
    "Junction_37": {"x": 1173, "y": 554, "neighbors": ["Junction_36", "Junction_38"]},
    "Junction_38": {"x": 1167, "y": 695, "neighbors": ["Junction_37", "Junction_39"]},
    "Junction_39": {"x": 1094, "y": 701, "neighbors": ["Junction_38", "Junction_40"]},
    "Junction_40": {"x": 1096, "y": 685, "neighbors": ["Junction_39", "Junction_41"]},
    "Junction_41": {"x": 1025, "y": 689, "neighbors": ["Junction_40", "Junction_34"]}  # Loops back up
}
# =====================================================================
# 2. PATHFINDING LOGIC (BFS Engine)
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
        edge_to_block = (path1[i], path1[i+1])
        alt_path = find_path_bfs(graph, start, target, blocked_edge=edge_to_block)
        if alt_path:
            alternative_paths.append(alt_path)

    path2 = None
    if alternative_paths:
        alternative_paths.sort(key=len)
        best_alt = alternative_paths[0]
        if len(best_alt) <= len(path1) + 6:  # Slightly wider threshold for the split loops
            path2 = best_alt

    return path1, path2

# =====================================================================
# 3. UI PRESENTATION ENGINE (Tkinter)
# =====================================================================
class SubdivisionMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Updated 4-Lane & Dual Spine Road Network")
        self.root.configure(bg="#0f141c")
        
        sorted_keys = sorted(SUBDIVISION_MAP.keys())
        
        control_frame = tk.Frame(root, padx=15, pady=15, bg="#161c26")
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        lbl_style = {"bg": "#161c26", "fg": "#ffffff", "font": ("Arial", 10, "bold")}
        
        tk.Label(control_frame, text="Start Node:", **lbl_style).pack(side=tk.LEFT, padx=5)
        self.start_var = tk.StringVar(value="Junction_1")
        self.start_menu = tk.OptionMenu(control_frame, self.start_var, *sorted_keys)
        self.start_menu.config(bg="#242e3e", fg="white", highlightthickness=0, borderwidth=0, font=("Arial", 9))
        self.start_menu.pack(side=tk.LEFT, padx=5)
        
        tk.Label(control_frame, text="End Node:", **lbl_style).pack(side=tk.LEFT, padx=15)
        self.target_var = tk.StringVar(value="Right_Terminal_Spur")
        self.target_menu = tk.OptionMenu(control_frame, self.target_var, *sorted_keys)
        self.target_menu.config(bg="#242e3e", fg="white", highlightthickness=0, borderwidth=0, font=("Arial", 9))
        self.target_menu.pack(side=tk.LEFT, padx=5)
        
        btn_find = tk.Button(control_frame, text="Map Active Routes", command=self.update_map, 
                             bg="#00b4d8", fg="white", font=("Arial", 10, "bold"), padx=12, relief=tk.FLAT)
        btn_find.pack(side=tk.LEFT, padx=25)
        
        self.lbl_status = tk.Label(control_frame, text="Ready.", bg="#161c26", fg="#00b4d8", font=("Arial", 10))
        self.lbl_status.pack(side=tk.LEFT, padx=10)

        self.canvas = tk.Canvas(root, width=1020, height=750, bg="#0f141c", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.draw_base_graph()

    def draw_base_graph(self):
        self.canvas.delete("all")
        
        drawn_edges = set()
        for node, data in SUBDIVISION_MAP.items():
            for neighbor in data["neighbors"]:
                edge_id = tuple(sorted((node, neighbor)))
                if edge_id not in drawn_edges:
                    x1, y1 = data["x"], data["y"]
                    x2, y2 = SUBDIVISION_MAP[neighbor]["x"], SUBDIVISION_MAP[neighbor]["y"]
                    self.canvas.create_line(x1, y1, x2, y2, fill="#222c3c", width=12, capstyle=tk.ROUND)
                    self.canvas.create_line(x1, y1, x2, y2, fill="#2c3b52", width=10, capstyle=tk.ROUND)
                    drawn_edges.add(edge_id)
                    
        for node, data in SUBDIVISION_MAP.items():
            x, y = data["x"], data["y"]
            color = "#52b788" if "Roundabout" in node else "#4a5d78"
            r = 6 if "Roundabout" in node else 5
            
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="#0f141c", width=2)
            
            # Formatted cleaner label keys for scannability
            display_label = node.replace("Grid_Col", "C").replace("Roundabout_", "R_").replace("Spine_", "S_")
            self.canvas.create_text(x, y-15, text=display_label, fill="#78889f", font=("Arial", 7, "bold"))

    def draw_highlighted_path(self, path, color, offset=0):
        for i in range(len(path) - 1):
            n1, n2 = path[i], path[i+1]
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
            
        self.draw_highlighted_path(path1, "#2ec4b6")
        
        if path2:
            self.draw_highlighted_path(path2, "#e67e22", offset=3)
            self.lbl_status.config(text="Alternative pathways mapped completely over parallel channels.", fg="#2ec4b6")
        else:
            self.lbl_status.config(text="Optimal path mapped.", fg="#90e0ef")

if __name__ == "__main__":
    root = tk.Tk()
    app = SubdivisionMapApp(root)
    root.mainloop()