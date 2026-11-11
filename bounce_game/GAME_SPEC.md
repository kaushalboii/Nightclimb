# BOUNCE Game Specification — Nokia Classic Recreation

## Overview
Faithful recreation of **Nokia Bounce** (Nokia 3310/5110, ~2008) — a physics-based platformer where you guide a red ball through 12 levels, collecting stars and avoiding spikes.

**Core feel**: Weighty, bouncy, precise. The ball has momentum — it doesn't stop instantly. Jumps are committed. Physics are consistent.

---

## Physics Constants (Tuned to Match Original)

| Constant | Value | Description |
|----------|-------|-------------|
| `GRAVITY` | 25.0 px/s² | Downward acceleration |
| `JUMP_FORCE` | -18.0 px/s | Initial upward velocity on jump |
| `MOVE_FORCE` | 12.0 px/s² | Horizontal acceleration while holding key |
| `MAX_HORIZONTAL_SPEED` | 10.0 px/s | Terminal horizontal speed |
| `BOUNCE_DAMPING` | 0.65 | Velocity retained after bounce (0–1) |
| `FRICTION` | 0.85/frame | Ground friction (when `ground_contact`) |
| `AIR_FRICTION` | 0.98/frame | Air resistance (when airborne) |
| `TERMINAL_VELOCITY` | 25.0 px/s | Max fall speed |
| `WATER_GRAVITY` | 8.0 px/s² | Reduced gravity underwater |
| `WATER_DRAG` | 0.85/frame | Water resistance |

**Frame rate**: 60 FPS fixed timestep (dt = 1/60)

---

## Ball Physics

### State
- `center_x`, `center_y`: Center position (float, sub-pixel precision)
- `radius`: 1.5 (ball is 3×3 chars visually)
- `vx`, `vy`: Velocity (px/s)
- `input_left`, `input_right`, `input_jump`: Input flags (set each frame)

### Movement
```
# Horizontal (applied every frame when key held)
if input_left:  vx -= MOVE_FORCE * dt
if input_right: vx += MOVE_FORCE * dt

# Clamp
vx = clamp(vx, -MAX_HORIZONTAL_SPEED, MAX_HORIZONTAL_SPEED)

# Jump (only when ground_contact is True)
if input_jump and ground_contact:
    vy = JUMP_FORCE
    ground_contact = False  # Prevent double-jump
```

### Gravity & Drag (every frame)
```
gravity = WATER_GRAVITY if in_water else GRAVITY
vy += gravity * dt

drag = WATER_DRAG if in_water else (FRICTION if ground_contact else AIR_FRICTION)
vx *= drag ** dt
vy *= drag ** dt

# Clamp vertical
vy = clamp(vy, -TERMINAL_VELOCITY, TERMINAL_VELOCITY)

# Integrate position
center_x += vx * dt
center_y += vy * dt
```

### Collision Resolution (AABB, using ball bounds = center ± radius)

**Order of checks** (first match wins):
1. **Spikes** → Instant death (reset level, lose life)
2. **Moving platforms** → Resolve, transfer platform velocity (0.3×)
3. **Static platforms** → Resolve, set `ground_contact = True`
4. **Breakable blocks** → Resolve; if hit from below with `vy > 10`, break block & bounce
5. **Screen boundaries** → Bounce with `BOUNCE_DAMPING`

**Collision direction detection** (using previous frame position):
- Store `prev_center_x`, `prev_center_y` before integration
- Ball's previous bounds: `[prev_x - r, prev_x + r] × [prev_y - r, prev_y + r]`
- Platform bounds: `[px, px + pw] × [py, py + ph]`

| Direction | Condition | Resolution |
|-----------|-----------|------------|
| Top (land) | `prev_bottom ≤ platform_top` AND `vy ≥ 0` | `center_y = platform_top - radius`, `vy = -vy * BOUNCE_DAMPING`, `ground_contact = True` |
| Bottom (hit head) | `prev_top ≥ platform_bottom` AND `vy ≤ 0` | `center_y = platform_bottom + radius`, `vy = -vy * BOUNCE_DAMPING` |
| Left | `prev_right ≤ platform_left` AND `vx ≥ 0` | `center_x = platform_left - radius`, `vx = -vx * BOUNCE_DAMPING` |
| Right | `prev_left ≥ platform_right` AND `vx ≤ 0` | `center_x = platform_right + radius`, `vx = -vx * BOUNCE_DAMPING` |

