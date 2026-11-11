#!/usr/bin/env python3
"""Game entities for Snake: Snake, Food, Obstacles, Power-ups, Particles."""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import math
import random


# Directions
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)
DIRECTIONS = [DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT]


@dataclass
class Snake:
    """The player-controlled snake."""
    body: List[Tuple[int, int]] = field(default_factory=list)
    direction: Tuple[int, int] = DIR_RIGHT
    next_direction: Tuple[int, int] = DIR_RIGHT
    grow_pending: int = 0
    speed: float = 10.0  # Moves per second
    move_timer: float = 0.0

    # Power-up states
    has_shield: bool = False
    shield_timer: float = 0.0
    has_speed: bool = False
    speed_timer: float = 0.0
    has_slow: bool = False
    slow_timer: float = 0.0
    has_ghost: bool = False  # Pass through walls/self
    ghost_timer: float = 0.0
    score_multiplier: float = 1.0
    multiplier_timer: float = 0.0

    def __post_init__(self):
        if not self.body:
            # Default spawn in center
            self.body = [(20, 12), (19, 12), (18, 12)]

    @property
    def head(self) -> Tuple[int, int]:
        return self.body[0]

    @property
    def length(self) -> int:
        return len(self.body)

    def set_direction(self, new_dir: Tuple[int, int]):
        """Set next direction, preventing 180-degree turns."""
        # Can't reverse direction - check against queued direction
        if (new_dir[0] == -self.next_direction[0] and new_dir[1] == -self.next_direction[1]):
            return
        self.next_direction = new_dir

    def update(self, dt: float, width: int, height: int, obstacles: List['Obstacle']) -> Tuple[bool, str]:
        """
        Update snake position.
        Returns: (alive, event) where event is 'ate_food', 'hit_wall', 'hit_self', 'hit_obstacle', 'shield_blocked', or ''
        """
        # Update power-up timers
        self._update_powerups(dt)

        # Calculate current speed
        current_speed = self.speed
        if self.has_speed:
            current_speed *= 1.5
        if self.has_slow:
            current_speed *= 0.5

        self.move_timer += dt
        move_interval = 1.0 / current_speed

        moves_this_frame = 0
        max_moves_per_frame = 5  # Prevent spiral of death
        last_event = ''

        while self.move_timer >= move_interval and moves_this_frame < max_moves_per_frame:
            self.move_timer -= move_interval
            moves_this_frame += 1

            # Apply direction change
            self.direction = self.next_direction

            # Calculate new head position
            new_head = (self.head[0] + self.direction[0], self.head[1] + self.direction[1])

            # Check wall collision
            if not self.has_ghost:
                if new_head[0] < 0 or new_head[0] >= width or new_head[1] < 0 or new_head[1] >= height:
                    if self.has_shield:
                        self.has_shield = False
                        self.shield_timer = 0
                        return True, 'shield_blocked'  # Shield consumed, stop moving this frame
                    return False, 'hit_wall'

            # Wrap around if ghost mode
            if self.has_ghost:
                new_head = (new_head[0] % width, new_head[1] % height)

            # Check self collision
            if not self.has_ghost and new_head in self.body:
                if self.has_shield:
                    self.has_shield = False
                    self.shield_timer = 0
                    last_event = 'shield_blocked'
                    continue
                return False, 'hit_self'

            # Check obstacle collision
            hit_obstacle = False
            for obs in obstacles:
                if new_head == (obs.x, obs.y):
                    hit_obstacle = True
                    break

            if hit_obstacle:
                if self.has_shield:
                    self.has_shield = False
                    self.shield_timer = 0
                    last_event = 'shield_blocked'
                    continue
                if self.has_ghost:
                    pass  # Ghost passes through
                else:
                    return False, 'hit_obstacle'

            # Move snake
            self.body.insert(0, new_head)

            # Handle growth
            if self.grow_pending > 0:
                self.grow_pending -= 1
            else:
                self.body.pop()

        return True, last_event

    def _update_powerups(self, dt: float):
        if self.has_shield:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.has_shield = False
        if self.has_speed:
            self.speed_timer -= dt
            if self.speed_timer <= 0:
                self.has_speed = False
        if self.has_slow:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.has_slow = False
        if self.has_ghost:
            self.ghost_timer -= dt
            if self.ghost_timer <= 0:
                self.has_ghost = False
        if self.score_multiplier > 1.0:
            self.multiplier_timer -= dt
            if self.multiplier_timer <= 0:
                self.score_multiplier = 1.0

    def grow(self, amount: int = 1):
        self.grow_pending += amount

    def apply_powerup(self, ptype: str, duration: float = 10.0):
        if ptype == 'shield':
            self.has_shield = True
            self.shield_timer = duration
        elif ptype == 'speed':
            self.has_speed = True
            self.speed_timer = duration
        elif ptype == 'slow':
            self.has_slow = True
            self.slow_timer = duration
        elif ptype == 'ghost':
            self.has_ghost = True
            self.ghost_timer = duration
        elif ptype == 'multiplier':
            self.score_multiplier = 2.0
            self.multiplier_timer = duration
        elif ptype == 'shrink':
            # Remove tail segments
            for _ in range(min(3, len(self.body) - 3)):
                self.body.pop()


