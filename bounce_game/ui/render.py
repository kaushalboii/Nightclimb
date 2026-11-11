#!/usr/bin/env python3
"""Rendering system for Bounce game."""

import curses
import math
from world.entities import Ball, Platform, Spike, Star, Exit, Block, MovingPlatform


class Renderer:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.game_width = 80
        self.game_height = 24
        self.offset_x = max(0, (self.width - self.game_width) // 2)
        self.offset_y = max(0, (self.height - self.game_height) // 2)

        # Screen shake
        self.shake_intensity = 0
        self.shake_timer = 0

        # Character set for different entities
        self.chars = {
            'ball': '●',
            'ball_squash': '◆',
            'platform': '▀',
            'platform_thin': '─',
            'spike_up': '▲',
            'spike_down': '▼',
            'spike_left': '◄',
            'spike_right': '►',
            'star': '★',
            'star_empty': '☆',
            'exit_closed': '█',
            'exit_open': '░',
            'block': '█',
            'block_cracked': '▓',
            'water': '≈',
            'bg': ' ',
        }

    def render(self, state):
        """Main render function."""
        self.stdscr.erase()

        # Calculate shake offset
        shake_x, shake_y = 0, 0
        if self.shake_timer > 0:
            import random
            shake_x = random.randint(-self.shake_intensity, self.shake_intensity)
            shake_y = random.randint(-self.shake_intensity, self.shake_intensity)
            self.shake_timer -= 1

        # Draw background
        self.draw_background(state)

        # Draw water
        if state.water_level > 0:
            self.draw_water(state, shake_x, shake_y)

        # Draw platforms
        for platform in state.platforms:
            self.draw_platform(platform, shake_x, shake_y)

        # Draw moving platforms
        for mp in state.moving_platforms:
            self.draw_moving_platform(mp, shake_x, shake_y)

        # Draw blocks
        for block in state.blocks:
            self.draw_block(block, shake_x, shake_y)

        # Draw spikes
        for spike in state.spikes:
            self.draw_spike(spike, shake_x, shake_y)

        # Draw stars
        for star in state.stars:
            self.draw_star(star, shake_x, shake_y)

        # Draw exit
        for exit_obj in state.exits:
            self.draw_exit(exit_obj, state, shake_x, shake_y)

        # Draw ball (last so it's on top)
        if state.ball:
            self.draw_ball(state.ball, shake_x, shake_y)

        # Draw UI
        self.draw_ui(state)

        # Draw overlays
        if state.level_complete:
            self.draw_level_complete(state)
        elif state.game_over:
            self.draw_game_over(state)
        elif state.paused:
            self.draw_paused(state)

        self.stdscr.refresh()

    def draw_background(self, state):
        """Draw sky/background."""
        for y in range(self.game_height):
            for x in range(self.game_width):
                # Parallax stars in background
                if (x * 7 + y * 11) % 37 == 0 and y < self.game_height - 3:
                    self.safe_put(y, x, '·', 6)

    def draw_water(self, state, shake_x, shake_y):
        """Draw water area."""
        water_y = int(state.water_level)
        # Use time-based animation instead of ball.anim_timer
        import time
        anim_time = time.time()
        for y in range(water_y, self.game_height):
            for x in range(self.game_width):
                if (x + y + int(anim_time * 2)) % 4 == 0:
                    self.safe_put(y, x, '≈', 7, shake_x, shake_y)

    def draw_platform(self, platform, shake_x, shake_y):
        """Draw static platform."""
        color = curses.color_pair(platform.color) | curses.A_BOLD
        for x in range(int(platform.width)):
            for y in range(int(platform.height)):
                px = int(platform.x) + x
                py = int(platform.y) + y
                if platform.height == 1:
                    self.safe_put(py, px, '▀', platform.color, shake_x, shake_y)
                else:
                    self.safe_put(py, px, '█', platform.color, shake_x, shake_y)

    def draw_moving_platform(self, mp, shake_x, shake_y):
        """Draw moving platform with distinct style."""
        color = curses.color_pair(mp.color) | curses.A_BOLD
        for x in range(int(mp.width)):
            for y in range(int(mp.height)):
                px = int(mp.x) + x
                py = int(mp.y) + y
                # Animated pattern
                char = '▀' if int(mp.anim_timer * 4 + x) % 2 == 0 else '▄'
                self.safe_put(py, px, char, mp.color, shake_x, shake_y)

    def draw_block(self, block, shake_x, shake_y):
        """Draw breakable block."""
        if block.broken:
            return
        color = block.color
        char = '█' if block.hits == block.max_hits else '▓'
        for x in range(int(block.width)):
            for y in range(int(block.height)):
                self.safe_put(int(block.y) + y, int(block.x) + x, char, color, shake_x, shake_y)

    def draw_spike(self, spike, shake_x, shake_y):
        """Draw spike with orientation."""
        color = curses.color_pair(spike.color) | curses.A_BOLD
        # Animate spikes
        anim = int(spike.anim_timer * 4) % 2

        if spike.orientation == 'up':
            char = '▲' if anim == 0 else '△'
            for x in range(int(spike.width)):
                self.safe_put(int(spike.y), int(spike.x) + x, char, spike.color, shake_x, shake_y)
        elif spike.orientation == 'down':
            char = '▼' if anim == 0 else '▽'
            for x in range(int(spike.width)):
                self.safe_put(int(spike.y), int(spike.x) + x, char, spike.color, shake_x, shake_y)
        elif spike.orientation == 'left':
            char = '◄' if anim == 0 else '◀'
            for y in range(int(spike.height)):
                self.safe_put(int(spike.y) + y, int(spike.x), char, spike.color, shake_x, shake_y)
        elif spike.orientation == 'right':
            char = '►' if anim == 0 else '▶'
            for y in range(int(spike.height)):
                self.safe_put(int(spike.y) + y, int(spike.x) + int(spike.width) - 1, char, spike.color, shake_x, shake_y)

    def draw_star(self, star, shake_x, shake_y):
        """Draw collectible star."""
        if star.collected:
            return
        color = curses.color_pair(star.color) | curses.A_BOLD | curses.A_BLINK
        char = '★' if int(star.anim_timer * 6) % 2 == 0 else '✦'
        y = int(star.y) + int(star.bob_offset)
        self.safe_put(y, int(star.x), char, star.color, shake_x, shake_y)

    def draw_exit(self, exit_obj, state, shake_x, shake_y):
        """Draw level exit."""
        color = curses.color_pair(exit_obj.color) | curses.A_BOLD
        if exit_obj.open:
            # Pulsing open exit
            alpha = int(exit_obj.anim_timer * 8) % 4
            chars = ['░', '▒', '▓', '█']
            char = chars[alpha]
        else:
            char = '█'
        for x in range(int(exit_obj.width)):
            for y in range(int(exit_obj.height)):
                self.safe_put(int(exit_obj.y) + y, int(exit_obj.x) + x, char, exit_obj.color, shake_x, shake_y)

    def draw_ball(self, ball, shake_x, shake_y):
        """Draw the player ball with squash animation."""
        color = curses.color_pair(1) | curses.A_BOLD

        # Squash effect based on velocity
        if abs(ball.vy) > 15:
            ball.squash = 0.6
        elif abs(ball.vy) > 8:
            ball.squash = 0.8
        else:
            ball.squash = 1.0

        # Trail effect (use center coordinates)
        ball.trail.append((ball.center_x, ball.center_y, ball.squash))
        if len(ball.trail) > 5:
            ball.trail.pop(0)

        for i, (tx, ty, tsquash) in enumerate(ball.trail):
            alpha = (i + 1) / len(ball.trail) * 0.5
            trail_char = '·' if tsquash < 1 else '○'
            self.safe_put(int(ty), int(tx), trail_char, 1, shake_x, shake_y)

        # Main ball (use center coordinates)
        x, y = int(ball.center_x), int(ball.center_y)
        if ball.squash < 1.0:
            # Squashed horizontally
            self.safe_put(y, x - 1, '◆', 1, shake_x, shake_y)
            self.safe_put(y, x, '◆', 1, shake_x, shake_y)
            self.safe_put(y, x + 1, '◆', 1, shake_x, shake_y)
        else:
            self.safe_put(y, x, '●', 1, shake_x, shake_y)

    def draw_ui(self, state):
        """Draw HUD: level, lives, stars, score."""
        # Top bar
        level_name = LEVEL_NAMES[state.current_level] if state.current_level < len(LEVEL_NAMES) else f"Level {state.current_level + 1}"
        hud = f" BOUNCE | {level_name} | Lives: {'♥' * state.lives}{'♡' * (3 - state.lives)} | Stars: {state.stars_collected}/{state.total_stars} | Score: {state.score} "
        self.safe_put(0, 0, hud[:self.width - 1], 6)

        # Best time
        if state.current_level in state.best_times:
            best = state.best_times[state.current_level]
            time_str = f"Best: {best:.1f}s"
            self.safe_put(0, self.width - len(time_str) - 2, time_str, 6)

        # Controls hint
        if state.current_level == 0 and not state.level_complete:
            hint = " [←/→] Move  [↑/Space] Jump  [P] Pause  [R] Restart  [M] Menu "
            self.safe_put(self.game_height - 1, 0, hint, 6)

    def draw_level_complete(self, state):
        """Draw level complete overlay."""
        msg = " LEVEL COMPLETE! "
        msg2 = f" Stars: {state.stars_collected}/{state.total_stars}  Time: {time.time() - state.level_start_time:.1f}s  Score: +{max(0, int(5000 - (time.time() - state.level_start_time) * 100))} "
        msg3 = " [Enter/Space] Next Level  [R] Restart  [M] Menu "

        cy = self.game_height // 2
        cx = self.game_width // 2

        self.draw_box(cy - 2, cx - len(msg) // 2 - 2, 5, len(msg) + 4, 9)
        self.safe_put(cy - 1, cx - len(msg) // 2, msg, 9)
        self.safe_put(cy, cx - len(msg2) // 2, msg2, 9)
        self.safe_put(cy + 1, cx - len(msg3) // 2, msg3, 9)

    def draw_game_over(self, state):
        """Draw game over overlay."""
        msg = " GAME OVER "
        msg2 = f" Final Score: {state.score} "
        msg3 = " [R] Restart Game  [M] Menu  [Q] Quit "

        cy = self.game_height // 2
        cx = self.game_width // 2

        self.draw_box(cy - 2, cx - len(msg) // 2 - 2, 5, len(msg) + 4, 8)
        self.safe_put(cy - 1, cx - len(msg) // 2, msg, 8)
        self.safe_put(cy, cx - len(msg2) // 2, msg2, 8)
        self.safe_put(cy + 1, cx - len(msg3) // 2, msg3, 8)

    def draw_paused(self, state):
        """Draw paused overlay."""
        msg = " PAUSED "
        msg2 = " [P] Resume  [R] Restart  [M] Menu  [Q] Quit "

        cy = self.game_height // 2
        cx = self.game_width // 2

        self.draw_box(cy - 1, cx - len(msg) // 2 - 2, 3, len(msg) + 4, 6)
        self.safe_put(cy, cx - len(msg) // 2, msg, 6)
        self.safe_put(cy + 1, cx - len(msg2) // 2, msg2, 6)

    def draw_box(self, y, x, h, w, color_pair):
        """Draw a box."""
        color = curses.color_pair(color_pair)
        for dy in range(h):
            for dx in range(w):
                if dy == 0 or dy == h - 1:
                    ch = '═' if dx not in (0, w - 1) else ('╔' if dy == 0 else '╚') if dx == 0 else ('╗' if dy == 0 else '╝')
                elif dx == 0 or dx == w - 1:
                    ch = '║'
                else:
                    ch = ' '
                self.stdscr.addch(self.offset_y + y + dy, self.offset_x + x + dx, ch, color)

    def safe_put(self, y, x, text, color_pair, shake_x=0, shake_y=0):
        """Safely put character or string at position with bounds checking."""
        sy = self.offset_y + y + shake_y
        sx = self.offset_x + x + shake_x
        if 0 <= sy < self.height and 0 <= sx < self.width - 1:
            try:
                if len(text) == 1:
                    self.stdscr.addch(sy, sx, text, curses.color_pair(color_pair) | curses.A_BOLD)
                else:
                    # For strings, use addstr but clip to screen width
                    max_len = self.width - sx - 1
                    clipped = text[:max_len]
                    self.stdscr.addstr(sy, sx, clipped, curses.color_pair(color_pair) | curses.A_BOLD)
            except curses.error:
                pass

    def trigger_shake(self, intensity=2, duration=0.3):
        """Trigger screen shake."""
        self.shake_intensity = intensity
        self.shake_timer = int(duration * 60)

    def show_menu(self, stdscr, state):
        """Show main menu."""
        self.stdscr.erase()
        options = ["Resume", "Restart Level", "Level Select", "Quit"]
        selected = 0

        while True:
            self.stdscr.erase()
            cy = self.height // 2
            cx = self.width // 2

            title = " B O U N C E "
            self.stdscr.addstr(cy - 6, cx - len(title) // 2, title, curses.color_pair(1) | curses.A_BOLD)

            subtitle = f" Level {state.current_level + 1}: {LEVEL_NAMES[state.current_level]} "
            self.stdscr.addstr(cy - 4, cx - len(subtitle) // 2, subtitle, curses.color_pair(6))

            for i, opt in enumerate(options):
                y = cy - 1 + i
                prefix = " ► " if i == selected else "   "
                color = curses.color_pair(3) | curses.A_BOLD if i == selected else curses.color_pair(6)
                self.stdscr.addstr(y, cx - len(opt) // 2 - 2, prefix + opt, color)

            self.stdscr.refresh()

            key = self.stdscr.getch()
            if key in (curses.KEY_UP, ord('k'), ord('w')):
                selected = (selected - 1) % len(options)
            elif key in (curses.KEY_DOWN, ord('j'), ord('s')):
                selected = (selected + 1) % len(options)
            elif key in (curses.KEY_ENTER, 10, 13, ord(' ')):
                return options[selected].lower().replace(' ', '_')
            elif key in (ord('q'), 27):  # Escape
                return "quit"

    def show_level_select(self, stdscr, state):
        """Show level select screen."""
        self.stdscr.erase()
        selected = state.current_level

        while True:
            self.stdscr.erase()
            cy = self.height // 2
            cx = self.width // 2

            title = " SELECT LEVEL "
            self.stdscr.addstr(cy - 8, cx - len(title) // 2, title, curses.color_pair(1) | curses.A_BOLD)

            # Show 10 levels at a time
            start = max(0, selected - 5)
            end = min(len(LEVEL_NAMES), start + 10)

            for i in range(start, end):
                y = cy - 5 + (i - start)
                name = LEVEL_NAMES[i]
                stars = "★" * (3 if i in state.best_times else 0)  # Simplified
                prefix = " ► " if i == selected else "   "
                suffix = " ✓" if i < state.current_level or i in state.best_times else ""
                color = curses.color_pair(3) | curses.A_BOLD if i == selected else curses.color_pair(6)
                line = f"{prefix}{i+1:2d}. {name}{suffix}"
                self.stdscr.addstr(y, cx - len(line) // 2, line, color)

            hint = " [↑/↓] Navigate  [Enter] Select  [Esc] Back "
            self.stdscr.addstr(cy + 6, cx - len(hint) // 2, hint, curses.color_pair(6))

            self.stdscr.refresh()

            key = self.stdscr.getch()
            if key in (curses.KEY_UP, ord('k'), ord('w')):
                selected = (selected - 1) % len(LEVEL_NAMES)
            elif key in (curses.KEY_DOWN, ord('j'), ord('s')):
                selected = (selected + 1) % len(LEVEL_NAMES)
            elif key in (curses.KEY_ENTER, 10, 13, ord(' ')):
                return selected
            elif key in (ord('q'), 27):
                return None


# Import here to avoid circular import
import time
from world.levels import LEVEL_NAMES