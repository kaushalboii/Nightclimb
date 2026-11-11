#!/usr/bin/env python3
"""
BREAKOUT — Classic Paddle & Bricks
Power-ups, multi-ball, 20 levels, paddle physics.
"""

import curses
import time
import random
import traceback
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional


SAVE_FILE = Path.home() / ".breakout_save.json"

SCREEN_W = 80
SCREEN_H = 24
PADDLE_W = 10
PADDLE_Y = SCREEN_H - 3
BALL_RADIUS = 1

# Brick layout: 10 rows x 12 cols = 120 bricks max
BRICK_ROWS = 8
BRICK_COLS = 12
BRICK_W = 6
BRICK_H = 1


@dataclass
class Ball:
    x: float = SCREEN_W // 2
    y: float = PADDLE_Y - 2
    vx: float = 0
    vy: float = 0
    radius: int = 1
    speed: float = 8.0
    launched: bool = False

    def launch(self, angle: float = -1.0):
        self.vx = self.speed * 0.7 * angle
        self.vy = -self.speed
        self.launched = True

    def update(self, dt: float):
        if not self.launched:
            return
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60

    def reflect_x(self):
        self.vx = -self.vx

    def reflect_y(self):
        self.vy = -abs(self.vy)


@dataclass
class Paddle:
    x: float = (SCREEN_W - PADDLE_W) // 2
    width: int = PADDLE_W
    y: int = PADDLE_Y
    vx: float = 0
    speed: float = 12.0

    def update(self, dt: float, target_x: Optional[float] = None):
        if target_x is not None:
            # Move toward target
            diff = target_x - (self.x + self.width / 2)
            if abs(diff) > 0.5:
                self.vx = self.speed if diff > 0 else -self.speed
            else:
                self.vx = 0
        self.x += self.vx * dt * 60
        # Clamp
        self.x = max(1, min(SCREEN_W - self.width - 1, self.x))


@dataclass
class Brick:
    x: int
    y: int
    color: int
    hits: int = 1
    powerup_type: Optional[str] = None

    @property
    def rect(self):
        return (self.x, self.y, self.x + BRICK_W, self.y + BRICK_H)


@dataclass
class PowerUp:
    x: float
    y: float
    type: str  # 'wide', 'multi', 'slow', 'fast', 'life', 'catch'
    vy: float = 2.0
    char: str = '?'
    color: int = 3

    POWERUP_TYPES = {
        'wide': {'char': 'W', 'color': 2, 'name': 'Wide Paddle'},
        'multi': {'char': 'M', 'color': 5, 'name': 'Multi-Ball'},
        'slow': {'char': 'S', 'color': 6, 'name': 'Slow Ball'},
        'fast': {'char': 'F', 'color': 1, 'name': 'Fast Ball'},
        'life': {'char': '♥', 'color': 1, 'name': 'Extra Life'},
        'catch': {'char': 'C', 'color': 3, 'name': 'Catch Ball'},
    }

    def __post_init__(self):
        info = self.POWERUP_TYPES.get(self.type, self.POWERUP_TYPES['wide'])
        self.char = info['char']
        self.color = info['color']

    def update(self, dt: float):
        self.y += self.vy * dt * 60


@dataclass
class GameState:
    paddle: Paddle = field(default_factory=Paddle)
    balls: List[Ball] = field(default_factory=lambda: [Ball()])
    bricks: List[Brick] = field(default_factory=list)
    powerups: List[PowerUp] = field(default_factory=list)
    level: int = 1
    score: int = 0
    high_score: int = 0
    lives: int = 3
    game_over: bool = False
    won: bool = False
    paused: bool = False
    catch_mode: bool = False
    catch_timer: float = 0
    wide_timer: float = 0
    level_start_time: float = 0

    def __post_init__(self):
        self.load_level()

    def load_level(self):
        self.bricks.clear()
        self.powerups.clear()
        self.balls = [Ball()]
        self.paddle = Paddle()
        self.catch_mode = False
        self.catch_timer = 0
        self.wide_timer = 0
        self.level_start_time = time.time()

        # Create brick pattern based on level
        colors = [1, 3, 5, 2, 4, 6]
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                # Skip some bricks for pattern variety
                if (row + col + self.level) % 3 == 0 and self.level > 3:
                    continue
                x = 4 + col * (BRICK_W + 1)
                y = 3 + row * (BRICK_H + 1)
                hits = 1 + (self.level - 1) // 3
                color = colors[row % len(colors)]

                # Random powerup chance
                powerup = None
                if random.random() < 0.08:
                    powerup = random.choice(list(PowerUp.POWERUP_TYPES.keys()))

                self.bricks.append(Brick(x, y, color, hits, powerup))

    def check_collisions(self):
        for ball in self.balls[:]:
            if not ball.launched:
                continue

            # Wall collisions
            if ball.x - ball.radius <= 1:
                ball.x = 1 + ball.radius
                ball.reflect_x()
            elif ball.x + ball.radius >= SCREEN_W - 1:
                ball.x = SCREEN_W - 1 - ball.radius
                ball.reflect_x()

            if ball.y - ball.radius <= 1:
                ball.y = 1 + ball.radius
                ball.reflect_y()

            # Bottom - lose life
            if ball.y + ball.radius >= SCREEN_H:
                self.balls.remove(ball)
                continue

            # Paddle collision
            paddle_left = self.paddle.x
            paddle_right = self.paddle.x + self.paddle.width
            if (ball.y + ball.radius >= self.paddle.y and
                ball.y - ball.radius <= self.paddle.y + 1 and
                ball.x + ball.radius >= paddle_left and
                ball.x - ball.radius <= paddle_right):

                # Calculate bounce angle based on hit position
                hit_pos = (ball.x - (self.paddle.x + self.paddle.width / 2)) / (self.paddle.width / 2)
                hit_pos = max(-1, min(1, hit_pos))
                ball.x = self.paddle.y - ball.radius
                ball.reflect_y()
                ball.vx = ball.speed * 0.7 * hit_pos
                self.catch_mode = False

            # Brick collisions
            for brick in self.bricks[:]:
                bx1, by1, bx2, by2 = brick.rect
                if (ball.x + ball.radius >= bx1 and ball.x - ball.radius <= bx2 and
                    ball.y + ball.radius >= by1 and ball.y - ball.radius <= by2):

                    # Determine hit side
                    overlap_x = min(ball.x + ball.radius, bx2) - max(ball.x - ball.radius, bx1)
                    overlap_y = min(ball.y + ball.radius, by2) - max(ball.y - ball.radius, by1)

                    if overlap_x < overlap_y:
                        ball.reflect_x()
                    else:
                        ball.reflect_y()

                    brick.hits -= 1
                    self.score += 10 * self.level

                    if brick.hits <= 0:
                        self.bricks.remove(brick)
                        self.score += 50 * self.level
                        # Spawn powerup
                        if brick.powerup_type:
                            self.powerups.append(PowerUp(
                                brick.x + BRICK_W / 2,
                                brick.y + BRICK_H / 2,
                                brick.powerup_type
                            ))
                    break

    def check_powerups(self):
        for pup in self.powerups[:]:
            pup.update(1/60)
            # Check paddle catch
            if (pup.y >= self.paddle.y - 1 and
                pup.x >= self.paddle.x and pup.x <= self.paddle.x + self.paddle.width):
                self.apply_powerup(pup.type)
                self.powerups.remove(pup)
            elif pup.y > SCREEN_H:
                self.powerups.remove(pup)

    def apply_powerup(self, ptype: str):
        if ptype == 'wide':
            self.paddle.width = min(20, self.paddle.width + 4)
            self.wide_timer = 15.0
        elif ptype == 'multi':
            # Add 2 more balls
            for _ in range(2):
                new_ball = Ball()
                new_ball.x = self.balls[0].x
                new_ball.y = self.balls[0].y
                new_ball.launched = True
                new_ball.vx = random.uniform(-0.7, 0.7) * new_ball.speed
                new_ball.vy = -new_ball.speed
                self.balls.append(new_ball)
        elif ptype == 'slow':
            for ball in self.balls:
                ball.speed = max(4.0, ball.speed * 0.7)
        elif ptype == 'fast':
            for ball in self.balls:
                ball.speed = min(16.0, ball.speed * 1.3)
        elif ptype == 'life':
            self.lives = min(5, self.lives + 1)
        elif ptype == 'catch':
            self.catch_mode = True
            self.catch_timer = 10.0

    def update(self, dt: float):
        if self.paused or self.game_over or self.won:
            return

        # Update timers
        if self.wide_timer > 0:
            self.wide_timer -= dt
            if self.wide_timer <= 0:
                self.paddle.width = PADDLE_W

        if self.catch_timer > 0:
            self.catch_timer -= dt
            if self.catch_timer <= 0:
                self.catch_mode = False

        # Auto-launch stuck balls
        for ball in self.balls:
            if not ball.launched:
                ball.x = self.paddle.x + self.paddle.width / 2
                if random.random() < 0.02:  # Random auto-launch
                    ball.launch(random.uniform(-0.5, 0.5))

        # Update paddle
        self.paddle.update(dt)

        # Update balls
        for ball in self.balls:
            ball.update(dt)

        self.check_collisions()
        self.check_powerups()

        # Check win
        if not self.bricks:
            self.won = True
            self.level += 1
            if self.level > 20:
                self.game_over = True
            else:
                # Brief pause then next level
                time.sleep(1)
                self.load_level()

        # Check game over
        if not self.balls:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                # Reset ball
                self.balls = [Ball()]

    def save(self, path: Path):
        data = {"high_score": max(self.high_score, self.score)}
        try:
            import json
            with open(path, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass

    def load(self, path: Path):
        try:
            import json
            if path.exists():
                with open(path, 'r') as f:
                    data = json.load(f)
                self.high_score = data.get("high_score", 0)
        except Exception:
            pass


class InputHandler:
    HOLD_GRACE = 0.15

    def __init__(self):
        self.held = set()
        self.pressed = set()
        self._last_seen = {}
        self._pressed_this_frame = set()

    def poll(self, stdscr):
        now = time.time()
        self.pressed.clear()
        self._pressed_this_frame.clear()

        while True:
            key = stdscr.getch()
            if key == -1:
                break
            self._last_seen[key] = now
            if key not in self.held:
                self.held.add(key)
                self.pressed.add(key)
                self._pressed_this_frame.add(key)

        keys_to_release = set()
        for key in self.held:
            if key in {curses.KEY_LEFT, curses.KEY_RIGHT, ord('a'), ord('d'), ord(' ')}:
                last = self._last_seen.get(key, 0)
                if now - last > self.HOLD_GRACE:
                    keys_to_release.add(key)
            elif key not in self._pressed_this_frame:
                keys_to_release.add(key)

        self.held -= keys_to_release

    def any_held(self, key_set):
        return any(k in self.held for k in key_set)

    def any_pressed(self, key_set):
        return any(k in self.pressed for k in key_set)

    def update(self, state: GameState, stdscr) -> Optional[str]:
        self.poll(stdscr)

        if state.game_over or state.won:
            if self.any_pressed({ord('r'), ord('R'), curses.KEY_ENTER, 10, 13}):
                return "restart"
            if self.any_pressed({ord('q'), 27, ord('m'), ord('M')}):
                return "menu"
            return None

        if self.any_pressed({ord('p'), ord('P')}):
            return "pause"
        if self.any_pressed({ord('q'), 27, ord('m'), ord('M')}):
            return "menu"
        if self.any_pressed({ord('r'), ord('R')}):
            return "restart"

        # Paddle movement
        target_x = None
        if self.any_held({curses.KEY_LEFT, ord('a'), ord('A'), ord('h'), ord('H')}):
            target_x = self.paddle.x - 1
        if self.any_held({curses.KEY_RIGHT, ord('d'), ord('D'), ord('l'), ord('L')}):
            target_x = self.paddle.x + self.paddle.width + 1

        # Mouse-like: move paddle toward target
        if target_x is not None:
            state.paddle.update(1/60, target_x)
        else:
            state.paddle.update(1/60)

        # Launch ball
        if self.any_pressed({ord(' '), curses.KEY_UP, ord('w'), ord('W')}):
            for ball in state.balls:
                if not ball.launched:
                    ball.launch(random.uniform(-0.5, 0.5))

        return None


class Renderer:
    def __init__(self, stdscr):
        self.stdscr = stdscr

    def render(self, state: GameState):
        self.stdscr.erase()
        h, w = self.stdscr.getmaxyx()

        # Colors
        for i in range(1, 8):
            curses.init_pair(i, i, -1)

        # Draw border
        self.stdscr.addstr(0, 0, '╔' + '═' * (SCREEN_W - 2) + '╗', curses.color_pair(6))
        for y in range(1, SCREEN_H - 1):
            self.stdscr.addstr(y, 0, '║', curses.color_pair(6))
            self.stdscr.addstr(y, SCREEN_W - 1, '║', curses.color_pair(6))
        self.stdscr.addstr(SCREEN_H - 1, 0, '╚' + '═' * (SCREEN_W - 2) + '╝', curses.color_pair(6))

        # Draw bricks
        for brick in state.bricks:
            for i in range(BRICK_W):
                self.stdscr.addstr(brick.y, brick.x + i, '█', curses.color_pair(brick.color))

        # Draw balls
        for ball in state.balls:
            if ball.launched:
                x, y = int(ball.x), int(ball.y)
                if 0 <= x < SCREEN_W and 0 <= y < SCREEN_H:
                    self.stdscr.addstr(y, x, '●', curses.color_pair(3))

        # Draw paddle
        paddle_str = '█' * state.paddle.width
        self.stdscr.addstr(state.paddle.y, int(state.paddle.x), paddle_str, curses.color_pair(2))

        # Draw powerups
        for pup in state.powerups:
            x, y = int(pup.x), int(pup.y)
            if 0 <= x < SCREEN_W and 0 <= y < SCREEN_H:
                self.stdscr.addstr(y, x, pup.char, curses.color_pair(pup.color) | curses.A_BOLD)

        # HUD
        self.stdscr.addstr(SCREEN_H - 1, 2, f" SCORE: {state.score} ", curses.color_pair(3))
        self.stdscr.addstr(SCREEN_H - 1, 18, f" BEST: {max(state.high_score, state.score)} ", curses.color_pair(5))
        self.stdscr.addstr(SCREEN_H - 1, 35, f" LEVEL: {state.level} ", curses.color_pair(4))
        self.stdscr.addstr(SCREEN_H - 1, 48, f" LIVES: {'♥' * state.lives} ", curses.color_pair(1))

        # Game over / win
        if state.game_over:
            self.draw_overlay("GAME OVER", "R - Restart  Q/M - Menu")
        elif state.won and state.level > 20:
            self.draw_overlay("YOU WIN!", f"FINAL SCORE: {state.score}", "R - Restart  Q/M - Menu")

        self.stdscr.refresh()

    def draw_overlay(self, *lines):
        oy = SCREEN_H // 2 - len(lines) - 1
        ox = SCREEN_W // 2 - 12
        self.stdscr.addstr(oy, ox, '╔' + '═' * 22 + '╗', curses.color_pair(1))
        for i, line in enumerate(lines):
            self.stdscr.addstr(oy + 1 + i, ox, '║' + line.center(22) + '║', curses.color_pair(1))
        self.stdscr.addstr(oy + len(lines) + 1, ox, '╚' + '═' * 22 + '╝', curses.color_pair(1))


def main(stdscr):
    try:
        _main_loop(stdscr)
    except Exception as e:
        stdscr.nodelay(False)
        stdscr.erase()
        stdscr.addstr(0, 0, f"ERROR: {e}")
        stdscr.addstr(1, 0, traceback.format_exc())
        stdscr.addstr(20, 0, "Press any key to exit...")
        stdscr.refresh()
        stdscr.getch()


def _main_loop(stdscr):
    curses.curs_set(0)
    stdscr.timeout(16)
    stdscr.keypad(True)
    curses.noecho()
    curses.start_color()
    curses.use_default_colors()

    for i in range(1, 8):
        curses.init_pair(i, i, -1)

    renderer = Renderer(stdscr)
    input_handler = InputHandler()
    state = GameState()
    state.load(SAVE_FILE)

    last_time = time.time()

    while True:
        current_time = time.time()
        dt = min(current_time - last_time, 0.1)
        last_time = current_time

        action = input_handler.update(state, stdscr)
        if action == "quit" or action == "menu":
            state.save(SAVE_FILE)
            break
        elif action == "pause":
            state.paused = not state.paused
        elif action == "restart":
            state = GameState()
            state.load(SAVE_FILE)

        state.update(dt)
        renderer.render(state)

    state.save(SAVE_FILE)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass