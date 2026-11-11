#!/usr/bin/env python3
"""
PAC-MAN — Classic Maze Chase
4 ghosts, power pellets, fruit bonus, intermissions.
"""

import curses
import time
import random
import traceback
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


SAVE_FILE = Path.home() / ".pacman_save.json"

# Maze (1 = wall, 0 = dot, 2 = power pellet, 3 = empty)
MAZE = [
    "####################",
    "#........##........#",
    "#.####.##.##.####.#",
    "#o####.##.##.####o#",
    "#..................#",
    "#.####.######.####.#",
    "#......##....##....#",
    "######.## #### ##.##",
    "     #.##        ## #",
    "     #.## ###### ## #",
    "     #.## #      # ##",
    "######.## #      # ##",
    "      .    #      #  ",
    "######.## #      # ##",
    "     #.## ###### ## #",
    "     #.##        ## #",
     "     #.## ###### ## #",
    "######.##        ## #",
    "#........##........#",
    "#.####.##.##.####.#",
    "#o..##........##..o#",
    "###.##.## #### ##.##",
    "#......##....##....#",
    "#.##########.########",
    "#..................#",
    "####################",
]

MAZE_H = len(MAZE)
MAZE_W = len(MAZE[0])
TILE_W = 2  # Each tile is 2 chars wide for aspect ratio

SCREEN_W = MAZE_W * TILE_W
SCREEN_H = MAZE_H + 4  # Extra for HUD

GHOST_STARTS = [
    (13, 11),  # Blinky (red)
    (14, 11),  # Pinky (pink)
    (15, 11),  # Inky (cyan)
    (16, 11),  # Clyde (orange)
]

PACMAN_START = (13, 20)

FRUIT_POS = (13, 17)
FRUIT_SCORES = [100, 300, 500, 700, 1000, 2000, 3000, 5000]
FRUIT_CHARS = ['🍒', '🍓', '🍊', '🍎', '🍑', '🍇', '🍈', '🔑']


@dataclass
class PacMan:
    x: float = PACMAN_START[0]
    y: float = PACMAN_START[1]
    direction: Tuple[int, int] = (0, 0)
    next_direction: Tuple[int, int] = (0, 0)
    speed: float = 0.15  # tiles per frame at 60fps
    anim_frame: int = 0
    anim_timer: float = 0
    lives: int = 3
    invulnerable: float = 0


@dataclass
class Ghost:
    x: float
    y: float
    color: int
    name: str
    target_x: float = 0
    target_y: float = 0
    state: str = 'house'  # house, chase, scatter, frightened, eaten
    direction: Tuple[int, int] = (0, -1)
    speed: float = 0.13
    fright_timer: float = 0
    release_timer: float = 0


@dataclass
class Fruit:
    x: int
    y: int
    type: int = 0
    timer: float = 10.0
    active: bool = False


@dataclass
class GameState:
    maze: List[List[int]] = field(default_factory=list)
    pacman: PacMan = field(default_factory=PacMan)
    ghosts: List[Ghost] = field(default_factory=list)
    fruit: Fruit = field(default_factory=lambda: Fruit(*FRUIT_POS))
    score: int = 0
    high_score: int = 0
    level: int = 1
    dots_remaining: int = 0
    game_over: bool = False
    won: bool = False
    paused: bool = False
    ready_timer: float = 3.0
    scatter_timer: float = 0
    scatter_mode: bool = False
    fruit_eaten_count: int = 0

    def __post_init__(self):
        self.load_level()

    def load_level(self):
        self.maze = []
        self.dots_remaining = 0
        self.pacman = PacMan()
        self.ghosts = []
        self.fruit = Fruit(*FRUIT_POS)
        self.ready_timer = 3.0
        self.scatter_timer = 0
        self.scatter_mode = False

        # Parse maze
        for row, line in enumerate(MAZE):
            maze_row = []
            for col, char in enumerate(line):
                if char == '#':
                    maze_row.append(1)  # Wall
                elif char == '.':
                    maze_row.append(0)  # Dot
                    self.dots_remaining += 1
                elif char == 'o':
                    maze_row.append(2)  # Power pellet
                    self.dots_remaining += 1
                else:
                    maze_row.append(3)  # Empty
            self.maze.append(maze_row)

        # Create ghosts
        ghost_data = [
            (1, 'Blinky', 0),   # Red - chases directly
            (5, 'Pinky', 0),    # Pink - ambushes
            (6, 'Inky', 0),     # Cyan - complex
            (3, 'Clyde', 0),    # Orange - random
        ]
        for i, (color, name, _) in enumerate(ghost_data):
            sx, sy = GHOST_STARTS[i]
            self.ghosts.append(Ghost(sx, sy, color, name, release_timer=i * 2.0))

    def is_wall(self, x: int, y: int) -> bool:
        if 0 <= y < MAZE_H and 0 <= x < MAZE_W:
            return self.maze[y][x] == 1
        return True

    def can_move(self, x: float, y: float, direction: Tuple[int, int]) -> bool:
        """Check if pacman/ghost can move in direction from position."""
        nx, ny = x + direction[0], y + direction[1]
        # Check center of next tile
        return not self.is_wall(int(nx), int(ny))

    def get_valid_directions(self, x: float, y: float, current_dir: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid movement directions (no 180° turns)."""
        dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        valid = []
        for d in dirs:
            # Prevent 180-degree turns
            if d[0] == -current_dir[0] and d[1] == -current_dir[1]:
                continue
            if self.can_move(x, y, d):
                valid.append(d)
        return valid

    def update_pacman(self, dt: float):
        if self.ready_timer > 0:
            return

        # Animation
        self.pacman.anim_timer += dt
        if self.pacman.anim_timer > 0.1:
            self.pacman.anim_frame = 1 - self.pacman.anim_frame
            self.pacman.anim_timer = 0

        # Try to change direction
        if self.pacman.next_direction != (0, 0):
            if self.can_move(self.pacman.x, self.pacman.y, self.pacman.next_direction):
                self.pacman.direction = self.pacman.next_direction
                self.pacman.next_direction = (0, 0)

        # Move
        if self.pacman.direction != (0, 0):
            self.pacman.x += self.pacman.direction[0] * self.pacman.speed * 60 * dt
            self.pacman.y += self.pacman.direction[1] * self.pacman.speed * 60 * dt

            # Snap to grid center when close
            if abs(self.pacman.x - round(self.pacman.x)) < 0.05:
                self.pacman.x = round(self.pacman.x)
            if abs(self.pacman.y - round(self.pacman.y)) < 0.05:
                self.pacman.y = round(self.pacman.y)

            # Tunnel wrap
            if self.pacman.x < 0:
                self.pacman.x = MAZE_W - 1
            elif self.pacman.x >= MAZE_W:
                self.pacman.x = 0

        # Eat dots/pellets
        tx, ty = int(self.pacman.x), int(self.pacman.y)
        if 0 <= ty < MAZE_H and 0 <= tx < MAZE_W:
            if self.maze[ty][tx] == 0:  # Dot
                self.maze[ty][tx] = 3
                self.dots_remaining -= 1
                self.score += 10
            elif self.maze[ty][tx] == 2:  # Power pellet
                self.maze[ty][tx] = 3
                self.dots_remaining -= 1
                self.score += 50
                self.frighten_ghosts()

        # Check fruit
        if self.fruit.active and tx == self.fruit.x and ty == self.fruit.y:
            self.score += FRUIT_SCORES[min(self.fruit.type, len(FRUIT_SCORES) - 1)]
            self.fruit.active = False
            self.fruit_eaten_count += 1

        # Invulnerability
        if self.pacman.invulnerable > 0:
            self.pacman.invulnerable -= dt

        # Win check
        if self.dots_remaining == 0:
            self.won = True

    def frighten_ghosts(self):
        for ghost in self.ghosts:
            if ghost.state != 'eaten':
                ghost.state = 'frightened'
                ghost.fright_timer = 8.0 - self.level * 0.5
                ghost.speed = 0.08
                # Reverse direction
                ghost.direction = (-ghost.direction[0], -ghost.direction[1])

    def update_ghosts(self, dt: float):
        if self.ready_timer > 0:
            for ghost in self.ghosts:
                if ghost.release_timer > 0:
                    ghost.release_timer -= dt
            return

        # Scatter/chase mode timer
        if self.scatter_timer > 0:
            self.scatter_timer -= dt
            if self.scatter_timer <= 0:
                self.scatter_mode = not self.scatter_mode
                self.scatter_timer = 7.0 if self.scatter_mode else 20.0
                # Reverse all ghost directions
                for ghost in self.ghosts:
                    if ghost.state in ('chase', 'scatter'):
                        ghost.direction = (-ghost.direction[0], -ghost.direction[1])

        # Initialize scatter timer
        if self.scatter_timer == 0:
            self.scatter_mode = True
            self.scatter_timer = 7.0

        for ghost in self.ghosts:
            # Release from house
            if ghost.release_timer > 0:
                ghost.release_timer -= dt
                if ghost.release_timer <= 0:
                    ghost.state = 'chase'
                continue

            # Frightened timer
            if ghost.state == 'frightened':
                ghost.fright_timer -= dt
                if ghost.fright_timer <= 0:
                    ghost.state = 'chase'
                    ghost.speed = 0.13

            # Eaten state - return to house
            if ghost.state == 'eaten':
                ghost.speed = 0.25
                # Move toward house center
                tx, ty = 13, 11
                if abs(ghost.x - tx) < 0.5 and abs(ghost.y - ty) < 0.5:
                    ghost.x, ghost.y = tx, ty
                    ghost.state = 'house'
                    ghost.release_timer = 2.0
                    ghost.speed = 0.13
                    ghost.direction = (0, -1)
                continue

            # Determine target
            if ghost.state == 'frightened':
                # Random movement
                valid = self.get_valid_directions(ghost.x, ghost.y, ghost.direction)
                if valid and random.random() < 0.1:
                    ghost.direction = random.choice(valid)
            elif ghost.state == 'house':
                # Move up and down in house
                if ghost.y <= 10:
                    ghost.direction = (0, 1)
                elif ghost.y >= 12:
                    ghost.direction = (0, -1)
            else:
                # Chase or scatter
                self.set_ghost_target(ghost)

            # Move ghost
            if self.can_move(ghost.x, ghost.y, ghost.direction):
                ghost.x += ghost.direction[0] * ghost.speed * 60 * dt
                ghost.y += ghost.direction[1] * ghost.speed * 60 * dt
            else:
                # Pick new direction
                valid = self.get_valid_directions(ghost.x, ghost.y, ghost.direction)
                if valid:
                    ghost.direction = self.choose_best_direction(ghost, valid)

            # Tunnel wrap
            if ghost.x < 0:
                ghost.x = MAZE_W - 1
            elif ghost.x >= MAZE_W:
                ghost.x = 0

            # Check collision with pacman
            if (abs(ghost.x - self.pacman.x) < 0.7 and abs(ghost.y - self.pacman.y) < 0.7):
                self.ghost_collision(ghost)

    def set_ghost_target(self, ghost: Ghost):
        """Set ghost target based on personality."""
        px, py = int(self.pacman.x), int(self.pacman.y)
        pdx, pdy = self.pacman.direction

        if ghost.state == 'scatter' or self.scatter_mode:
            # Scatter corners
            targets = {
                'Blinky': (MAZE_W - 2, 0),
                'Pinky': (1, 0),
                'Inky': (MAZE_W - 2, MAZE_H - 1),
                'Clyde': (1, MAZE_H - 1),
            }
            ghost.target_x, ghost.target_y = targets.get(ghost.name, (1, 1))
        else:
            # Chase modes
            if ghost.name == 'Blinky':
                ghost.target_x, ghost.target_y = px, py
            elif ghost.name == 'Pinky':
                ghost.target_x, ghost.target_y = px + pdx * 4, py + pdy * 4
            elif ghost.name == 'Inky':
                # Inky uses Blinky position + vector from Blinky to 2 tiles ahead of Pac-Man
                blinky = next((g for g in self.ghosts if g.name == 'Blinky'), None)
                if blinky:
                    bx, by = int(blinky.x), int(blinky.y)
                    tx, ty = px + pdx * 2, py + pdy * 2
                    ghost.target_x, ghost.target_y = tx + (tx - bx), ty + (ty - by)
                else:
                    ghost.target_x, ghost.target_y = px, py
            elif ghost.name == 'Clyde':
                dist = abs(ghost.x - px) + abs(ghost.y - py)
                if dist > 8:
                    ghost.target_x, ghost.target_y = px, py
                else:
                    ghost.target_x, ghost.target_y = 1, MAZE_H - 1

    def choose_best_direction(self, ghost: Ghost, valid: List[Tuple[int, int]]) -> Tuple[int, int]:
        """Choose direction that minimizes distance to target."""
        best_dir = valid[0]
        best_dist = float('inf')

        for d in valid:
            nx, ny = ghost.x + d[0], ghost.y + d[1]
            dist = (nx - ghost.target_x) ** 2 + (ny - ghost.target_y) ** 2
            if dist < best_dist:
                best_dist = dist
                best_dir = d

        return best_dir

    def ghost_collision(self, ghost: Ghost):
        if ghost.state == 'frightened':
            # Eat ghost
            ghost.state = 'eaten'
            self.score += 200 * (2 ** self.ghosts.index(ghost))
        elif ghost.state != 'eaten' and ghost.state != 'house' and self.pacman.invulnerable <= 0:
            # Pac-Man dies
            self.pacman.lives -= 1
            self.pacman.invulnerable = 2.0
            if self.pacman.lives <= 0:
                self.game_over = True
            else:
                self.reset_positions()

    def reset_positions(self):
        self.pacman.x, self.pacman.y = PACMAN_START
        self.pacman.direction = (0, 0)
        self.pacman.next_direction = (0, 0)
        for i, ghost in enumerate(self.ghosts):
            sx, sy = GHOST_STARTS[i]
            ghost.x, ghost.y = sx, sy
            ghost.state = 'house'
            ghost.release_timer = i * 2.0
            ghost.direction = (0, -1)
            ghost.speed = 0.13
        self.ready_timer = 3.0

    def update_fruit(self, dt: float):
        # Spawn fruit twice per level (at 70 and 170 dots eaten)
        dots_eaten = 244 - self.dots_remaining  # Total dots in maze
        if not self.fruit.active and dots_eaten in (70, 170):
            self.fruit.active = True
            self.fruit.timer = 10.0
            self.fruit.type = min(self.level - 1, len(FRUIT_SCORES) - 1)

        if self.fruit.active:
            self.fruit.timer -= dt
            if self.fruit.timer <= 0:
                self.fruit.active = False

    def update(self, dt: float):
        if self.paused or self.game_over or self.won:
            return

        if self.ready_timer > 0:
            self.ready_timer -= dt
            return

        self.update_pacman(dt)
        self.update_ghosts(dt)
        self.update_fruit(dt)

        # Level complete
        if self.won:
            time.sleep(1)
            self.level += 1
            self.load_level()

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
            if key in {curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN,
                       ord('a'), ord('d'), ord('w'), ord('s')}:
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

        # Direction input (queued)
        if self.any_pressed({curses.KEY_UP, ord('w'), ord('W'), ord('k'), ord('K')}):
            state.pacman.next_direction = (0, -1)
        elif self.any_pressed({curses.KEY_DOWN, ord('s'), ord('S'), ord('j'), ord('J')}):
            state.pacman.next_direction = (0, 1)
        elif self.any_pressed({curses.KEY_LEFT, ord('a'), ord('A'), ord('h'), ord('H')}):
            state.pacman.next_direction = (-1, 0)
        elif self.any_pressed({curses.KEY_RIGHT, ord('d'), ord('D'), ord('l'), ord('L')}):
            state.pacman.next_direction = (1, 0)

        return None


class Renderer:
    def __init__(self, stdscr):
        self.stdscr = stdscr

    def render(self, state: GameState):
        self.stdscr.erase()
        h, w = self.stdscr.getmaxyx()

        for i in range(1, 8):
            curses.init_pair(i, i, -1)

        # Draw maze
        for y in range(MAZE_H):
            for x in range(MAZE_W):
                cell = state.maze[y][x]
                sx, sy = x * 2, y
                if cell == 1:  # Wall
                    self.stdscr.addstr(sy, sx, '██', curses.color_pair(4))
                elif cell == 0:  # Dot
                    self.stdscr.addstr(sy, sx, '· ', curses.color_pair(6))
                elif cell == 2:  # Power pellet
                    self.stdscr.addstr(sy, sx, '○ ', curses.color_pair(3) | curses.A_BOLD)

        # Draw fruit
        if state.fruit.active:
            fx, fy = state.fruit.x * 2, state.fruit.y
            char = FRUIT_CHARS[min(state.fruit.type, len(FRUIT_CHARS) - 1)]
            self.stdscr.addstr(fy, fx, char + ' ', curses.color_pair(3) | curses.A_BOLD)

        # Draw ghosts
        for ghost in state.ghosts:
            gx, gy = int(ghost.x * 2), int(ghost.y)
            if state.ready_timer > 0 and ghost.release_timer > 0:
                continue

            if ghost.state == 'frightened':
                if ghost.fright_timer < 2 and int(time.time() * 5) % 2 == 0:
                    char = '??'
                    color = 3
                else:
                    char = '░░'
                    color = 6
            elif ghost.state == 'eaten':
                char = '👁'
                color = 6
            else:
                char = '██'
                color = ghost.color

            if ghost.state != 'eaten' or int(time.time() * 10) % 2 == 0:
                self.stdscr.addstr(gy, gx, char, curses.color_pair(color))

        # Draw Pac-Man
        if state.pacman.invulnerable <= 0 or int(time.time() * 10) % 2 == 0:
            px, py = int(state.pacman.x * 2), int(state.pacman.y)
            # Animation frames
            if state.pacman.direction == (1, 0):  # Right
                char = '▶▶' if state.pacman.anim_frame else '▷▷'
            elif state.pacman.direction == (-1, 0):  # Left
                char = '◀◀' if state.pacman.anim_frame else '◁◁'
            elif state.pacman.direction == (0, -1):  # Up
                char = '▲▲' if state.pacman.anim_frame else '△△'
            elif state.pacman.direction == (0, 1):  # Down
                char = '▼▼' if state.pacman.anim_frame else '▽▽'
            else:
                char = '○ '

            self.stdscr.addstr(py, px, char, curses.color_pair(3) | curses.A_BOLD)

        # HUD
        self.stdscr.addstr(MAZE_H, 0, f"SCORE: {state.score}", curses.color_pair(3))
        self.stdscr.addstr(MAZE_H, 20, f"HIGH: {max(state.high_score, state.score)}", curses.color_pair(5))
        self.stdscr.addstr(MAZE_H + 1, 0, f"LEVEL: {state.level}", curses.color_pair(4))
        self.stdscr.addstr(MAZE_H + 1, 15, f"LIVES: {'●' * state.pacman.lives}", curses.color_pair(1))

        # Ready/Game Over
        if state.ready_timer > 0:
            self.draw_center("READY!", curses.color_pair(3))
        elif state.game_over:
            self.draw_center("GAME OVER", curses.color_pair(1))
            self.draw_center("R - Restart  Q/M - Menu", curses.color_pair(6), MAZE_H // 2 + 2)
        elif state.won:
            self.draw_center(f"LEVEL {state.level - 1} CLEAR!", curses.color_pair(2))

        self.stdscr.refresh()

    def draw_center(self, text: str, attr, y: Optional[int] = None):
        if y is None:
            y = MAZE_H // 2
        x = (MAZE_W * 2 - len(text)) // 2
        self.stdscr.addstr(y, max(0, x), text, attr)


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