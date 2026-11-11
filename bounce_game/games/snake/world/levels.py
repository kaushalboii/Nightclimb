#!/usr/bin/env python3
"""Game modes for Snake."""

MODES = [
    {
        'id': 'classic',
        'name': 'Classic',
        'desc': 'Pure snake — no obstacles, no power-ups',
        'width': 40,
        'height': 20,
        'obstacles': False,
        'powerups': False,
        'wrap_walls': False,
    },
    {
        'id': 'arcade',
        'name': 'Arcade',
        'desc': 'Obstacles, power-ups, increasing difficulty',
        'width': 40,
        'height': 20,
        'obstacles': True,
        'obstacle_count': 5,
        'powerups': True,
        'wrap_walls': False,
    },
    {
        'id': 'survival',
        'name': 'Survival',
        'desc': 'Walls close in, speed increases, one life',
        'width': 40,
        'height': 20,
        'obstacles': True,
        'obstacle_count': 8,
        'powerups': True,
        'wrap_walls': False,
        'shrinking': True,
    },
    {
        'id': 'time_attack',
        'name': 'Time Attack',
        'desc': '2 minutes — max score, wrap-around walls',
        'width': 30,
        'height': 15,
        'obstacles': False,
        'powerups': True,
        'wrap_walls': True,
        'time_limit': 120,
    },
    {
        'id': 'cozy',
        'name': 'Cozy',
        'desc': 'Large grid, slow speed, no obstacles — relax',
        'width': 60,
        'height': 30,
        'obstacles': False,
        'powerups': True,
        'wrap_walls': False,
        'slow': True,
    },
]

MODE_NAMES = [m['name'] for m in MODES]
MODE_IDS = [m['id'] for m in MODES]