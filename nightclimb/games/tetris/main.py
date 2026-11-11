#!/usr/bin/env python3
"""
TETRIS — Classic Falling Blocks
Complete implementation with ghost piece, hold, next queue, scoring.
"""

import curses
import time
import random
import traceback
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


SAVE_FILE = Path.home() / ".tetris_save.json"


# Tetromino definitions (SRS - Super Rotation System)
TETROMINOS = {
    'I': {
        'shape': [(0, 1), (1, 1), (2, 1), (3, 1)],
        'color': 6,  # Cyan
        'spawn': (3, 0),
    },
    'J': {
        'shape': [(0, 0), (0, 1), (1, 1), (2, 1)],
        'color': 4,  # Blue
        'spawn': (3, 0),
    },
    'L': {
        'shape': [(2, 0), (0, 1), (1, 1), (2, 1)],
        'color': 3,  # Orange
        'spawn': (3, 0),
    },
    'O': {
        'shape': [(1, 0), (2, 0), (1, 1), (2, 1)],
        'color': 5,  # Yellow
        'spawn': (4, 0),
    },
    'S': {
        'shape': [(1, 0), (2, 0), (0, 1), (1, 1)],
        'color': 2,  # Green
        'spawn': (3, 0),
    },
    'T': {
        'shape': [(1, 0), (0, 1), (1, 1), (2, 1)],
        'color': 5,  # Magenta
        'spawn': (3, 0),
    },
    'Z': {
        'shape': [(0, 0), (1, 0), (1, 1), (2, 1)],
        'color': 1,  # Red
        'spawn': (3, 0),
    },
}

# SRS Wall Kick Data (JLSTZ)
WALL_KICKS = {
    0: [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],  # 0->R
    1: [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],      # R->2
    2: [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],     # 2->L
    3: [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],   # L->0
}

# I-piece Wall Kicks
I_WALL_KICKS = {
    0: [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
    1: [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
    2: [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
    3: [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
}

BOARD_W = 10
BOARD_H = 20
VISIBLE_H = 20


@dataclass
class Piece:
    type: str
    x: int
    y: int
    rotation: int = 0

    def get_blocks(self) -> List[Tuple[int, int]]:
        """Get absolute block positions."""
        t = TETROMINOS[self.type]
        shape = t['shape']
        blocks = []
        for bx, by in shape:
            # Rotate around center
            rx, ry = self.rotate(bx, by, self.rotation)
            blocks.append((self.x + rx, self.y + ry))
        return blocks

    def rotate(self, x: int, y: int, rot: int) -> Tuple[int, int]:
        """Rotate coordinates around piece center."""
        for _ in range(rot):
            x, y = -y, x
        return x, y


@dataclass
class GameState:
    board: List[List[int]] = field(default_factory=lambda: [[0]*BOARD_W for _ in range(BOARD_H)])
    current: Optional[Piece] = None
    hold: Optional[str] = None
    hold_used: bool = False
    next_queue: List[str] = field(default_factory=list)
    score: int = 0
    level: int = 1
    lines: int = 0
    high_score: int = 0
    game_over: bool = False
    paused: bool = False
    last_fall: float = 0
    fall_interval: float = 0.8
    lock_delay: float = 0.5
    lock_timer: float = 0
    last_lock_time: float = 0
    combo: int = -1
    last_clear: int = 0

    def __post_init__(self):
        self.refill_queue()
        self.spawn_piece()

    def refill_queue(self):
        """7-bag randomizer."""
        while len(self.next_queue) < 5:
            bag = list(TETROMINOS.keys())
            random.shuffle(bag)
            self.next_queue.extend(bag)

    def spawn_piece(self):
        """Spawn next piece from queue."""
        if not self.next_queue:
            self.refill_queue()

        self.current = Piece(self.next_queue.pop(0), *TETROMINOS[self.next_queue[0]]['spawn'] if self.next_queue else (3, 0))
        self.current.type = self.next_queue.pop(0) if self.next_queue else 'T'
        self.current.x, self.current.y = TETROMINOS[self.current.type]['spawn']
        self.current.rotation = 0
        self.hold_used = False
        self.lock_timer = 0

        # Check game over
        if self.collides(self.current):
            self.game_over = True

        self.refill_queue()

    def collides(self, piece: Piece, dx: int = 0, dy: int = 0, drot: int = 0) -> bool:
        """Check collision with board or walls."""
        new_rot = (piece.rotation + drot) % 4
        for bx, by in piece.get_blocks():
            nx, ny = bx + dx, by + dy
            # Recalculate with new rotation
            if drot:
                t = TETROMINOS[piece.type]
                # Get relative position from piece center
                rel_x, rel_y = bx - piece.x, by - piece.y
                rx, ry = piece.rotate(rel_x, rel_y, new_rot)
                nx, ny = piece.x + rx + dx, piece.y + ry + dy

            if nx < 0 or nx >= BOARD_W or ny >= BOARD_H:
                return True
            if ny >= 0 and self.board[ny][nx]:
                return True
        return False

    def try_move(self, dx: int, dy: int) -> bool:
        """Try to move piece, return success."""
        if self.collides(self.current, dx, dy):
            return False
        self.current.x += dx
        self.current.y += dy
        self.lock_timer = 0
        return True

    def try_rotate(self, drot: int) -> bool:
        """Try to rotate with wall kicks."""
        kicks = I_WALL_KICKS if self.current.type == 'I' else WALL_KICKS
        for kx, ky in kicks[self.current.rotation]:
            if not self.collides(self.current, kx, ky, drot):
                self.current.x += kx
                self.current.y += ky
                self.current.rotation = (self.current.rotation + drot) % 4
                self.lock_timer = 0
                return True
        return False

    def hard_drop(self):
        """Drop piece to bottom instantly."""
        while self.try_move(0, 1):
            self.score += 2
        self.lock_piece()

    def get_ghost_y(self) -> int:
        """Get ghost piece Y position."""
        ghost = Piece(self.current.type, self.current.x, self.current.y, self.current.rotation)
        while not self.collides(ghost, 0, 1):
            ghost.y += 1
        return ghost.y

    def lock_piece(self):
        """Lock current piece to board."""
        for bx, by in self.current.get_blocks():
            if 0 <= by < BOARD_H and 0 <= bx < BOARD_W:
                self.board[by][bx] = TETROMINOS[self.current.type]['color']

        self.clear_lines()
        self.spawn_piece()
        self.lock_timer = 0

    def clear_lines(self):
        """Clear completed lines."""
        lines_cleared = 0
        new_board = []
        for row in self.board:
            if all(cell != 0 for cell in row):
                lines_cleared += 1
            else:
                new_board.append(row)

        for _ in range(lines_cleared):
            new_board.insert(0, [0]*BOARD_W)

        self.board = new_board

        if lines_cleared > 0:
            self.lines += lines_cleared
            self.combo += 1
            self.last_clear = lines_cleared

            # Scoring (NES-style)
            base = [0, 40, 100, 300, 1200][lines_cleared]
            self.score += base * self.level
            self.score += 50 * self.combo * self.level

            # Level up every 10 lines
            self.level = self.lines // 10 + 1
            self.fall_interval = max(0.05, 0.8 - (self.level - 1) * 0.07)
        else:
            self.combo = -1
            self.last_clear = 0

    def try_hold(self):
        """Swap current piece with hold."""
        if self.hold_used:
            return
        if self.hold is None:
            self.hold = self.current.type
            self.spawn_piece()
        else:
            self.hold, self.current.type = self.current.type, self.hold
            self.current.x, self.current.y = TETROMINOS[self.current.type]['spawn']
            self.current.rotation = 0
        self.hold_used = True

    def update(self, dt: float):
        """Update game state."""
        if self.game_over or self.paused:
            return

        now = time.time()

        # Gravity
        if now - self.last_fall >= self.fall_interval:
            if not self.try_move(0, 1):
                # Piece landed
                if self.lock_timer == 0:
                    self.lock_timer = now
                elif now - self.lock_timer >= self.lock_delay:
                    self.lock_piece()
            else:
                self.lock_timer = 0
            self.last_fall = now

    def save(self, path: Path):
        """Save high score."""
        data = {"high_score": max(self.high_score, self.score)}
        try:
            import json
            with open(path, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass

    def load(self, path: Path):
        """Load high score."""
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
            if key in {curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_DOWN,
                       ord('a'), ord('d'), ord('s'), ord(' ')}:
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

        if state.game_over:
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

        # Movement
        if self.any_pressed({curses.KEY_LEFT, ord('a'), ord('A'), ord('h'), ord('H')}):
            state.try_move(-1, 0)
        if self.any_pressed({curses.KEY_RIGHT, ord('d'), ord('D'), ord('l'), ord('L')}):
            state.try_move(1, 0)

        # Soft drop (held)
        if self.any_held({curses.KEY_DOWN, ord('s'), ord('S'), ord('j'), ord('J')}):
            if state.try_move(0, 1):
                state.score += 1

        # Rotate
        if self.any_pressed({curses.KEY_UP, ord('w'), ord('W'), ord('k'), ord('K'), ord('x'), ord('X')}):
            state.try_rotate(1)  # CW
        if self.any_pressed({ord('z'), ord('Z'), ord('c'), ord('C')}):
            state.try_rotate(-1)  # CCW

        # Hard drop
        if self.any_pressed({ord(' '), curses.KEY_ENTER, 10, 13}):
            state.hard_drop()

        # Hold
        if self.any_pressed({ord('c'), ord('C'), ord('v'), ord('V'), ord('f'), ord('F')}):
            state.try_hold()

        return None


class Renderer:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.shake = 0

    def render(self, state: GameState):
        self.stdscr.erase()
        h, w = self.stdscr.getmaxyx()

        # Colors
        for i in range(1, 8):
            curses.init_pair(i, i, -1)

        # Calculate board position (centered)
        board_x = (w - BOARD_W * 2 - 30) // 2
        board_y = (h - BOARD_H - 2) // 2

        # Draw title
        title = "T E T R I S"
        self.stdscr.addstr(board_y - 3, board_x + 2, title, curses.color_pair(5) | curses.A_BOLD)

        # Draw board border
        self.draw_board(state, board_x, board_y)

        # Draw side panels
        self.draw_sidebar(state, board_x + BOARD_W * 2 + 4, board_y)

        # Game over overlay
        if state.game_over:
            self.draw_game_over(board_x, board_y)

        self.stdscr.refresh()

    def draw_board(self, state: GameState, bx: int, by: int):
        # Border
        self.stdscr.addstr(by - 1, bx - 1, '╔' + '═' * (BOARD_W * 2) + '╗', curses.color_pair(6))
        for y in range(BOARD_H):
            self.stdscr.addstr(by + y, bx - 1, '║', curses.color_pair(6))
            self.stdscr.addstr(by + y, bx + BOARD_W * 2, '║', curses.color_pair(6))
        self.stdscr.addstr(by + BOARD_H, bx - 1, '╚' + '═' * (BOARD_W * 2) + '╝', curses.color_pair(6))

        # Board cells
        for y in range(BOARD_H):
            for x in range(BOARD_W):
                color = state.board[y][x]
                if color:
                    self.stdscr.addstr(by + y, bx + x * 2, '██', curses.color_pair(color))

        # Ghost piece
        if state.current and not state.game_over:
            ghost_y = state.get_ghost_y()
            for bx_rel, by_rel in state.current.get_blocks():
                gy = ghost_y + (by_rel - state.current.y)
                if 0 <= gy < BOARD_H:
                    self.stdscr.addstr(by + gy, bx + bx_rel * 2, '░░', curses.color_pair(6) | curses.A_DIM)

        # Current piece
        if state.current and not state.game_over:
            for bx_rel, by_rel in state.current.get_blocks():
                if by_rel >= 0:
                    color = TETROMINOS[state.current.type]['color']
                    self.stdscr.addstr(by + by_rel, bx + bx_rel * 2, '██', curses.color_pair(color))

    def draw_sidebar(self, state: GameState, sx: int, sy: int):
        # Hold
        self.stdscr.addstr(sy, sx, "HOLD", curses.color_pair(6))
        if state.hold:
            t = TETROMINOS[state.hold]
            for bx, by in t['shape']:
                rx, ry = bx - 1, by
                self.stdscr.addstr(sy + 1 + ry, sx + rx * 2, '██',
                                   curses.color_pair(t['color']) if not state.hold_used else curses.color_pair(6) | curses.A_DIM)

        # Next queue
        self.stdscr.addstr(sy + 5, sx, "NEXT", curses.color_pair(6))
        for i, piece_type in enumerate(state.next_queue[:4]):
            t = TETROMINOS[piece_type]
            for bx, by in t['shape']:
                rx, ry = bx - 1, by
                self.stdscr.addstr(sy + 6 + i * 3 + ry, sx + rx * 2, '██', curses.color_pair(t['color']))

        # Stats
        stats_y = sy + 18
        self.stdscr.addstr(stats_y, sx, f"SCORE: {state.score}", curses.color_pair(3))
        self.stdscr.addstr(stats_y + 1, sx, f"BEST:  {max(state.high_score, state.score)}", curses.color_pair(5))
        self.stdscr.addstr(stats_y + 2, sx, f"LEVEL: {state.level}", curses.color_pair(2))
        self.stdscr.addstr(stats_y + 3, sx, f"LINES: {state.lines}", curses.color_pair(4))
        if state.combo > 0:
            self.stdscr.addstr(stats_y + 4, sx, f"COMBO: {state.combo}!", curses.color_pair(1) | curses.A_BOLD)

        # Controls
        self.stdscr.addstr(stats_y + 6, sx, "←/→ Move  ↑/X Rotate", curses.color_pair(6) | curses.A_DIM)
        self.stdscr.addstr(stats_y + 7, sx, "↓ Soft Drop  Space Hard", curses.color_pair(6) | curses.A_DIM)
        self.stdscr.addstr(stats_y + 8, sx, "C/V Hold  P Pause", curses.color_pair(6) | curses.A_DIM)

    def draw_game_over(self, bx: int, by: int):
        overlay_y = by + BOARD_H // 2 - 3
        overlay_x = bx + 2
        self.stdscr.addstr(overlay_y, overlay_x, "╔════════════════╗", curses.color_pair(1))
        self.stdscr.addstr(overlay_y + 1, overlay_x, "║  GAME OVER    ║", curses.color_pair(1))
        self.stdscr.addstr(overlay_y + 2, overlay_x, "║  R - Restart  ║", curses.color_pair(1))
        self.stdscr.addstr(overlay_y + 3, overlay_x, "║  Q/M - Menu   ║", curses.color_pair(1))
        self.stdscr.addstr(overlay_y + 4, overlay_x, "╚════════════════╝", curses.color_pair(1))


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

    # Color pairs (1-7)
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