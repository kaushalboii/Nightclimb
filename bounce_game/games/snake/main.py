#!/usr/bin/env python3
"""
SNAKE — Enhanced Retro Arcade Classic
Smooth movement, power-ups, obstacles, high scores, multiple modes.
"""

import curses
import time
import random
from pathlib import Path

from world.entities import Snake, Food, Obstacle, PowerUp, Particle
from ui.render import Renderer
from ui.input import InputHandler
from game.state import GameState


SAVE_FILE = Path.home() / ".snake_save.json"


def main(stdscr):
    # Initialize curses
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    curses.noecho()
    curses.start_color()
    curses.use_default_colors()

    # Color pairs
    curses.init_pair(1, curses.COLOR_GREEN, -1)       # Snake head
    curses.init_pair(2, curses.COLOR_CYAN, -1)        # Snake body
    curses.init_pair(3, curses.COLOR_YELLOW, -1)      # Food
    curses.init_pair(4, curses.COLOR_RED, -1)         # Danger food / Obstacles
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)     # Power-ups
    curses.init_pair(6, curses.COLOR_WHITE, -1)       # UI text
    curses.init_pair(7, curses.COLOR_BLUE, -1)        # Special food
    curses.init_pair(8, curses.COLOR_RED, curses.COLOR_WHITE)   # Game over
    curses.init_pair(9, curses.COLOR_GREEN, curses.COLOR_BLACK) # Level complete
    curses.init_pair(10, curses.COLOR_CYAN, -1)       # Particles
    curses.init_pair(11, curses.COLOR_GREEN, -1)      # Snake body alt

    # Game components
    renderer = Renderer(stdscr)
    input_handler = InputHandler()
    state = GameState()

    # Load save
    state.load(SAVE_FILE)

    # Main game loop
    last_time = time.time()
    running = True

    while running:
        current_time = time.time()
        dt = min(current_time - last_time, 0.1)
        last_time = current_time

        # Handle input
        action = input_handler.update_snake(state.snake, stdscr)
        if action == "quit":
            state.save(SAVE_FILE)
            break
        elif action == "pause":
            state.paused = not state.paused
        elif action == "restart":
            state.restart_game()
        elif action == "menu":
            choice = renderer.show_menu(stdscr, state)
            if choice == "quit":
                state.save(SAVE_FILE)
                break
            elif choice == "restart":
                state.restart_game()
            elif choice == "mode_select":
                mode = renderer.show_mode_select(stdscr, state)
                if mode is not None:
                    state.set_mode(mode)
            elif choice == "resume":
                state.paused = False

        # Update game state
        if not state.paused and not state.game_over:
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

        # Frame rate cap
        time.sleep(1/60)

    # Final save on exit
    state.save(SAVE_FILE)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass