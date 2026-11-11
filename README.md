# Nightclimb Arcade

Terminal arcade collection — **BOUNCE** (Nokia classic) + **SNAKE** (enhanced retro).

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

### Windows
```bash
pip install windows-curses
nightclimb
```

---

## 🎮 Games Included

### BOUNCE — Nokia Classic Recreation
Faithful recreation of the Nokia Bounce game with:
- **12 Levels** — Tutorial → Spike Hell
- **Authentic Physics** — Gravity, bounce, friction, air/water drag
- **All Mechanics** — Spikes, moving platforms, breakable blocks, water, stars, exits
- **Power-ups** — Shield, Double Jump, Speed Boost
- **Auto-Save** — Progress saved to `~/.bounce_save.json`
- **Best Times** — Per-level leaderboard

### SNAKE — Enhanced Retro Classic
Modern take on the arcade classic with:
- **5 Game Modes** — Classic, Arcade, Survival, Time Attack, Cozy
- **Power-ups** — Shield, Speed, Ghost, 2x Score, Slow, Shrink
- **Special Foods** — Bonus, Poison, Speed, Shrink, Ghost, Multiplier, Shield
- **Obstacles** — Static blocks in Arcade/Survival modes
- **High Scores** — Per-mode leaderboards saved to `~/.snake_save.json`

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
│   ├── README.md               # Full documentation
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
└── README.md                   # This file
```

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

## 🤝 Credits

- **BOUNCE Original:** Nokia Bounce (Nokia 3310/5110, ~2008)
- **SNAKE Original:** Classic arcade game (1976 Blockade → 1997 Nokia Snake)
- **Recreation:** Built with Python `curses`

---

**Enjoy the nostalgia!** 🎮