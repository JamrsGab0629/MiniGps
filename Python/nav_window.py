"""
Navigation Window — a clean schematic view of your road network with
Start Point / Destination dropdowns and a Find Route button, similar to
a real turn-by-turn navigation UI.

Requires gps_router.py in the same folder.

Usage:
    python nav_window.py
"""

import tkinter as tk
from tkinter import ttk, filedialog
import json
import os
import re

from gps_router import shortest_path

BG = "#0f1420"
PANEL_BG = "#161c26"
EDGE_COLOR = "#3d5a80"
JUNCTION_COLOR = "#5a6a7a"
NAMED_COLOR = "#ffb703"
ROUTE_COLOR = "#06d6a0"
START_COLOR = "#06d6a0"
END_COLOR = "#ef476f"


def sort_key(name):
    """Sort so Gate-like nodes come first, then named locations (numeric-aware),
    then plain auto-numbered junctions."""
    lower = name.lower()
    match = re.search(r"(\d+)$", name)
    number = int(match.group(1)) if match else 0

    if "gate" in lower:
        return (0, number, name)
    if name.startswith("Junction_") or name.startswith("Ring_"):
        return (2, number, name)
    return (1, number, name)


class NavigationWindow:
    def __init__(self, root, graph_path):
        self.root = root
        self.root.title("Subdivision Navigation System")

        with open(graph_path) as f:
            self.graph = json.load(f)

        self.scale = 1.0
        self.min_scale = 0.15
        self.max_scale = 6.0
        self.offset_x = 0.0
        self.offset_y = 0.0

        self.path = None
        self.distance = None

        self._build_ui()
        self._fit_to_view()
        self.redraw()

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        top = tk.Frame(self.root, bg=PANEL_BG, pady=10, padx=10)
        top.pack(side=tk.TOP, fill=tk.X)

        node_names = sorted(self.graph.keys(), key=sort_key)

        tk.Label(top, text="Start Point:", bg=PANEL_BG, fg="white",
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 6))
        self.start_var = tk.StringVar(value=node_names[0] if node_names else "")
        self.start_combo = ttk.Combobox(top, textvariable=self.start_var, values=node_names,
                                         width=18, state="normal")
        self.start_combo.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(top, text="Destination:", bg=PANEL_BG, fg="white",
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 6))
        self.end_var = tk.StringVar(value=node_names[-1] if node_names else "")
        self.end_combo = ttk.Combobox(top, textvariable=self.end_var, values=node_names,
                                       width=18, state="normal")
        self.end_combo.pack(side=tk.LEFT, padx=(0, 20))

        tk.Button(top, text="🧭 Find Route", command=self.find_route,
                  bg="#00b4d8", fg="white", font=("Arial", 10, "bold"),
                  padx=10).pack(side=tk.LEFT, padx=(0, 15))

        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(top, textvariable=self.status_var, bg=PANEL_BG, fg="#8ecae6",
                 font=("Arial", 10)).pack(side=tk.LEFT)

        self.canvas = tk.Canvas(self.root, width=1200, height=800, bg=BG, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-2>", self.on_pan_start)
        self.canvas.bind("<B2-Motion>", self.on_pan_drag)
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<Button-4>", self.on_zoom)
        self.canvas.bind("<Button-5>", self.on_zoom)

    # ---------------------------------------------------- coordinate math

    def _fit_to_view(self):
        if not self.graph:
            return
        xs = [d["x"] for d in self.graph.values()]
        ys = [d["y"] for d in self.graph.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max(max_x - min_x, 1)
        span_y = max(max_y - min_y, 1)

        canvas_w, canvas_h = 1200, 800
        padding = 60
        scale_x = (canvas_w - 2 * padding) / span_x
        scale_y = (canvas_h - 2 * padding) / span_y
        self.scale = max(self.min_scale, min(self.max_scale, min(scale_x, scale_y)))

        self.offset_x = padding - min_x * self.scale
        self.offset_y = padding - min_y * self.scale

    def image_to_canvas(self, ix, iy):
        return ix * self.scale + self.offset_x, iy * self.scale + self.offset_y

    def canvas_to_image(self, cx, cy):
        return (cx - self.offset_x) / self.scale, (cy - self.offset_y) / self.scale

    # ------------------------------------------------------------ drawing

    def redraw(self):
        self.canvas.delete("all")

        drawn_edges = set()
        for name, data in self.graph.items():
            x1, y1 = self.image_to_canvas(data["x"], data["y"])
            for neighbor in data["neighbors"]:
                edge_key = tuple(sorted([name, neighbor]))
                if edge_key in drawn_edges:
                    continue
                drawn_edges.add(edge_key)
                ndata = self.graph.get(neighbor)
                if not ndata:
                    continue
                x2, y2 = self.image_to_canvas(ndata["x"], ndata["y"])
                self.canvas.create_line(x1, y1, x2, y2, fill=EDGE_COLOR,
                                         width=max(1, int(2.5 * self.scale)))

        if self.path:
            for i in range(len(self.path) - 1):
                a, b = self.path[i], self.path[i + 1]
                x1, y1 = self.image_to_canvas(self.graph[a]["x"], self.graph[a]["y"])
                x2, y2 = self.image_to_canvas(self.graph[b]["x"], self.graph[b]["y"])
                self.canvas.create_line(x1, y1, x2, y2, fill=ROUTE_COLOR,
                                         width=max(2, int(4.5 * self.scale)), capstyle=tk.ROUND)

        for name, data in self.graph.items():
            x, y = self.image_to_canvas(data["x"], data["y"])
            is_named = not (name.startswith("Junction_") or name.startswith("Ring_"))
            r = max(3, 5 * self.scale) if is_named else max(2, 3 * self.scale)
            color = NAMED_COLOR if is_named else JUNCTION_COLOR
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")
            if is_named:
                self.canvas.create_text(x, y - r - 9, text=name, fill="white",
                                         font=("Arial", 8))

        if self.path:
            sx, sy = self.image_to_canvas(self.graph[self.path[0]]["x"], self.graph[self.path[0]]["y"])
            ex, ey = self.image_to_canvas(self.graph[self.path[-1]]["x"], self.graph[self.path[-1]]["y"])
            r = max(5, 8 * self.scale)
            self.canvas.create_oval(sx - r, sy - r, sx + r, sy + r, fill=START_COLOR, outline="white", width=2)
            self.canvas.create_oval(ex - r, ey - r, ex + r, ey + r, fill=END_COLOR, outline="white", width=2)

    # ------------------------------------------------------------- events

    def find_route(self):
        start = self.start_var.get().strip()
        end = self.end_var.get().strip()

        if start not in self.graph:
            self.status_var.set(f"'{start}' not found.")
            return
        if end not in self.graph:
            self.status_var.set(f"'{end}' not found.")
            return

        path, distance = shortest_path(self.graph, start, end)
        if path is None:
            self.path, self.distance = None, None
            self.status_var.set("No route exists between these points.")
        else:
            self.path, self.distance = path, distance
            self.status_var.set(f"Route found: {len(path)} stops, {distance:.0f} px.")
        self.redraw()

    def on_pan_start(self, event):
        self._pan_start = (event.x, event.y)
        self._pan_offset_start = (self.offset_x, self.offset_y)

    def on_pan_drag(self, event):
        dx = event.x - self._pan_start[0]
        dy = event.y - self._pan_start[1]
        self.offset_x = self._pan_offset_start[0] + dx
        self.offset_y = self._pan_offset_start[1] + dy
        self.redraw()

    def on_zoom(self, event):
        if hasattr(event, "delta") and event.delta != 0:
            direction = 1 if event.delta > 0 else -1
        else:
            direction = 1 if getattr(event, "num", 4) == 4 else -1
        factor = 1.15 if direction > 0 else 1 / 1.15
        new_scale = max(self.min_scale, min(self.max_scale, self.scale * factor))
        if new_scale == self.scale:
            return
        img_x, img_y = self.canvas_to_image(event.x, event.y)
        self.scale = new_scale
        self.offset_x = event.x - img_x * self.scale
        self.offset_y = event.y - img_y * self.scale
        self.redraw()


if __name__ == "__main__":
    root = tk.Tk()

    graph_path = "road_network.json"
    if not os.path.exists(graph_path):
        graph_path = filedialog.askopenfilename(
            title="Select your saved road_network.json",
            filetypes=[("JSON files", "*.json")])
        if not graph_path:
            raise SystemExit("No graph file selected.")

    app = NavigationWindow(root, graph_path)
    root.mainloop()
