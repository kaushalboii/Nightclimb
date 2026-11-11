# Nightclimb Arcade

A terminal arcade collection featuring two classic games recreated in pure Python with `curses`.

---

## 🚀 Quick Start — **COPY PASTE INTO TERMINAL.APP:**

```bash
python3 -m pip install git+https://github.com/kaushalboii/Nightclimb.git && export PATH="/Users/kaushal/Library/Python/3.9/bin:$PATH" && nightclimb
```

---

## Alternative Ways to Run

### After install (permanent PATH):
```bash
echo 'export PATH="/Users/kaushal/Library/Python/3.9/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
nightclimb    # Launcher
bounce        # BOUNCE
snake         # SNAKE
```

### Without PATH:
```bash
python3 -m nightclimb.launcher
python3 -m nightclimb.games.bounce.main
python3 -m nightclimb.games.snake.main
```

### Clone & run locally:
```bash
git clone https://github.com/kaushalboii/Nightclimb.git
cd Nightclimb/nightclimb
python3 run.py
```

---

## 🎮 Games

### BOUNCE — Nokia Classic
- 12 Levels, authentic physics, spikes, moving platforms, water, breakable blocks
- Power-ups: Shield, Double Jump, Speed
- Auto-save to `~/.bounce_save.json`

### SNAKE — Enhanced Retro
- 5 Modes: Classic, Arcade, Survival, Time Attack, Cozy
- Power-ups: Shield, Speed, Ghost, 2x Score, Slow, Shrink
- High scores per mode in `~/.snake_save.json`

---

## 🕹️ Controls

| Game | Keys |
|------|------|
| **Launcher** | `↑/↓` Navigate • `Enter/Space` Select • `Q/Esc` Quit |
| **BOUNCE** | `←/→` Move • `↑/Space` Jump • `P` Pause • `R` Restart • `M` Menu |
| **SNAKE** | `←/→/↑/↓` Turn • `P` Pause • `R` Restart • `M` Menu |

---

## 💾 Saves
Auto-saves every 10s + on quit. Reset: `rm ~/.bounce_save.json ~/.snake_save.json`

---

## 🧪 Tests
```bash
cd nightclimb && python3 test_game.py
cd nightclimb/games/snake && python3 test_snake.py
```

---

## 📜 License
MIT — free to use, modify, distribute.

---

**Enjoy!** 🎮