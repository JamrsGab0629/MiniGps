# 🧭 Earth and Homes Subdivision Navigation System

## Overview

The **Earth and Homes Subdivision Navigation System** is a desktop-based interactive map editor and GPS navigation application developed in **Python** using the **Tkinter** graphical user interface library. The system is designed to help users model, edit, and navigate within the Earth and Homes Subdivision by computing the shortest and alternative routes between selected locations.

The application models the subdivision as an **unweighted graph**, where intersections are represented as junctions and roads are represented as edges connecting those junctions. It uses **Breadth-First Search (BFS)** to determine the shortest path and generates an alternative route by temporarily blocking each edge of the shortest path and running BFS again.

In addition to route computation, the application provides an interactive canvas to dynamically add, edit, drag, connect, or delete houses and road junctions, automatically saving all map configurations locally.

---

# Features

* 🗺 **Interactive Map & Editor:** Real-time visual editor to create, connect, move, and remove houses and road junctions.
* 🏠 **House & Landmark Selection:** Choose any registered house as a start or target location using dynamic drop-down menus.
* 📍 **Smart Node Snapping:** Automatically snaps houses and landmarks to their nearest road junction.
* 🚶 **Travel Time & Distance Estimation:** Displays total distance in meters along with real-time estimated walking and driving times.
* 🟢 **Primary Route Visualization:** Animates and highlights the shortest path in teal.
* 🟡 **Alternative Route Generation:** Highlights a viable second-shortest route in yellow when available.
* 💾 **Auto-Persistence:** Automatically updates and saves map layout changes to a local data file (`map_data.txt`).

---

# How to Use the Map Editor & Navigation

### 🛠️ Mode Selection
* **Toggle Edit Mode:** Click the **`🛠️ Edit Mode: ON / OFF`** button in the top navigation bar to switch between editing map structures and locked navigation view.

### ➕ Adding Map Elements (Edit Mode ON)
* **Add a House:** **Double-click** anywhere on the canvas. 
  * A prompt will ask for the house name.
  * You will be prompted to select if the house is a special designation (**Purple**) or standard (**Coral**).
* **Add a Junction:** **Shift + Double-click** anywhere on the canvas. A new junction node (`Junction_N`) will be created at that point.

### 🔗 Connecting Road Junctions (Edit Mode ON)
1. **Right-click** on the first junction (it will highlight in yellow/amber).
2. **Right-click** on a second junction to draw a road between them.
3. *Note: Right-clicking an existing connection between two junctions will remove that road.*

### ✋ Dragging & Moving Nodes (Edit Mode ON)
* **Click and drag** any house or junction node across the canvas to reposition it. Road connections and nearest-junction snaps will re-calculate dynamically upon release.

### 🗑️ Deleting Elements & Clearing
* **Delete a Single Node:** Click on any house or junction to select it (highlighted in red), then press **`Delete`** or **`Backspace`** on your keyboard.
* **Clear Entire Map:** Click the **`🗑️ Clear All`** button in the control panel to erase all houses, junctions, and roads to start fresh.

### 🎯 Computing & Animating Routes
1. Choose a **Start** house and a **Target** house from the top drop-down menus.
2. Click **`🎯 Route`**.
3. The system will calculate path metrics, display the information box in the upper right corner, and sequentially animate the primary and alternative paths step-by-step.

---

# Technologies Used

* **Python 3.x**
* **Tkinter** (GUI and Canvas Animation)
* **Collections** (`deque` for queue-based BFS)
* **Math Library** (Euclidean distance calculations)
* **JSON / File I/O** (Data persistence)

---

# Algorithms & Mathematical Principles Used

## 1. Breadth-First Search (BFS)
Breadth-First Search is used to compute the shortest route between two locations. Because the subdivision road network is represented as an **unweighted graph**, BFS guarantees the shortest path in terms of the fewest road segment hops.

### Process
1. Start from the selected location.
2. Visit all neighboring junctions level-by-level.
3. Skip nodes designated as other houses (house-bypass safeguard) unless it is the explicit target.
4. Stop once the destination is reached.
5. Reconstruct the path using parent node tracking.

## 2. Alternative Route Generation
To generate a secondary route, the system executes an edge-blocking strategy:
1. Compute the primary shortest path using BFS.
2. Iterate through each edge of the primary path, temporarily blocking one edge at a time.
3. Re-run BFS for each blocked-edge variation.
4. Collect all valid secondary paths and sort them by total node hops (`key=len`).
5. Select the shortest valid alternative that meets reasonable distance constraints relative to the primary path.

## 3. Pythagorean Theorem
After a path is computed, the Euclidean distance between every consecutive coordinate pair $(x_1, y_1)$ and $(x_2, y_2)$ is calculated:

$$d = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$$

The segment distances are summed to calculate the total path length in pixels.

## 4. Pixel-to-Meter Conversion
Pixel lengths are converted into real-world meters using a calibrated scaling factor:

$$\text{Distance (meters)} = \text{Distance (pixels)} \times 0.65$$

## 5. Travel Time Estimation
Travel times are estimated using speed assumptions tailored to a subdivision setting:
* **Walking Speed:** $80 \text{ meters/min} \approx 4.8 \text{ km/h}$
* **Driving Speed:** $333 \text{ meters/min} \approx 20 \text{ km/h}$

$$\text{Time (minutes)} = \frac{\text{Distance (meters)}}{\text{Speed (meters/min)}}$$

---

# Project Structure

```text
gps_navigation/
│
├── main.py          # Application entry point & Tkinter UI / canvas renderer
├── config.py        # Speed constants, pixel scale, & delay configurations
├── map_data.py      # MapGraph state manager & node relationship graph
├── geometry.py      # Euclidean distance math & node click proximity checks
├── pathfinding.py   # BFS algorithm & alternate route generation logic
├── storage.py       # Local file storage (JSON/map_data.txt loader and saver)
└── map_data.txt     # Saved JSON configuration for houses and junctions