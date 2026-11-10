#!/usr/bin/env python3
"""
A Fool's Errand - The Dark Tower Ascent
A 1-bit retro climber inspired by Browning's "Childe Roland to the Dark Tower Came"
Terminal ASCII version using curses
"""

import curses
import random
import time
import json
import os
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class Config:
    # Display
    WIDTH: int = 40
    HEIGHT: int = 24
    FPS: int = 30

    # Game
    STARTING_STEP: int = 0
    STARTING_TORCHES: int = 3
    MAX_TORCHES: int = 3
    CHECKPOINT_INTERVAL: int = 300

    # Tower geometry
    TOWER_RADIUS: int = 8
    STAIR_WIDTH: int = 4
    STEPS_PER_TURN: int = 12
    PIXELS_PER_STEP: float = 1.0

    # Barrels
    BARREL_MIN_STEP: int = 50
    BARREL_BASE_CHANCE: float = 0.02
    BARREL_CHANCE_INCREASE: float = 0.003
    BARREL_MAX_CHANCE: float = 0.12
    BARREL_SPEED: float = 2.5  # steps per second
    BARREL_WARNING_TIME: float = 1.5

    # Animation
    WALK_CYCLE_SPEED: float = 8.0
    BOB_AMPLITUDE: float = 0.3
    BOB_FREQUENCY: float = 1.5

    # Ranks
    RANKS: List[tuple] = field(default_factory=lambda: [
        (0, "VAGRANT"),
        (500, "PILGRIM"),
        (1200, "SQUIRE"),
        (2000, "CHILDE ROLAND"),
        (3000, "TOWER WALKER"),
    ])

    # Story beats (from Browning)
    STORY_BEATS: List[dict] = field(default_factory=lambda: [
        {"step": 0, "act": "ACT I - THE DESOLATE GATE", "poem": "My first thought was, he lied in every word..."},
        {"step": 100, "act": "ACT I - THE DESOLATE GATE", "poem": "That hoary cripple, with malicious eye..."},
        {"step": 250, "act": "ACT I - THE DESOLATE GATE", "poem": "For mark! no sooner was I fairly found pledged to the plain..."},
        {"step": 500, "act": "ACT II - THE WINDING STAIRS", "poem": "Gray plain all round: nothing but plain to the horizon's bound."},
        {"step": 900, "act": "ACT II - THE WINDING STAIRS", "poem": "So, on I went. I think I never saw such starved ignoble nature..."},
        {"step": 1300, "act": "ACT III - THE TRAP OF ROLLED OAK", "poem": "A sudden little river crossed my path... grass grew scant as hair in leprosy."},
        {"step": 1800, "act": "ACT III - THE TRAP OF ROLLED OAK", "poem": "What bad use was that engine for? To wheel men's bodies into the dark void!"},
        {"step": 2200, "act": "ACT IV - THE BLIND SPIRE", "poem": "The round squat turret, blind as the fool's heart, built of brown stone..."},
        {"step": 2700, "act": "ACT IV - THE DARK TOWER REACHED", "poem": "And yet dauntless the slug-horn to my lips I set, and blew: 'Childe Roland to the Dark Tower came.'"},
    ])

    # Save file
    SAVE_FILE: str = os.path.expanduser("~/.fools_errand_save.json")

    # Colors (curses color pairs)
    COLOR_BG: int = 0
    COLOR_FG: int = 1
    COLOR_DIM: int = 2
    COLOR_ACCENT: int = 3
    COLOR_WARNING: int = 4
    COLOR_TORCH: int = 5
    COLOR_STAIR: int = 6


CFG = Config()


# =============================================================================
# DATA CLASSES
# =============================================================================

class Lane(Enum):
    LEFT = -1
    MID = 0
    RIGHT = 1

    @property
    def name(self) -> str:
        return {Lane.LEFT: "LEFT", Lane.MID: "MID", Lane.RIGHT: "RIGHT"}[self]

    @property
    def offset(self) -> int:
        return {Lane.LEFT: -2, Lane.MID: 0, Lane.RIGHT: 2}[self]


@dataclass
class Barrel:
    active: bool = False
    step: float = 0.0
    lane: Lane = Lane.MID
    rotation: float = 0.0
    speed: float = CFG.BARREL_SPEED
    warning_timer: float = 0.0
    collision_checked: bool = False

    def spawn(self, player_step: int):
        self.active = True
        self.step = player_step + 8
        self.lane = random.choice(list(Lane))
        self.speed = CFG.BARREL_SPEED + random.uniform(0, 1.5)
        self.rotation = 0.0
        self.warning_timer = CFG.BARREL_WARNING_TIME
        self.collision_checked = False

    def update(self, dt: float, player_step: float) -> Optional[bool]:
        """Returns True if hit player, False if passed, None if still active"""
        if not self.active:
            return None

        if self.warning_timer > 0:
            self.warning_timer -= dt
            if self.warning_timer <= 0:
                self.collision_checked = False
            return None

        self.step -= self.speed * dt
        self.rotation += self.speed * dt * 2.0

        # Check collision near player
        step_diff = self.step - player_step
        if not self.collision_checked and -0.5 <= step_diff <= 0.5:
            self.collision_checked = True
            return None  # Signal to check collision

        # Passed player
        if self.step < player_step - 5:
            self.active = False
            return False

        return None

    def check_collision(self, player_lane: Lane) -> bool:
        return self.lane == player_lane


