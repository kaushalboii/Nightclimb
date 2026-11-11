#!/usr/bin/env python3
"""Rendering system for Snake game."""

import curses
import time
from world.entities import Snake, Food, Obstacle, PowerUp, Particle


class Renderer:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()

        # Screen shake
        self.shake_intensity = 0
        self.shake_timer = 0

    def render(self, state):
        """Main render function."""
        self.stdscr.erase()

        # Update screen shake from state
        if state.shake_timer > 0:
            self.shake_intensity = state.shake_intensity
            self.shake_timer = state.shake_timer
            state.shake_timer = max(0, state.shake_timer - 1/60)

        # Calculate shake offset
        shake_x, shake_y = 0, 0
        if self.shake_timer > 0:
            import random
            shake_x = random.randint(-self.shake_intensity, self.shake_intensity)
            shake_y = random.randint(-self.shake_intensity, self.shake_intensity)
            self.shake_timer -= 1/60

        # Calculate game area position
        game_w = state.grid_width * 2  # Each cell = 2 chars wide
        game_h = state.grid_height
        offset_x = max(0, (self.width - game_w) // 2)
        offset_y = max(0, (self.height - game_h) // 2 - 2)

        # Draw border
        self.draw_border(offset_x, offset_y, game_w, game_h)

        # Draw obstacles
        for obs in state.obstacles:
            self.draw_cell(offset_x, offset_y, obs.x, obs.y, obs.char, obs.color, shake_x, shake_y)

        # Draw foods
        for food in state.foods:
            self.draw_food(offset_x, offset_y, food, shake_x, shake_y)

        # Draw power-ups
        for pup in state.powerups:
            self.draw_powerup(offset_x, offset_y, pup, shake_x, shake_y)

        # Draw particles
        for particle in state.particles:
            self.draw_particle(offset_x, offset_y, particle, shake_x, shake_y)

        # Draw snake
        if state.snake:
            self.draw_snake(offset_x, offset_y, state.snake, shake_x, shake_y)

        # Draw UI
        self.draw_ui(state, offset_x, offset_y, game_w)

        # Draw overlays
        if state.level_complete:
            self.draw_level_complete(state)
        elif state.game_over:
            self.draw_game_over(state)
        elif state.paused:
            self.draw_paused(state)

        self.stdscr.refresh()

    def draw_border(self, ox, oy, gw, gh):
        """Draw game area border."""
        color = curses.color_pair(6)
        # Top & bottom
        for x in range(gw + 2):
            self.stdscr.addch(oy, ox + x, '═', color)
            self.stdscr.addch(oy + gh + 1, ox + x, '═', color)
        # Sides
        for y in range(gh + 2):
            self.stdscr.addch(oy + y, ox, '║', color)
            self.stdscr.addch(oy + y, ox + gw + 1, '║', color)
        # Corners
        self.stdscr.addch(oy, ox, '╔', color)
        self.stdscr.addch(oy, ox + gw + 1, '╗', color)
        self.stdscr.addch(oy + gh + 1, ox, '╚', color)
        self.stdscr.addch(oy + gh + 1, ox + gw + 1, '╝', color)

    def draw_cell(self, ox, oy, gx, gy, char, color_pair, shake_x=0, shake_y=0):
        """Draw a single grid cell (2 chars wide)."""
        sx = ox + 1 + gx * 2 + shake_x
        sy = oy + 1 + gy + shake_y
        if 0 <= sy < self.height and 0 <= sx < self.width - 1:
            try:
                self.stdscr.addstr(sy, sx, char * 2, curses.color_pair(color_pair) | curses.A_BOLD)
            except curses.error:
                pass

    def draw_food(self, ox, oy, food, shake_x, shake_y):
        """Draw food with animation."""
        if food.collected:
            return
        # Pulse animation
        char = food.char
        if int(food.anim_timer * 4) % 2 == 0:
            char = food.char
        else:
            char = '·'
        self.draw_cell(ox, oy, food.x, food.y, char, food.color, shake_x, shake_y)

    def draw_powerup(self, ox, oy, pup, shake_x, shake_y):
        """Draw power-up with bob animation."""
        if pup.collected:
            return
        char = pup.char
        if int(pup.anim_timer * 3) % 2 == 0:
            char = pup.char
        else:
            char = '·'
        # Apply bob offset
        by = int(pup.bob_offset)
        self.draw_cell(ox, oy, pup.x, pup.y + by, char, pup.color, shake_x, shake_y)

    def draw_particle(self, ox, oy, particle, shake_x, shake_y):
        """Draw a particle."""
        if particle.life <= 0:
            return
        sx = ox + 1 + int(particle.x * 2) + shake_x
        sy = oy + 1 + int(particle.y) + shake_y
        if 0 <= sy < self.height and 0 <= sx < self.width - 1:
            try:
                alpha = particle.life / particle.max_life
                attr = curses.color_pair(particle.color)
                if alpha < 0.3:
                    attr |= curses.A_DIM
                self.stdscr.addstr(sy, sx, particle.char, attr)
            except curses.error:
                pass

    def draw_snake(self, ox, oy, snake, shake_x, shake_y):
        """Draw snake with head, body, and power-up effects."""
        for i, (x, y) in enumerate(snake.body):
            if i == 0:
                # Head
                char = '▲'
                if snake.direction == (0, 1):
                    char = '▼'
                elif snake.direction == (-1, 0):
                    char = '◄'
                elif snake.direction == (1, 0):
                    char = '►'

                color = 1  # Green head
                if snake.has_ghost:
                    color = 6  # Cyan for ghost
                elif snake.has_shield:
                    color = 6  # Cyan for shield
                elif snake.has_speed:
                    color = 3  # Yellow for speed

                self.draw_cell(ox, oy, x, y, char, color, shake_x, shake_y)

                # Shield indicator
                if snake.has_shield:
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        self.draw_cell(ox, oy, x + dx, y + dy, '○', 6, shake_x, shake_y)
            else:
                # Body
                color = 2 if i % 2 == 0 else 11  # Alternate cyan/green
                if snake.has_ghost:
                    color = 6
                # Body segment character based on direction
                char = '█'
                self.draw_cell(ox, oy, x, y, char, color, shake_x, shake_y)

    def draw_ui(self, state, ox, oy, gw):
        """Draw HUD: score, high score, level, mode, power-up timers."""
        # Top bar - score
        mode_info = MODES[state.mode_index]
        score_str = f" SCORE: {state.score} "
        self.safe_put(oy - 2, ox, score_str, 6)

        # High score
        hs = state.high_scores.get(state.mode, 0)
        hs_str = f" BEST: {hs} "
        self.safe_put(oy - 2, ox + gw - len(hs_str), hs_str, 3)

        # Level
        level_str = f" LEVEL: {state.level} "
        self.safe_put(oy - 1, ox, level_str, 6)

        # Mode
        mode_str = f" {mode_info['name'].upper()} "
        self.safe_put(oy - 1, ox + (gw - len(mode_str)) // 2, mode_str, 4)

        # Length
        len_str = f" LENGTH: {state.snake.length if state.snake else 0} "
        self.safe_put(oy - 1, ox + gw - len(len_str), len_str, 6)

        # Power-up timers (below game area)
        y = oy + state.grid_height + 2
        if state.snake:
            x = ox
            if state.snake.has_shield:
                t = max(0, int(state.snake.shield_timer))
                self.safe_put(y, x, f" 🛡 Shield: {t}s ", 6)
                x += 16
            if state.snake.has_speed:
                t = max(0, int(state.snake.speed_timer))
                self.safe_put(y, x, f" ⚡ Speed: {t}s ", 3)
                x += 16
            if state.snake.has_ghost:
                t = max(0, int(state.snake.ghost_timer))
                self.safe_put(y, x, f" 👻 Ghost: {t}s ", 6)
                x += 16
            if state.snake.has_slow:
                t = max(0, int(state.snake.slow_timer))
                self.safe_put(y, x, f" 🐌 Slow: {t}s ", 2)
                x += 16
            if state.snake.score_multiplier > 1.0:
                t = max(0, int(state.snake.multiplier_timer))
                self.safe_put(y, x, f" ✦ 2x Score: {t}s ", 5)

        # Controls hint
        hint = " [←/→/↑/↓] Move  [P] Pause  [R] Restart  [M] Menu  [Q] Quit "
        self.safe_put(oy + state.grid_height + 3, max(0, (self.width - len(hint)) // 2), hint, 6)

    def draw_level_complete(self, state):
        """Draw level complete overlay."""
        msg = " LEVEL COMPLETE! "
        msg2 = f" Level {state.level} → {state.level + 1}  Score: {state.score} "
        msg3 = " [Enter/Space] Continue  [R] Restart  [M] Menu "

        cy = self.height // 2
        cx = self.width // 2

        self.draw_box(cy - 2, cx - len(msg) // 2 - 2, 5, len(msg) + 4, 9)
        self.safe_put(cy - 1, cx - len(msg) // 2, msg, 9)
        self.safe_put(cy, cx - len(msg2) // 2, msg2, 9)
        self.safe_put(cy + 1, cx - len(msg3) // 2, msg3, 9)

    def draw_game_over(self, state):
        """Draw game over overlay."""
        msg = " GAME OVER "
        hs = state.high_scores.get(state.mode, 0)
        is_new = state.score >= hs and state.score > 0
        msg2 = f" Final Score: {state.score}  Best: {hs} {'★ NEW RECORD!' if is_new else ''} "
        msg3 = " [R] Restart  [M] Menu  [Q] Quit "

        cy = self.height // 2
        cx = self.width // 2

        self.draw_box(cy - 2, cx - len(msg) // 2 - 2, 5, len(msg) + 4, 8)
        self.safe_put(cy - 1, cx - len(msg) // 2, msg, 8)
        self.safe_put(cy, cx - len(msg2) // 2, msg2, 8)
        self.safe_put(cy + 1, cx - len(msg3) // 2, msg3, 8)

    def draw_paused(self, state):
        """Draw paused overlay."""
        msg = " PAUSED "
        msg2 = " [P] Resume  [R] Restart  [M] Menu  [Q] Quit "

        cy = self.height // 2
        cx = self.width // 2

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
                try:
                    self.stdscr.addch(y + dy, x + dx, ch, color)
                except curses.error:
                    pass

    def safe_put(self, y, x, text, color_pair, shake_x=0, shake_y=0):
        """Safely put string at position."""
        sy = y + shake_y
        sx = x + shake_x
        if 0 <= sy < self.height and 0 <= sx < self.width - 1:
            try:
                max_len = self.width - sx - 1
                clipped = text[:max_len]
                self.stdscr.addstr(sy, sx, clipped, curses.color_pair(color_pair) | curses.A_BOLD)
            except curses.error:
                pass

    def show_menu(self, stdscr, state):
        """Show main menu."""
        self.stdscr.erase()
        options = ["Resume", "Restart", "Mode Select", "Quit"]
        selected = 0

        while True:
            self.stdscr.erase()
            cy = self.height // 2
            cx = self.width // 2

            title = " S N A K E "
            self.stdscr.addstr(cy - 6, cx - len(title) // 2, title, curses.color_pair(1) | curses.A_BOLD)

            mode_info = MODES[state.mode_index]
            subtitle = f" Mode: {mode_info['name']}  •  Score: {state.score}  •  Level: {state.level} "
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
            elif key in (ord('q'), 27):
                return "quit"

    def show_mode_select(self, stdscr, state):
        """Show mode select screen."""
        self.stdscr.erase()
        selected = state.mode_index

        while True:
            self.stdscr.erase()
            cy = self.height // 2
            cx = self.width // 2

            title = " SELECT MODE "
            self.stdscr.addstr(cy - 8, cx - len(title) // 2, title, curses.color_pair(1) | curses.A_BOLD)

            for i, mode in enumerate(MODES):
                y = cy - 6 + i
                hs = state.high_scores.get(mode['id'], 0)
                prefix = " ► " if i == selected else "   "
                suffix = f"  [Best: {hs}]" if hs > 0 else ""
                color = curses.color_pair(3) | curses.A_BOLD if i == selected else curses.color_pair(6)
                line = f"{prefix}{mode['name']}: {mode['desc']}{suffix}"
                self.stdscr.addstr(y, cx - len(line) // 2, line, color)

            hint = " [↑/↓] Navigate  [Enter] Select  [Esc] Back "
            self.stdscr.addstr(cy + 4, cx - len(hint) // 2, hint, curses.color_pair(6))

            self.stdscr.refresh()

            key = self.stdscr.getch()
            if key in (curses.KEY_UP, ord('k'), ord('w')):
                selected = (selected - 1) % len(MODES)
            elif key in (curses.KEY_DOWN, ord('j'), ord('s')):
                selected = (selected + 1) % len(MODES)
            elif key in (curses.KEY_ENTER, 10, 13, ord(' ')):
                return selected
            elif key in (ord('q'), 27):
                return None


# Import at bottom to avoid circular
from world.levels import MODES