@dataclass
class Food:
    """Collectible food item."""
    x: int
    y: int
    ftype: str = 'normal'  # normal, bonus, poison, speed, shrink
    value: int = 10
    color: int = 3
    char: str = '●'
    anim_timer: float = 0.0
    collected: bool = False

    FOOD_TYPES = {
        'normal': {'value': 10, 'color': 3, 'char': '●', 'grow': 1},
        'bonus': {'value': 50, 'color': 7, 'char': '◆', 'grow': 2},
        'poison': {'value': -20, 'color': 4, 'char': '☠', 'grow': 0},
        'speed': {'value': 15, 'color': 5, 'char': '⚡', 'grow': 1, 'powerup': 'speed'},
        'shrink': {'value': 25, 'color': 11, 'char': '◈', 'grow': 0, 'powerup': 'shrink'},
        'ghost': {'value': 30, 'color': 6, 'char': '👻', 'grow': 1, 'powerup': 'ghost'},
        'multiplier': {'value': 20, 'color': 5, 'char': '✦', 'grow': 1, 'powerup': 'multiplier'},
        'shield': {'value': 15, 'color': 6, 'char': '🛡', 'grow': 1, 'powerup': 'shield'},
    }

    def __init__(self, x: int, y: int, ftype: str = 'normal'):
        self.x = x
        self.y = y
        self.ftype = ftype
        info = self.FOOD_TYPES.get(ftype, self.FOOD_TYPES['normal'])
        self.value = info['value']
        self.color = info['color']
        self.char = info['char']
        self.grow_amount = info.get('grow', 1)
        self.powerup = info.get('powerup')
        self.collected = False
        self.anim_timer = 0.0

    def update(self, dt: float):
        self.anim_timer += dt

    @classmethod
    def random_food(cls, x: int, y: int, level: int = 1) -> 'Food':
        """Generate random food based on level."""
        weights = {
            'normal': 50,
            'bonus': 15,
            'poison': 10,
            'speed': 8,
            'shrink': 5,
            'ghost': 5,
            'multiplier': 4,
            'shield': 3,
        }
        # Increase special food chance with level
        if level > 3:
            weights['bonus'] += (level - 3) * 2
            weights['speed'] += (level - 3)
            weights['ghost'] += (level - 3)

        ftype = random.choices(list(weights.keys()), weights=list(weights.values()))[0]
        return cls(x, y, ftype)


@dataclass
class Obstacle:
    """Static obstacle."""
    x: int
    y: int
    char: str = '█'
    color: int = 4


@dataclass
class PowerUp:
    """Floating power-up (different from food)."""
    x: int
    y: int
    ptype: str
    char: str = '?'
    color: int = 5
    duration: float = 10.0
    anim_timer: float = 0.0
    bob_offset: float = 0.0
    collected: bool = False

    TYPES = {
        'shield': {'char': '🛡', 'color': 6, 'name': 'Shield', 'duration': 10},
        'speed': {'char': '⚡', 'color': 3, 'name': 'Speed', 'duration': 8},
        'slow': {'char': '🐌', 'color': 2, 'name': 'Slow', 'duration': 8},
        'ghost': {'char': '👻', 'color': 6, 'name': 'Ghost', 'duration': 6},
        'multiplier': {'char': '✦', 'color': 5, 'name': '2x Score', 'duration': 10},
    }

    def __init__(self, x: int, y: int, ptype: str):
        self.x = x
        self.y = y
        self.ptype = ptype
        info = self.TYPES.get(ptype, self.TYPES['shield'])
        self.char = info['char']
        self.color = info['color']
        self.duration = info['duration']
        self.anim_timer = 0.0
        self.bob_offset = 0.0
        self.collected = False

    def update(self, dt: float):
        self.anim_timer += dt
        self.bob_offset = math.sin(self.anim_timer * 3) * 0.3


@dataclass
class Particle:
    """Visual particle effect."""
    x: float
    y: float
    vx: float
    vy: float
    life: float = 1.0
    max_life: float = 1.0
    char: str = '·'
    color: int = 6

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 5 * dt  # Gravity
        self.life -= dt


def create_particles(x, y, count, color=6, char='·', spread=2.0):
    """Create a burst of particles at position."""
    particles = []
    for _ in range(count):
        angle = random.random() * 2 * math.pi
        speed = random.uniform(1, 5)
        particles.append(Particle(
            x=x, y=y,
            vx=math.cos(angle) * speed,
            vy=math.sin(angle) * speed - random.uniform(0, 3),
            life=random.uniform(0.3, 0.8),
            max_life=0.8,
            char=char,
            color=color
        ))
    return particles


def create_eat_particles(x, y, ftype='normal'):
    """Create particles for eating food."""
    colors = {'normal': 3, 'bonus': 7, 'poison': 4, 'speed': 5, 'ghost': 6}
    chars = {'normal': '·', 'bonus': '✦', 'poison': '☠', 'speed': '⚡', 'ghost': '~'}
    return create_particles(x, y, 8, color=colors.get(ftype, 3), char=chars.get(ftype, '·'))


def create_death_particles(x, y):
    """Create dramatic death explosion."""
    return create_particles(x, y, 20, color=4, char='█', spread=3.0)


def create_levelup_particles(x, y):
    """Create level up celebration."""
    return create_particles(x, y, 15, color=7, char='★', spread=2.0)