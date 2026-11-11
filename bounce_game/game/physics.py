#!/usr/bin/env python3
"""Physics engine for Bounce game - gravity, collision, movement."""

from world.entities import Ball, Platform, Spike, Star, Exit, Block, MovingPlatform


# Physics constants
GRAVITY = 25.0          # pixels/sec^2
JUMP_FORCE = -18.0      # Initial jump velocity
MOVE_FORCE = 12.0       # Horizontal acceleration
MAX_HORIZONTAL_SPEED = 10.0
BOUNCE_DAMPING = 0.65   # Energy loss on bounce
FRICTION = 0.85         # Ground friction
AIR_FRICTION = 0.98     # Air resistance
TERMINAL_VELOCITY = 25.0
WATER_GRAVITY = 8.0     # Reduced gravity in water
WATER_DRAG = 0.85       # Water resistance


class PhysicsEngine:
    def __init__(self):
        self.ground_contact = False

    def update(self, state, dt):
        """Update all physics for one frame."""
        ball = state.ball
        if ball is None:
            return

        # Store previous position for collision resolution
        prev_x, prev_y = ball.center_x, ball.center_y

        # Apply input forces
        self.apply_input(ball, state, dt)

        # Apply gravity
        gravity = WATER_GRAVITY if self.in_water(ball, state) else GRAVITY
        ball.vy += gravity * dt

        # Apply drag
        drag = WATER_DRAG if self.in_water(ball, state) else (AIR_FRICTION if not self.ground_contact else FRICTION)
        ball.vx *= drag ** dt
        ball.vy *= drag ** dt

        # Clamp velocities
        ball.vx = max(-MAX_HORIZONTAL_SPEED, min(MAX_HORIZONTAL_SPEED, ball.vx))
        ball.vy = max(-TERMINAL_VELOCITY, min(TERMINAL_VELOCITY, ball.vy))

        # Integrate position (using center coordinates)
        ball.center_x += ball.vx * dt
        ball.center_y += ball.vy * dt

        # Collision detection & resolution
        self.ground_contact = False
        self.resolve_collisions(ball, state, prev_x, prev_y)

    def apply_input(self, ball, state, dt):
        """Apply player input forces to ball."""
        if ball.input_left:
            ball.vx -= MOVE_FORCE * dt
        if ball.input_right:
            ball.vx += MOVE_FORCE * dt
        if ball.input_jump and self.ground_contact:
            ball.vy = JUMP_FORCE
            self.ground_contact = False

    def in_water(self, ball, state) -> bool:
        """Check if ball is in water."""
        return state.water_level > 0 and ball.center_y + ball.radius > state.water_level

    def resolve_collisions(self, ball, state, prev_x, prev_y):
        """Resolve collisions with all level objects."""
        # Check spikes FIRST (instant death)
        for spike in state.spikes:
            if ball.collides_with(spike):
                state.die()
                return

        # Check moving platforms
        for mp in state.moving_platforms:
            if self.resolve_platform_collision(ball, mp, prev_x, prev_y):
                # Transfer platform velocity to ball
                ball.vx += mp.velocity_x * 0.3
                self.ground_contact = True

        # Check static platforms
        for platform in state.platforms:
            if self.resolve_platform_collision(ball, platform, prev_x, prev_y):
                self.ground_contact = True

        # Check blocks (breakable)
        for block in state.blocks[:]:
            if not block.broken and self.resolve_platform_collision(ball, block, prev_x, prev_y):
                if ball.vy > 10:  # Hit from below with force
                    block.break_block()
                    ball.vy = -ball.vy * 0.5
                self.ground_contact = True

        # Remove broken blocks
        state.blocks = [b for b in state.blocks if not b.broken]

        # Screen boundaries (using center coordinates)
        if ball.center_x - ball.radius < 0:
            ball.center_x = ball.radius
            ball.vx = abs(ball.vx) * BOUNCE_DAMPING
        elif ball.center_x + ball.radius > 80:  # Screen width
            ball.center_x = 80 - ball.radius
            ball.vx = -abs(ball.vx) * BOUNCE_DAMPING

        # Ceiling
        if ball.center_y - ball.radius < 0:
            ball.center_y = ball.radius
            ball.vy = abs(ball.vy) * BOUNCE_DAMPING

    def resolve_platform_collision(self, ball, platform, prev_x, prev_y) -> bool:
        """Resolve collision between ball and a platform-like object.
        Returns True if collision occurred."""
        # Quick AABB check using ball's bounds properties
        if not (ball.x + ball.width > platform.x and
                ball.x < platform.x + platform.width and
                ball.y + ball.height > platform.y and
                ball.y < platform.y + platform.height):
            return False

        # Determine collision direction by checking previous position
        # prev_x, prev_y are center positions
        was_above = prev_y - ball.radius <= platform.y
        was_below = prev_y + ball.radius >= platform.y + platform.height
        was_left = prev_x + ball.radius <= platform.x
        was_right = prev_x - ball.radius >= platform.x + platform.width

        # Top collision (landing on platform)
        if was_above and ball.vy >= 0:
            ball.center_y = platform.y - ball.radius
            ball.vy = -ball.vy * BOUNCE_DAMPING
            return True

        # Bottom collision (hitting head)
        if was_below and ball.vy <= 0:
            ball.center_y = platform.y + platform.height + ball.radius
            ball.vy = -ball.vy * BOUNCE_DAMPING
            return True

        # Side collisions
        if was_left and ball.vx >= 0:
            ball.center_x = platform.x - ball.radius
            ball.vx = -ball.vx * BOUNCE_DAMPING
            return True

        if was_right and ball.vx <= 0:
            ball.center_x = platform.x + platform.width + ball.radius
            ball.vx = -ball.vx * BOUNCE_DAMPING
            return True

        # Fallback: push out based on minimum penetration
        overlap_x = min(ball.x + ball.width, platform.x + platform.width) - max(ball.x, platform.x)
        overlap_y = min(ball.y + ball.height, platform.y + platform.height) - max(ball.y, platform.y)

        if overlap_x < overlap_y:
            # Horizontal push
            if ball.center_x < platform.x + platform.width / 2:
                ball.center_x = platform.x - ball.radius
            else:
                ball.center_x = platform.x + platform.width + ball.radius
            ball.vx = -ball.vx * BOUNCE_DAMPING
        else:
            # Vertical push
            if ball.center_y < platform.y + platform.height / 2:
                ball.center_y = platform.y - ball.radius
                ball.vy = -abs(ball.vy) * BOUNCE_DAMPING
                return True  # Count as ground contact
            else:
                ball.center_y = platform.y + platform.height + ball.radius
                ball.vy = abs(ball.vy) * BOUNCE_DAMPING

        return True