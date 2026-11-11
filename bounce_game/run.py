#!/usr/bin/env python3
"""
Run script for Bounce game.
Simple entry point - just run: python run.py
"""

import sys
import os

# Add the game directory to path
game_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, game_dir)

from main import main
import curses

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()