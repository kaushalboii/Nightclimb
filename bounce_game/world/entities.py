#!/usr/bin/env python3
"""Game entities: Ball, Platforms, Spikes, Stars, Exit, Blocks."""

from dataclasses import dataclass, field
from typing import Optional
import math


@dataclass
class Entity:
    """Base entity with position and size (top-left origin)."""
    x: float
    y: float
    width: float = 1.0
    height: float = 1.0

    def collides_with(self, other: 'Entity') -> bool:
        """AABB collision check."""
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)

    def get_center(self):
        return (self.x + self.width / 2, self.y + self.height / 2)


@dataclass
class Ball:
    """The player-controlled bouncing ball. Uses center coordinates for physics."""
    center_x: float = 10.0
    center_y: float = 10.0
    radius: float = 1.5
    vx: float = 0.0
    vy: float = 0.0

    # Input state (set by input handler)
    input_left: bool = False
    input_right: bool = False
    input_jump: bool = False

    # Visual
    squash: float = 1.0
    trail: list = field(default_factory=list)

    @property
    def x(self):
        """Left edge for collision."""
        return self.center_x - self.radius

    @property
    def y(self):
        """Top edge for collision."""
        return self.center_y - self.radius

    @property
    def width(self):
        return self.radius * 2

    @property
    def height(self):
        return self.radius * 2

    def collides_with(self, other: Entity) -> bool:
        """AABB collision check using ball's bounds."""
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)

    def update_rect(self):
        """Compatibility method - no-op since properties compute bounds."""
        pass


@dataclass
class Platform(Entity):
    """Static platform."""
    def __init__(self, x, y, width, height=1):
        super().__init__(x, y, width, height)
        self.color = 2  # Green


@dataclass
class MovingPlatform(Platform):
    """Platform that moves back and forth."""
    def __init__(self, x, y, width, height, range_x, speed=2.0, vertical=False):
        super().__init__(x, y, width, height)
        self.start_x = x
        self.start_y = y
        self.range_x = range_x
        self.range_y = 0
        self.speed = speed
        self.vertical = vertical
        self.direction = 1
        self.velocity_x = 0
        self.velocity_y = 0
        self.color = 6  # Cyan
        self.anim_timer = 0

    def update(self, dt):
        self.anim_timer += dt
        if self.vertical:
            self.y += self.direction * self.speed * dt
            self.velocity_y = self.direction * self.speed
            self.velocity_x = 0
            if self.y >= self.start_y + self.range_x or self.y <= self.start_y:
                self.direction *= -1
        else:
            self.x += self.direction * self.speed * dt
            self.velocity_x = self.direction * self.speed
            self.velocity_y = 0
            if self.x >= self.start_x + self.range_x or self.x <= self.start_x:
                self.direction *= -1


@dataclass
class Spike(Entity):
    """Deadly spike - instant death on contact."""
    def __init__(self, x, y, width=1, height=1, orientation='up'):
        super().__init__(x, y, width, height)
        self.orientation = orientation  # 'up', 'down', 'left', 'right'
        self.color = 5  # Magenta
        self.anim_timer = 0

    def update(self, dt):
        self.anim_timer += dt


@dataclass
class Star(Entity):
    """Collectible star."""
    def __init__(self, x, y):
        super().__init__(x, y, 1, 1)
        self.collected = False
        self.color = 3  # Yellow
        self.anim_timer = 0
        self.bob_offset = 0

    def update(self, dt):
        self.anim_timer += dt
        self.bob_offset = math.sin(self.anim_timer * 3) * 0.3


@dataclass
class Exit(Entity):
    """Level exit - requires all stars collected."""
    def __init__(self, x, y):
        super().__init__(x, y, 2, 3)
        self.color = 4  # Cyan
        self.anim_timer = 0
        self.open = False

    def update(self, dt, stars_collected, total_stars):
        self.anim_timer += dt
        self.open = stars_collected >= total_stars


@dataclass
class Block(Entity):
    """Breakable block."""
    def __init__(self, x, y, width=1, height=1, hits=1):
        super().__init__(x, y, width, height)
        self.hits = hits
        self.max_hits = hits
        self.broken = False
        self.color = 2  # Green

    def break_block(self):
        self.hits -= 1
        if self.hits <= 0:
            self.broken = True