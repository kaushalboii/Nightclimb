#!/usr/bin/env python3
"""Input handling for Bounce game - Fixed key state tracking."""

import curses


# Key mappings
LEFT_KEYS  = {curses.KEY_LEFT, ord('a'), ord('A'), ord('h'), ord('H')}
RIGHT_KEYS = {curses.KEY_RIGHT, ord('d'), ord('D'), ord('l'), ord('L')}
JUMP_KEYS  = {curses.KEY_UP, ord('w'), ord('W'), ord('k'), ord('K'), ord(' ')}
QUIT_KEYS  = {ord('q'), 27}  # 27 = Escape
PAUSE_KEYS = {ord('p'), ord('P')}
MENU_KEYS  = {ord('m'), ord('M')}
RESTART_KEYS = {ord('r'), ord('R')}
NEXT_KEYS  = {curses.KEY_ENTER, 10, 13, ord('n'), ord('N'), ord(' ')}
PREV_KEYS  = {ord('b'), ord('B')}


class InputHandler:
    """
    Robust input handling with proper key state tracking.

    Tracks three sets per frame:
    - held: keys currently held down (for continuous movement)
    - pressed: keys pressed THIS frame only (for jump, menu actions)
    - released: keys released THIS frame (not used but tracked for completeness)
    """

    def __init__(self):
        self.held = set()      # Keys currently held
        self.pressed = set()   # Keys pressed this frame
        self._seen_this_frame = set()  # Keys seen in current poll()

    def poll(self, stdscr):
        """Poll all available key events from curses."""
        self.pressed.clear()
        self._seen_this_frame.clear()

        # Read all available keys (non-blocking)
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

    def is_held(self, key):
        return key in self.held

    def was_pressed(self, key):
        return key in self.pressed

    def any_held(self, key_set):
        """Check if any key in the set is currently held."""
        return any(k in self.held for k in key_set)

    def any_pressed(self, key_set):
        """Check if any key in the set was pressed this frame."""
        return any(k in self.pressed for k in key_set)

    def update_ball(self, ball, stdscr):
        """
        Update ball input state and return any menu action.
        Returns: action string or None
        """
        if ball is None:
            return None

        self.poll(stdscr)

        # Continuous movement (held keys)
        ball.input_left = self.any_held(LEFT_KEYS)
        ball.input_right = self.any_held(RIGHT_KEYS)

        # Jump is a single press (not held) - prevents auto-jump on landing
        ball.input_jump = self.any_pressed(JUMP_KEYS)

        # Menu / special actions (pressed this frame only)
        if self.any_pressed(QUIT_KEYS):
            return "quit"
        if self.any_pressed(PAUSE_KEYS):
            return "pause"
        if self.any_pressed(MENU_KEYS):
            return "menu"
        if self.any_pressed(RESTART_KEYS):
            return "restart"
        if self.any_pressed(NEXT_KEYS):
            return "next_level"
        if self.any_pressed(PREV_KEYS):
            return "prev_level"

        return None


# Backward compatibility alias
BetterInputHandler = InputHandler