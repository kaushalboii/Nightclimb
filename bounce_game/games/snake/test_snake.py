#!/usr/bin/env python3
"""Test script for Snake game logic."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from world.entities import Snake, Food, Obstacle, PowerUp, Particle
from game.state import GameState
from world.levels import MODES


def test_snake_movement():
    print("Testing snake movement...")
    snake = Snake(body=[(10, 10), (9, 10), (8, 10)])
    assert snake.head == (10, 10)
    assert snake.length == 3

    # Test direction change
    snake.set_direction((0, -1))  # Up
    assert snake.next_direction == (0, -1)

    # Test can't reverse
    snake.set_direction((0, 1))  # Down - should be ignored
    assert snake.next_direction == (0, -1)

    # Test valid turn
    snake.set_direction((-1, 0))  # Left
    assert snake.next_direction == (-1, 0)
    print("  ✓ Direction handling works")

    # Test movement
    snake.direction = (1, 0)
    snake.next_direction = (1, 0)
    snake.move_timer = 0
    snake.speed = 10
    alive, event = snake.update(0.2, 20, 20, [])  # 0.2s = 2 moves at speed 10
    assert alive
    assert snake.head == (12, 10)  # Moved 2 steps right
    print("  ✓ Movement works")

    # Test growth (1 segment per move)
    snake.grow(2)
    snake.move_timer = 0
    alive, _ = snake.update(0.1, 20, 20, [])
    assert snake.length == 4  # Was 3, grew 1 (first of 2 pending)
    snake.move_timer = 0
    alive, _ = snake.update(0.1, 20, 20, [])
    assert snake.length == 5  # Was 4, grew 1 (second of 2 pending)
    print("  ✓ Growth works")

    return True


def test_snake_collision():
    print("\nTesting snake collision...")
    snake = Snake(body=[(10, 10), (9, 10), (8, 10)])
    snake.direction = (1, 0)
    snake.next_direction = (1, 0)
    snake.move_timer = 0
    snake.speed = 10

    # Wall collision
    snake.body = [(19, 10), (18, 10), (17, 10)]
    snake.direction = (1, 0)
    alive, event = snake.update(0.2, 20, 20, [])
    assert not alive
    assert event == 'hit_wall'
    print("  ✓ Wall collision works")

    # Self collision
    snake = Snake(body=[(10, 10), (10, 11), (10, 12), (11, 12), (11, 11)])
    snake.direction = (0, 1)  # Down into self (y increases downward)
    snake.next_direction = (0, 1)
    snake.move_timer = 0
    alive, event = snake.update(0.2, 20, 20, [])
    assert not alive
    assert event == 'hit_self'
    print("  ✓ Self collision works")

    # Shield blocks death
    snake = Snake(body=[(19, 10), (18, 10), (17, 10)])
    snake.direction = (1, 0)
    snake.has_shield = True
    snake.shield_timer = 5.0
    snake.move_timer = 0
    alive, event = snake.update(0.2, 20, 20, [])
    assert alive
    assert event == 'shield_blocked'
    assert not snake.has_shield
    print("  ✓ Shield blocks death")

    return True


def test_food():
    print("\nTesting food system...")
    food = Food(5, 5, 'normal')
    assert food.value == 10
    assert food.grow_amount == 1

    bonus = Food(5, 5, 'bonus')
    assert bonus.value == 50
    assert bonus.grow_amount == 2

    poison = Food(5, 5, 'poison')
    assert poison.value == -20
    assert poison.grow_amount == 0

    speed_food = Food(5, 5, 'speed')
    assert speed_food.powerup == 'speed'

    # Random food
    random_food = Food.random_food(5, 5, 1)
    assert random_food.ftype in Food.FOOD_TYPES
    print("  ✓ Food types work")

    return True


def test_obstacles():
    print("\nTesting obstacles...")
    snake = Snake(body=[(10, 10), (9, 10), (8, 10)])
    snake.direction = (1, 0)
    snake.move_timer = 0
    snake.speed = 10

    obs = Obstacle(12, 10)
    alive, event = snake.update(0.2, 20, 20, [obs])
    assert not alive
    assert event == 'hit_obstacle'
    print("  ✓ Obstacle collision works")

    # Ghost mode passes through
    snake = Snake(body=[(10, 10), (9, 10), (8, 10)])
    snake.direction = (1, 0)
    snake.has_ghost = True
    snake.ghost_timer = 5.0
    snake.move_timer = 0
    alive, event = snake.update(0.2, 20, 20, [obs])
    assert alive
    print("  ✓ Ghost mode works")

    return True


def test_powerups():
    print("\nTesting power-ups...")
    snake = Snake(body=[(10, 10), (9, 10), (8, 10)])

    snake.apply_powerup('shield', 5.0)
    assert snake.has_shield
    assert snake.shield_timer == 5.0

    snake.apply_powerup('speed', 5.0)
    assert snake.has_speed
    assert snake.speed_timer == 5.0

    snake.apply_powerup('ghost', 5.0)
    assert snake.has_ghost

    snake.apply_powerup('multiplier', 5.0)
    assert snake.score_multiplier == 2.0

    # Timer decay
    snake._update_powerups(6.0)
    assert not snake.has_shield
    assert not snake.has_speed
    assert not snake.has_ghost
    assert snake.score_multiplier == 1.0
    print("  ✓ Power-ups work")

    # Shrink
    snake = Snake(body=[(10, 10), (9, 10), (8, 10), (7, 10), (6, 10)])
    snake.apply_powerup('shrink')
    assert snake.length == 3  # Min length preserved
    print("  ✓ Shrink works")

    return True


def test_game_state():
    print("\nTesting game state...")
    state = GameState()
    state.mode = 'classic'
    state.mode_index = 0
    state.init_game()

    assert state.snake is not None
    assert len(state.foods) >= 1
    assert state.score == 0
    assert state.level == 1
    print("  ✓ Game init works")

    # Test eating food
    food = state.foods[0]
    # Position snake adjacent to food, facing it
    # Food at (fx, fy), snake head at (fx-1, fy), moving RIGHT
    state.snake.body = [(food.x - 1, food.y), (food.x - 2, food.y), (food.x - 3, food.y)]
    state.snake.direction = (1, 0)
    state.snake.next_direction = (1, 0)
    state.snake.move_timer = 0
    initial_score = state.score
    state.update(0.1)
    assert state.score > initial_score, f"Score didn't increase: {state.score} vs {initial_score}"
    print("  ✓ Eating food works")

    return True


def test_modes():
    print("\nTesting game modes...")
    assert len(MODES) == 5
    mode_ids = [m['id'] for m in MODES]
    assert 'classic' in mode_ids
    assert 'arcade' in mode_ids
    assert 'survival' in mode_ids
    assert 'time_attack' in mode_ids
    assert 'cozy' in mode_ids
    print("  ✓ All 5 modes defined")

    return True


def test_particles():
    print("\nTesting particles...")
    from world.entities import create_particles, create_eat_particles, create_death_particles

    particles = create_particles(10, 10, 5, color=3, char='·')
    assert len(particles) == 5
    for p in particles:
        p.update(0.1)
        assert p.life < 1.0

    eat_particles = create_eat_particles(5, 5, 'bonus')
    assert len(eat_particles) > 0

    death_particles = create_death_particles(10, 10)
    assert len(death_particles) == 20
    print("  ✓ Particles work")

    return True


if __name__ == "__main__":
    print("=" * 50)
    print("SNAKE GAME - LOGIC TESTS")
    print("=" * 50)

    all_passed = True
    for test in [test_snake_movement, test_snake_collision, test_food,
                 test_obstacles, test_powerups, test_game_state,
                 test_modes, test_particles]:
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
    else:
        print("SOME TESTS FAILED ✗")
    print("=" * 50)