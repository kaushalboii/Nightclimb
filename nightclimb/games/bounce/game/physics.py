#!/usr/bin/env python3
"""Physics engine for Bounce game - gravity, collision, movement.

Enhanced with:
- Power-up effects (speed boost, double jump)
- Water surface jumping
- Better collision resolution
"""

from ..world.entities import Ball, Platform, Spike, Star, Exit, Block, MovingPlatform


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
        self.water_surface_contact = False

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

        # Speed boost increases max speed
        max_speed = MAX_HORIZONTAL_SPEED * (1.5 if ball.has_speed_boost else 1.0)

        # Clamp velocities
        ball.vx = max(-max_speed, min(max_speed, ball.vx))
        ball.vy = max(-TERMINAL_VELOCITY, min(TERMINAL_VELOCITY, ball.vy))

        # Integrate position (using center coordinates)
        ball.center_x += ball.vx * dt
        ball.center_y += ball.vy * dt

        # Reset ground contact, will be set by collision resolution
        self.ground_contact = False
        self.water_surface_contact = False

        # Collision detection & resolution
        self.resolve_collisions(ball, state, prev_center_x, prev_center_y)

    def apply_input(self, ball, dt):
        """Apply player input forces to ball."""
        move_force = MOVE_FORCE * (1.3 if ball.has_speed_boost else 1.0)

        if ball.input_left:
            ball.vx -= move_force * dt
        if ball.input_right:
            ball.vx += move_force * dt

        # Jump logic: ground contact OR water surface contact
        can_jump = self.ground_contact or self.water_surface_contact
        if ball.input_jump and can_jump:
            ball.vy = JUMP_FORCE
            self.ground_contact = False
            self.water_surface_contact = False
            # Reset double jump
            if ball.has_double_jump:
                ball.double_jump_used = False
        # Double jump
        elif ball.input_jump and ball.has_double_jump and not ball.double_jump_used and not can_jump:
            ball.vy = JUMP_FORCE * 0.9  # Slightly weaker double jump
            ball.double_jump_used = True

    def in_water(self, ball, state) -> bool:
        """Check if ball is in water (center_y + radius > water_level)."""
        return state.water_level > 0 and ball.center_y + ball.radius > state.water_level

    def at_water_surface(self, ball, state) -> bool:
        """Check if ball is at water surface (touching from above)."""
        if state.water_level <= 0:
            return False
        # Ball bottom is near water level, and moving downward
        return (abs(ball.center_y + ball.radius - state.water_level) < 1.0 and
                ball.vy >= 0)

    def resolve_collisions(self, ball, state, prev_x, prev_y):
        """Resolve collisions with all level objects. Order matters!"""

        # 1. SPIKES - instant death (check first)
        for spike in state.spikes:
            if ball.collides_with(spike):
                # Shield protects from spikes
                if ball.has_shield:
                    ball.has_shield = False
                    ball.shield_timer = 0
                    ball.vy = -10  # Bounce away
                    return
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
                    from world.entities import create_block_break_particles
                    state.particles.extend(create_block_break_particles(block.x + block.width/2, block.y + block.height/2))
                self.ground_contact = True

        # Remove broken blocks
        state.blocks = [b for b in state.blocks if not b.broken]

        # 5. WATER SURFACE - can jump from water surface
        if self.at_water_surface(ball, state):
            self.water_surface_contact = True
            # Buoyancy - push up slightly
            if ball.vy > 0:
                ball.vy *= 0.5

        # 6. SCREEN BOUNDARIES
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
        was_above = prev_bottom <= plat_top
        was_below = prev_top >= plat_bottom
        was_left = prev_right <= plat_left
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