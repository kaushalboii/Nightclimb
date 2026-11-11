#!/usr/bin/env python3
"""Game state management: levels, progress, save/load."""

import json
import time
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

from world.levels import LEVELS
from world.entities import Ball, Platform, Spike, Star, Exit, Block, MovingPlatform, Particle, PowerUp


SAVE_FILE = Path.home() / ".bounce_save.json"


@dataclass
class GameState:
    current_level: int = 0
    stars_collected: int = 0
    total_stars: int = 0
    lives: int = 3
    score: int = 0
    best_times: dict = field(default_factory=dict)  # level_index -> time
    level_start_time: float = 0.0
    last_autosave: float = 0.0
    paused: bool = False
    level_complete: bool = False
    game_over: bool = False
    show_menu: bool = False

    # Runtime entities (not saved)
    ball: Optional[Ball] = None
    platforms: list = field(default_factory=list)
    spikes: list = field(default_factory=list)
    stars: list = field(default_factory=list)
    exits: list = field(default_factory=list)
    blocks: list = field(default_factory=list)
    moving_platforms: list = field(default_factory=list)
    water_level: float = -1
    particles: list = field(default_factory=list)
    powerups: list = field(default_factory=list)

    # Screen shake
    shake_intensity: float = 0
    shake_timer: float = 0

    def __post_init__(self):
        self.load_level()

    def load_level(self):
        """Load current level data and initialize entities."""
        if self.current_level >= len(LEVELS):
            self.current_level = len(LEVELS) - 1

        level_data = LEVELS[self.current_level]

        # Ball spawn
        spawn = level_data.get("spawn", (10, 10))
        self.ball = Ball(spawn[0], spawn[1])

        # Static platforms
        self.platforms = [Platform(*p) for p in level_data.get("platforms", [])]

        # Moving platforms
        self.moving_platforms = [MovingPlatform(*p) for p in level_data.get("moving_platforms", [])]

        # Spikes
        self.spikes = [Spike(*s) for s in level_data.get("spikes", [])]

        # Stars
        self.stars = [Star(*s) for s in level_data.get("stars", [])]
        self.total_stars = len(self.stars)

        # Exit
        exit_data = level_data.get("exit", (70, 5))
        self.exits = [Exit(*exit_data)]

        # Blocks (breakable)
        self.blocks = [Block(*b) for b in level_data.get("blocks", [])]

        # Water level
        self.water_level = level_data.get("water", -1)

        # Power-ups (spawn some randomly on certain levels)
        self.powerups = []
        if self.current_level >= 3:  # Later levels get power-ups
            import random
            for star in self.stars:
                if random.random() < 0.15:  # 15% chance per star location
                    ptype = random.choice(['shield', 'double_jump', 'speed'])
                    self.powerups.append(PowerUp(star.x + random.uniform(-2, 2), star.y - 2, ptype))

        # Reset level state
        self.level_complete = False
        self.game_over = False
        self.stars_collected = 0
        self.level_start_time = time.time()
        self.paused = False
        self.particles = []
        self.shake_intensity = 0
        self.shake_timer = 0

    def trigger_shake(self, intensity=2, duration=0.3):
        """Trigger screen shake effect."""
        self.shake_intensity = intensity
        self.shake_timer = duration

    def update(self, dt):
        """Update game state."""
        if self.ball is None:
            return

        # Update moving platforms
        for mp in self.moving_platforms:
            mp.update(dt)

        # Update spikes animation
        for spike in self.spikes:
            spike.update(dt)

        # Update stars
        for star in self.stars:
            star.update(dt)

        # Update exit
        for exit_obj in self.exits:
            exit_obj.update(dt, self.stars_collected, self.total_stars)

        # Update power-ups
        for pup in self.powerups[:]:
            pup.update(dt)
            if not pup.collected and self.ball.collides_with(pup):
                self.collect_powerup(pup)

        # Check star collection
        for star in self.stars[:]:
            if not star.collected and self.ball.collides_with(star):
                star.collected = True
                self.stars_collected += 1
                self.score += 100
                # Create sparkle particles
                from world.entities import create_star_particles
                self.particles.extend(create_star_particles(star.x + 0.5, star.y + 0.5))

        # Check exit
        for exit_obj in self.exits:
            if self.ball.collides_with(exit_obj) and self.stars_collected >= self.total_stars:
                self.complete_level()

        # Check death (fall off screen or spikes handled in physics)
        if self.ball.y > 50:  # Fell off bottom
            self.die()

        # Update power-up timers on ball
        if self.ball.has_shield:
            self.ball.shield_timer -= dt
            if self.ball.shield_timer <= 0:
                self.ball.has_shield = False
        if self.ball.has_speed_boost:
            self.ball.speed_boost_timer -= dt
            if self.ball.speed_boost_timer <= 0:
                self.ball.has_speed_boost = False

    def collect_powerup(self, pup):
        """Apply power-up effect to ball."""
        pup.collected = True
        self.powerups.remove(pup)

        if pup.ptype == 'shield':
            self.ball.has_shield = True
            self.ball.shield_timer = pup.duration
        elif pup.ptype == 'double_jump':
            self.ball.has_double_jump = True
            self.ball.double_jump_used = False
        elif pup.ptype == 'speed':
            self.ball.has_speed_boost = True
            self.ball.speed_boost_timer = pup.duration
        elif pup.ptype == 'extra_life':
            self.lives = min(5, self.lives + 1)

        self.score += 500
        from world.entities import create_star_particles
        self.particles.extend(create_star_particles(pup.x, pup.y))

    def complete_level(self):
        """Handle level completion."""
        self.level_complete = True
        elapsed = time.time() - self.level_start_time

        # Save best time
        if self.current_level not in self.best_times or elapsed < self.best_times[self.current_level]:
            self.best_times[self.current_level] = elapsed

        # Bonus score for time
        time_bonus = max(0, int(5000 - elapsed * 100))
        self.score += time_bonus

        # Completion bonus
        self.score += 1000 + self.stars_collected * 200

    def die(self):
        """Handle player death."""
        # Shield protects from one death
        if self.ball.has_shield:
            self.ball.has_shield = False
            self.ball.shield_timer = 0
            # Bounce back up
            self.ball.vy = -15
            self.ball.center_y = 20
            # Particles
            from world.entities import create_death_particles
            self.particles.extend(create_death_particles(self.ball.center_x, self.ball.center_y))
            self.trigger_shake(1, 0.15)
            return

        self.lives -= 1
        self.trigger_shake(3, 0.4)

        # Death particles
        from world.entities import create_death_particles
        self.particles.extend(create_death_particles(self.ball.center_x, self.ball.center_y))

        if self.lives <= 0:
            self.game_over = True
            self.lives = 0
        else:
            # Respawn at level start
            self.load_level()

    def restart_level(self):
        """Restart current level."""
        self.lives = 3
        self.score = 0
        self.load_level()

    def next_level(self):
        """Advance to next level."""
        if self.current_level < len(LEVELS) - 1:
            self.current_level += 1
            self.load_level()
        else:
            # Game complete - loop to first level
            self.current_level = 0
            self.load_level()

    def prev_level(self):
        """Go to previous level."""
        if self.current_level > 0:
            self.current_level -= 1
            self.load_level()

    def set_level(self, level_index: int):
        """Jump to specific level."""
        if 0 <= level_index < len(LEVELS):
            self.current_level = level_index
            self.load_level()

    def should_autosave(self) -> bool:
        """Check if we should auto-save."""
        return time.time() - self.last_autosave > 10.0  # Every 10 seconds

    def save(self, path: Path):
        """Save game state to file."""
        data = {
            "current_level": self.current_level,
            "stars_collected": self.stars_collected,
            "total_stars": self.total_stars,
            "lives": self.lives,
            "score": self.score,
            "best_times": self.best_times,
            "last_autosave": time.time(),
        }
        try:
            with open(path, 'w') as f:
                json.dump(data, f)
            self.last_autosave = time.time()
        except Exception as e:
            pass  # Silent fail for autosave

    def load(self, path: Path):
        """Load game state from file."""
        try:
            path = Path(path)  # Ensure it's a Path object
            if path.exists():
                with open(path, 'r') as f:
                    data = json.load(f)

                self.current_level = data.get("current_level", 0)
                self.lives = data.get("lives", 3)
                self.score = data.get("score", 0)
                # JSON saves dict keys as strings, convert back to int
                self.best_times = {int(k): v for k, v in data.get("best_times", {}).items()}
                self.last_autosave = data.get("last_autosave", time.time())

                # Clamp level
                self.current_level = max(0, min(self.current_level, len(LEVELS) - 1))

                # Reload level with saved progress
                self.load_level()
        except Exception:
            # Corrupted save - start fresh
            self.current_level = 0
            self.load_level()