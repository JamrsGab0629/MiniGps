import tkinter as tk
from tkinter import simpledialog, messagebox

from pathfinder import calculate_paths, calculate_path_distance
from storage import StorageManager
from map_data import MapGraph

WALK_SPEED_MPM = 80     # ~4.8 km/h walking speed
DRIVE_SPEED_MPM = 333   # ~20 km/h driving speed
ANIMATION_DELAY_MS = 200


class SubdivisionMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Subdivision Interactive Map Editor")
        self.root.configure(bg="#0f141c")

        self.storage = StorageManager()
        self.map_graph = MapGraph()

        self.edit_mode = True  
        self.selected_node_a = None
        self.selected_node_delete = None
        self.dragging_node = None
        self.anim_job = None

        # Load saved state
        self.map_graph.junctions, self.map_graph.houses = self.storage.load()

        # UI Setup
        self._setup_ui()

        # Bindings
        self._bind_events()

        # Initial Render
        self.update_dropdowns()
        self.map_graph.rebuild()
        self.draw_base_graph()

    def _setup_ui(self):
        control_frame = tk.Frame(self.root, padx=10, pady=8, bg="#161c26")
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

        self.canvas = tk.Canvas(self.root, width=1200, height=730, bg="#0f141c", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def _bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self.on_left_click_press)
        self.canvas.bind("<B1-Motion>", self.on_left_click_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_click_release)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<Shift-Double-Button-1>", self.on_shift_double_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.root.bind("<Delete>", self.delete_selected_node)
        self.root.bind("<BackSpace>", self.delete_selected_node)

    def auto_save(self):
        self.storage.save(self.map_graph.junctions, self.map_graph.houses)

    def update_dropdowns(self):
        nodes = sorted(list(self.map_graph.houses.keys()))
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
            self.map_graph.junctions = {}
            self.map_graph.houses = {}
            self.start_var.set("")
            self.target_var.set("")
            self.update_dropdowns()
            self.map_graph.rebuild()
            self.auto_save()
            self.draw_base_graph()

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        if self.edit_mode:
            self.btn_edit.config(text="🛠️ Edit Mode: ON", bg="#2a9d8f")
        else:
            self.btn_edit.config(text="🛠️ Edit Mode: OFF", bg="#e63946")
            self.selected_node_a = None
            self.selected_node_delete = None
        self.draw_base_graph()

    def cancel_animation(self):
        if self.anim_job:
            self.root.after_cancel(self.anim_job)
            self.anim_job = None

    def on_left_click_press(self, event):
        self.cancel_animation()
        node, node_type = self.map_graph.find_node_near_click(event.x, event.y)
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
            self.map_graph.junctions[node]["x"], self.map_graph.junctions[node]["y"] = event.x, event.y
        else:
            self.map_graph.houses[node]["x"], self.map_graph.houses[node]["y"] = event.x, event.y

        self.map_graph.rebuild()
        self.draw_base_graph()

    def on_left_click_release(self, event):
        if self.dragging_node:
            self.dragging_node = None
            self.auto_save()

    def on_double_click(self, event):
        if not self.edit_mode: return
        name = simpledialog.askstring("Add House", "Enter new House name:", parent=self.root)
        if name:
            name = name.strip()
            if name in self.map_graph.houses:
                messagebox.showerror("Error", "A house with that name already exists!")
                return
            
            is_purple = messagebox.askyesno("House Color", "Should this house be Purple?", parent=self.root)
            color_type = "purple" if is_purple else "default"

            self.map_graph.houses[name] = {"x": event.x, "y": event.y, "type": color_type}
            self.update_dropdowns()
            self.map_graph.rebuild()
            self.auto_save()
            self.draw_base_graph()

    def on_shift_double_click(self, event):
        if not self.edit_mode: return
        j_id = f"Junction_{len(self.map_graph.junctions) + 1}"
        self.map_graph.junctions[j_id] = {"x": event.x, "y": event.y, "neighbors": []}
        self.map_graph.rebuild()
        self.auto_save()
        self.draw_base_graph()

    def on_right_click(self, event):
        if not self.edit_mode: return
        node, node_type = self.map_graph.find_node_near_click(event.x, event.y)
        if not node or node_type != "junction":
            return

        if self.selected_node_a is None:
            self.selected_node_a = node
            self.lbl_status.config(text=f"Selected '{node}'. Right-click 2nd junction to connect.", fg="#ffb703")
        else:
            nA, nB = self.selected_node_a, node
            if nA != nB:
                if nB in self.map_graph.junctions[nA]["neighbors"]:
                    self.map_graph.junctions[nA]["neighbors"].remove(nB)
                    if nA in self.map_graph.junctions[nB]["neighbors"]:
                        self.map_graph.junctions[nB]["neighbors"].remove(nA)
                else:
                    self.map_graph.junctions[nA]["neighbors"].append(nB)
                    self.map_graph.junctions[nB]["neighbors"].append(nA)

            self.selected_node_a = None
            self.map_graph.rebuild()
            self.auto_save()
            self.draw_base_graph()

    def delete_selected_node(self, event=None):
        if not self.edit_mode or not self.selected_node_delete:
            return
        node, node_type = self.selected_node_delete

        if node_type == "junction":
            del self.map_graph.junctions[node]
            for j_data in self.map_graph.junctions.values():
                if node in j_data["neighbors"]:
                    j_data["neighbors"].remove(node)
        elif node_type == "house":
            del self.map_graph.houses[node]
            self.update_dropdowns()

        self.selected_node_delete = None
        self.map_graph.rebuild()
        self.auto_save()
        self.draw_base_graph()

    def draw_base_graph(self):
        self.canvas.delete("all")
        drawn_edges = set()
        non_road = list(self.map_graph.houses.keys())

        # Draw roads
        for node, data in self.map_graph.subdivision_map.items():
            if node in non_road: continue
            for neighbor in data["neighbors"]:
                if neighbor in non_road: continue
                edge = tuple(sorted((node, neighbor)))
                if edge not in drawn_edges and neighbor in self.map_graph.subdivision_map:
                    x1, y1 = data["x"], data["y"]
                    x2, y2 = self.map_graph.subdivision_map[neighbor]["x"], self.map_graph.subdivision_map[neighbor]["y"]
                    self.canvas.create_line(x1, y1, x2, y2, fill="#1c2536", width=8, capstyle=tk.ROUND)
                    self.canvas.create_line(x1, y1, x2, y2, fill="#3a4b6e", width=3, capstyle=tk.ROUND)
                    drawn_edges.add(edge)

        # Draw junctions
        if self.edit_mode:
            for j_name, j_data in self.map_graph.junctions.items():
                jx, jy = j_data["x"], j_data["y"]
                color = "#ffb703" if j_name == self.selected_node_a else ("#ff4d6d" if self.selected_node_delete and self.selected_node_delete[0] == j_name else "#00f5d4")
                self.canvas.create_oval(jx - 5, jy - 5, jx + 5, jy + 5, fill=color, outline="#ffffff")

        # Draw houses
        for node, data in self.map_graph.subdivision_map.items():
            x, y = data["x"], data["y"]
            if node in self.map_graph.houses:
                h_info = self.map_graph.houses[node]
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
        max_steps = max(len(p1) - 1 if p1 else 0, len(p2) - 1 if p2 else 0)

        if step_idx < max_steps:
            if p1 and step_idx < len(p1) - 1:
                n1, n2 = p1[step_idx], p1[step_idx + 1]
                x1, y1 = self.map_graph.subdivision_map[n1]["x"], self.map_graph.subdivision_map[n1]["y"]
                x2, y2 = self.map_graph.subdivision_map[n2]["x"], self.map_graph.subdivision_map[n2]["y"]
                self.canvas.create_line(x1, y1, x2, y2, fill="#00f5d4", width=5, capstyle=tk.ROUND)

            if p2 and step_idx < len(p2) - 1:
                n1, n2 = p2[step_idx], p2[step_idx + 1]
                x1, y1 = self.map_graph.subdivision_map[n1]["x"] + 3, self.map_graph.subdivision_map[n1]["y"] + 3
                x2, y2 = self.map_graph.subdivision_map[n2]["x"] + 3, self.map_graph.subdivision_map[n2]["y"] + 3
                self.canvas.create_line(x1, y1, x2, y2, fill="#ffb703", width=5, capstyle=tk.ROUND)

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

        p1, p2 = calculate_paths(
            self.map_graph.subdivision_map, 
            start, 
            target, 
            house_names=set(self.map_graph.houses.keys())
        )
        
        if p1:
            dist1 = calculate_path_distance(self.map_graph.subdivision_map, p1)
            dist2 = calculate_path_distance(self.map_graph.subdivision_map, p2) if p2 else 0.0

            self.draw_info_box(dist1, p2, dist2)
            self.animate_paths_step(p1, p2, 0)
            self.lbl_status.config(text=f"Routing from '{start}' to '{target}'...", fg="#00f5d4")
        else:
            self.lbl_status.config(text="No valid path found between selected houses.", fg="#ff4d6d")


if __name__ == "__main__":
    root = tk.Tk()
    app = SubdivisionMapApp(root)
    root.mainloop()