# =====================================================================
# MAP GEOMETRY & ROAD NETWORK DATA (Earth and Homes Subdivision)
#
# Pure data module -- no logic here. If you need to add/move a junction,
# house, or landmark, this is the only file you should need to touch.
# =====================================================================

JUNCTION_GRAPH = {
    # === ENTRANCE GATE ===
    "Entrance_Gate_J1": {"x": 131, "y": 86, "neighbors": ["Junction_2"]},
    "Junction_2": {"x": 191, "y": 188, "neighbors": ["Entrance_Gate_J1", "Junction_3"]},

    # West Grid Row 1
    "Junction_3": {"x": 144, "y": 205, "neighbors": ["Junction_2", "Junction_4", "Junction_9"]},
    "Junction_4": {"x": 99,  "y": 232, "neighbors": ["Junction_3", "Junction_5", "Junction_8"]},
    "Junction_5": {"x": 60,  "y": 265, "neighbors": ["Junction_4", "Junction_6"]},

    # West Grid Row 2
    "Junction_6": {"x": 112, "y": 451, "neighbors": ["Junction_5", "Junction_7", "Junction_10"]},
    "Junction_7": {"x": 182, "y": 451, "neighbors": ["Junction_6", "Junction_8", "Junction_11"]},
    "Junction_8": {"x": 230, "y": 430, "neighbors": ["Junction_7", "Junction_4", "Junction_9", "Junction_12"]},
    "Junction_9": {"x": 284, "y": 392, "neighbors": ["Junction_8", "Junction_3", "Junction_13"]},

    # West Grid Row 3
    "Junction_10": {"x": 160, "y": 570, "neighbors": ["Junction_6", "Junction_11"]},
    "Junction_11": {"x": 218, "y": 562, "neighbors": ["Junction_10", "Junction_7", "Junction_12"]},
    "Junction_12": {"x": 252, "y": 562, "neighbors": ["Junction_11", "Junction_8", "Junction_13", "Junction_15"]},
    "Junction_13": {"x": 334, "y": 526, "neighbors": ["Junction_12", "Junction_9", "Junction_14"]},

    # Mid-subdivision Transition Junctions
    "Junction_14": {"x": 363, "y": 560, "neighbors": ["Junction_13", "Junction_17"]},
    "Junction_15": {"x": 263, "y": 569, "neighbors": ["Junction_12", "Junction_16"]},

    # Western Bends & Central Spine
    "Junction_16": {"x": 349, "y": 620, "neighbors": ["Junction_15", "Junction_18"]},
    "Junction_17": {"x": 357, "y": 568, "neighbors": ["Junction_14", "Junction_18", "Junction_19"]},
    "Junction_18": {"x": 352, "y": 607, "neighbors": ["Junction_16", "Junction_17", "Junction_20"]},

    # Central Main Avenue
    "Junction_19": {"x": 419, "y": 560, "neighbors": ["Junction_17", "Junction_21"]},
    "Junction_21": {"x": 422, "y": 574, "neighbors": ["Junction_19", "Junction_25"]},
    "Junction_25": {"x": 649, "y": 474, "neighbors": ["Junction_21", "Junction_23"]},
    "Junction_23": {"x": 642, "y": 466, "neighbors": ["Junction_25", "Junction_31"]},

    "Junction_20": {"x": 416, "y": 628, "neighbors": ["Junction_18", "Junction_22"]},
    "Junction_22": {"x": 424, "y": 618, "neighbors": ["Junction_20", "Junction_26"]},
    "Junction_26": {"x": 725, "y": 539, "neighbors": ["Junction_22", "Junction_24"]},
    "Junction_24": {"x": 728, "y": 553, "neighbors": ["Junction_26", "Junction_28"]},

    # === CURVED EASTERN SECTION ===
    "Junction_28": {"x": 816, "y": 544, "neighbors": ["Junction_24", "Junction_30", "Junction_35"]},
    "Junction_30": {"x": 824, "y": 531, "neighbors": ["Junction_28", "Junction_29"]},
    "Junction_29": {"x": 838, "y": 484, "neighbors": ["Junction_30", "Junction_27"]},
    "Junction_27": {"x": 840, "y": 476, "neighbors": ["Junction_29", "Junction_31"]},

    "Junction_31": {"x": 900, "y": 480, "neighbors": ["Junction_23", "Junction_27", "Curve_31_32_1", "Junction_35"]},

    # Top Curved Cul-de-sac Loop
    "Curve_31_32_1": {"x": 950, "y": 472, "neighbors": ["Junction_31", "Curve_31_32_2"]},
    "Curve_31_32_2": {"x": 1000, "y": 475, "neighbors": ["Curve_31_32_1", "Junction_32"]},
    "Junction_32":    {"x": 1050, "y": 490, "neighbors": ["Curve_31_32_2"]},

    # Mid Vertical Connector
    "Junction_35": {"x": 900, "y": 550, "neighbors": ["Junction_31", "Junction_28", "Curve_35_34_1", "Curve_35_37_1"]},

    # Center Curved Connector
    "Curve_35_34_1": {"x": 965, "y": 542, "neighbors": ["Junction_35", "Curve_35_34_2"]},
    "Curve_35_34_2": {"x": 1015, "y": 548, "neighbors": ["Curve_35_34_1", "Junction_34"]},
    "Junction_34":    {"x": 1060, "y": 565, "neighbors": ["Curve_35_34_2", "Curve_34_36_1"]},

    # Right Curved Bend
    "Curve_34_36_1": {"x": 1070, "y": 615, "neighbors": ["Junction_34", "Junction_36"]},
    "Junction_36":    {"x": 1045, "y": 665, "neighbors": ["Curve_34_36_1", "Curve_36_37_1"]},

    # Bottom Curved Loop
    "Curve_36_37_1": {"x": 975, "y": 675, "neighbors": ["Junction_36", "Junction_37"]},
    "Junction_37":    {"x": 905, "y": 655, "neighbors": ["Curve_36_37_1", "Curve_35_37_1"]},
    "Curve_35_37_1": {"x": 895, "y": 600, "neighbors": ["Junction_37", "Junction_35"]}
}

