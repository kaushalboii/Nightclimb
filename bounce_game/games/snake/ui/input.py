#!/usr/bin/env python3
"""Input handling for Snake game."""

import curses


# Key mappings for snake (4-directional)
UP_KEYS    = {curses.KEY_UP, ord('w'), ord('W'), ord('k'), ord('K')}
DOWN_KEYS  = {curses.KEY_DOWN, ord('s'), ord('S'), ord('j'), ord('J')}
LEFT_KEYS  = {curses.KEY_LEFT, ord('a'), ord('A'), ord('h'), ord('H')}
RIGHT_KEYS = {curses.KEY_RIGHT, ord('d'), ord('D'), ord('l'), ord('L')}

QUIT_KEYS  = {ord('q'), 27}
PAUSE_KEYS = {ord('p'), ord('P')}
MENU_KEYS  = {ord('m'), ord('M')}
RESTART_KEYS = {ord('r'), ord('R')}


class InputHandler:
    """Input handling with proper key state tracking for Snake."""

    def __init__(self):
        self.held = set()
        self.pressed = set()
        self._seen_this_frame = set()

    def poll(self, stdscr):
        """Poll all available key events from curses."""
        self.pressed.clear()
        self._seen_this_frame.clear()

        while True:
            key = stdscr.getch()
            if key == -1:
                break
            self._seen_this_frame.add(key)
            if key not in self.held:
                self.held.add(key)
                self.pressed.add(key)

        # Any key that was held but not seen this frame = released
        released = self.held - self._seen_this_frame
        self.held -= released

    def any_held(self, key_set):
        return any(k in self.held for k in key_set)

    def any_pressed(self, key_set):
        return any(k in self.pressed for k in key_set)

    def update_snake(self, snake, stdscr):
        """
        Update snake direction from input and return any menu action.
        Returns: action string or None
        """
        if snake is None:
            return None

        self.poll(stdscr)

        # Directional input (held keys work, but we use pressed for responsiveness)
        # For snake, we want immediate response to direction changes
        if self.any_pressed(UP_KEYS):
            snake.set_direction((0, -1))
        elif self.any_pressed(DOWN_KEYS):
            snake.set_direction((0, 1))
        elif self.any_pressed(LEFT_KEYS):
            snake.set_direction((-1, 0))
        elif self.any_pressed(RIGHT_KEYS):
            snake.set_direction((1, 0))

        # Menu / special actions
        if self.any_pressed(QUIT_KEYS):
            return "quit"
        if self.any_pressed(PAUSE_KEYS):
            return "pause"
        if self.any_pressed(MENU_KEYS):
            return "menu"
        if self.any_pressed(RESTART_KEYS):
            return "restart"

        return None