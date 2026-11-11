#!/usr/bin/env python3
"""Physics engine for Bounce game - gravity, collision, movement.

Matches original Nokia Bounce physics:
- Weighty momentum-based movement
- Fixed jump height (no variable jump)
- Weak air control
- Bounce damping on all collisions
- Moving platform velocity transfer
"""

from world.entities import Ball, Platform, Spike, Star, Exit, Block, MovingPlatform


# Physics constants (tuned to match original Nokia Bounce)
GRAVITY = 25.0              # px/s^2 downward
JUMP_FORCE = -18.0          # Initial jump velocity (px/s)
MOVE_FORCE = 12.0           # Horizontal acceleration (px/s^2)
MAX_HORIZONTAL_SPEED = 10.0 # Terminal horizontal speed (px/s)
BOUNCE_DAMPING = 0.65       # Energy retained on bounce (0-1)
FRICTION = 0.85             # Ground friction per frame
AIR_FRICTION = 0.98         # Air resistance per frame
TERMINAL_VELOCITY = 25.0    # Max fall speed (px/s)
WATER_GRAVITY = 8.0         # Reduced gravity in water
WATER_DRAG = 0.85           # Water resistance per frame


class PhysicsEngine:
    def __init__(self):
        self.ground_contact = False

    def update(self, state, dt):
        """Update all physics for one frame."""
        ball = state.ball
        if ball is None:
            return

        # Store previous position for collision resolution
        prev_center_x, prev_center_y = ball.center_x, ball.center_y

        # Apply input forces
        self.apply_input(ball, dt)

        # Apply gravity
        gravity = WATER_GRAVITY if self.in_water(ball, state) else GRAVITY
        ball.vy += gravity * dt

        # Apply drag
        if self.in_water(ball, state):
            drag = WATER_DRAG
        elif self.ground_contact:
            drag = FRICTION
        else:
            drag = AIR_FRICTION
        ball.vx *= drag ** dt
        ball.vy *= drag ** dt

        # Clamp velocities
        ball.vx = max(-MAX_HORIZONTAL_SPEED, min(MAX_HORIZONTAL_SPEED, ball.vx))
        ball.vy = max(-TERMINAL_VELOCITY, min(TERMINAL_VELOCITY, ball.vy))

        # Integrate position (using center coordinates)
        ball.center_x += ball.vx * dt
        ball.center_y += ball.vy * dt

        # Reset ground contact, will be set by collision resolution
        self.ground_contact = False

        # Collision detection & resolution
        self.resolve_collisions(ball, state, prev_center_x, prev_center_y)

    def apply_input(self, ball, dt):
        """Apply player input forces to ball."""
        if ball.input_left:
            ball.vx -= MOVE_FORCE * dt
        if ball.input_right:
            ball.vx += MOVE_FORCE * dt
        if ball.input_jump and self.ground_contact:
            ball.vy = JUMP_FORCE
            self.ground_contact = False  # Prevent double-jump

    def in_water(self, ball, state) -> bool:
        """Check if ball is in water (center_y + radius > water_level)."""
        return state.water_level > 0 and ball.center_y + ball.radius > state.water_level

    def resolve_collisions(self, ball, state, prev_x, prev_y):
        """Resolve collisions with all level objects. Order matters!"""

        # 1. SPIKES - instant death (check first)
        for spike in state.spikes:
            if ball.collides_with(spike):
                state.die()
                return

        # 2. MOVING PLATFORMS - resolve and transfer velocity
        for mp in state.moving_platforms:
            if self.resolve_platform_collision(ball, mp, prev_x, prev_y):
                # Transfer platform velocity to ball (30%)
                ball.vx += mp.velocity_x * 0.3
                ball.vy += mp.velocity_y * 0.3
                self.ground_contact = True

        # 3. STATIC PLATFORMS
        for platform in state.platforms:
            if self.resolve_platform_collision(ball, platform, prev_x, prev_y):
                self.ground_contact = True

        # 4. BREAKABLE BLOCKS
        for block in state.blocks[:]:  # Copy list since we may remove
            if not block.broken and self.resolve_platform_collision(ball, block, prev_x, prev_y):
                # Break if hit from below with sufficient force
                if ball.vy > 10:  # Moving upward fast = hit from below
                    block.break_block()
                    ball.vy = -ball.vy * 0.5  # Bounce back down
                self.ground_contact = True

        # Remove broken blocks
        state.blocks = [b for b in state.blocks if not b.broken]

        # 5. SCREEN BOUNDARIES
        radius = ball.radius
        # Left wall
        if ball.center_x - radius < 0:
            ball.center_x = radius
            ball.vx = abs(ball.vx) * BOUNCE_DAMPING
        # Right wall (screen width = 80)
        elif ball.center_x + radius > 80:
            ball.center_x = 80 - radius
            ball.vx = -abs(ball.vx) * BOUNCE_DAMPING

        # Ceiling
        if ball.center_y - radius < 0:
            ball.center_y = radius
            ball.vy = abs(ball.vy) * BOUNCE_DAMPING

        # Floor death is handled in state.update() (ball.y > 50)

    def resolve_platform_collision(self, ball, platform, prev_x, prev_y) -> bool:
        """
        Resolve collision between ball and a platform-like object.
        Returns True if collision occurred and was resolved.

        Uses previous frame position (center coordinates) to determine
        collision direction for proper sliding/bouncing behavior.
        """
        radius = ball.radius

        # Ball bounds (current frame)
        ball_left = ball.center_x - radius
        ball_right = ball.center_x + radius
        ball_top = ball.center_y - radius
        ball_bottom = ball.center_y + radius

        # Platform bounds (top-left origin)
        plat_left = platform.x
        plat_right = platform.x + platform.width
        plat_top = platform.y
        plat_bottom = platform.y + platform.height

        # Quick AABB check - no overlap = no collision
        if ball_right <= plat_left or ball_left >= plat_right:
            return False
        if ball_bottom <= plat_top or ball_top >= plat_bottom:
            return False

        # Previous frame ball bounds (center coordinates)
        prev_left = prev_x - radius
        prev_right = prev_x + radius
        prev_top = prev_y - radius
        prev_bottom = prev_y + radius

        # Determine collision direction from previous position
        # Ball was ABOVE platform (landed on top)
        was_above = prev_bottom <= plat_top
        # Ball was BELOW platform (hit head)
        was_below = prev_top >= plat_bottom
        # Ball was LEFT of platform
        was_left = prev_right <= plat_left
        # Ball was RIGHT of platform
        was_right = prev_left >= plat_right

        # Priority: vertical collisions first (more common)
        # Top collision - landing on platform
        if was_above and ball.vy >= 0:
            ball.center_y = plat_top - radius
            ball.vy = -ball.vy * BOUNCE_DAMPING
            return True

        # Bottom collision - hitting head on platform
        if was_below and ball.vy <= 0:
            ball.center_y = plat_bottom + radius
            ball.vy = -ball.vy * BOUNCE_DAMPING
            return True

        # Side collisions
        if was_left and ball.vx >= 0:
            ball.center_x = plat_left - radius
            ball.vx = -ball.vx * BOUNCE_DAMPING
            return True

        if was_right and ball.vx <= 0:
            ball.center_x = plat_right + radius
            ball.vx = -ball.vx * BOUNCE_DAMPING
            return True

        # Fallback: push out by minimum penetration
        overlap_x = min(ball_right, plat_right) - max(ball_left, plat_left)
        overlap_y = min(ball_bottom, plat_bottom) - max(ball_top, plat_top)

        if overlap_x < overlap_y:
            # Horizontal push
            if ball.center_x < plat_left + platform.width / 2:
                ball.center_x = plat_left - radius
            else:
                ball.center_x = plat_right + radius
            ball.vx = -ball.vx * BOUNCE_DAMPING
        else:
            # Vertical push
            if ball.center_y < plat_top + platform.height / 2:
                ball.center_y = plat_top - radius
                ball.vy = -abs(ball.vy) * BOUNCE_DAMPING
                return True  # Count as ground contact
            else:
                ball.center_y = plat_bottom + radius
                ball.vy = abs(ball.vy) * BOUNCE_DAMPING

        return True