**Fallback** (if direction ambiguous): Push out by minimum penetration.

### Screen Boundaries
- Left: `center_x = radius`, `vx = |vx| * BOUNCE_DAMPING`
- Right: `center_x = 80 - radius`, `vx = -|vx| * BOUNCE_DAMPING`
- Top: `center_y = radius`, `vy = |vy| * BOUNCE_DAMPING`
- Bottom (fall death): `center_y > 50` → `die()`

### Water Buoyancy
- Water level = `water_level` (y-coordinate, top of water)
- Ball is "in water" if `center_y + radius > water_level`
- In water: reduced gravity, increased drag, can jump from water surface (`ground_contact` set when touching water surface from above)

---

## Input Handling

### Requirements
- **Non-blocking** (curses `nodelay=True`)
- **Held keys** for movement (left/right continuous)
- **Single-press** for jump (tap to jump, not hold)
- **Immediate response** — no input lag

### Key Mappings
| Action | Keys |
|--------|------|
| Move Left | `←`, `A`, `H` |
| Move Right | `→`, `D`, `L` |
| Jump | `↑`, `W`, `K`, `Space` |
| Pause | `P` |
| Restart Level | `R` |
| Menu | `M` |
| Next Level | `N`, `Enter`, `Space` (when level complete) |
| Previous Level | `B` |
| Quit | `Q`, `Esc` |

### Implementation: Key State Tracking
```python
class InputHandler:
    def __init__(self):
        self.held = set()      # Keys currently held this frame
        self.pressed = set()   # Keys pressed THIS frame (for jump)
        self.released = set()  # Keys released THIS frame

    def poll(self, stdscr):
        self.pressed.clear()
        self.released.clear()
        
        # Read all available keys
        while True:
            key = stdscr.getch()
            if key == -1:
                break
            if key not in self.held:
                self.held.add(key)
                self.pressed.add(key)
        
        # Track releases: any key in held but not seen this frame = released
        # We need to remember what we saw last frame
        # Simpler: use a "seen_this_frame" set
        seen = set()
        while True:
            key = stdscr.getch()
            if key == -1: break
            seen.add(key)
            if key not in self.held:
                self.held.add(key)
                self.pressed.add(key)
        
        # Released = was held, not seen now
        for key in list(self.held):
            if key not in seen:
                self.held.remove(key)
                self.released.add(key)

    def update_ball(self, ball):
        ball.input_left  = any(k in self.held for k in LEFT_KEYS)
        ball.input_right = any(k in self.held for k in RIGHT_KEYS)
        ball.input_jump  = any(k in self.pressed for k in JUMP_KEYS)
        
        # Return menu actions from pressed keys
        if any(k in self.pressed for k in QUIT_KEYS): return "quit"
        ...
```

---

## Level Structure

### Level Data Format (in `world/levels.py`)
```python
{
    "name": "Level Name",
    "spawn": (center_x, center_y),           # Ball spawn position
    "platforms": [(x, y, w, h), ...],        # Static platforms
    "moving_platforms": [(x, y, w, h, range, speed, vertical?), ...],
    "spikes": [(x, y, w, h, orientation), ...],  # orientation: 'up','down','left','right'
    "stars": [(x, y), ...],                  # Collectibles
    "exit": (x, y),                          # Exit door position
    "blocks": [(x, y, w, h, hits), ...],     # Breakable blocks
    "water": water_y_level_or_-1,            # Water surface y-coordinate
}
```

### Coordinate System
- **Origin**: Top-left (0, 0)
- **Screen**: 80 wide × 24 high (game area)
- **Ball spawn**: Center coordinates
- **All entities**: Top-left coordinates (except ball)

### 12 Levels (Progressive Difficulty)
| # | Name | New Mechanic |
|---|------|--------------|
| 1 | Welcome Back | Basics |
| 2 | Sharp Edges | Spikes (ground) |
| 3 | Ride the Wave | Moving platforms (horizontal) |
| 4 | Break Through | Breakable blocks |
| 5 | Deep Waters | Water buoyancy |
| 6 | Skyward | Vertical climbing |
| 7 | Thread the Needle | Precision |
| 8 | The Gauntlet | Combined |
| 9 | Submerged Secrets | Water + moving |
| 10 | Final Descent | All mechanics |
| 11 | The Pit | Deep vertical (bonus) |
| 12 | Spike Hell | Maximum difficulty (bonus) |