@dataclass
class Player:
    step: float = 0.0
    target_step: float = 0.0
    velocity: float = 0.0
    lane: Lane = Lane.MID
    target_lane: Lane = Lane.MID
    torches: int = CFG.STARTING_TORCHES
    checkpoint: int = 0
    high_score: int = 0
    walk_cycle: float = 0.0
    last_footstep: float = 0.0
    step_count: int = 0
    last_cadence_time: float = 0.0
    cadence: int = 0

    is_game_started: bool = False
    is_game_over: bool = False
    death_reason: str = ""

    sfx_enabled: bool = True
    crt_enabled: bool = True

    def start_game(self):
        self.is_game_started = True
        self.is_game_over = False
        self.step = self.checkpoint
        self.target_step = self.checkpoint
        self.lane = Lane.MID
        self.target_lane = Lane.MID
        self.torches = CFG.MAX_TORCHES
        self.walk_cycle = 0.0
        self.last_footstep = self.step
        self.step_count = 0
        self.cadence = 0
        self.last_cadence_time = time.time()
        self.death_reason = ""

    def resume_from_checkpoint(self):
        self.is_game_over = False
        self.step = self.checkpoint
        self.target_step = self.checkpoint
        self.lane = Lane.MID
        self.target_lane = Lane.MID
        self.walk_cycle = 0.0
        self.last_footstep = self.step
        self.death_reason = ""

    def restart_from_beginning(self):
        self.checkpoint = CFG.STARTING_STEP
        self.torches = CFG.STARTING_TORCHES
        self.high_score = 0
        self.start_game()

    def game_over(self, reason: str):
        self.is_game_over = True
        self.death_reason = reason
        if int(self.step) > self.high_score:
            self.high_score = int(self.step)

    def ascend(self, steps: float = 1.0) -> bool:
        if not self.is_game_started or self.is_game_over:
            return False
        if steps < 0 and self.target_step <= 0:
            return False
        self.target_step += steps
        self.step_count += abs(int(steps))
        return True

    def dodge(self, direction: int) -> bool:
        if not self.is_game_started or self.is_game_over:
            return False
        new_lane_val = max(-1, min(1, self.lane.value + direction))
        new_lane = Lane(new_lane_val)
        if new_lane != self.lane:
            self.lane = new_lane
            self.target_lane = new_lane
            return True
        return False

    def lose_torch(self):
        self.torches = max(0, self.torches - 1)
        if self.torches <= 0:
            self.game_over("Crushed under the trap of rolled oak.")
        else:
            self.target_step = max(self.checkpoint, self.target_step - 30)

    def update(self, dt: float):
        if not self.is_game_started or self.is_game_over:
            return

        # Smooth step interpolation
        diff = self.target_step - self.step
        self.velocity = diff * 12.0
        self.step += self.velocity * dt

        # Walk cycle
        if abs(self.velocity) > 0.05:
            self.walk_cycle += abs(self.velocity) * dt * CFG.WALK_CYCLE_SPEED
            if abs(self.step - self.last_footstep) >= 0.8:
                self.last_footstep = self.step

        # Check checkpoint
        next_checkpoint = int(self.target_step // CFG.CHECKPOINT_INTERVAL) * CFG.CHECKPOINT_INTERVAL
        if next_checkpoint > self.checkpoint and next_checkpoint > 0:
            self.checkpoint = next_checkpoint
            self.torches = min(self.torches + 1, CFG.MAX_TORCHES)

        # Cadence
        now = time.time()
        if now - self.last_cadence_time >= 1.0:
            self.cadence = self.step_count
            self.step_count = 0
            self.last_cadence_time = now

    def get_rank(self) -> str:
        rank = CFG.RANKS[0][1]
        for min_step, title in CFG.RANKS:
            if self.step >= min_step:
                rank = title
            else:
                break
        return f"RANK: {rank}"

    def get_story_beat(self) -> dict:
        beat = CFG.STORY_BEATS[0]
        for b in CFG.STORY_BEATS:
            if self.step >= b["step"]:
                beat = b
            else:
                break
        return beat


# =============================================================================
# RENDERER
# =============================================================================

class Renderer:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.width = CFG.WIDTH
        self.height = CFG.HEIGHT
        self.time = 0.0
        self.shake_time = 0.0
        self.shake_offset = (0, 0)

        # Frame buffer
        self.buffer = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.color_buffer = [[0 for _ in range(self.width)] for _ in range(self.height)]

    def clear(self):
        for y in range(self.height):
            for x in range(self.width):
                self.buffer[y][x] = ' '
                self.color_buffer[y][x] = 0

    def put(self, x: int, y: int, char: str, color: int = 0):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.buffer[y][x] = char
            self.color_buffer[y][x] = color

    def puts(self, x: int, y: int, text: str, color: int = 0):
        for i, ch in enumerate(text):
            self.put(x + i, y, ch, color)

    def draw_tower(self, player_step: float):
        cx = self.width // 2
        tower_r = CFG.TOWER_RADIUS
        stair_w = CFG.STAIR_WIDTH
        steps_per_turn = CFG.STEPS_PER_TURN
        px_per_step = CFG.PIXELS_PER_STEP

        cam_y = self.height // 2 + 2

        # Tower cylinder - draw vertical strips with shading
        for row in range(self.height):
            for col in range(max(0, cx - tower_r), min(self.width, cx + tower_r + 1)):
                dx = col - cx
                if dx * dx <= tower_r * tower_r:
                    # Cylindrical shading
                    shade = int(3 * (1 - abs(dx) / tower_r))
                    self.put(col, row, '█', CFG.COLOR_STAIR + shade)

        # Stone courses (horizontal lines)
        course_h = 2
        scroll = int(player_step * px_per_step) % course_h
        for y in range(-course_h, self.height + course_h, course_h):
            line_y = y + scroll
            if 0 <= line_y < self.height:
                for x in range(max(0, cx - tower_r), min(self.width, cx + tower_r + 1)):
                    if self.buffer[line_y][x] != ' ':
                        self.put(x, line_y, '▀', self.color_buffer[line_y][x])

        # Wall torches
        torch_every = 10
        base = int((player_step - 15) // torch_every) * torch_every
        for ts in range(base, int(player_step) + 20, torch_every):
            angle = -(ts / steps_per_turn) * 2 * 3.14159
            cos_a = int(3.14159 * 1000 * abs(int(1000 * angle)))  # pseudo-random
            if cos_a % 3 == 0:  # front-facing only
                sy = cam_y - int((ts - player_step) * px_per_step)
                sx = cx + int(math.sin(angle) * (tower_r - 1))
                if 0 <= sy < self.height and 0 <= sx < self.width:
                    flicker = int(self.time * 20 + ts) % 3
                    torch_chars = ['▲', '▼', '◆']
                    self.put(sx, sy - 1, torch_chars[flicker], CFG.COLOR_TORCH)
                    self.put(sx, sy, '│', CFG.COLOR_DIM)

    def draw_stairs(self, player_step: float, front_only: bool):
        cx = self.width // 2
        tower_r = CFG.TOWER_RADIUS
        stair_w = CFG.STAIR_WIDTH
        steps_per_turn = CFG.STEPS_PER_TURN
        px_per_step = CFG.PIXELS_PER_STEP
        cam_y = self.height // 2 + 2

        range_steps = 12
        min_s = int(player_step - range_steps)
        max_s = int(player_step + range_steps)

        for s in range(min_s, max_s + 1):
            delta = s - player_step
            y = cam_y - int(delta * px_per_step)

            angle = -(s / steps_per_turn) * 2 * 3.14159
            sin_a = math.sin(angle)
            cos_a = math.cos(angle)

            inner_x = cx + int(sin_a * tower_r)
            outer_x = cx + int(sin_a * (tower_r + stair_w))

            is_front = cos_a >= -0.2
            if is_front != front_only:
                continue

            if 0 <= y < self.height:
                shade = int(3 * max(0.2, (cos_a + 1.0) * 0.4))
                color = CFG.COLOR_STAIR + shade if front_only else CFG.COLOR_DIM

                # Step tread
                for x in range(min(inner_x, outer_x), max(inner_x, outer_x) + 1):
                    if 0 <= x < self.width:
                        self.put(x, y, '▄' if front_only else '▀', color)

                # Bright edge on front
                if front_only:
                    for x in range(min(inner_x, outer_x), max(inner_x, outer_x) + 1):
                        if 0 <= x < self.width:
                            self.put(x, y, '▀', CFG.COLOR_FG)

    def draw_barrel(self, barrel: Barrel, player_step: float):
        if not barrel.active or barrel.warning_timer > 0:
            return

        cx = self.width // 2
        tower_r = CFG.TOWER_RADIUS
        stair_w = CFG.STAIR_WIDTH
        steps_per_turn = CFG.STEPS_PER_TURN
        px_per_step = CFG.PIXELS_PER_STEP
        cam_y = self.height // 2 + 2

        delta = barrel.step - player_step
        y = cam_y - int(delta * px_per_step)

        angle = -(barrel.step / steps_per_turn) * 2 * 3.14159
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)

        lane_offset = barrel.lane.value * 2
        radius = tower_r + stair_w // 2 + lane_offset
        x = cx + int(sin_a * radius)

        is_front = cos_a >= -0.3
        if not is_front and cos_a < -0.5:
            return

        if 0 <= y < self.height and 0 <= x < self.width:
            # Rotating barrel
            rot = int(barrel.rotation * 4) % 4
            barrel_chars = ['@', 'O', '0', 'O']
            self.put(x, y, barrel_chars[rot], CFG.COLOR_WARNING if is_front else CFG.COLOR_DIM)

    def draw_player(self, player: Player):
        cx = self.width // 2
        tower_r = CFG.TOWER_RADIUS
        stair_w = CFG.STAIR_WIDTH
        steps_per_turn = CFG.STEPS_PER_TURN
        px_per_step = CFG.PIXELS_PER_STEP
        cam_y = self.height // 2 + 2

        angle = -(player.step / steps_per_turn) * 2 * 3.14159
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)

        lane_offset = player.lane.value * 2
        radius = tower_r + stair_w // 2 + lane_offset
        x = cx + int(sin_a * radius)
        y = cam_y

        # Body bob
        bob = 0
        leg_phase = 0
        if abs(player.velocity) > 0.05:
            leg_phase = player.walk_cycle * 3.14159 * 2
            bob = int(abs(math.sin(leg_phase)) * 1)

        # Torch light halo (dithered)
        for dy in range(-3, 4):
            for dx in range(-5, 6):
                dist = math.sqrt(dx*dx + dy*dy)
                if dist <= 4 and random.random() < max(0, 1 - dist/4):
                    hx, hy = x + dx, y + dy - 3
                    if 0 <= hx < self.width and 0 <= hy < self.height:
                        if self.buffer[hy][hx] == ' ':
                            self.put(hx, hy, '·', CFG.COLOR_TORCH)

        # Player sprite (facing left/up the stairs)
        py = y - bob

        # Legs
        front_leg = max(0, int(math.sin(leg_phase) * 2))
        back_leg = max(0, int(-math.sin(leg_phase) * 1))

        # Back leg
        self.put(x - 1, py + 1 - back_leg, '/', CFG.COLOR_FG)
        # Front leg
        self.put(x + 1, py + 1 - front_leg, '\\', CFG.COLOR_FG)

        # Body
        self.put(x, py, '█', CFG.COLOR_FG)
        self.put(x, py - 1, '█', CFG.COLOR_FG)

        # Head
        self.put(x, py - 2, '■', CFG.COLOR_FG)
        self.put(x - 1, py - 2, '▄', CFG.COLOR_FG)  # hood

        # Torch in hand
        self.put(x + 2, py - 1, '│', CFG.COLOR_FG)
        torch_flicker = int(self.time * 15) % 3
        torch_top = ['▲', '◆', '▼']
        self.put(x + 2, py - 2, torch_top[torch_flicker], CFG.COLOR_TORCH)

    def draw_arch_window(self, player_step: float):
        # Gothic window top-left with moon
        win_x = 4
        win_y = 3 + int((player_step * 0.5) % 10)
        if 0 <= win_y < self.height - 6:
            # Window frame
            self.put(win_x, win_y, '╭', CFG.COLOR_DIM)
            self.put(win_x + 1, win_y, '─', CFG.COLOR_DIM)
            self.put(win_x + 2, win_y, '╮', CFG.COLOR_DIM)
            self.put(win_x, win_y + 1, '│', CFG.COLOR_DIM)
            self.put(win_x + 2, win_y + 1, '│', CFG.COLOR_DIM)
            self.put(win_x, win_y + 2, '╰', CFG.COLOR_DIM)
            self.put(win_x + 1, win_y + 2, '─', CFG.COLOR_DIM)
            self.put(win_x + 2, win_y + 2, '╯', CFG.COLOR_DIM)
            # Moon
            self.put(win_x + 1, win_y + 1, '☾', CFG.COLOR_FG)

    def draw_hud(self, player: Player, barrel: Barrel):
        # Top bar
        self.puts(0, 0, f"STEP: {int(player.step):4d} ♠  {player.get_rank():20s}", CFG.COLOR_FG)
        self.puts(0, 1, f"LANE: {player.lane.name:5s}  🔥 {player.torches}/{CFG.MAX_TORCHES}  CADENCE: {player.cadence:2d}/s", CFG.COLOR_FG)

        # Act/Poem
        beat = player.get_story_beat()
        self.puts(0, 2, beat['act'], CFG.COLOR_ACCENT)
        poem = beat['poem']
        if len(poem) > self.width - 2:
            poem = poem[:self.width - 5] + "..."
        self.puts(0, 3, f"\"{poem}\"", CFG.COLOR_DIM)

        # Barrel warning
        if barrel.active and barrel.warning_timer > 0:
            warn = "⚠ BARREL INCOMING! DODGE [←/→] ⚠"
            x = (self.width - len(warn)) // 2
            self.puts(x, 5, warn, CFG.COLOR_WARNING)

        # Dodge feedback
        if hasattr(self, 'dodge_msg') and self.dodge_msg:
            msg, timer = self.dodge_msg
            if timer > 0:
                x = (self.width - len(msg)) // 2
                self.puts(x, self.height - 4, msg, CFG.COLOR_ACCENT)
                self.dodge_msg = (msg, timer - 1)
            else:
                self.dodge_msg = None

        # Controls hint
        self.puts(0, self.height - 2, "↑/W=Climb  ↓/S=Back  ←/A=Left  →/D=Right  Q=Quit", CFG.COLOR_DIM)

    def draw_title_screen(self):
        self.clear()
        title = [
            "╔══════════════════════════════════╗",
            "║      A FOOL'S ERRAND             ║",
            "║    The Dark Tower Ascent         ║",
            "╠══════════════════════════════════╣",
            "║                                  ║",
            "║  \"My first thought was, he       ║",
            "║   lied in every word...          ║",
            "║   yet to the Dark Tower came.\"  ║",
            "║                                  ║",
            "║  Poem: R. Browning  |  Est. 1843 ║",
            "║                                  ║",
            "║  [SPACE] Ascend the Spire        ║",
            "║  [Q] Quit                        ║",
            "║                                  ║",
            "╚══════════════════════════════════╝",
        ]
        start_y = (self.height - len(title)) // 2
        for i, line in enumerate(title):
            self.puts((self.width - len(line)) // 2, start_y + i, line, CFG.COLOR_FG)

    def draw_game_over(self, player: Player):
        self.clear()
        msg = [
            "    ☠  THE FOOL HAS PERISHED  ☠    ",
            "                                    ",
            f"  {player.death_reason}  ",
            "                                    ",
            f"  Final Step: {int(player.step)}  ",
            f"  Best: {player.high_score}  ",
            "                                    ",
            "  [SPACE] Resume from Checkpoint  ",
            "  [R] Restart at Bottom (0)      ",
            "  [Q] Quit                        ",
        ]
        start_y = (self.height - len(msg)) // 2
        for i, line in enumerate(msg):
            color = CFG.COLOR_WARNING if i == 0 else CFG.COLOR_FG
            self.puts((self.width - len(line)) // 2, start_y + i, line, color)

    def apply_shake(self):
        if self.shake_time > 0:
            self.shake_offset = (random.randint(-1, 1), random.randint(-1, 1))
        else:
            self.shake_offset = (0, 0)

    def present(self):
        self.apply_shake()
        sx, sy = self.shake_offset
        for y in range(self.height):
            line = ''.join(self.buffer[y])
            color = self.color_buffer[y][0] if self.color_buffer[y] else 0
            try:
                self.stdscr.addstr(y + sy, sx, line, curses.color_pair(color) if color else 0)
            except curses.error:
                pass
        self.stdscr.refresh()


# =============================================================================
# SAVE/LOAD
# =============================================================================

def load_game(player: Player):
    try:
        with open(CFG.SAVE_FILE, 'r') as f:
            data = json.load(f)
        player.checkpoint = data.get('checkpoint', 0)
        player.torches = data.get('torches', CFG.STARTING_TORCHES)
        player.high_score = data.get('high_score', 0)
        player.sfx_enabled = data.get('sfx', True)
        player.crt_enabled = data.get('crt', True)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

def save_game(player: Player):
    try:
        data = {
            'checkpoint': player.checkpoint,
            'torches': player.torches,
            'high_score': player.high_score,
            'sfx': player.sfx_enabled,
            'crt': player.crt_enabled,
        }
        with open(CFG.SAVE_FILE, 'w') as f:
            json.dump(data, f)
    except Exception:
        pass


# =============================================================================
# AUDIO (terminal bell / simple beep)
# =============================================================================

class Audio:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    def set_enabled(self, enabled: bool):
        self.enabled = enabled

    def step(self):
        if self.enabled:
            print('\a', end='', flush=True)  # terminal bell

    def dodge(self):
        if self.enabled:
            print('\a\a', end='', flush=True)

    def warning(self):
        if self.enabled:
            for _ in range(3):
                print('\a', end='', flush=True)
                time.sleep(0.05)

    def impact(self):
        if self.enabled:
            for _ in range(5):
                print('\a', end='', flush=True)
                time.sleep(0.02)

    def checkpoint(self):
        if self.enabled:
            for freq in [523, 659, 784, 1047]:
                print('\a', end='', flush=True)
                time.sleep(0.08)

    def game_over(self):
        if self.enabled:
            for _ in range(4):
                print('\a', end='', flush=True)
                time.sleep(0.15)


# =============================================================================
# MAIN GAME
# =============================================================================

import math

def main(stdscr):
    # Setup curses
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)
    curses.start_color()
    curses.use_default_colors()

    # Color pairs
    curses.init_pair(1, curses.COLOR_WHITE, -1)      # FG
    curses.init_pair(2, curses.COLOR_BLUE, -1)       # DIM
    curses.init_pair(3, curses.COLOR_YELLOW, -1)     # ACCENT
    curses.init_pair(4, curses.COLOR_RED, -1)        # WARNING
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)    # TORCH
    curses.init_pair(6, curses.COLOR_GREEN, -1)      # STAIR

    # Game objects
    player = Player()
    barrel = Barrel()
    audio = Audio()
    renderer = Renderer(stdscr)

    load_game(player)
    audio.set_enabled(player.sfx_enabled)

    # Game loop
    last_time = time.time()
    frame_time = 1.0 / CFG.FPS

    state = "TITLE"  # TITLE, PLAYING, GAME_OVER

    while True:
        current_time = time.time()
        dt = min(current_time - last_time, 0.1)
        last_time = current_time
        renderer.time += dt

        if renderer.shake_time > 0:
            renderer.shake_time -= dt

        # Input
        try:
            key = stdscr.getch()
        except:
            key = -1

        if state == "TITLE":
            if key in (ord(' '), ord('\n'), ord('\r'), curses.KEY_ENTER):
                player.start_game()
                state = "PLAYING"
            elif key in (ord('q'), ord('Q')):
                break

        elif state == "PLAYING":
            if key in (ord('q'), ord('Q')):
                break
            elif key in (ord('w'), ord('W'), curses.KEY_UP, ord(' ')):
                if player.ascend(1):
                    audio.step()
            elif key in (ord('s'), ord('S'), curses.KEY_DOWN):
                player.ascend(-1)
            elif key in (ord('a'), ord('A'), curses.KEY_LEFT):
                if player.dodge(-1):
                    audio.dodge()
                    renderer.dodge_msg = ("EVADED LEFT!", 30)
            elif key in (ord('d'), ord('D'), curses.KEY_RIGHT):
                if player.dodge(1):
                    audio.dodge()
                    renderer.dodge_msg = ("EVADED RIGHT!", 30)
            elif key in (ord('m'), ord('M')):
                player.sfx_enabled = not player.sfx_enabled
                audio.set_enabled(player.sfx_enabled)
                save_game(player)
            elif key in (ord('c'), ord('C')):
                player.crt_enabled = not player.crt_enabled
                save_game(player)

            # Update game
            player.update(dt)

            # Barrel spawn check
            if not barrel.active and player.step >= CFG.BARREL_MIN_STEP:
                chance = CFG.BARREL_BASE_CHANCE + (max(0, player.step - CFG.BARREL_MIN_STEP) / 100) * CFG.BARREL_CHANCE_INCREASE
                chance = min(chance, CFG.BARREL_MAX_CHANCE)
                if random.random() < chance * dt * CFG.FPS:
                    barrel.spawn(int(player.step))
                    audio.warning()

            # Barrel update
            result = barrel.update(dt, player.step)
            if result is not None:
                if result:  # Hit
                    renderer.shake_time = 0.4
                    audio.impact()
            elif result is None and barrel.active and barrel.warning_timer <= 0:
                # Check collision window
                step_diff = barrel.step - player.step
                if -0.5 <= step_diff <= 0.5 and not barrel.collision_checked:
                    barrel.collision_checked = True
                    if barrel.check_collision(player.lane):
                        player.lose_torch()
                        barrel.active = False
                        renderer.shake_time = 0.4
                        audio.impact()
                        if player.is_game_over:
                            state = "GAME_OVER"
                            audio.game_over()
                        else:
                            renderer.dodge_msg = (f"STRUCK! TORCHES: {player.torches}", 60)

            # Check game over
            if player.is_game_over:
                state = "GAME_OVER"
                audio.game_over()
                save_game(player)

            # Checkpoint sound
            if hasattr(player, '_last_checkpoint') and player.checkpoint != player._last_checkpoint:
                audio.checkpoint()
            player._last_checkpoint = player.checkpoint

            # Render
            renderer.clear()
            renderer.draw_arch_window(player.step)
            renderer.draw_stairs(player.step, front_only=False)
            renderer.draw_tower(player.step)
            renderer.draw_stairs(player.step, front_only=True)
            renderer.draw_barrel(barrel, player.step)
            renderer.draw_player(player)
            renderer.draw_hud(player, barrel)

        elif state == "GAME_OVER":
            if key in (ord(' '), ord('\n'), ord('\r'), curses.KEY_ENTER):
                player.resume_from_checkpoint()
                barrel.active = False
                state = "PLAYING"
            elif key in (ord('r'), ord('R')):
                player.restart_from_beginning()
                barrel.active = False
                state = "PLAYING"
            elif key in (ord('q'), ord('Q')):
                break

            renderer.draw_game_over(player)

        renderer.present()

        # Frame pacing
        elapsed = time.time() - current_time
        sleep_time = frame_time - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

    save_game(player)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass