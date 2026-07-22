# =====================================================================
# UI PRESENTATION ENGINE (Tkinter)
# =====================================================================
import math
import tkinter as tk

from map_data import HOUSES, CUSTOM_PURPLE_LANDMARKS
from geometry import SUBDIVISION_MAP
from pathfinding import calculate_paths, calculate_path_distance_meters


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

        distance_meters = calculate_path_distance_meters(SUBDIVISION_MAP, path1)
        walk_time_mins = math.ceil(distance_meters / (4.5 * 1000 / 60))
        drive_time_mins = math.ceil(distance_meters / (20.0 * 1000 / 60))

        status_txt = f"Distance: {int(distance_meters)}m | 🚶 Walk: ~{walk_time_mins} min | 🚗 Drive: ~{drive_time_mins} min"

        if path2:
            self.draw_highlighted_path(path2, "#ffb703", offset=3)
            self.lbl_status.config(text=f"{status_txt} (Alt Route in Gold)", fg="#00f5d4")
        else:
            self.lbl_status.config(text=status_txt, fg="#90e0ef")