---

## Game Flow

### States
1. **Playing** — Normal gameplay
2. **Paused** — Overlay, time stopped
3. **Level Complete** — Overlay, show stats, wait for input
4. **Game Over** — Overlay, final score, restart/quit
5. **Menu** — Level select, resume, quit

### Life System
- Start with 3 lives (`♥♥♥`)
- Spike contact / fall death → lose 1 life, respawn at level start
- 0 lives → Game Over
- Level complete → keep lives, advance

### Scoring
- Star collected: +100
- Level complete time bonus: `max(0, 5000 - time_seconds × 100)`
- Best time saved per level

### Auto-Save
- Every 10 seconds during play
- On quit (Q/Esc), menu exit, game over
- File: `~/.bounce_save.json`
- Saves: current_level, lives, score, best_times

---

## Visuals (Curses/Terminal)

### Character Set
| Entity | Char | Color Pair |
|--------|------|------------|
| Ball (normal) | `●` | Red (1) |
| Ball (squash) | `◆` | Red (1) |
| Platform (thin) | `▀` | Green (2) |
| Platform (thick) | `█` | Green (2) |
| Moving Platform | `▀`/`▄` animated | Cyan (6) |
| Spike (up) | `▲`/`△` animated | Magenta (5) |
| Spike (down) | `▼`/`▽` animated | Magenta (5) |
| Star | `★`/`✦` blinking | Yellow (3) |
| Exit (closed) | `█` | Cyan (4) |
| Exit (open) | `░`/`▒`/`▓`/`█` pulsing | Cyan (4) |
| Block (solid) | `█` | Green (2) |
| Block (cracked) | `▓` | Green (2) |
| Water | `≈` animated | Blue (7) |
| Background | `·` sparse | White (6) |

### Effects
- **Screen shake**: On death (intensity 2, 0.3s)
- **Ball squash**: Horizontal stretch when `|vy| > 8` (0.8×) or `> 15` (0.6×)
- **Trail**: 5-frame fading dots behind ball
- **Star bob**: `sin(time × 3) × 0.3` vertical offset
- **Water animation**: Time-based wave pattern

---

## Technical Requirements

### Dependencies
- Python 3.7+
- Standard library only (`curses`, `json`, `time`, `math`, `dataclasses`, `pathlib`, `typing`)

### Platform Notes
- **Linux/macOS/WSL**: Built-in `curses`
- **Windows**: `pip install windows-curses`
- **Terminal**: UTF-8 support required, 80×24 minimum

### Performance
- 60 FPS fixed timestep
- No allocations in hot path (reuse lists)
- O(n) collision checks (n ≤ 50 entities)

---

## Testing Checklist

Run `python3 test_game.py` — must output `ALL TESTS PASSED ✓`

Manual playtest each level:
- [ ] Level 1: Basic movement, jump, star collection, exit
- [ ] Level 2: Spike death works, respawn
- [ ] Level 3: Moving platform rides correctly
- [ ] Level 4: Blocks break from below, not sides
- [ ] Level 5: Water buoyancy, jump from water surface
- [ ] Level 6-10: Combined mechanics
- [ ] Level 11-12: Bonus difficulty
- [ ] Pause/resume works
- [ ] Level select works
- [ ] Auto-save loads correctly after restart
- [ ] Best times persist

---

## Known Original Game Behaviors to Match

1. **Ball doesn't stop instantly** — momentum carries you
2. **Jump height is fixed** — tapping vs holding doesn't change height (no variable jump)
3. **Can't steer mid-air well** — air control is weak (AIR_FRICTION = 0.98)
4. **Moving platforms carry you** — velocity transfers (0.3×)
5. **Spikes are instant death** — no invincibility frames
6. **Water slows everything** — gravity 8, drag 0.85
7. **Breakable blocks** — only break from below with momentum
8. **Exit only opens with all stars** — must collect all
9. **Screen shake on death** — brief, not nauseating
10. **Auto-save is invisible** — no UI interruption

---

## Future: Web Version (Not Yet Implemented)

Target: Canvas-based, same physics constants, same level data (JSON), keyboard + touch controls.

---

*This spec is the source of truth. All code must match these behaviors.*