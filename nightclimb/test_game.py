#!/usr/bin/env python3
"""
Test script to verify game logic without curses.
Run: python test_game.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from games.bounce.world.levels import LEVELS, LEVEL_NAMES
from games.bounce.world.entities import Ball, Platform, Spike, Star, Exit, Block, MovingPlatform
from games.bounce.game.state import GameState
from games.bounce.game.physics import PhysicsEngine


def test_levels():
    print("Testing levels...")
    assert len(LEVELS) == 12, f"Expected 12 levels, got {len(LEVELS)}"
    assert len(LEVEL_NAMES) == 12
    print(f"  ✓ {len(LEVELS)} levels loaded")
    for i, level in enumerate(LEVELS):
        print(f"  Level {i+1}: {level['name']} - {len(level.get('stars', []))} stars, {len(level.get('spikes', []))} spike groups")
    return True


def test_entities():
    print("\nTesting entities...")

    # Ball - uses center coordinates
    ball = Ball(center_x=10, center_y=10)
    assert ball.radius == 1.5
    assert ball.center_x == 10
    assert ball.center_y == 10
    assert ball.x == 8.5  # left edge
    assert ball.y == 8.5  # top edge
    assert ball.width == 3.0
    assert ball.height == 3.0
    print("  ✓ Ball creation")

    # Platform
    plat = Platform(0, 20, 80, 2)
    assert plat.width == 80
    assert plat.height == 2
    print("  ✓ Platform creation")

    # Spike
    spike = Spike(10, 10, 5, 1, 'up')
    assert spike.orientation == 'up'
    print("  ✓ Spike creation")

    # Star
    star = Star(15, 15)
    assert not star.collected
    print("  ✓ Star creation")

    # Exit
    exit_obj = Exit(75, 5)
    assert exit_obj.width == 2
    assert exit_obj.height == 3
    print("  ✓ Exit creation")

    # Block
    block = Block(20, 20, 2, 2, 2)
    assert block.hits == 2
    assert not block.broken
    block.break_block()
    assert block.hits == 1
    block.break_block()
    assert block.broken
    print("  ✓ Block creation and breaking")

    # MovingPlatform
    mp = MovingPlatform(10, 10, 4, 1, 10, 2.0)
    mp.update(0.5)
    assert mp.x > 10
    print("  ✓ MovingPlatform creation and update")

    return True


def test_physics():
    print("\nTesting physics...")
    physics = PhysicsEngine()
    state = GameState()
    state.current_level = 0
    state.load_level()

    # Simulate a few frames - ball should fall
    initial_y = state.ball.center_y
    for _ in range(10):
        physics.update(state, 1/60)
        state.update(1/60)

    assert state.ball is not None
    assert state.ball.center_y > initial_y  # Should fall due to gravity
    print("  ✓ Gravity works")

    # Test jump - need ground contact, move right first to clear platform above
    state.ball.vy = 0
    state.ball.vx = 0
    state.ball.input_right = True
    physics.ground_contact = True
    # Move right for a few frames
    for _ in range(10):
        physics.update(state, 1/60)

    # Now jump
    state.ball.input_right = False
    state.ball.input_jump = True
    physics.ground_contact = True
    physics.update(state, 1/60)
    assert state.ball.vy < 0  # Should jump up
    print("  ✓ Jump works")

    # Test horizontal movement
    state.ball.vx = 0
    state.ball.input_right = True
    physics.update(state, 1/60)
    assert state.ball.vx > 0
    print("  ✓ Horizontal movement works")

    return True


def test_state_save_load():
    print("\nTesting save/load...")
    import tempfile
    import json

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name

    try:
        state = GameState()
        state.current_level = 3
        state.lives = 2
        state.score = 1500
        state.best_times = {0: 45.2, 1: 32.1}
        state.save(temp_path)

        # Load into new state
        new_state = GameState()
        new_state.load(temp_path)

        assert new_state.current_level == 3
        assert new_state.lives == 2
        assert new_state.score == 1500
        assert new_state.best_times == {0: 45.2, 1: 32.1}
        print("  ✓ Save/load works")

        # Test level progression
        state.next_level()
        assert state.current_level == 4
        state.prev_level()
        assert state.current_level == 3
        print("  ✓ Level navigation works")

    finally:
        os.unlink(temp_path)

    return True


def test_collision():
    print("\nTesting collision detection...")
    ball = Ball(center_x=10, center_y=10)
    platform = Platform(8, 12, 5, 1)  # Platform at y=12, ball center at y=10 (top at 8.5)

    # Ball above platform - check collision
    # Ball bounds: x=8.5 to 11.5, y=8.5 to 11.5
    # Platform bounds: x=8 to 13, y=12 to 13
    # These don't overlap yet (ball bottom at 11.5 < platform top at 12)
    assert not ball.collides_with(platform)

    # Move ball down to touch platform
    ball.center_y = 11.5  # Ball bottom at 13, platform top at 12
    assert ball.collides_with(platform)
    print("  ✓ Collision detection works")

    return True


if __name__ == "__main__":
    print("=" * 50)
    print("BOUNCE GAME - LOGIC TESTS")
    print("=" * 50)

    all_passed = True
    for test in [test_levels, test_entities, test_physics, test_state_save_load, test_collision]:
        try:
            test()
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("ALL TESTS PASSED ✓")
        print("\nTo play the game, run in a real terminal:")
        print("  python run.py")
    else:
        print("SOME TESTS FAILED ✗")
    print("=" * 50)