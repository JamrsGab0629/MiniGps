# =====================================================================
# GEOMETRY / MAP ASSEMBLY
#
# Turns the raw JUNCTION_GRAPH + house/landmark dicts from map_data.py
# into one combined, routable graph (SUBDIVISION_MAP) by projecting
# each house/landmark onto its nearest road edge and wiring it in.
# =====================================================================
import math

from map_data import JUNCTION_GRAPH, CUSTOM_PURPLE_LANDMARKS, HOUSES


def point_to_segment_projection(px, py, ax, ay, bx, by):
    abx = bx - ax
    aby = by - ay
    ab_len_sq = abx**2 + aby**2
    if ab_len_sq == 0:
        return ax, ay, 0, 0
    t = max(0, min(1, ((px - ax) * abx + (py - ay) * aby) / ab_len_sq))
    proj_x = ax + t * abx
    proj_y = ay + t * aby
    return proj_x, proj_y, abx, aby


def snap_houses_to_road_edges(houses_dict, junctions_dict, offset_dist=10):
    edges = set()
    for u, u_data in junctions_dict.items():
        for v in u_data["neighbors"]:
            if v in junctions_dict:
                edge = tuple(sorted((u, v)))
                edges.add(edge)

    snapped = {}
    for name, h_data in houses_dict.items():
        hx, hy = h_data["x"], h_data["y"]

        best_dist = float("inf")
        best_snapped_pos = (hx, hy)
        best_junction = None

        for u, v in edges:
            ax, ay = junctions_dict[u]["x"], junctions_dict[u]["y"]
            bx, by = junctions_dict[v]["x"], junctions_dict[v]["y"]

            proj_x, proj_y, dx, dy = point_to_segment_projection(hx, hy, ax, ay, bx, by)
            dist = math.hypot(hx - proj_x, hy - proj_y)

            if dist < best_dist:
                best_dist = dist

                norm_len = math.hypot(dx, dy)
                if norm_len > 0:
                    nx, ny = -dy / norm_len, dx / norm_len
                    dot = (hx - proj_x) * nx + (hy - proj_y) * ny
                    if dot < 0:
                        nx, ny = -nx, -ny
                    offset_x = proj_x + nx * offset_dist
                    offset_y = proj_y + ny * offset_dist
                else:
                    offset_x, offset_y = proj_x, proj_y

                best_snapped_pos = (int(offset_x), int(offset_y))
                dist_u = math.hypot(proj_x - ax, proj_y - ay)
                dist_v = math.hypot(proj_x - bx, proj_y - by)
                best_junction = u if dist_u < dist_v else v

        snapped[name] = {
            "x": best_snapped_pos[0],
            "y": best_snapped_pos[1],
            "junction": best_junction
        }
    return snapped


def assemble_full_map():
    snapped_houses = snap_houses_to_road_edges(HOUSES, JUNCTION_GRAPH, offset_dist=12)
    snapped_purple = snap_houses_to_road_edges(CUSTOM_PURPLE_LANDMARKS, JUNCTION_GRAPH, offset_dist=8)

    full_map = {node: dict(data) for node, data in JUNCTION_GRAPH.items()}

    for house_name, h_data in snapped_houses.items():
        hx, hy = h_data["x"], h_data["y"]
        target_j = h_data["junction"]
        full_map[house_name] = {"x": hx, "y": hy, "neighbors": [target_j]}
        full_map[target_j]["neighbors"].append(house_name)

    for p_name, p_data in snapped_purple.items():
        px, py = p_data["x"], p_data["y"]
        target_j = p_data["junction"]
        full_map[p_name] = {"x": px, "y": py, "neighbors": [target_j]}
        full_map[target_j]["neighbors"].append(p_name)

    return full_map



SUBDIVISION_MAP = assemble_full_map()
