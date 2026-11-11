#!/usr/bin/env python3
"""Game state management for Snake."""

import json
import time
import random
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional

from ..world.entities import Snake, Food, Obstacle, PowerUp, Particle
from ..world.levels import MODES


SAVE_FILE = Path.home() / ".snake_save.json"


@dataclass
class GameState:
    # Game mode
    mode: str = 'classic'  # classic, arcade, survival, time_attack
    mode_index: int = 0

    # Grid
    grid_width: int = 40
    grid_height: int = 20

    # Game state
    snake: Optional[Snake] = None
    foods: List[Food] = field(default_factory=list)
    obstacles: List[Obstacle] = field(default_factory=list)
    powerups: List[PowerUp] = field(default_factory=list)
    particles: List[Particle] = field(default_factory=list)

    # Score & progress
    score: int = 0
    high_scores: dict = field(default_factory=dict)  # mode -> score
    level: int = 1
    foods_eaten: int = 0
    level_food_target: int = 5

    # State flags
    paused: bool = False
    game_over: bool = False
    level_complete: bool = False
    show_menu: bool = False

    # Timing
    level_start_time: float = 0.0
    game_start_time: float = 0.0
    last_autosave: float = 0.0

    # Screen shake
    shake_intensity: float = 0
    shake_timer: float = 0

    def __post_init__(self):
        self.init_game()

    def init_game(self):
        """Initialize a new game."""
        mode_info = MODES[self.mode_index]
        self.grid_width = mode_info.get('width', 40)
        self.grid_height = mode_info.get('height', 20)

        # Create snake in center
        cx, cy = self.grid_width // 2, self.grid_height // 2
        self.snake = Snake(body=[(cx, cy), (cx-1, cy), (cx-2, cy)])

        # Clear entities
        self.foods = []
        self.obstacles = []
        self.powerups = []
        self.particles = []

        # Spawn initial food
        self.spawn_food(3)

        # Spawn obstacles based on mode
        if mode_info.get('obstacles', False):
            self.spawn_obstacles(mode_info.get('obstacle_count', 5))

        # Reset stats
        self.score = 0
        self.level = 1
        self.foods_eaten = 0
        self.level_food_target = 5
        self.level_start_time = time.time()
        self.game_start_time = time.time()
        self.paused = False
        self.game_over = False
        self.level_complete = False
        self.shake_intensity = 0
        self.shake_timer = 0

    def spawn_food(self, count: int = 1):
        """Spawn food at random empty positions."""
        for _ in range(count):
            attempts = 0
            while attempts < 50:
                x = random.randint(0, self.grid_width - 1)
                y = random.randint(0, self.grid_height - 1)

                # Check not on snake
                if (x, y) in self.snake.body:
                    attempts += 1
                    continue

                # Check not on obstacle
                if any(o.x == x and o.y == y for o in self.obstacles):
                    attempts += 1
                    continue

                # Check not on existing food
                if any(f.x == x and f.y == y for f in self.foods):
                    attempts += 1
                    continue

                self.foods.append(Food.random_food(x, y, self.level))
                break

    def spawn_obstacles(self, count: int):
        """Spawn obstacles at random positions."""
        for _ in range(count):
            attempts = 0
            while attempts < 50:
                x = random.randint(0, self.grid_width - 1)
                y = random.randint(0, self.grid_height - 1)

                # Keep away from snake start
                if abs(x - self.grid_width//2) < 5 and abs(y - self.grid_height//2) < 5:
                    attempts += 1
                    continue

                # Check not on existing obstacle
                if any(o.x == x and o.y == y for o in self.obstacles):
                    attempts += 1
                    continue

                self.obstacles.append(Obstacle(x, y))
                break

    def spawn_powerup(self):
        """Randomly spawn a power-up."""
        if random.random() < 0.15:  # 15% chance per food eaten
            attempts = 0
            while attempts < 20:
                x = random.randint(0, self.grid_width - 1)
                y = random.randint(0, self.grid_height - 1)

                if (x, y) in self.snake.body:
                    attempts += 1
                    continue
                if any(o.x == x and o.y == y for o in self.obstacles):
                    attempts += 1
                    continue
                if any(f.x == x and f.y == y for f in self.foods):
                    attempts += 1
                    continue

                ptype = random.choice(['shield', 'speed', 'ghost', 'multiplier'])
                self.powerups.append(PowerUp(x, y, ptype))
                break

    def update(self, dt: float):
        """Update game state."""
        if self.snake is None:
            return

        # Update snake
        alive, event = self.snake.update(dt, self.grid_width, self.grid_height, self.obstacles)

        if not alive:
            self.die(event)
            return

        # Handle shield block event
        if event == 'shield_blocked':
            self.trigger_shake(1, 0.15)
            from ..world.entities import create_death_particles
            hx, hy = self.snake.head
            self.particles.extend(create_death_particles(hx, hy))

        # Check food collision
        for food in self.foods[:]:
            if not food.collected and self.snake.head == (food.x, food.y):
                self.eat_food(food)
                break

        # Check power-up collision
        for pup in self.powerups[:]:
            if not pup.collected and self.snake.head == (pup.x, pup.y):
                self.collect_powerup(pup)
                break

        # Update foods
        for food in self.foods:
            food.update(dt)

        # Update power-ups
        for pup in self.powerups[:]:
            pup.update(dt)
            # Despawn old power-ups
            if pup.anim_timer > 15.0:
                self.powerups.remove(pup)

        # Ensure minimum food
        if len(self.foods) < 2:
            self.spawn_food(2 - len(self.foods))

        # Check level progression
        if self.foods_eaten >= self.level_food_target:
            self.next_level()

    def eat_food(self, food: Food):
        """Handle eating food."""
        food.collected = True
        self.foods.remove(food)

        # Score
        points = int(food.value * self.snake.score_multiplier)
        self.score += points
        self.foods_eaten += 1

        # Growth
        self.snake.grow(food.grow_amount)

        # Power-up from food
        if food.powerup:
            self.snake.apply_powerup(food.powerup)

        # Particles
        from ..world.entities import create_eat_particles
        self.particles.extend(create_eat_particles(food.x, food.y, food.ftype))

        # Screen shake for special food
        if food.ftype in ('bonus', 'poison'):
            self.trigger_shake(1, 0.2)

        # Spawn new food
        self.spawn_food(1)

        # Chance to spawn power-up
        self.spawn_powerup()

    def collect_powerup(self, pup: PowerUp):
        """Handle collecting power-up."""
        pup.collected = True
        self.powerups.remove(pup)
        self.snake.apply_powerup(pup.ptype, pup.duration)

        from ..world.entities import create_eat_particles
        self.particles.extend(create_eat_particles(pup.x, pup.y, 'bonus'))
        self.trigger_shake(1, 0.15)

    def next_level(self):
        """Advance to next level."""
        self.level += 1
        self.foods_eaten = 0
        self.level_food_target = 5 + self.level * 2
        self.level_start_time = time.time()

        # Increase snake speed slightly
        self.snake.speed = min(20, 10 + self.level * 0.5)

        # Add more obstacles in arcade mode
        if self.mode == 'arcade' and self.level % 2 == 0:
            self.spawn_obstacles(2)

        # Level up particles
        from ..world.entities import create_levelup_particles
        cx, cy = self.grid_width // 2, self.grid_height // 2
        self.particles.extend(create_levelup_particles(cx, cy))
        self.trigger_shake(2, 0.3)

    def die(self, cause: str):
        """Handle death."""
        self.game_over = True
        self.trigger_shake(3, 0.5)

        from ..world.entities import create_death_particles
        hx, hy = self.snake.head
        self.particles.extend(create_death_particles(hx, hy))

        # Update high score
        if self.mode not in self.high_scores or self.score > self.high_scores[self.mode]:
            self.high_scores[self.mode] = self.score

    def restart_game(self):
        """Restart current game."""
        self.init_game()

    def set_mode(self, mode_index: int):
        """Change game mode."""
        self.mode_index = mode_index
        self.mode = MODES[mode_index]['id']
        self.restart_game()

    def trigger_shake(self, intensity=2, duration=0.3):
        """Trigger screen shake."""
        self.shake_intensity = intensity
        self.shake_timer = duration

    def should_autosave(self) -> bool:
        return time.time() - self.last_autosave > 10.0

    def save(self, path: Path):
        """Save game state."""
        data = {
            "mode_index": self.mode_index,
            "high_scores": self.high_scores,
            "last_autosave": time.time(),
        }
        try:
            with open(path, 'w') as f:
                json.dump(data, f)
            self.last_autosave = time.time()
        except Exception:
            pass

    def load(self, path: Path):
        """Load game state."""
        try:
            path = Path(path)
            if path.exists():
                with open(path, 'r') as f:
                    data = json.load(f)

                self.mode_index = data.get("mode_index", 0)
                self.mode = MODES[self.mode_index]['id']
                self.high_scores = data.get("high_scores", {})
                self.last_autosave = data.get("last_autosave", time.time())
        except Exception:
            self.mode_index = 0
            self.mode = MODES[0]['id']
            self.high_scores = {}