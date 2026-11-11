# Nightclimb Arcade

Terminal arcade collection — **BOUNCE** (Nokia classic) + **SNAKE** (enhanced retro).

---

## 🚀 Quick Start — **COPY PASTE THIS INTO TERMINAL.APP:**

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
```

### Without PATH (always works):
```bash
python3 -m nightclimb.launcher          # Launcher
python3 -m nightclimb.games.bounce.main  # BOUNCE
python3 -m nightclimb.games.snake.main   # SNAKE
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

## 🎮 Games Included

### BOUNCE — Nokia Classic Recreation
- **12 Levels** — Tutorial → Spike Hell
- **Authentic Physics** — Gravity, bounce, friction, air/water drag
- **All Mechanics** — Spikes, moving platforms, breakable blocks, water, stars, exits
- **Power-ups** — Shield, Double Jump, Speed Boost
- **Auto-Save** — `~/.bounce_save.json`
- **Best Times** — Per-level leaderboard

### SNAKE — Enhanced Retro Classic
- **5 Game Modes** — Classic, Arcade, Survival, Time Attack, Cozy
- **Power-ups** — Shield, Speed, Ghost, 2x Score, Slow, Shrink
- **Special Foods** — Bonus, Poison, Speed, Shrink, Ghost, Multiplier, Shield
- **Obstacles** — Static blocks in Arcade/Survival
- **High Scores** — Per-mode leaderboards in `~/.snake_save.json`

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

Auto-saves every 10s + on quit:
- **BOUNCE**: `~/.bounce_save.json` — level, lives, score, best times
- **SNAKE**: `~/.snake_save.json` — high scores per mode

Reset progress:
```bash
rm ~/.bounce_save.json ~/.snake_save.json
```

---

## 🧪 Testing

```bash
# BOUNCE tests
python3 -c "import sys; sys.path.insert(0, 'nightclimb'); exec(open('nightclimb/test_game.py').read())"

# SNAKE tests
python3 -c "import sys; sys.path.insert(0, 'nightclimb'); exec(open('nightclimb/games/snake/test_snake.py').read())"
```

Expected: `ALL TESTS PASSED ✓`

---

## 📁 Project Structure

```
Nightclimb/
├── nightclimb/                 # Main package
│   ├── run.py                  # Entry point
│   ├── launcher.py             # Game selector
│   ├── test_game.py            # BOUNCE tests
│   ├── games/
│   │   ├── bounce/             # BOUNCE game
│   │   │   ├── main.py
│   │   │   ├── game/state.py
│   │   │   ├── game/physics.py
│   │   │   ├── world/entities.py
│   │   │   ├── world/levels.py
│   │   │   ├── ui/render.py
│   │   │   └── ui/input.py
│   │   └── snake/              # SNAKE game
│   │       ├── main.py
│   │       ├── game/state.py
│   │       ├── world/entities.py
│   │       ├── world/levels.py
│   │       ├── ui/render.py
│   │       └── ui/input.py
├── web/                        # Web version (WIP)
│   └── index.html
├── pyproject.toml              # Package config
├── .gitignore
└── README.md
```

---

## 📜 License

MIT License — free to use, modify, distribute.

---

## 🤝 Credits

- **BOUNCE Original:** Nokia Bounce (Nokia 3310/5110, ~2008)
- **SNAKE Original:** Classic arcade (1976 Blockade → 1997 Nokia Snake)
- **Recreation:** Python `curses`

---

**Enjoy the nostalgia!** 🎮