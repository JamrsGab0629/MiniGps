import os
import math
import tkinter as tk
from PIL import Image, ImageTk

class SubdivisionMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Earth and Homes Subdivision - GPS Navigator")

        self.WIDTH = 1024
        self.HEIGHT = 630

        self.canvas = tk.Canvas(root, width=self.WIDTH, height=self.HEIGHT, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Load Background Image
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_name = "Screenshot (627).jpg"
        if not os.path.exists(os.path.join(script_dir, image_name)):
            image_name = "map.png"

        image_path = os.path.join(script_dir, image_name)

        try:
            self.raw_img = Image.open(image_path)
            self.raw_img = self.raw_img.resize((self.WIDTH, self.HEIGHT), Image.Resampling.LANCZOS)
            self.bg_map = ImageTk.PhotoImage(self.raw_img)
        except Exception as e:
            print(f"Error loading image '{image_path}': {e}")
            self.bg_map = None

        # --- CALIBRATED GRAPH DATA BASED ON YOUR SCREENSHOT ---
        self.nodes = {
            # Main Entrance & West Side Grid
            "J_Entrance": {"x": 55, "y": 480, "type": "road", "neighbors": ["J_West_Spine"]},
            "J_West_Spine": {"x": 195, "y": 380, "type": "road", "neighbors": ["J_Entrance", "J_Mid_Spine"]},
            
            # Central Spine & Landmark Intersections
            "J_Mid_Spine": {"x": 315, "y": 440, "type": "road", "neighbors": ["J_West_Spine", "Earth_and_Homes", "J_Coco_Turn"]},
            "J_Coco_Turn": {"x": 560, "y": 375, "type": "road", "neighbors": ["J_Mid_Spine", "Coco_House", "Claros_Residence", "J_East_Turn"]},
            
            # East & Loop Intersections
            "J_East_Turn": {"x": 750, "y": 340, "type": "road", "neighbors": ["J_Coco_Turn", "Tats_San_Juan", "Dolindo_Residence"]},
            "J_Loop_South": {"x": 750, "y": 510, "type": "road", "neighbors": ["J_East_Turn", "Dolindo_Residence"]},

            # --- PINPOINTED HOUSES & LANDMARKS ---
            "Earth_and_Homes": {"x": 325, "y": 490, "type": "house", "neighbors": ["J_Mid_Spine"]},
            "Claros_Residence": {"x": 585, "y": 260, "type": "house", "neighbors": ["J_Coco_Turn"]},
            "Coco_House": {"x": 575, "y": 380, "type": "house", "neighbors": ["J_Coco_Turn"]},
            "Tats_San_Juan": {"x": 760, "y": 340, "type": "house", "neighbors": ["J_East_Turn"]},
            "Dolindo_Residence": {"x": 755, "y": 510, "type": "house", "neighbors": ["J_East_Turn", "J_Loop_South"]}
        }

        self.canvas.bind("<Button-1>", self.on_map_click)
        self.draw_base_map()

        # Test route: Entrance -> Earth and Homes -> Coco House -> Dolindo Residence
        demo_path = ["J_Entrance", "J_West_Spine", "J_Mid_Spine", "Earth_and_Homes", "J_Mid_Spine", "J_Coco_Turn", "Coco_House", "J_Coco_Turn", "J_East_Turn", "Dolindo_Residence"]
        self.draw_route(demo_path, color="#00f5d4")

    def on_map_click(self, event):
        print(f"Clicked Pixel Coordinates: ({event.x}, {event.y})")

    def draw_base_map(self):
        self.canvas.delete("all")
        if self.bg_map:
            self.canvas.create_image(0, 0, image=self.bg_map, anchor="nw")

        # Draw Roads
        drawn_edges = set()
        for u, data in self.nodes.items():
            for v in data["neighbors"]:
                if (v, u) not in drawn_edges and v in self.nodes:
                    x1, y1 = data["x"], data["y"]
                    x2, y2 = self.nodes[v]["x"], self.nodes[v]["y"]
                    self.canvas.create_line(x1, y1, x2, y2, fill="#00b4d8", width=3, dash=(3, 3))
                    drawn_edges.add((u, v))

        # Draw Nodes
        for node_name, data in self.nodes.items():
            x, y = data["x"], data["y"]
            if data.get("type") == "house":
                size = 5
                self.canvas.create_rectangle(x - size, y - size, x + size, y + size, fill="#ffb703", outline="black")
                self.canvas.create_text(x, y - 12, text=node_name.replace("_", " "), fill="white", font=("Arial", 9, "bold"))
            else:
                self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="#03045e", outline="#00f5d4", width=1.5)

    def draw_route(self, path, color="#00f5d4", width=5):
        if not path or len(path) < 2:
            return
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            if u in self.nodes and v in self.nodes:
                x1, y1 = self.nodes[u]["x"], self.nodes[u]["y"]
                x2, y2 = self.nodes[v]["x"], self.nodes[v]["y"]
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, capstyle=tk.ROUND)

if __name__ == "__main__":
    root = tk.Tk()
    app = SubdivisionMapApp(root)
    root.mainloop()