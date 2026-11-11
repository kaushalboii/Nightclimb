# Nightclimb Arcade

Terminal arcade collection — **6 classic games** in pure Python + curses.

---

## 🚀 Quick Start — **COPY PASTE INTO TERMINAL.APP:**

```bash
python3 -m pip install git+https://github.com/kaushalboii/Nightclimb.git && export PATH="/Users/kaushal/Library/Python/3.9/bin:$PATH" && nightclimb
```

**That's it — runs the launcher menu to pick a game.**

---

## Alternative Ways to Run

### After install (add to ~/.zshrc for permanent PATH):
```bash
echo 'export PATH="/Users/kaushal/Library/Python/3.9/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
nightclimb      # Launcher menu
bounce          # BOUNCE directly
snake           # SNAKE directly
tetris          # TETRIS directly
breakout        # BREAKOUT directly
invaders        # SPACE INVADERS directly
pacman          # PAC-MAN directly
```

### Without PATH (always works):
```bash
python3 -m nightclimb.launcher
python3 -m nightclimb.games.bounce.main
python3 -m nightclimb.games.snake.main
python3 -m nightclimb.games.tetris.main
python3 -m nightclimb.games.breakout.main
python3 -m nightclimb.games.invaders.main
python3 -m nightclimb.games.pacman.main
```

### Clone & run locally (no pip):
```bash
git clone https://github.com/kaushalboii/Nightclimb.git
cd Nightclimb/nightclimb
python3 run.py
```

### Windows:
```bash
pip install windows-curses
python3 -m pip install git+https://github.com/kaushalboii/Nightclimb.git
python3 -m nightclimb.launcher
```

---

## 🎮 Games Included (6 Total)

### 1. BOUNCE — Nokia Classic Recreation
- **12 Levels** — Tutorial → Spike Hell
- **Authentic Physics** — Gravity, bounce, friction, air/water drag
- **All Mechanics** — Spikes, moving platforms, breakable blocks, water, stars, exits
- **Power-ups** — Shield, Double Jump, Speed Boost
- **Auto-Save** — `~/.bounce_save.json` — level, lives, score, best times

### 2. SNAKE — Enhanced Retro Classic
- **5 Game Modes** — Classic, Arcade, Survival, Time Attack, Cozy
- **Power-ups** — Shield, Speed, Ghost, 2x Score, Slow, Shrink
- **Special Foods** — Bonus, Poison, Speed, Shrink, Ghost, Multiplier, Shield
- **Obstacles** — Static blocks in Arcade/Survival
- **High Scores** — Per-mode leaderboards in `~/.snake_save.json`

### 3. TETRIS — Falling Blocks Classic
- **SRS Rotation** — Official Super Rotation System with wall kicks
- **7-Bag Randomizer** — Fair piece distribution
- **Ghost Piece** — Shows landing position
- **Hold & Next Queue** — Strategic play
- **Combos & Level Scaling** — NES-style scoring
- **High Score** — `~/.tetris_save.json`

### 4. BREAKOUT — Paddle & Bricks Arcade
- **20 Levels** — Progressive brick patterns
- **6 Power-ups** — Wide paddle, Multi-ball, Slow/Fast ball, Extra life, Catch
- **Paddle Physics** — Angle based on hit position
- **High Score** — `~/.breakout_save.json`

### 5. SPACE INVADERS — Classic Fixed Shooter
- **5×11 Invader Grid** — 3 types (30/20/10 pts)
- **4 Shields** — Destructible cover
- **UFO Bonus** — Random high-value target
- **Progressive Speed** — Fewer invaders = faster
- **High Score** — `~/.invaders_save.json`

### 6. PAC-MAN — Maze Chase Classic
- **Original Maze Layout** — 244 dots + 4 power pellets
- **4 Ghosts with Unique AI**:
  - **Blinky** (Red) — Direct chase
  - **Pinky** (Pink) — Ambushes ahead
  - **Inky** (Cyan) — Complex Blinky-relative
  - **Clyde** (Orange) — Random when far
- **Power Pellets** — Eat ghosts for 200/400/800/1600 pts
- **Fruit Bonus** — 2 per level (Cherry → Key)
- **High Score** — `~/.pacman_save.json`

---

## 🕹️ Controls

