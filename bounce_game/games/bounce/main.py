#!/usr/bin/env python3
"""
BOUNCE — Enhanced Nokia Classic Recreation
Physics platformer with 12 levels, auto-save, particle effects, screen shake.
"""

import curses
import time
import random
import traceback
from pathlib import Path

from world.levels import LEVELS, LEVEL_NAMES
from world.entities import Ball, Platform, Spike, Star, Exit, Block, MovingPlatform, Particle
from ui.render import Renderer
from ui.input import InputHandler
from game.state import GameState
from game.physics import PhysicsEngine


SAVE_FILE = Path.home() / ".bounce_save.json"


def main(stdscr):
    try:
        _main_loop(stdscr)
    except Exception as e:
        # Show error on screen before exiting
        stdscr.nodelay(False)
        stdscr.erase()
        stdscr.addstr(0, 0, f"ERROR: {e}")
        stdscr.addstr(1, 0, traceback.format_exc())
        stdscr.addstr(20, 0, "Press any key to exit...")
        stdscr.refresh()
        stdscr.getch()


def _main_loop(stdscr):
    # Initialize curses
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    curses.noecho()
    curses.start_color()
    curses.use_default_colors()

    # Color pairs
    curses.init_pair(1, curses.COLOR_RED, -1)        # Ball
    curses.init_pair(2, curses.COLOR_GREEN, -1)      # Platforms/Blocks
    curses.init_pair(3, curses.COLOR_YELLOW, -1)     # Stars
    curses.init_pair(4, curses.COLOR_CYAN, -1)       # Exit
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)    # Spikes
    curses.init_pair(6, curses.COLOR_WHITE, -1)      # UI text
    curses.init_pair(7, curses.COLOR_BLUE, -1)       # Water
    curses.init_pair(8, curses.COLOR_RED, curses.COLOR_WHITE)   # Game over
    curses.init_pair(9, curses.COLOR_GREEN, curses.COLOR_BLACK) # Level complete
    curses.init_pair(10, curses.COLOR_CYAN, -1)      # Particles
    curses.init_pair(11, curses.COLOR_MAGENTA, -1)   # Power-ups

    # Game components
    renderer = Renderer(stdscr)
    input_handler = InputHandler()
    physics = PhysicsEngine()
    state = GameState()

    # Load save
    state.load(SAVE_FILE)

    # Main game loop
    last_time = time.time()
    running = True

    while running:
        current_time = time.time()
        dt = min(current_time - last_time, 0.1)  # Cap dt
        last_time = current_time

        # Handle input
        action = input_handler.update_ball(state.ball, stdscr)
        if action == "quit":
            state.save(SAVE_FILE)
            break
        elif action == "pause":
            state.paused = not state.paused
        elif action == "restart":
            state.restart_level()
        elif action == "menu":
            choice = renderer.show_menu(stdscr, state)
            if choice == "quit":
                state.save(SAVE_FILE)
                break
            elif choice == "restart_level":
                state.restart_level()
            elif choice == "level_select":
                level = renderer.show_level_select(stdscr, state)
                if level is not None:
                    state.set_level(level)
            elif choice == "resume":
                state.paused = False
        elif action == "next_level" and state.level_complete:
            state.next_level()
        elif action == "prev_level":
            state.prev_level()

        # Update game state
        if not state.paused and not state.level_complete and not state.game_over:
            physics.update(state, dt)
            state.update(dt)

            # Update particles
            for particle in state.particles[:]:
                particle.update(dt)
                if particle.life <= 0:
                    state.particles.remove(particle)

            # Auto-save periodically
            if state.should_autosave():
                state.save(SAVE_FILE)

        # Render
        renderer.render(state)

        # Frame rate cap ~60 FPS
        time.sleep(1/60)

    # Final save on exit
    state.save(SAVE_FILE)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass