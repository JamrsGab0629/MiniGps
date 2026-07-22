import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import math
import json
import os

try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE = Image.LANCZOS


class RoadDrawerTool:
    def __init__(self, root, image_path):
        self.root = root
        self.root.title("Subdivision Road Mapping & Coordinate Generator Tool")

        # --- Image / view state ---
        self.raw_img = Image.open(image_path).convert("RGB")
        self.img_w, self.img_h = self.raw_img.size
        self.scale = 1.0
        self.min_scale = 0.15
        self.max_scale = 6.0
        self.offset_x = 0.0
        self.offset_y = 0.0

        # --- Graph state (all coordinates stored in ORIGINAL image space) ---
        self.node_count = 1
        self.graph = {}
        self.current_segment_nodes = []
        self.action_log = []          # for undo
        self.roundabout_mode = False
        self.roundabout_center = None

        # Thresholds (image-space pixels, so they mean the same thing at any zoom)
        self.min_drag_distance = 10
        self.snap_radius_canvas = 14  # canvas px; converted to image space using current scale

        self._build_ui()

        print("\n" + "=" * 70)
        print(" ROAD MAPPER STARTED")
        print(" Scroll = zoom | Middle-drag = pan | Left-drag = draw road")
        print(" Double-click node = rename | Right-click node = delete | Ctrl+Z = undo | Ctrl+S = save")
        print("=" * 70)

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        control_frame = tk.Frame(self.root, bg="#161c26", pady=6)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        def make_btn(text, cmd, color):
            b = tk.Button(control_frame, text=text, command=cmd, bg=color, fg="white",
                          font=("Arial", 10, "bold"), padx=8)
            b.pack(side=tk.LEFT, padx=4)
            return b

        make_btn("✅ Finish Segment", self.finish_segment, "#00b4d8")
        make_btn("⭕ Roundabout Mode", self.enable_roundabout_mode, "#7209b7")
        make_btn("↩ Undo (Ctrl+Z)", self.undo, "#8d99ae")
        make_btn("💾 Save JSON", self.save_json, "#2a9d8f")
        make_btn("📂 Load JSON", self.load_json, "#457b9d")
        make_btn("🗑 Clear All", self.clear_all, "#e63946")

        self.show_labels_var = tk.BooleanVar(value=True)
        tk.Checkbutton(control_frame, text="Show labels", variable=self.show_labels_var,
                        command=self.redraw, bg="#161c26", fg="white",
                        selectcolor="#161c26", font=("Arial", 9)).pack(side=tk.LEFT, padx=10)

        self.lbl_info = tk.Label(
            control_frame,
            text="Left-drag to trace roads (snaps to existing junctions). Double-click a junction to name it.",
            bg="#161c26", fg="#ffffff", font=("Arial", 9))
        self.lbl_info.pack(side=tk.LEFT, padx=15)

        canvas_w = min(self.img_w, 1200)
        canvas_h = min(self.img_h, 800)
        self.canvas = tk.Canvas(self.root, width=canvas_w, height=canvas_h, bg="#0f141c")
        self.canvas.pack()

        status_frame = tk.Frame(self.root, bg="#161c26")
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var = tk.StringVar()
        self.coord_var = tk.StringVar()
        tk.Label(status_frame, textvariable=self.status_var, bg="#161c26", fg="#00f5d4",
                 font=("Arial", 9)).pack(side=tk.LEFT, padx=10)
        tk.Label(status_frame, textvariable=self.coord_var, bg="#161c26", fg="#ffb703",
                 font=("Arial", 9)).pack(side=tk.RIGHT, padx=10)

        # Mouse bindings
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<ButtonPress-2>", self.on_pan_start)
        self.canvas.bind("<B2-Motion>", self.on_pan_drag)
        self.canvas.bind("<ButtonPress-3>", self.on_right_click)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<MouseWheel>", self.on_zoom)       # Windows / Mac
        self.canvas.bind("<Button-4>", self.on_zoom)         # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_zoom)         # Linux scroll down

        # Keyboard shortcuts
        self.root.bind("<Control-z>", self.undo)
        self.root.bind("<Control-s>", lambda e: self.save_json())
        self.root.bind("<Escape>", self.cancel_roundabout)

        self.redraw()

    # ---------------------------------------------------- coordinate math

    def canvas_to_image(self, cx, cy):
        return (cx - self.offset_x) / self.scale, (cy - self.offset_y) / self.scale

    def image_to_canvas(self, ix, iy):
        return ix * self.scale + self.offset_x, iy * self.scale + self.offset_y

    def find_nearby_node(self, x, y, exclude=None, radius=None):
        if radius is None:
            radius = self.snap_radius_canvas / self.scale
        closest, closest_dist = None, radius
        for name, data in self.graph.items():
            if name == exclude:
                continue
            d = math.hypot(data["x"] - x, data["y"] - y)
            if d <= closest_dist:
                closest, closest_dist = name, d
        return closest

    # ------------------------------------------------------------ drawing

    def redraw(self):
        self.canvas.delete("all")
        disp_w = max(1, int(self.img_w * self.scale))
        disp_h = max(1, int(self.img_h * self.scale))
        resized = self.raw_img.resize((disp_w, disp_h), RESAMPLE)
        self.tk_img = ImageTk.PhotoImage(resized)
        self.canvas.create_image(self.offset_x, self.offset_y, anchor=tk.NW, image=self.tk_img)

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
                self.canvas.create_line(x1, y1, x2, y2, fill="#00f5d4",
                                         width=max(1, int(3 * self.scale)), capstyle=tk.ROUND)

        radius = max(2, 4 * self.scale)
        show_labels = self.show_labels_var.get()
        for name, data in self.graph.items():
            x, y = self.image_to_canvas(data["x"], data["y"])
            if name.startswith("Ring"):
                color = "#ffb703"
            elif name.startswith("Junction_"):
                color = "#00f5d4"
            else:
                color = "#ff9f1c"  # named/tagged node (e.g. House_1, Gate)
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                     fill=color, outline="")
            if show_labels and self.scale > 0.6:
                self.canvas.create_text(x, y - radius - 8, text=name.split("_")[-1],
                                         fill="white", font=("Arial", 8))

        if self.roundabout_center is not None:
            cx, cy = self.image_to_canvas(*self.roundabout_center)
            self.canvas.create_oval(cx - 4, cy - 4, cx + 4, cy + 4, fill="#7209b7")

        self.status_var.set(f"Zoom: {int(self.scale * 100)}%  |  Nodes: {len(self.graph)}")

    # ------------------------------------------------------------- events

    def on_press(self, event):
        if self.roundabout_mode:
            self.handle_roundabout(event.x, event.y)
            return
        img_x, img_y = self.canvas_to_image(event.x, event.y)
        existing = self.find_nearby_node(img_x, img_y)
        if existing:
            self.add_node(img_x, img_y, existing_name=existing)
        else:
            self.add_node(img_x, img_y)

    def on_drag(self, event):
        if self.roundabout_mode or not self.current_segment_nodes:
            return
        img_x, img_y = self.canvas_to_image(event.x, event.y)
        last_node = self.current_segment_nodes[-1]
        lx, ly = self.graph[last_node]["x"], self.graph[last_node]["y"]
        if math.hypot(img_x - lx, img_y - ly) < self.min_drag_distance:
            return

        existing = self.find_nearby_node(img_x, img_y, exclude=last_node)
        if existing:
            self.add_node(img_x, img_y, existing_name=existing)
            self.finish_segment()  # road met an existing junction: end segment here
        else:
            self.add_node(img_x, img_y)

    def on_release(self, event):
        if not self.roundabout_mode:
            self.finish_segment()

    def on_right_click(self, event):
        img_x, img_y = self.canvas_to_image(event.x, event.y)
        target = self.find_nearby_node(img_x, img_y)
        if not target:
            return
        if not messagebox.askyesno("Delete Junction", f"Delete {target} and its connections?"):
            return
        for data in self.graph.values():
            if target in data["neighbors"]:
                data["neighbors"].remove(target)
        del self.graph[target]
        self.current_segment_nodes = [n for n in self.current_segment_nodes if n != target]
        self.action_log = [a for a in self.action_log if a["node"] != target]
        self.redraw()

    def on_double_click(self, event):
        img_x, img_y = self.canvas_to_image(event.x, event.y)
        target = self.find_nearby_node(img_x, img_y)
        if not target:
            return
        new_name = simpledialog.askstring(
            "Rename Junction",
            f"New name for '{target}' (e.g. Gate, House_1, Clubhouse):",
            initialvalue=target)
        if not new_name:
            return
        new_name = new_name.strip().replace(" ", "_")
        if not new_name or new_name == target:
            return
        if new_name in self.graph:
            messagebox.showerror("Name Taken", f"'{new_name}' already exists. Choose a different name.")
            return
        self.rename_node(target, new_name)
        self.redraw()

    def rename_node(self, old_name, new_name):
        data = self.graph.pop(old_name)
        self.graph[new_name] = data
        for node in self.graph.values():
            if old_name in node["neighbors"]:
                idx = node["neighbors"].index(old_name)
                node["neighbors"][idx] = new_name
        self.current_segment_nodes = [new_name if n == old_name else n for n in self.current_segment_nodes]
        for action in self.action_log:
            if action["node"] == old_name:
                action["node"] = new_name
            if action["prev"] == old_name:
                action["prev"] = new_name

    def on_mouse_move(self, event):
        img_x, img_y = self.canvas_to_image(event.x, event.y)
        self.coord_var.set(f"Image coords: ({int(img_x)}, {int(img_y)})")

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

    # -------------------------------------------------------------- graph

    def add_node(self, x, y, existing_name=None):
        if existing_name:
            node_name = existing_name
            is_new = False
        else:
            node_name = f"Junction_{self.node_count}"
            self.node_count += 1
            self.graph[node_name] = {"x": x, "y": y, "neighbors": []}
            is_new = True

        prev_node = self.current_segment_nodes[-1] if self.current_segment_nodes else None
        if prev_node and prev_node != node_name:
            if node_name not in self.graph[prev_node]["neighbors"]:
                self.graph[prev_node]["neighbors"].append(node_name)
            if prev_node not in self.graph[node_name]["neighbors"]:
                self.graph[node_name]["neighbors"].append(prev_node)

        self.current_segment_nodes.append(node_name)
        self.action_log.append({"node": node_name, "is_new": is_new, "prev": prev_node})
        self.redraw()
        return node_name

    def undo(self, event=None):
        if not self.action_log:
            return
        action = self.action_log.pop()
        node_name, prev, is_new = action["node"], action["prev"], action["is_new"]

        if prev:
            if node_name in self.graph.get(prev, {}).get("neighbors", []):
                self.graph[prev]["neighbors"].remove(node_name)
            if node_name in self.graph and prev in self.graph[node_name]["neighbors"]:
                self.graph[node_name]["neighbors"].remove(prev)

        if is_new and node_name in self.graph:
            del self.graph[node_name]

        if self.current_segment_nodes and self.current_segment_nodes[-1] == node_name:
            self.current_segment_nodes.pop()

        self.redraw()

    def finish_segment(self):
        if self.current_segment_nodes:
            print(f"--- Segment finished ({len(self.current_segment_nodes)} nodes) ---")
            self.current_segment_nodes = []

    # -------------------------------------------------------- roundabout

    def enable_roundabout_mode(self):
        self.roundabout_mode = True
        self.roundabout_center = None
        self.lbl_info.config(text="ROUNDABOUT MODE: click CENTER, then click OUTER EDGE. Esc to cancel.",
                              fg="#ffb703")

    def cancel_roundabout(self, event=None):
        self.roundabout_mode = False
        self.roundabout_center = None
        self.lbl_info.config(text="Cancelled. Back to freehand drag mode.", fg="#ffffff")
        self.redraw()

    def handle_roundabout(self, cx, cy):
        img_x, img_y = self.canvas_to_image(cx, cy)
        if self.roundabout_center is None:
            self.roundabout_center = (img_x, img_y)
            self.lbl_info.config(text="Center set! Click the outer edge of the roundabout.")
            self.redraw()
            return

        ccx, ccy = self.roundabout_center
        radius = math.hypot(img_x - ccx, img_y - ccy)
        ring_nodes = []
        num_points = 8
        for i in range(num_points):
            angle = (2 * math.pi / num_points) * i
            nx = ccx + radius * math.cos(angle)
            ny = ccy + radius * math.sin(angle)
            node_name = f"Ring_{self.node_count}"
            self.node_count += 1
            self.graph[node_name] = {"x": nx, "y": ny, "neighbors": []}
            ring_nodes.append(node_name)

        for i in range(num_points):
            curr, nxt = ring_nodes[i], ring_nodes[(i + 1) % num_points]
            self.graph[curr]["neighbors"].append(nxt)
            self.graph[nxt]["neighbors"].append(curr)

        self.roundabout_center = None
        self.roundabout_mode = False
        self.lbl_info.config(text="Roundabout created! Back to freehand drag mode.", fg="#ffffff")
        self.redraw()

    # --------------------------------------------------------- save/load

    def save_json(self):
        path = filedialog.asksaveasfilename(defaultextension=".json",
                                             filetypes=[("JSON files", "*.json")])
        if not path:
            return
        with open(path, "w") as f:
            json.dump(self.graph, f, indent=2)
        messagebox.showinfo("Saved", f"Graph saved to:\n{path}")

    def load_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return
        with open(path) as f:
            data = json.load(f)
        self.graph = data
        self.current_segment_nodes = []
        self.action_log = []
        max_id = 0
        for name in self.graph:
            try:
                max_id = max(max_id, int(name.split("_")[-1]))
            except ValueError:
                pass
        self.node_count = max_id + 1
        self.redraw()

    def clear_all(self):
        if not messagebox.askyesno("Clear All", "Erase the entire graph?"):
            return
        self.graph = {}
        self.current_segment_nodes = []
        self.action_log = []
        self.node_count = 1
        self.redraw()


if __name__ == "__main__":
    root = tk.Tk()
    default_path = "Screenshot (608).png"
    image_path = default_path
    if not os.path.exists(image_path):
        image_path = filedialog.askopenfilename(
            title="Select your subdivision map image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if not image_path:
            raise SystemExit("No image selected.")
    app = RoadDrawerTool(root, image_path)
    root.mainloop()
