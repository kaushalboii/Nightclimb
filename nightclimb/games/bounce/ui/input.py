#!/usr/bin/env python3
"""Input handling for Bounce game - Fixed key state tracking with hold grace period."""

import curses
import time


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

# All movement keys for grace period tracking
MOVEMENT_KEYS = LEFT_KEYS | RIGHT_KEYS | JUMP_KEYS


class InputHandler:
    """
    Robust input handling with key hold grace period.

    Problem: curses nodelay mode doesn't reliably send key repeat events
    for held keys on many terminals. This causes movement to stop after
    one frame.

    Solution: Track "last seen" timestamp for each key. Keys are considered
    "held" for a grace period (HOLD_GRACE) after last being seen. This
    allows smooth continuous movement even without key repeat events.
    """

    HOLD_GRACE = 0.15  # Seconds to consider key held after last seen (150ms)

    def __init__(self):
        self.held = set()              # Keys currently considered held
        self.pressed = set()           # Keys pressed this frame (new presses)
        self._last_seen = {}           # key -> timestamp of last getch() event
        self._pressed_this_frame = set()  # Keys newly pressed this frame

    def poll(self, stdscr):
        """Poll all available key events from curses."""
        now = time.time()
        self.pressed.clear()
        self._pressed_this_frame.clear()

        # Read all available keys (non-blocking)
        while True:
            key = stdscr.getch()
            if key == -1:
                break
            self._last_seen[key] = now
            if key not in self.held:
                self.held.add(key)
                self.pressed.add(key)
                self._pressed_this_frame.add(key)

        # Grace period: keep movement keys "held" for HOLD_GRACE after last seen
        # This compensates for terminals that don't send key repeat events
        keys_to_release = set()
        for key in self.held:
            if key in MOVEMENT_KEYS:
                last = self._last_seen.get(key, 0)
                if now - last > self.HOLD_GRACE:
                    keys_to_release.add(key)
            # Non-movement keys (quit, pause, menu) release immediately when not seen
            elif key not in self._pressed_this_frame:
                keys_to_release.add(key)

        self.held -= keys_to_release

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

        # Continuous movement (held keys with grace period)
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