### Launcher Menu
| Key | Action |
|-----|--------|
| `↑` / `↓` / `W` / `S` | Navigate |
| `Enter` / `Space` | Select game |
| `Q` / `Esc` | Quit |

### BOUNCE
| Key | Action |
|-----|--------|
| `←` / `A` / `H` | Move left (hold) |
| `→` / `D` / `L` | Move right (hold) |
| `↑` / `W` / `K` / `Space` | Jump (tap) |
| `P` | Pause / Resume |
| `R` | Restart level |
| `M` | Menu (level select, quit) |

### SNAKE
| Key | Action |
|-----|--------|
| `←` / `A` / `H` | Turn left |
| `→` / `D` / `L` | Turn right |
| `↑` / `W` / `K` | Turn up |
| `↓` / `S` / `J` | Turn down |
| `P` | Pause / Resume |
| `R` | Restart game |
| `M` | Menu (mode select, quit) |

### TETRIS
| Key | Action |
|-----|--------|
| `←` / `A` | Move left |
| `→` / `D` | Move right |
| `↓` / `S` | Soft drop |
| `↑` / `W` / `X` | Rotate CW |
| `Z` / `C` | Rotate CCW |
| `Space` / `Enter` | Hard drop |
| `C` / `V` / `F` | Hold piece |
| `P` | Pause |

### BREAKOUT
| Key | Action |
|-----|--------|
| `←` / `A` | Move paddle left |
| `→` / `D` | Move paddle right |
| `Space` / `↑` / `W` | Launch ball |
| `P` | Pause |

### SPACE INVADERS
| Key | Action |
|-----|--------|
| `←` / `A` | Move left |
| `→` / `D` | Move right |
| `Space` / `↑` / `W` / `Enter` | Fire |
| `P` | Pause |

### PAC-MAN
| Key | Action |
|-----|--------|
| `←` / `A` / `H` | Turn left |
| `→` / `D` / `L` | Turn right |
| `↑` / `W` / `K` | Turn up |
| `↓` / `S` / `J` | Turn down |
| `P` | Pause |

---

## 💾 Save System

Auto-saves high scores on quit:
- **BOUNCE**: `~/.bounce_save.json` — level, lives, score, best times
- **SNAKE**: `~/.snake_save.json` — high scores per mode
- **TETRIS**: `~/.tetris_save.json` — high score
- **BREAKOUT**: `~/.breakout_save.json` — high score
- **INVADERS**: `~/.invaders_save.json` — high score
- **PAC-MAN**: `~/.pacman_save.json` — high score

Reset all progress:
```bash
rm ~/.bounce_save.json ~/.snake_save.json ~/.tetris_save.json ~/.breakout_save.json ~/.invaders_save.json ~/.pacman_save.json
```

---

## 🧪 Testing

```bash
# BOUNCE tests
cd nightclimb && python3 test_game.py

# SNAKE tests
cd nightclimb/games/snake && python3 test_snake.py
```

Expected: `ALL TESTS PASSED ✓`

---

## 📁 Project Structure

```
Nightclimb/
├── nightclimb/                 # Main package
│   ├── run.py                  # Entry point
│   ├── launcher.py             # Game selector (6 games)
│   ├── test_game.py            # BOUNCE tests
│   ├── games/
│   │   ├── bounce/             # BOUNCE
│   │   ├── snake/              # SNAKE
│   │   ├── tetris/             # TETRIS
│   │   ├── breakout/           # BREAKOUT
│   │   ├── invaders/           # SPACE INVADERS
│   │   └── pacman/             # PAC-MAN
├── web/                        # Web version (WIP)
├── pyproject.toml              # Package config
├── .gitignore
└── README.md
```

---

## 📜 License

MIT License — free to use, modify, distribute.

---

## 🤝 Credits

- **BOUNCE**: Nokia Bounce (Nokia 3310/5110, ~2008)
- **SNAKE**: Blockade (1976) → Nokia Snake (1997)
- **TETRIS**: Alexey Pajitnov (1984)
- **BREAKOUT**: Atari (1976)
- **SPACE INVADERS**: Taito (1978)
- **PAC-MAN**: Namco (1980)
- **Recreation**: Python `curses`

---

**Enjoy the nostalgia!** 🎮