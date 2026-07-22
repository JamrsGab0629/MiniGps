import tkinter as tk
from PIL import Image, ImageTk
import os

# Automatically finds the folder where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(SCRIPT_DIR, "map.png")

class MapBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Coordinate Mapper (Houses & Junctions)")

        # Load background layout image
        try:
            self.bg_image = Image.open(IMAGE_PATH)
            self.tk_image = ImageTk.PhotoImage(self.bg_image)
            width, height = self.bg_image.size
        except Exception as e:
            print(f"Error loading image '{IMAGE_PATH}': {e}")
            width, height = 1000, 700
            self.tk_image = None

        # Control Panel
        control_frame = tk.Frame(root, padx=10, pady=10, bg="#161c26")
        control_frame.pack(side=tk.TOP, fill=tk.X)

        self.mode = "house"  # Modes: 'house' or 'junction'
        self.house_count = 1
        self.junction_count = 1

        # Buttons to toggle between placing Houses or Junctions
        self.btn_house = tk.Button(
            control_frame, 
            text="🏠 Place Houses", 
            command=self.set_mode_house, 
            bg="#00b4d8", fg="white", font=("Arial", 9, "bold"), relief=tk.FLAT, padx=10, pady=4
        )
        self.btn_house.pack(side=tk.LEFT, padx=5)

        self.btn_junction = tk.Button(
            control_frame, 
            text="🔴 Place Junctions", 
            command=self.set_mode_junction, 
            bg="#242e3e", fg="white", font=("Arial", 9, "bold"), relief=tk.FLAT, padx=10, pady=4
        )
        self.btn_junction.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(
            control_frame, 
            text="Active Mode: Placing HOUSES (Click canvas to record coordinates)", 
            bg="#161c26", fg="#90e0ef", font=("Arial", 9, "bold")
        )
        self.status_label.pack(side=tk.LEFT, padx=15)

        # Main Canvas
        self.canvas = tk.Canvas(root, width=width, height=height, bg="#0f141c")
        self.canvas.pack()

        if self.tk_image:
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        # Canvas Click Listener
        self.canvas.bind("<Button-1>", self.record_coordinate)

        print("==========================================================")
        print(" CLICK ON YOUR MAP TO GENERATE PYTHON DICTIONARY CODE ")
        print("==========================================================\n")

    def set_mode_house(self):
        self.mode = "house"
        self.btn_house.config(bg="#00b4d8")
        self.btn_junction.config(bg="#242e3e")
        self.status_label.config(text="Active Mode: Placing HOUSES")

    def set_mode_junction(self):
        self.mode = "junction"
        self.btn_junction.config(bg="#ef233c")
        self.btn_house.config(bg="#242e3e")
        self.status_label.config(text="Active Mode: Placing JUNCTIONS")

    def record_coordinate(self, event):
        x, y = event.x, event.y

        if self.mode == "house":
            node_name = f"House {self.house_count}"
            color = "#00b4d8"  # Teal/Blue for houses
            self.house_count += 1
        else:
            node_name = f"Junction_{self.junction_count}"
            color = "#ef233c"  # Red for junctions
            self.junction_count += 1

        # Visual marker on canvas
        self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=color, outline="white", width=1.5)
        self.canvas.create_text(x, y - 12, text=node_name, fill=color, font=("Arial", 8, "bold"))

        # Pre-formatted string printed to terminal
        print(f'    "{node_name}": {{"x": {x}, "y": {y}, "neighbors": []}},')


if __name__ == "__main__":
    root = tk.Tk()
    app = MapBuilder(root)
    root.mainloop()