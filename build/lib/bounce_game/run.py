#!/usr/bin/env python3
"""
Run script for Nightclimb Arcade.
Entry point - just run: python run.py
Launches the game selector menu.
"""

import sys
import os

# Add the game directory to path
game_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, game_dir)

from launcher import main
import curses

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass