#!/usr/bin/env python3
"""
SPACE INVADERS — Classic Fixed Shooter
Alien waves, shields, UFO bonus, progressive difficulty.
"""

import curses
import time
import random
import traceback
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional


SAVE_FILE = Path.home() / ".invaders_save.json"

SCREEN_W = 80
SCREEN_H = 24
PLAYER_Y = SCREEN_H - 3

INVADER_ROWS = 5
INVADER_COLS = 11
INVADER_SPACING_X = 4
INVADER_SPACING_Y = 2
INVADER_START_X = 10
INVADER_START_Y = 3

SHIELD_COUNT = 4
SHIELD_Y = SCREEN_H - 8
SHIELD_W = 8
SHIELD_H = 4


@dataclass
class Invader:
    x: float
    y: float
    type: int  # 0, 1, 2 = points 30, 20, 10
    alive: bool = True
    anim_frame: int = 0


@dataclass
class Player:
    x: float = SCREEN_W // 2
    lives: int = 3
    cooldown: float = 0
    invulnerable: float = 0


@dataclass
class Shot:
    x: float
    y: float
    vy: float
    is_player: bool = True


@dataclass
class Shield:
    x: int
    y: int
    # 8x4 grid of blocks
    blocks: List[List[bool]] = field(default_factory=lambda: [[True]*8 for _ in range(4)])


@dataclass
class UFO:
    x: float = -10
    y: int = 1
    active: bool = False
    direction: int = 1
    spawn_timer: float = 0


@dataclass
class Explosion:
    x: float
    y: float
    timer: float = 0.3
    chars: List[str] = field(default_factory=lambda: ['*', 'X', '#', '+', '.'])


@dataclass
class GameState:
    player: Player = field(default_factory=Player)
    invaders: List[Invader] = field(default_factory=list)
    shots: List[Shot] = field(default_factory=list)
    shields: List[Shield] = field(default_factory=list)
    ufo: UFO = field(default_factory=UFO)
    explosions: List[Explosion] = field(default_factory=list)
    level: int = 1
    score: int = 0
    high_score: int = 0
    game_over: bool = False
    won: bool = False
    paused: bool = False
    invader_dir: int = 1
    invader_speed: float = 0.5
    invader_move_timer: float = 0
    invader_drop: bool = False
    last_shot_time: float = 0
    ufo_spawn_timer: float = 30

    def __post_init__(self):
        self.load_level()

    def load_level(self):
        self.invaders.clear()
        self.shots.clear()
        self.shields.clear()
        self.explosions.clear()
        self.ufo = UFO()
        self.invader_dir = 1
        self.invader_speed = max(0.1, 0.5 - (self.level - 1) * 0.04)
        self.invader_move_timer = 0
        self.invader_drop = False

        # Create invaders
        for row in range(INVADER_ROWS):
            for col in range(INVADER_COLS):
                x = INVADER_START_X + col * INVADER_SPACING_X
                y = INVADER_START_Y + row * INVADER_SPACING_Y
                inv_type = row // 2  # 0=top(30pts), 1=mid(20pts), 2=bottom(10pts)
                self.invaders.append(Invader(x, y, inv_type))

        # Create shields
        for i in range(SHIELD_COUNT):
            x = 8 + i * (SCREEN_W - 16) // (SHIELD_COUNT - 1)
            self.shields.append(Shield(x, SHIELD_Y))

        self.player.x = SCREEN_W // 2
        self.player.cooldown = 0
        self.player.invulnerable = 2.0  # Brief invulnerability on respawn
        self.ufo_spawn_timer = random.uniform(20, 40)

    def get_live_invaders(self) -> List[Invader]:
        return [inv for inv in self.invaders if inv.alive]

    def get_edges(self) -> tuple:
        live = self.get_live_invaders()
        if not live:
            return 0, 0
        min_x = min(inv.x for inv in live)
        max_x = max(inv.x for inv in live)
        return min_x, max_x

    def update_invaders(self, dt: float):
        if not self.get_live_invaders():
            self.won = True
            return

        self.invader_move_timer += dt
        move_interval = self.invader_speed * (1.0 - len(self.get_live_invaders()) / (INVADER_ROWS * INVADER_COLS) * 0.7)

        if self.invader_move_timer >= move_interval:
            self.invader_move_timer = 0
            min_x, max_x = self.get_edges()

            # Check edge collision
            if (self.invader_dir > 0 and max_x >= SCREEN_W - 8) or \
               (self.invader_dir < 0 and min_x <= 8):
                # Drop down and reverse
                for inv in self.get_live_invaders():
                    inv.y += INVADER_SPACING_Y
                    inv.anim_frame = 1 - inv.anim_frame
                self.invader_dir *= -1
                self.invader_drop = True

                # Check game over (invaders reach player)
                if any(inv.y >= PLAYER_Y - 2 for inv in self.get_live_invaders()):
                    self.game_over = True
            else:
                for inv in self.get_live_invaders():
                    inv.x += self.invader_dir * INVADER_SPACING_X
                    inv.anim_frame = 1 - inv.anim_frame

        # Invader shooting
        if random.random() < 0.003 * len(self.get_live_invaders()):
            shooter = random.choice(self.get_live_invaders())
            self.shots.append(Shot(shooter.x + 1, shooter.y + 1, 3.0, is_player=False))

    def update_ufo(self, dt: float):
        self.ufo_spawn_timer -= dt
        if not self.ufo.active and self.ufo_spawn_timer <= 0:
            self.ufo.active = True
            self.ufo.x = -5 if random.random() < 0.5 else SCREEN_W + 5
            self.ufo.direction = 1 if self.ufo.x < 0 else -1
            self.ufo.y = 1

        if self.ufo.active:
            self.ufo.x += self.ufo.direction * 4 * dt * 60
            if self.ufo.x < -10 or self.ufo.x > SCREEN_W + 10:
                self.ufo.active = False
                self.ufo_spawn_timer = random.uniform(20, 40)

    def update_shots(self, dt: float):
        for shot in self.shots[:]:
            shot.y += shot.vy * dt * 60

            # Off screen
            if shot.y < 0 or shot.y >= SCREEN_H:
                self.shots.remove(shot)
                continue

            if shot.is_player:
                # Player shot - check invader hit
                for inv in self.get_live_invaders():
                    if (abs(shot.x - inv.x) < 1.5 and abs(shot.y - inv.y) < 1):
                        inv.alive = False
                        self.shots.remove(shot)
                        points = [30, 20, 10][inv.type]
                        self.score += points * self.level
                        self.explosions.append(Explosion(inv.x, inv.y))
                        break

                # Check UFO hit
                if self.ufo.active and abs(shot.x - self.ufo.x) < 2 and abs(shot.y - self.ufo.y) < 1:
                    self.shots.remove(shot)
                    self.ufo.active = False
                    self.score += random.choice([50, 100, 150, 300]) * self.level
                    self.explosions.append(Explosion(self.ufo.x, self.ufo.y))
                    self.ufo_spawn_timer = random.uniform(20, 40)

                # Check shield hit
                for shield in self.shields:
                    rel_x = int(shot.x - shield.x)
                    rel_y = int(shot.y - shield.y)
                    if 0 <= rel_x < SHIELD_W and 0 <= rel_y < SHIELD_H:
                        if shield.blocks[rel_y][rel_x]:
                            shield.blocks[rel_y][rel_x] = False
                            self.shots.remove(shot)
                            break

            else:
                # Invader shot - check player hit
                if (self.player.invulnerable <= 0 and
                    abs(shot.x - self.player.x) < 2 and
                    abs(shot.y - PLAYER_Y) < 1):
                    self.shots.remove(shot)
                    self.player.lives -= 1
                    self.player.invulnerable = 2.0
                    self.explosions.append(Explosion(self.player.x, PLAYER_Y))
                    if self.player.lives <= 0:
                        self.game_over = True

                # Check shield hit
                for shield in self.shields:
                    rel_x = int(shot.x - shield.x)
                    rel_y = int(shot.y - shield.y)
                    if 0 <= rel_x < SHIELD_W and 0 <= rel_y < SHIELD_H:
                        if shield.blocks[rel_y][rel_x]:
                            shield.blocks[rel_y][rel_x] = False
                            self.shots.remove(shot)
                            break

    def update(self, dt: float):
        if self.paused or self.game_over or self.won:
            return

        # Update timers
        if self.player.cooldown > 0:
            self.player.cooldown -= dt
        if self.player.invulnerable > 0:
            self.player.invulnerable -= dt

        for exp in self.explosions[:]:
            exp.timer -= dt
            if exp.timer <= 0:
                self.explosions.remove(exp)

        self.update_invaders(dt)
        self.update_ufo(dt)
        self.update_shots(dt)

        # Check win
        if not self.get_live_invaders():
            self.won = True

        # Next level
        if self.won:
            time.sleep(1)
            self.level += 1
            self.load_level()

    def fire(self):
        if self.player.cooldown <= 0 and len([s for s in self.shots if s.is_player]) < 2:
            self.shots.append(Shot(self.player.x, PLAYER_Y - 1, -6.0, is_player=True))
            self.player.cooldown = 0.3

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

        # Player movement
        if self.any_held({curses.KEY_LEFT, ord('a'), ord('A'), ord('h'), ord('H')}):
            state.player.x = max(2, state.player.x - 0.8)
        if self.any_held({curses.KEY_RIGHT, ord('d'), ord('D'), ord('l'), ord('L')}):
            state.player.x = min(SCREEN_W - 2, state.player.x + 0.8)

        # Fire
        if self.any_held({ord(' '), curses.KEY_UP, ord('w'), ord('W'), curses.KEY_ENTER, 10, 13}):
            state.fire()

        return None


