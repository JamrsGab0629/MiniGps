# 🧭 Earth and Homes Subdivision Navigation System

## Overview

The **Earth and Homes Subdivision Navigation System** is a desktop-based GPS navigation application developed in **Python** using the **Tkinter** graphical user interface library. The system is designed to help users navigate within the Earth and Homes Subdivision by computing the shortest and an alternative route between two selected locations.

The application models the subdivision as an **unweighted graph**, where intersections are represented as junctions and roads are represented as edges connecting those junctions. It uses **Breadth-First Search (BFS)** to determine the shortest path and generates an alternative route by temporarily blocking each edge of the shortest path and running BFS again.

In addition to route computation, the application estimates the travel distance using the **Pythagorean Theorem**, converts pixel distances into meters through a calibrated conversion factor, and estimates walking and driving travel times.

---

# Features

* 🗺 Interactive subdivision map
* 🏠 Select any available landmark or house as the starting point
* 📍 Select any available destination
* 🚶 Displays estimated walking time
* 🚗 Displays estimated driving time
* 📏 Displays total travel distance in meters
* 🟢 Highlights the shortest route
* 🟡 Highlights an alternative route when available
* 📌 Automatically snaps landmarks and houses to the nearest road

---

# Technologies Used

* Python 3.x
* Tkinter (GUI)
* Collections (Deque)
* Math Library

---

# Algorithms Used

## 1. Breadth-First Search (BFS)

Breadth-First Search is used to compute the shortest route between two locations.

Because the subdivision road network is represented as an **unweighted graph**, BFS guarantees the shortest path in terms of the fewest road segments.

### Process

1. Start from the selected location.
2. Visit all neighboring junctions.
3. Continue exploring level by level.
4. Stop once the destination is reached.
5. Reconstruct the path using parent nodes.

---

## 2. Alternative Route Generation

To generate a second route, the program performs the following steps:

1. Compute the shortest path using BFS.
2. Temporarily block one edge of that shortest path.
3. Execute BFS again.
4. Store the newly generated route.
5. Repeat the process for every edge in the original shortest path.
6. Compare all generated routes.
7. Select the shortest valid alternative.

This allows the navigation system to suggest another possible route whenever one exists.

---

## 3. Pythagorean Theorem

After the shortest path is computed, the distance between every consecutive node is calculated using the Pythagorean Theorem.

Formula:

d = √((x₂ − x₁)² + (y₂ − y₁)²)

The distances of all road segments are added together to obtain the total path length in pixels.

---

## 4. Pixel-to-Meter Conversion

The application converts pixel measurements into real-world distance using a calibrated conversion factor.

```
1 Pixel = 0.65 meters
```

Formula:

Distance (meters) = Distance (pixels) × 0.65

---

## 5. Travel Time Estimation

Travel time is estimated using average movement speeds.

Walking Speed

```
4.5 km/h
```

Driving Speed

```
20 km/h
```

Formula

```
Time = Distance ÷ Speed
```

The resulting travel time is displayed in minutes.

---

# Project Structure

```
gps_navigation/
│
├── main.py
├── config.py
├── map_data.py
├── geometry.py
├── pathfinding.py
├── ui.py

```

### main.py

Starts the application.

### map_data.py

Contains all map data including:

* Junctions
* Houses
* Landmarks
* Road connections

### geometry.py

Contains all mathematical computations including:

* Pythagorean distance calculation
* Point projection
* House snapping
* Pixel-to-meter conversion

### pathfinding.py

Contains the navigation algorithms:

* Breadth-First Search (BFS)
* Alternative route generation

### ui.py

Responsible for:

* Graphical User Interface
* Drawing roads
* Drawing landmarks
* Displaying routes
* User interactions


---

# How to Run

1. Install Python 3.x.
2. Place all project files in one folder.
3. Open a terminal inside the project folder.
4. Run:

```
python main.py
```

---

# Future Improvements

* Implement A* Search Algorithm
* Add Dijkstra's Algorithm
* Real-time traffic simulation
* Multiple route suggestions
* Dynamic speed limits
* Mobile application version
* Database integration
* GPS location tracking

---

# Author

Developed by **James Gabriel Santos**

Bachelor of Science in Computer Science

---

# License

This projec/activity was developed for academic purposes as part of a Computer Science course. It may be modified and extended for educational and research purposes.
