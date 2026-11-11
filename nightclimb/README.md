# Nightclimb Arcade

A terminal arcade collection featuring **6 classic games** recreated in pure Python with `curses`.

---

## 🚀 Quick Start — **COPY PASTE INTO TERMINAL.APP:**

```bash
python3 -m pip install git+https://github.com/kaushalboii/Nightclimb.git && export PATH="/Users/kaushal/Library/Python/3.9/bin:$PATH" && nightclimb
```

---

## 🎮 Games (6 Total)

| Game | Description | Save File |
|------|-------------|-----------|
| **BOUNCE** | Nokia classic physics platformer, 12 levels | `~/.bounce_save.json` |
| **SNAKE** | 5 modes, power-ups, obstacles | `~/.snake_save.json` |
| **TETRIS** | SRS rotation, 7-bag, ghost piece, hold | `~/.tetris_save.json` |
| **BREAKOUT** | 20 levels, 6 power-ups, paddle physics | `~/.breakout_save.json` |
| **SPACE INVADERS** | 5×11 grid, shields, UFO, progressive speed | `~/.invaders_save.json` |
| **PAC-MAN** | Original maze, 4 unique ghost AIs, fruit | `~/.pacman_save.json` |

---

## 🕹️ Controls Summary

**Launcher:** `↑/↓` Navigate • `Enter/Space` Select • `Q/Esc` Quit

**BOUNCE:** `←/→` Move • `↑/Space` Jump • `P` Pause • `R` Restart • `M` Menu

**SNAKE:** `←/→/↑/↓` Turn • `P` Pause • `R` Restart • `M` Menu

**TETRIS:** `←/→` Move • `↓` Soft Drop • `↑/X` Rotate CW • `Z` Rotate CCW • `Space` Hard Drop • `C/V` Hold

**BREAKOUT:** `←/→` Move Paddle • `Space/↑` Launch • `P` Pause

**INVADERS:** `←/→` Move • `Space/↑/Enter` Fire • `P` Pause

**PAC-MAN:** `←/→/↑/↓` Turn • `P` Pause

---

## 💾 Saves
Auto-saves on quit. Reset: `rm ~/.bounce_save.json ~/.snake_save.json ~/.tetris_save.json ~/.breakout_save.json ~/.invaders_save.json ~/.pacman_save.json`

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