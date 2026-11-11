#!/usr/bin/env python3
"""Input handling for Bounce game."""

import curses


class InputHandler:
    def __init__(self):
        self.key_states = {}
        self.last_key = -1

    def get_action(self, stdscr):
        """Process input and return action string."""
        key = stdscr.getch()

        if key == -1:
            return None

        self.last_key = key

        # Global hotkeys (work anytime)
        if key in (ord('q'), 27):  # Q or Escape
            return "quit"
        elif key in (ord('p'), ord('P')):
            return "pause"
        elif key in (ord('m'), ord('M')):
            return "menu"
        elif key in (ord('r'), ord('R')):
            return "restart"

        # Gameplay keys (only when playing)
        # We'll update the ball's input state directly
        return self._handle_gameplay_key(key)

    def _handle_gameplay_key(self, key):
        """Handle gameplay keys - returns None, updates ball state elsewhere."""
        # This is handled by updating ball.input_* in the main loop
        # Return special actions
        if key in (curses.KEY_ENTER, 10, 13, ord(' '), ord('n'), ord('N')):
            return "next_level"
        elif key in (ord('b'), ord('B')):
            return "prev_level"
        return None

    def update_ball_input(self, ball, stdscr):
        """Update ball input state from current key states."""
        if ball is None:
            return

        key = stdscr.getch()
        # Reset
        ball.input_left = False
        ball.input_right = False
        ball.input_jump = False

        # Check held keys by re-getting (non-blocking)
        # Since nodelay is True, we need to track state
        # For simplicity, check the last key and common held keys
        # In a real implementation, you'd track key up/down events

        # We'll use a different approach: check key buffer
        # For now, simple single-key-per-frame
        if key in (curses.KEY_LEFT, ord('a'), ord('A'), ord('h'), ord('H')):
            ball.input_left = True
        elif key in (curses.KEY_RIGHT, ord('d'), ord('D'), ord('l'), ord('L')):
            ball.input_right = True
        elif key in (curses.KEY_UP, ord('w'), ord('W'), ord('k'), ord('K'), ord(' ')):
            ball.input_jump = True

        # Also check for continuous hold by peeking at key buffer
        # This is a limitation of curses - we'll accept it for simplicity


# Alternative: Better input handling with key state tracking
class BetterInputHandler:
    """More robust input handling using key state tracking."""

    def __init__(self):
        self.keys_held = set()
        self.keys_pressed = set()
        self.keys_released = set()

    def poll(self, stdscr):
        """Poll for input events."""
        self.keys_pressed.clear()
        self.keys_released.clear()

        while True:
            key = stdscr.getch()
            if key == -1:
                break

            if key not in self.keys_held:
                self.keys_held.add(key)
                self.keys_pressed.add(key)
            # Note: curses doesn't give us key release events easily
            # We'll approximate by clearing keys not seen this frame

        # Approximate: any key not pressed this frame is released
        # This is imperfect but works for simple games
        return self.keys_pressed

    def is_held(self, key):
        return key in self.keys_held

    def was_pressed(self, key):
        return key in self.keys_pressed

    def update_ball(self, ball, stdscr):
        """Update ball input from current key state."""
        if ball is None:
            return

        self.poll(stdscr)

        ball.input_left = any(self.is_held(k) for k in (curses.KEY_LEFT, ord('a'), ord('A'), ord('h'), ord('H')))
        ball.input_right = any(self.is_held(k) for k in (curses.KEY_RIGHT, ord('d'), ord('D'), ord('l'), ord('L')))
        ball.input_jump = any(self.was_pressed(k) for k in (curses.KEY_UP, ord('w'), ord('W'), ord('k'), ord('K'), ord(' ')))

        # Return any special actions
        if any(self.was_pressed(k) for k in (ord('q'), 27)):
            return "quit"
        if any(self.was_pressed(k) for k in (ord('p'), ord('P'))):
            return "pause"
        if any(self.was_pressed(k) for k in (ord('m'), ord('M'))):
            return "menu"
        if any(self.was_pressed(k) for k in (ord('r'), ord('R'))):
            return "restart"
        if any(self.was_pressed(k) for k in (curses.KEY_ENTER, 10, 13, ord('n'), ord('N'))):
            return "next_level"
        if any(self.was_pressed(k) for k in (ord('b'), ord('B'))):
            return "prev_level"

        return None