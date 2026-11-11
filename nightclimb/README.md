# Nightclimb Arcade

A terminal arcade collection featuring two classic games recreated in pure Python with `curses`.

## 🎮 Games Included

### BOUNCE — Nokia Classic Recreation
Faithful recreation of the Nokia Bounce game (Nokia 3310/5110 era) with:
- **12 Levels** — Tutorial → Spike Hell, matching original progression
- **Authentic Physics** — Gravity, bounce damping, friction, air/water drag
- **All Mechanics** — Spikes, moving platforms, breakable blocks, water buoyancy, stars, exits
- **Power-ups** — Shield, Double Jump, Speed Boost
- **Auto-Save** — Progress saved to `~/.bounce_save.json`
- **Best Times** — Per-level leaderboard
- **Visual Polish** — Screen shake, ball squash, particle trails, blinking stars

### SNAKE — Enhanced Retro Classic
Modern take on the arcade classic with:
- **5 Game Modes** — Classic, Arcade, Survival, Time Attack, Cozy
- **Power-ups** — Shield, Speed, Ghost, 2x Score, Slow, Shrink
- **Special Foods** — Bonus, Poison, Speed, Shrink, Ghost, Multiplier, Shield
- **Obstacles** — Static blocks in Arcade/Survival modes
- **High Scores** — Per-mode leaderboards saved to `~/.snake_save.json`
- **Smooth Movement** — Configurable speed, responsive controls

---

## 🚀 Quick Start

### Option 1: Pip Install (Recommended)
```bash
pip install git+https://github.com/kaushalboii/Nightclimb.git
nightclimb          # Runs launcher to pick a game
bounce              # Runs BOUNCE directly
snake               # Runs SNAKE directly
```

### Option 2: Clone & Run Locally
```bash
git clone https://github.com/kaushalboii/Nightclimb.git
cd Nightclimb/nightclimb
python3 run.py
```

### Requirements
- **Python 3.7+**
- **Terminal** with curses support (Linux/macOS/WSL/Terminal.app)
- **80×24 minimum** terminal size

**Windows:** Install `windows-curses` first:
```bash
pip install windows-curses
nightclimb
```

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
| `N` / `Enter` | Next level (when complete) |
| `B` | Previous level |
| `Q` / `Esc` | Quit (auto-saves) |

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
| `Q` / `Esc` | Quit (auto-saves) |

---

## 🎯 BOUNCE Levels

| # | Name | Mechanics |
|---|------|-----------|
| 1 | Welcome Back | Basics |
| 2 | Sharp Edges | Ground spikes |
| 3 | Ride the Wave | Moving platforms |
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

## 🐍 SNAKE Modes

| Mode | Description |
|------|-------------|
| **Classic** | Pure snake — no obstacles, no power-ups |
| **Arcade** | Obstacles, power-ups, increasing difficulty |
| **Survival** | Walls close in, speed increases, one life |
| **Time Attack** | 2 minutes — max score, wrap-around walls |
| **Cozy** | Large grid, slow speed, no obstacles — relax |

---

## 💾 Save System

Both games auto-save:
- **Every 10 seconds** during play
- **On quit** (Q/Esc) or menu exit
- **BOUNCE**: `~/.bounce_save.json` — level, lives, score, best times
- **SNAKE**: `~/.snake_save.json` — high scores per mode

To reset progress:
```bash
rm ~/.bounce_save.json ~/.snake_save.json
```

---

## 🧪 Testing

Run tests for each game:
```bash
# BOUNCE tests
cd nightclimb
python3 test_game.py

# SNAKE tests
cd nightclimb/games/snake
python3 test_snake.py
```

Expected output: `ALL TESTS PASSED ✓`

---

## 📁 Project Structure

```
Nightclimb/
├── nightclimb/                 # Main package
│   ├── run.py                  # Entry point — run this to play
│   ├── launcher.py             # Game selector menu
│   ├── README.md               # This file
│   ├── test_game.py            # BOUNCE unit tests
│   ├── games/
│   │   ├── bounce/             # BOUNCE game
│   │   │   ├── main.py
│   │   │   ├── game/
│   │   │   │   ├── state.py
│   │   │   │   └── physics.py
│   │   │   ├── world/
│   │   │   │   ├── entities.py
│   │   │   │   └── levels.py
│   │   │   └── ui/
│   │   │       ├── render.py
│   │   │       └── input.py
│   │   └── snake/              # SNAKE game
│   │       ├── main.py
│   │       ├── game/
│   │       │   └── state.py
│   │       ├── world/
│   │       │   ├── entities.py
│   │       │   └── levels.py
│   │       └── ui/
│   │           ├── render.py
│   │           └── input.py
├── web/                        # Web version (WIP)
│   └── index.html
├── pyproject.toml              # Package config
├── .gitignore
└── README.md                   # Root readme (minimal)
```

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

## 🤝 Credits

- **BOUNCE Original:** Nokia Bounce (Nokia 3310/5110, ~2008)
- **SNAKE Original:** Classic arcade game (1976 Blockade → 1997 Nokia Snake)
- **Recreation:** Built with Python `curses`
- **Inspiration:** Countless hours on monochrome screens

---

## 🐛 Known Issues

- Requires terminal with UTF-8 support for special characters
- Minimum 80×24 terminal size; smaller terminals may truncate UI
- Windows requires `windows-curses` package
- Some emoji characters in Snake power-ups may not render on all terminals (fallbacks included)

---

**Enjoy the nostalgia!** 🎮