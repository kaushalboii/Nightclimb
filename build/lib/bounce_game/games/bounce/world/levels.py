#!/usr/bin/env python3
"""Level definitions for BOUNCE - 12 levels matching original Nokia progression."""

LEVELS = [
    # Level 1: Welcome Back - Tutorial
    {
        "name": "Welcome Back",
        "spawn": (8, 20),
        "platforms": [
            (0, 22, 80, 2),      # Ground
            (10, 17, 12, 1),     # Step 1
            (25, 14, 10, 1),     # Step 2
            (40, 11, 12, 1),     # Step 3
            (55, 8, 10, 1),      # Step 4
            (70, 5, 8, 1),       # Top platform
        ],
        "moving_platforms": [],
        "spikes": [],
        "stars": [(12, 16), (27, 13), (42, 10), (57, 7), (72, 4), (35, 10), (50, 6)],
        "exit": (72, 2),
        "blocks": [],
        "water": -1,
    },

    # Level 2: Sharp Edges - Ground Spikes
    {
        "name": "Sharp Edges",
        "spawn": (5, 20),
        "platforms": [
            (0, 22, 80, 2),
            (15, 18, 15, 1),
            (35, 15, 10, 1),
            (50, 12, 15, 1),
            (70, 8, 8, 1),
        ],
        "moving_platforms": [],
        "spikes": [
            (15, 21, 5, 1, 'up'),    # Spikes on ground
            (20, 21, 3, 1, 'up'),
            (40, 21, 8, 1, 'up'),
            (60, 21, 6, 1, 'up'),
        ],
        "stars": [(17, 17), (37, 14), (52, 11), (72, 7), (8, 19)],
        "exit": (72, 5),
        "blocks": [],
        "water": -1,
    },

    # Level 3: Ride the Wave - Moving Platforms
    {
        "name": "Ride the Wave",
        "spawn": (5, 20),
        "platforms": [
            (0, 22, 80, 2),
            (0, 15, 10, 1),
            (30, 10, 10, 1),
            (60, 6, 15, 1),
        ],
        "moving_platforms": [
            (10, 18, 6, 1, 20, 1.5, False),   # Horizontal mover
            (35, 13, 6, 1, 15, 2.0, False),
            (50, 10, 6, 1, 20, 1.8, False),
        ],
        "spikes": [
            (20, 21, 4, 1, 'up'),
            (45, 21, 4, 1, 'up'),
        ],
        "stars": [(12, 17), (32, 12), (52, 9), (65, 5), (72, 3), (25, 14), (55, 8)],
        "exit": (65, 3),
        "blocks": [],
        "water": -1,
    },

    # Level 4: Break Through - Breakable Blocks
    {
        "name": "Break Through",
        "spawn": (5, 20),
        "platforms": [
            (0, 22, 80, 2),
            (15, 17, 8, 1),
            (30, 13, 8, 1),
            (50, 9, 8, 1),
            (70, 5, 8, 1),
        ],
        "moving_platforms": [],
        "spikes": [],
        "stars": [(17, 16), (32, 12), (52, 8), (72, 4), (5, 19)],
        "exit": (72, 2),
        "blocks": [
            (20, 16, 2, 2, 2),   # Breakable wall
            (23, 16, 2, 2, 1),
            (40, 12, 3, 2, 3),   # Thick wall
            (60, 8, 2, 3, 2),
        ],
        "water": -1,
    },

    # Level 5: Deep Waters - Water Buoyancy
    {
        "name": "Deep Waters",
        "spawn": (5, 10),
        "platforms": [
            (0, 22, 80, 2),
            (10, 16, 8, 1),
            (30, 12, 8, 1),
            (50, 8, 8, 1),
            (70, 4, 8, 1),
        ],
        "moving_platforms": [],
        "spikes": [
            (15, 21, 5, 1, 'up'),
            (40, 21, 5, 1, 'up'),
        ],
        "stars": [(12, 15), (32, 11), (52, 7), (72, 3), (25, 13)],
        "exit": (72, 1),
        "blocks": [],
        "water": 18,  # Water starts at y=18
    },

    # Level 6: Skyward - Vertical Climbing
    {
        "name": "Skyward",
        "spawn": (40, 20),
        "platforms": [
            (0, 22, 80, 2),
            (35, 19, 10, 1),
            (25, 16, 8, 1),
            (45, 13, 8, 1),
            (30, 10, 6, 1),
            (50, 7, 6, 1),
            (35, 4, 10, 1),
        ],
        "moving_platforms": [
            (10, 15, 6, 1, 15, 1.5, True),   # Vertical mover
            (65, 10, 6, 1, 12, 2.0, True),
        ],
        "spikes": [
            (20, 21, 6, 1, 'up'),
            (55, 21, 6, 1, 'up'),
        ],
        "stars": [(37, 18), (27, 15), (47, 12), (32, 9), (52, 6), (37, 3), (15, 14)],
        "exit": (37, 1),
        "blocks": [],
        "water": -1,
    },

    # Level 7: Thread the Needle - Precision Platforming
    {
        "name": "Thread the Needle",
        "spawn": (5, 20),
        "platforms": [
            (0, 22, 80, 2),
            # Thin path
            (5, 19, 2, 1), (9, 18, 2, 1), (13, 17, 2, 1), (17, 16, 2, 1),
            (21, 15, 2, 1), (25, 14, 2, 1), (29, 13, 2, 1), (33, 12, 2, 1),
            (37, 11, 2, 1), (41, 10, 2, 1), (45, 9, 2, 1), (49, 8, 2, 1),
            (53, 7, 2, 1), (57, 6, 2, 1), (61, 5, 2, 1), (65, 4, 2, 1),
        ],
        "moving_platforms": [],
        "spikes": [
            (0, 21, 80, 1, 'up'),  # Floor spikes!
            (3, 18, 1, 2, 'right'),
            (7, 17, 1, 2, 'right'),
            (11, 16, 1, 2, 'right'),
            (15, 15, 1, 2, 'right'),
            (19, 14, 1, 2, 'right'),
            (23, 13, 1, 2, 'right'),
            (27, 12, 1, 2, 'right'),
            (31, 11, 1, 2, 'right'),
            (35, 10, 1, 2, 'right'),
            (39, 9, 1, 2, 'right'),
            (43, 8, 1, 2, 'right'),
            (47, 7, 1, 2, 'right'),
            (51, 6, 1, 2, 'right'),
            (55, 5, 1, 2, 'right'),
            (59, 4, 1, 2, 'right'),
            (63, 3, 1, 2, 'right'),
        ],
        "stars": [(7, 17), (15, 14), (23, 12), (31, 10), (39, 8), (47, 6), (55, 4)],
        "exit": (67, 2),
        "blocks": [],
        "water": -1,
    },

    # Level 8: The Gauntlet - Combined Obstacles
    {
        "name": "The Gauntlet",
        "spawn": (5, 20),
        "platforms": [
            (0, 22, 80, 2),
            (10, 18, 8, 1),
            (25, 15, 8, 1),
            (40, 12, 8, 1),
            (55, 9, 8, 1),
            (70, 6, 8, 1),
        ],
        "moving_platforms": [
            (18, 18, 6, 1, 10, 2.0, False),
            (33, 15, 6, 1, 10, 1.5, False),
            (48, 12, 6, 1, 10, 2.5, False),
            (63, 9, 6, 1, 10, 1.8, False),
        ],
        "spikes": [
            (5, 21, 3, 1, 'up'),
            (20, 21, 4, 1, 'up'),
            (35, 21, 4, 1, 'up'),
            (50, 21, 4, 1, 'up'),
            (65, 21, 4, 1, 'up'),
        ],
        "stars": [(12, 17), (27, 14), (42, 11), (57, 8), (72, 5), (30, 14), (50, 10)],
        "exit": (72, 3),
        "blocks": [
            (15, 17, 2, 1, 1),
            (45, 11, 2, 1, 2),
        ],
        "water": -1,
    },

    # Level 9: Submerged Secrets - Water + Moving Platforms
    {
        "name": "Submerged Secrets",
        "spawn": (5, 10),
        "platforms": [
            (0, 22, 80, 2),
            (10, 17, 8, 1),
            (25, 14, 8, 1),
            (45, 10, 8, 1),
            (65, 6, 8, 1),
        ],
        "moving_platforms": [
            (18, 17, 6, 1, 15, 1.5, False),
            (35, 14, 6, 1, 12, 2.0, False),
            (55, 10, 6, 1, 15, 1.8, True),  # Vertical in water
        ],
        "spikes": [
            (5, 21, 5, 1, 'up'),
            (40, 21, 5, 1, 'up'),
            (60, 21, 5, 1, 'up'),
        ],
        "stars": [(12, 16), (27, 13), (37, 12), (47, 9), (67, 5), (20, 15), (50, 8)],
        "exit": (67, 3),
        "blocks": [
            (30, 13, 3, 2, 2),
        ],
        "water": 16,
    },

    # Level 10: Final Descent - All Mechanics Combined
    {
        "name": "Final Descent",
        "spawn": (40, 20),
        "platforms": [
            (0, 22, 80, 2),
            (35, 19, 10, 1),
            (20, 16, 8, 1),
            (50, 14, 8, 1),
            (30, 11, 8, 1),
            (55, 8, 8, 1),
            (25, 5, 8, 1),
            (50, 2, 10, 1),
        ],
        "moving_platforms": [
            (10, 18, 6, 1, 15, 2.0, False),
            (40, 12, 6, 1, 12, 1.5, True),
            (60, 6, 6, 1, 10, 2.5, False),
        ],
        "spikes": [
            (0, 21, 5, 1, 'up'),
            (15, 21, 4, 1, 'up'),
            (30, 21, 4, 1, 'up'),
            (45, 21, 4, 1, 'up'),
            (60, 21, 4, 1, 'up'),
            (75, 21, 5, 1, 'up'),
            (10, 17, 1, 2, 'right'),
            (58, 10, 1, 3, 'right'),
        ],
        "stars": [(37, 18), (22, 15), (52, 13), (32, 10), (57, 7), (27, 4), (52, 1)],
        "exit": (52, 0),
        "blocks": [
            (18, 17, 2, 1, 2),
            (38, 11, 2, 2, 3),
            (58, 7, 1, 2, 1),
        ],
        "water": -1,
    },

    # Level 11: The Pit - Bonus Deep Vertical
    {
        "name": "The Pit",
        "spawn": (40, 20),
        "platforms": [
            (0, 22, 80, 2),
            # Spiral down
            (35, 19, 10, 1),
            (20, 17, 8, 1),
            (50, 15, 8, 1),
            (15, 13, 6, 1),
            (55, 11, 6, 1),
            (25, 9, 5, 1),
            (45, 7, 5, 1),
            (30, 5, 4, 1),
            (35, 2, 8, 1),
        ],
        "moving_platforms": [
            (10, 18, 6, 1, 10, 1.5, True),
            (65, 12, 6, 1, 10, 2.0, True),
            (40, 8, 6, 1, 5, 2.5, True),
        ],
        "spikes": [
            (5, 21, 8, 1, 'up'),
            (22, 16, 2, 1, 'up'),
            (30, 14, 2, 1, 'up'),
            (40, 12, 2, 1, 'up'),
            (50, 10, 2, 1, 'up'),
            (60, 8, 2, 1, 'up'),
            (20, 6, 1, 2, 'left'),
            (55, 4, 1, 2, 'right'),
        ],
        "stars": [(37, 18), (22, 16), (52, 14), (17, 12), (57, 10), (27, 8), (47, 6), (32, 4), (40, 1), (15, 10)],
        "exit": (37, 0),
        "blocks": [
            (18, 17, 2, 1, 1),
            (38, 10, 2, 1, 2),
            (48, 6, 2, 1, 1),
        ],
        "water": -1,
    },

    # Level 12: Spike Hell - Maximum Difficulty
    {
        "name": "Spike Hell",
        "spawn": (5, 20),
        "platforms": [
            (0, 22, 80, 2),
            (8, 18, 4, 1), (15, 17, 4, 1), (22, 16, 4, 1), (29, 15, 4, 1),
            (36, 14, 4, 1), (43, 13, 4, 1), (50, 12, 4, 1), (57, 11, 4, 1),
            (64, 10, 4, 1), (71, 9, 4, 1),
            (75, 5, 4, 1),
        ],
        "moving_platforms": [
            (10, 19, 4, 1, 8, 3.0, False),
            (25, 16, 4, 1, 8, 2.5, False),
            (40, 13, 4, 1, 8, 3.0, False),
            (55, 10, 4, 1, 8, 2.5, False),
            (70, 7, 4, 1, 8, 3.0, False),
        ],
        "spikes": [
            # Floor covered in spikes
            (0, 21, 8, 1, 'up'), (12, 21, 6, 1, 'up'), (20, 21, 6, 1, 'up'),
            (28, 21, 6, 1, 'up'), (36, 21, 6, 1, 'up'), (44, 21, 6, 1, 'up'),
            (52, 21, 6, 1, 'up'), (60, 21, 6, 1, 'up'), (68, 21, 6, 1, 'up'), (76, 21, 4, 1, 'up'),
            # Wall spikes
            (4, 17, 1, 3, 'right'), (11, 16, 1, 3, 'right'), (18, 15, 1, 3, 'right'),
            (25, 14, 1, 3, 'right'), (32, 13, 1, 3, 'right'), (39, 12, 1, 3, 'right'),
            (46, 11, 1, 3, 'right'), (53, 10, 1, 3, 'right'), (60, 9, 1, 3, 'right'),
            (67, 8, 1, 3, 'right'),
            # Ceiling spikes
            (10, 0, 4, 1, 'down'), (25, 0, 4, 1, 'down'), (45, 0, 4, 1, 'down'),
            (65, 0, 4, 1, 'down'),
        ],
        "stars": [(10, 17), (17, 16), (24, 15), (31, 14), (38, 13), (45, 12), (52, 11), (59, 10), (66, 9), (73, 8)],
        "exit": (75, 3),
        "blocks": [],
        "water": -1,
    },
]

LEVEL_NAMES = [level["name"] for level in LEVELS]