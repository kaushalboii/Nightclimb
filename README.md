# BOUNCE — Nokia Classic Recreation in Terminal

A faithful recreation of the classic Nokia **Bounce** game (from the Nokia 3310/5110 era) built in pure Python with `curses`. Features all 12 original levels, authentic physics, auto-save, and zero external dependencies.

![Game Preview](assets/preview.gif)

---

## 🎮 Play Now

```bash
# Clone and run
git clone https://github.com/kaushalboii/Nightclimb.git
cd Nightclimb/bounce_game
python3 run.py
```

### Requirements
- **Python 3.7+**
- **Terminal** with curses support (Linux/macOS/WSL/Terminal.app)
- **80×24 minimum** terminal size

**Windows:** Install `windows-curses` first:
```bash
pip install windows-curses
python run.py
```

---

## 🕹️ Controls

| Key | Action |
|-----|--------|
| `←` / `A` | Move left |
| `→` / `D` | Move right |
| `↑` / `W` / `Space` | Jump |
| `P` | Pause / Resume |
| `R` | Restart current level |
| `M` | Main menu (level select, quit) |
| `N` | Next level (when complete) |
| `Q` / `Esc` | Quit (auto-saves) |

---

## ✨ Features

| Feature | Details |
|---------|---------|
| **12 Levels** | Tutorial → Spike Hell, matching original progression |
| **Authentic Physics** | Gravity, bounce damping, friction, air/water drag |
| **All Mechanics** | Spikes (instant death), moving platforms, breakable blocks, water buoyancy, collectible stars, exit doors |
| **Auto-Save** | Progress saved to `~/.bounce_save.json` — survives reboots |
| **Best Times** | Per-level time tracking with leaderboard |
| **Visual Polish** | Screen shake on death, ball squash animation, particle trails, blinking stars |
| **Menus** | Pause overlay, level select with completion markers, game over screen |
| **Zero Dependencies** | Pure Python standard library |

---

## 📁 Project Structure

```
Nightclimb/
├── bounce_game/              # Main game package
│   ├── run.py                # Entry point — run this to play
│   ├── main.py               # Game loop, initialization
│   ├── test_game.py          # Unit tests (run: python test_game.py)
│   ├── game/
│   │   ├── __init__.py
│   │   ├── state.py          # Game state, save/load, level management
│   │   └── physics.py        # Physics engine (gravity, collision, movement)
│   ├── world/
│   │   ├── __init__.py
│   │   ├── entities.py       # Ball, Platform, Spike, Star, Exit, Block, MovingPlatform
│   │   └── levels.py         # 12 level definitions
│   └── ui/
│       ├── __init__.py
│       ├── render.py         # ASCII rendering with curses
│       └── input.py          # Input handling
├── .gitignore
└── README.md
```

---

## 🎯 Level List

| # | Name | Mechanics Introduced |
|---|------|---------------------|
| 1 | Welcome Back | Basic platforms, stars, exit |
| 2 | Sharp Edges | Ground spikes |
| 3 | Ride the Wave | Moving platforms |
| 4 | Break Through | Breakable blocks |
| 5 | Deep Waters | Water buoyancy |
| 6 | Skyward | Vertical climbing |
| 7 | Thread the Needle | Precision platforming |
| 8 | The Gauntlet | Combined obstacles |
| 9 | Submerged Secrets | Water + moving platforms |
| 10 | Final Descent | All mechanics combined |
| 11 | The Pit | Bonus: deep vertical |
| 12 | Spike Hell | Bonus: maximum difficulty |

---

## 💾 Save System

- **Auto-saves** every 10 seconds during play
- **Saves on quit** (Q/Esc) or menu exit
- **File location:** `~/.bounce_save.json`
- **Persists:** current level, lives, score, best times per level

To reset progress, delete the save file:
```bash
rm ~/.bounce_save.json
```

---

## 🧪 Testing

Run the test suite to verify all logic:
```bash
cd bounce_game
python3 test_game.py
```

Expected output: `ALL TESTS PASSED ✓`

---

## 🎨 Screenshots

```
┌────────────────────────────────────────────────┐
│ BOUNCE | Welcome Back | Lives: ♥♥♥ | Stars: 3/7 │
│                                                 │
│           ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    │  ← sky
│         ░  ▀▀▀▀▀▀  ░     @      ░  ▀▀▀▀▀▀  ░    │
│         ░  ░░░░░░  ░  ░░░░░░░░░  ░  ░░░░░░  ░    │
│         ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    │  ← ground
│                                                 │
│   [←/→] Move  [↑/Space] Jump  [P] Pause         │
│                                                 │
│   📬  Stars: 3/7  Score: 1200                   │
└────────────────────────────────────────────────┘
```

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

## 🤝 Credits

- **Original Game:** Nokia Bounce (Nokia 3310/5110)
- **Recreation:** Built with Python `curses`
- **Inspiration:** The countless hours spent guiding the red ball through spikes on a monochrome screen

---

## 🐛 Known Issues

- Requires terminal with UTF-8 support for special characters (★, ▲, ▼, ●, etc.)
- Minimum 80×24 terminal size; smaller terminals may truncate UI
- Windows requires `windows-curses` package

---

**Enjoy the nostalgia!** 🎮