# Explicitly positioned purple landmarks to prevent label collision
CUSTOM_PURPLE_LANDMARKS = {
    "Coco House": {"x": 515, "y": 515, "align": "above", "text_offset": (0, -10)},
    "Claros Residence": {"x": 590, "y": 470, "align": "above", "text_offset": (-20, -10)},
    "Tats San Juan": {"x": 670, "y": 450, "align": "below", "text_offset": (20, 10)},
    "Dolindo Residence": {"x": 480, "y": 620, "align": "below", "text_offset": (0, 10)},
    "Block 1 Lot A45": {"x": 1030, "y": 480, "align": "above", "text_offset": (0, -10)}
}

HOUSES = {
    "My House": {"x": 210, "y": 180},
    "Guard House": {"x": 230, "y": 180},
    "Gazebo": {"x": 240, "y": 580},
    "Community Center": {"x": 370, "y": 530},

    "House 4": {"x": 210, "y": 410},

    "House 6": {"x": 90,  "y": 450},
    "House 7": {"x": 80,  "y": 220},
    "House 8": {"x": 210, "y": 450},
    "House 9": {"x": 300, "y": 380},
    "House 10": {"x": 250, "y": 410},

    "House 13": {"x": 100, "y": 500},
    "House 14": {"x": 170, "y": 430},
    "House 15": {"x": 200, "y": 580},

    "House 18": {"x": 330, "y": 640},
    "House 19": {"x": 330, "y": 600},
    "House 20": {"x": 430, "y": 650},
    "House 21": {"x": 440, "y": 600},
    "House 22": {"x": 630, "y": 520},
    "House 23": {"x": 660, "y": 500},
    "House 24": {"x": 740, "y": 530},

    "House 26": {"x": 800, "y": 520},
    "House 27": {"x": 820, "y": 460},
    "House 28": {"x": 860, "y": 460},

    "House 30": {"x": 920, "y": 460},

    "House 34": {"x": 1030, "y": 540},
    "House 35": {"x": 1080, "y": 580},
    "House 36": {"x": 1060, "y": 680},
    "House 37": {"x": 920, "y": 670},
    "House 38": {"x": 980, "y": 690},
    "House 39": {"x": 880, "y": 620}
}

METERS_PER_PIXEL = 0.65