class Renderer:
    INVADER_SPRITES = {
        0: ['<=>', '<=>'],  # Top - 30 pts
        1: ['[=]', '[=]'],  # Mid - 20 pts
        2: ['( )', '( )'],  # Bot - 10 pts
    }

    def __init__(self, stdscr):
        self.stdscr = stdscr

    def render(self, state: GameState):
        self.stdscr.erase()
        h, w = self.stdscr.getmaxyx()

        for i in range(1, 8):
            curses.init_pair(i, i, -1)

        # Draw invaders
        for inv in state.get_live_invaders():
            sprites = self.INVADER_SPRITES[inv.type]
            sprite = sprites[inv.anim_frame]
            x, y = int(inv.x), int(inv.y)
            if 0 <= y < SCREEN_H:
                color = 3 if inv.type == 0 else (5 if inv.type == 1 else 2)
                self.stdscr.addstr(y, max(0, x - 1), sprite, curses.color_pair(color))

        # Draw player
        if state.player.invulnerable <= 0 or int(time.time() * 10) % 2 == 0:
            self.stdscr.addstr(PLAYER_Y, int(state.player.x) - 2, '▄███▄', curses.color_pair(6))

        # Draw shots
        for shot in state.shots:
            x, y = int(shot.x), int(shot.y)
            if 0 <= y < SCREEN_H:
                char = '│' if shot.is_player else '┃'
                color = 3 if shot.is_player else 1
                self.stdscr.addstr(y, x, char, curses.color_pair(color))

        # Draw shields
        for shield in state.shields:
            for ry in range(SHIELD_H):
                for rx in range(SHIELD_W):
                    if shield.blocks[ry][rx]:
                        self.stdscr.addstr(shield.y + ry, shield.x + rx, '█', curses.color_pair(2))

        # Draw UFO
        if state.ufo.active:
            x = int(state.ufo.x)
            if 0 <= x < SCREEN_W - 6:
                self.stdscr.addstr(state.ufo.y, x, '<◆◆◆>', curses.color_pair(5) | curses.A_BOLD)

        # Draw explosions
        for exp in state.explosions:
            x, y = int(exp.x), int(exp.y)
            if 0 <= y < SCREEN_H:
                idx = min(len(exp.chars) - 1, int((0.3 - exp.timer) * 10))
                self.stdscr.addstr(y, x, exp.chars[idx], curses.color_pair(3))

        # HUD
        self.stdscr.addstr(SCREEN_H - 1, 2, f" SCORE: {state.score} ", curses.color_pair(3))
        self.stdscr.addstr(SCREEN_H - 1, 20, f" BEST: {max(state.high_score, state.score)} ", curses.color_pair(5))
        self.stdscr.addstr(SCREEN_H - 1, 40, f" LEVEL: {state.level} ", curses.color_pair(4))
        self.stdscr.addstr(SCREEN_H - 1, 55, f" LIVES: {'▲' * state.player.lives} ", curses.color_pair(1))

        # Game over / level clear
        if state.game_over:
            self.draw_overlay("GAME OVER", f"FINAL SCORE: {state.score}", "R - Restart  Q/M - Menu")
        elif state.won:
            self.draw_overlay(f"LEVEL {state.level} CLEAR!", f"SCORE: {state.score}", "Next level starting...")

        self.stdscr.refresh()

    def draw_overlay(self, *lines):
        oy = SCREEN_H // 2 - len(lines)
        ox = SCREEN_W // 2 - 15
        self.stdscr.addstr(oy, ox, '╔' + '═' * 28 + '╗', curses.color_pair(1))
        for i, line in enumerate(lines):
            self.stdscr.addstr(oy + 1 + i, ox, '║' + line.center(28) + '║', curses.color_pair(1))
        self.stdscr.addstr(oy + len(lines) + 1, ox, '╚' + '═' * 28 + '╝', curses.color_pair(1))


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