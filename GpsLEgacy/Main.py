import tkinter as tk
from tkinter import simpledialog, messagebox
from collections import deque
import math
import json
import os

TXT_FILE_PATH = "map_data.txt"
METERS_PER_PIXEL = 0.65  # Scale: 1 pixel ≈ 0.65 meters

# Speed assumptions (in meters per minute)
WALK_SPEED_MPM = 80    # ~4.8 km/h walking speed
DRIVE_SPEED_MPM = 333   # ~20 km/h driving speed in a subdivision

# Delay between drawing line segments (in milliseconds)
ANIMATION_DELAY_MS = 200 

# =====================================================================
# PATHFINDING (BFS with House-Bypass Safeguard & Alternate Path)
# =====================================================================
def find_path_bfs(graph, start, target, blocked_edge=None, house_names=None):
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
    path1 = find_path_bfs(graph, start, target, house_names=house_names)
    if not path1:
        return None, None

    alt_paths = []
    for i in range(len(path1) - 1):
        alt = find_path_bfs(graph, start, target, blocked_edge=(path1[i], path1[i + 1]), house_names=house_names)
        if alt:
            alt_paths.append(alt)

    path2 = None
    if alt_paths:
        alt_paths.sort(key=len)
        if len(alt_paths[0]) <= len(path1) + 6:
            path2 = alt_paths[0]

    return path1, path2

def calculate_path_distance(graph, path):
    total_pixels = 0.0
    for i in range(len(path) - 1):
        n1, n2 = path[i], path[i + 1]
        x1, y1 = graph[n1]["x"], graph[n1]["y"]
        x2, y2 = graph[n2]["x"], graph[n2]["y"]
        total_pixels += math.hypot(x2 - x1, y2 - y1)
    return total_pixels * METERS_PER_PIXEL

# =====================================================================
# MAIN TKINTER APPLICATION
# =====================================================================
class SubdivisionMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Subdivision Interactive Map Editor")
        self.root.configure(bg="#0f141c")

        self.junctions = {}
        self.houses = {}
        self.edit_mode = True  
        self.selected_node_a = None
        self.selected_node_delete = None
        self.dragging_node = None
        self.subdivision_map = {}

        # Track active animation job so new clicks cancel old animations
        self.anim_job = None

        # UI Control Bar
        control_frame = tk.Frame(root, padx=10, pady=8, bg="#161c26")
        control_frame.pack(side=tk.TOP, fill=tk.X)

        self.start_var = tk.StringVar()
        self.target_var = tk.StringVar()

        tk.Label(control_frame, text="Start:", bg="#161c26", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=3)
        self.start_menu = tk.OptionMenu(control_frame, self.start_var, "")
        self.start_menu.config(bg="#242e3e", fg="white", highlightthickness=0, font=("Arial", 8))
        self.start_menu.pack(side=tk.LEFT, padx=3)

        tk.Label(control_frame, text="Target:", bg="#161c26", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=3)
        self.target_menu = tk.OptionMenu(control_frame, self.target_var, "")
        self.target_menu.config(bg="#242e3e", fg="white", highlightthickness=0, font=("Arial", 8))
        self.target_menu.pack(side=tk.LEFT, padx=3)

        btn_find = tk.Button(control_frame, text="🎯 Route", command=self.update_map, bg="#00b4d8", fg="white", font=("Arial", 9, "bold"), relief=tk.FLAT, cursor="hand2")
        btn_find.pack(side=tk.LEFT, padx=5)

        self.btn_edit = tk.Button(control_frame, text="🛠️ Edit Mode: ON", command=self.toggle_edit_mode, bg="#2a9d8f", fg="white", font=("Arial", 9, "bold"), relief=tk.FLAT, cursor="hand2")
        self.btn_edit.pack(side=tk.LEFT, padx=5)

        btn_clear = tk.Button(control_frame, text="🗑️ Clear All", command=self.clear_all, bg="#e63946", fg="white", font=("Arial", 9, "bold"), relief=tk.FLAT, cursor="hand2")
        btn_clear.pack(side=tk.LEFT, padx=5)

        self.lbl_status = tk.Label(control_frame, text="Double-click canvas to add a house | Shift+Double-click for a junction", bg="#161c26", fg="#ffb703", font=("Arial", 9))
        self.lbl_status.pack(side=tk.LEFT, padx=8)

        # Canvas
        self.canvas = tk.Canvas(root, width=1200, height=730, bg="#0f141c", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bindings
        self.canvas.bind("<ButtonPress-1>", self.on_left_click_press)
        self.canvas.bind("<B1-Motion>", self.on_left_click_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_click_release)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<Shift-Double-Button-1>", self.on_shift_double_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.root.bind("<Delete>", self.delete_selected_node)
        self.root.bind("<BackSpace>", self.delete_selected_node)

        # Load Saved Data
        self.load_from_txt()
        self.update_dropdowns()
        self.rebuild_map_data()
        self.draw_base_graph()

    def load_from_txt(self):
        if os.path.exists(TXT_FILE_PATH):
            try:
                with open(TXT_FILE_PATH, "r") as f:
                    data = json.load(f)
                    self.junctions = data.get("junctions", {})
                    self.houses = data.get("houses", {})
            except Exception as e:
                print(f"Error loading map_data.txt: {e}")

    def auto_save_to_txt(self):
        data = {"junctions": self.junctions, "houses": self.houses}
        with open(TXT_FILE_PATH, "w") as f:
            json.dump(data, f, indent=4)

    def update_dropdowns(self):
        nodes = sorted(list(self.houses.keys()))
        menu_s = self.start_menu["menu"]
        menu_t = self.target_menu["menu"]
        menu_s.delete(0, "end")
        menu_t.delete(0, "end")

        for item in nodes:
            menu_s.add_command(label=item, command=lambda v=item: self.start_var.set(v))
            menu_t.add_command(label=item, command=lambda v=item: self.target_var.set(v))

        if nodes and not self.start_var.get():
            self.start_var.set(nodes[0])
        if len(nodes) > 1 and not self.target_var.get():
            self.target_var.set(nodes[1])

    def clear_all(self):
        if messagebox.askyesno("Clear All", "Are you sure you want to delete everything and start fresh?"):
            self.cancel_animation()
            self.junctions = {}
            self.houses = {}
            self.start_var.set("")
            self.target_var.set("")
            self.update_dropdowns()
            self.rebuild_map_data()
            self.auto_save_to_txt()
            self.draw_base_graph()

    def rebuild_map_data(self):
        self.subdivision_map = {node: dict(data) for node, data in self.junctions.items()}
        
        for h_name, h_data in self.houses.items():
            if not self.junctions:
                continue
            hx, hy = h_data["x"], h_data["y"]
            nearest_j = min(self.junctions.keys(), key=lambda j: math.hypot(self.junctions[j]["x"] - hx, self.junctions[j]["y"] - hy))
            
            self.subdivision_map[h_name] = {"x": hx, "y": hy, "neighbors": [nearest_j]}
            self.subdivision_map[nearest_j]["neighbors"].append(h_name)

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        if self.edit_mode:
            self.btn_edit.config(text="🛠️ Edit Mode: ON", bg="#2a9d8f")
        else:
            self.btn_edit.config(text="🛠️ Edit Mode: OFF", bg="#e63946")
            self.selected_node_a = None
            self.selected_node_delete = None
        self.draw_base_graph()

    def find_node_near_click(self, x, y, max_dist=15):
        for node, data in self.junctions.items():
            if math.hypot(data["x"] - x, data["y"] - y) <= max_dist:
                return node, "junction"
        for name, data in self.houses.items():
            if math.hypot(data["x"] - x, data["y"] - y) <= max_dist:
                return name, "house"
        return None, None

    def cancel_animation(self):
        if self.anim_job:
            self.root.after_cancel(self.anim_job)
            self.anim_job = None

    def on_left_click_press(self, event):
        self.cancel_animation()
        node, node_type = self.find_node_near_click(event.x, event.y)
        if node:
            self.selected_node_delete = (node, node_type)
            if self.edit_mode:
                self.dragging_node = (node, node_type)
        else:
            self.selected_node_delete = None
        self.draw_base_graph()

    def on_left_click_drag(self, event):
        if not self.edit_mode or not self.dragging_node:
            return
        node, node_type = self.dragging_node
        if node_type == "junction":
            self.junctions[node]["x"], self.junctions[node]["y"] = event.x, event.y
        else:
            self.houses[node]["x"], self.houses[node]["y"] = event.x, event.y

        self.rebuild_map_data()
        self.draw_base_graph()

    def on_left_click_release(self, event):
        if self.dragging_node:
            self.dragging_node = None
            self.auto_save_to_txt()

    def on_double_click(self, event):
        if not self.edit_mode: return
        name = simpledialog.askstring("Add House", "Enter new House name:", parent=self.root)
        if name:
            name = name.strip()
            if name in self.houses:
                messagebox.showerror("Error", "A house with that name already exists!")
                return
            
            is_purple = messagebox.askyesno("House Color", "Should this house be Purple?", parent=self.root)
            color_type = "purple" if is_purple else "default"

            self.houses[name] = {"x": event.x, "y": event.y, "type": color_type}
            self.update_dropdowns()
            self.rebuild_map_data()
            self.auto_save_to_txt()
            self.draw_base_graph()

    def on_shift_double_click(self, event):
        if not self.edit_mode: return
        j_id = f"Junction_{len(self.junctions) + 1}"
        self.junctions[j_id] = {"x": event.x, "y": event.y, "neighbors": []}
        self.rebuild_map_data()
        self.auto_save_to_txt()
        self.draw_base_graph()

    def on_right_click(self, event):
        if not self.edit_mode: return
        node, node_type = self.find_node_near_click(event.x, event.y)
        if not node or node_type != "junction":
            return

        if self.selected_node_a is None:
            self.selected_node_a = node
            self.lbl_status.config(text=f"Selected '{node}'. Right-click 2nd junction to connect.", fg="#ffb703")
        else:
            nA, nB = self.selected_node_a, node
            if nA != nB:
                if nB in self.junctions[nA]["neighbors"]:
                    self.junctions[nA]["neighbors"].remove(nB)
                    if nA in self.junctions[nB]["neighbors"]:
                        self.junctions[nB]["neighbors"].remove(nA)
                else:
                    self.junctions[nA]["neighbors"].append(nB)
                    self.junctions[nB]["neighbors"].append(nA)

            self.selected_node_a = None
            self.rebuild_map_data()
            self.auto_save_to_txt()
            self.draw_base_graph()

    def delete_selected_node(self, event=None):
        if not self.edit_mode or not self.selected_node_delete:
            return
        node, node_type = self.selected_node_delete

        if node_type == "junction":
            del self.junctions[node]
            for j_data in self.junctions.values():
                if node in j_data["neighbors"]:
                    j_data["neighbors"].remove(node)
        elif node_type == "house":
            del self.houses[node]
            self.update_dropdowns()

        self.selected_node_delete = None
        self.rebuild_map_data()
        self.auto_save_to_txt()
        self.draw_base_graph()

    def draw_base_graph(self):
        self.canvas.delete("all")
        drawn_edges = set()
        non_road = list(self.houses.keys())

        # Draw roads
        for node, data in self.subdivision_map.items():
            if node in non_road: continue
            for neighbor in data["neighbors"]:
                if neighbor in non_road: continue
                edge = tuple(sorted((node, neighbor)))
                if edge not in drawn_edges and neighbor in self.subdivision_map:
                    x1, y1 = data["x"], data["y"]
                    x2, y2 = self.subdivision_map[neighbor]["x"], self.subdivision_map[neighbor]["y"]
                    self.canvas.create_line(x1, y1, x2, y2, fill="#1c2536", width=8, capstyle=tk.ROUND)
                    self.canvas.create_line(x1, y1, x2, y2, fill="#3a4b6e", width=3, capstyle=tk.ROUND)
                    drawn_edges.add(edge)

        # Draw junctions
        if self.edit_mode:
            for j_name, j_data in self.junctions.items():
                jx, jy = j_data["x"], j_data["y"]
                color = "#ffb703" if j_name == self.selected_node_a else ("#ff4d6d" if self.selected_node_delete and self.selected_node_delete[0] == j_name else "#00f5d4")
                self.canvas.create_oval(jx - 5, jy - 5, jx + 5, jy + 5, fill=color, outline="#ffffff")

        # Draw houses
        for node, data in self.subdivision_map.items():
            x, y = data["x"], data["y"]
            if node in self.houses:
                h_info = self.houses[node]
                if self.selected_node_delete and self.selected_node_delete[0] == node:
                    color = "#ff4d6d"
                elif h_info.get("type") == "purple":
                    color = "#9d4edd"
                else:
                    color = "#e76f51"

                self.canvas.create_polygon(x, y - 6, x - 5, y, x + 5, y, fill=color)
                self.canvas.create_rectangle(x - 4, y, x + 4, y + 5, fill="#e9c46a", outline="#264653")
                self.canvas.create_text(x, y + 12, text=node, fill="#ffffff", font=("Arial", 7, "bold"))

    def animate_paths_step(self, p1, p2, step_idx=0):
        """Draws one segment of the paths at a time using root.after()"""
        max_steps = max(len(p1) - 1 if p1 else 0, len(p2) - 1 if p2 else 0)

        if step_idx < max_steps:
            # Draw primary path segment (Teal)
            if p1 and step_idx < len(p1) - 1:
                n1, n2 = p1[step_idx], p1[step_idx + 1]
                x1, y1 = self.subdivision_map[n1]["x"], self.subdivision_map[n1]["y"]
                x2, y2 = self.subdivision_map[n2]["x"], self.subdivision_map[n2]["y"]
                self.canvas.create_line(x1, y1, x2, y2, fill="#00f5d4", width=5, capstyle=tk.ROUND)

            # Draw secondary path segment (Yellow offset)
            if p2 and step_idx < len(p2) - 1:
                n1, n2 = p2[step_idx], p2[step_idx + 1]
                x1, y1 = self.subdivision_map[n1]["x"] + 3, self.subdivision_map[n1]["y"] + 3
                x2, y2 = self.subdivision_map[n2]["x"] + 3, self.subdivision_map[n2]["y"] + 3
                self.canvas.create_line(x1, y1, x2, y2, fill="#ffb703", width=5, capstyle=tk.ROUND)

            # Schedule the next step in ANIMATION_DELAY_MS milliseconds
            self.anim_job = self.root.after(ANIMATION_DELAY_MS, self.animate_paths_step, p1, p2, step_idx + 1)

    def draw_info_box(self, dist1, path2=None, dist2=0.0):
        walk1_min = dist1 / WALK_SPEED_MPM
        drive1_min = dist1 / DRIVE_SPEED_MPM

        text = f"📍 PRIMARY ROUTE\n"
        text += f" Distance: {dist1:.1f} meters\n"
        text += f" 🚶 Walking: ~{walk1_min:.1f} mins\n"
        text += f" 🚗 Driving: ~{drive1_min:.1f} mins\n"

        if path2:
            walk2_min = dist2 / WALK_SPEED_MPM
            drive2_min = dist2 / DRIVE_SPEED_MPM
            text += f"\n🔀 SECOND SHORTEST ROUTE\n"
            text += f" Distance: {dist2:.1f} meters\n"
            text += f" 🚶 Walking: ~{walk2_min:.1f} mins\n"
            text += f" 🚗 Driving: ~{drive2_min:.1f} mins\n"

        x1, y1, x2, y2 = 910, 15, 1185, 175 if path2 else 110
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="#161c26", outline="#00b4d8", width=2)
        self.canvas.create_text(x1 + 10, y1 + 10, text=text, fill="#ffffff", font=("Consolas", 8), anchor="nw")

    def update_map(self):
        self.cancel_animation()
        start, target = self.start_var.get(), self.target_var.get()
        self.draw_base_graph()

        if not start or not target or start == target:
            return

        p1, p2 = calculate_paths(self.subdivision_map, start, target, house_names=set(self.houses.keys()))
        
        if p1:
            dist1 = calculate_path_distance(self.subdivision_map, p1)
            dist2 = calculate_path_distance(self.subdivision_map, p2) if p2 else 0.0

            # 1. Draw distance & estimated times overlay immediately
            self.draw_info_box(dist1, p2, dist2)

            # 2. Start slow animated line-drawing sequence step-by-step
            self.animate_paths_step(p1, p2, 0)

            self.lbl_status.config(text=f"Routing from '{start}' to '{target}'...", fg="#00f5d4")
        else:
            self.lbl_status.config(text="No valid path found between selected houses.", fg="#ff4d6d")

if __name__ == "__main__":
    root = tk.Tk()
    app = SubdivisionMapApp(root)
    root.mainloop()