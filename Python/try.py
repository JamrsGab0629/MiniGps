import tkinter as tk
from PIL import Image, ImageTk
import os

# This automatically finds the folder where try.py is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# If map.png is inside the 'Python' folder next to try.py:
IMAGE_PATH = os.path.join(SCRIPT_DIR, "map.png")

# (Alternative) If map.png is out in the main MINIGPS folder, use this instead:
# IMAGE_PATH = os.path.join(SCRIPT_DIR, "..", "map.png")

class MapBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Coordinate Mapper")
        
        # Load the original hand-drawn image
        self.bg_image = Image.open(IMAGE_PATH)
        self.tk_image = ImageTk.PhotoImage(self.bg_image)
        
        # Match canvas size perfectly to your image dimensions
        width, height = self.bg_image.size
        self.canvas = tk.Canvas(root, width=width, height=height)
        self.canvas.pack()
        
        # Draw the layout image onto the canvas background
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        
        # Track node click counts
        self.node_count = 1
        
        # Bind the left mouse click event
        self.canvas.bind("<Button-1>", self.record_coordinate)
        print("--- CLICK ON YOUR INTERSECTIONS IN ORDER ---")

    def record_coordinate(self, event):
        x, y = event.x, event.y
        node_name = f"Junction_{self.node_count}"
        
        # Visual confirmation: Place a red circle where you clicked
        self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="red", outline="white")
        self.canvas.create_text(x, y-12, text=node_name, fill="red", font=("Arial", 9, "bold"))
        
        # Print a perfectly pre-formatted Python line to your console terminal
        print(f'    "{node_name}": {{"x": {x}, "y": {y}, "neighbors": []}},')
        
        self.node_count += 1

if __name__ == "__main__":
    root = tk.Tk()
    app = MapBuilder(root)
    root.mainloop()