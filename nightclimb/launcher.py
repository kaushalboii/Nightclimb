#!/usr/bin/env python3
"""
Nightclimb Arcade Launcher
Unified menu for all retro games.
Auto-discovers games in games/ directory.
"""

import curses
import sys
import os
import importlib
import pkgutil

# Add game directories to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'games'))


def discover_games():
    """Auto-discover all games in games/ directory."""
    games_dir = os.path.join(BASE_DIR, 'games')
    discovered = []

    # Built-in game definitions with metadata
    game_registry = {
        'bounce': {
            'id': 'bounce',
            'name': 'BOUNCE',
            'subtitle': 'Nokia Classic Recreation',
            'desc': 'Physics platformer • 12 levels • Power-ups • Auto-save',
            'color': 1,
            'icon': '●',
            'module': 'games.bounce.main',
            'entry': 'main',
        },
        'snake': {
            'id': 'snake',
            'name': 'SNAKE',
            'subtitle': 'Retro Arcade Classic',
            'desc': '5 modes • Power-ups • Obstacles • High scores',
            'color': 2,
            'icon': '▲',
            'module': 'games.snake.main',
            'entry': 'main',
        },
        'tetris': {
            'id': 'tetris',
            'name': 'TETRIS',
            'subtitle': 'Falling Blocks Classic',
            'desc': '7 tetrominoes • Ghost piece • Hold • Next queue • High scores',
            'color': 3,
            'icon': '■',
            'module': 'games.tetris.main',
            'entry': 'main',
        },
        'breakout': {
            'id': 'breakout',
            'name': 'BREAKOUT',
            'subtitle': 'Paddle & Bricks Arcade',
            'desc': 'Power-ups • Multi-ball • 20 levels • Paddle physics',
            'color': 4,
            'icon': '█',
            'module': 'games.breakout.main',
            'entry': 'main',
        },
        'invaders': {
            'id': 'invaders',
            'name': 'SPACE INVADERS',
            'subtitle': 'Classic Fixed Shooter',
            'desc': 'Alien waves • Shields • UFO bonus • Progressive difficulty',
            'color': 5,
            'icon': '▼',
            'module': 'games.invaders.main',
            'entry': 'main',
        },
        'pacman': {
            'id': 'pacman',
            'name': 'PAC-MAN',
            'subtitle': 'Maze Chase Classic',
            'desc': '4 ghosts • Power pellets • Fruit bonus • Intermissions',
            'color': 6,
            'icon': '○',
            'module': 'games.pacman.main',
            'entry': 'main',
        },
    }

    # Check which games actually exist (have their main module)
    for game_id, info in game_registry.items():
        module_path = os.path.join(BASE_DIR, info['module'].replace('.', '/') + '.py')
        if os.path.exists(module_path):
            discovered.append(info)

    return discovered


def main(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    curses.noecho()
    curses.start_color()
    curses.use_default_colors()

    # Color pairs
    curses.init_pair(1, curses.COLOR_RED, -1)       # Accent
    curses.init_pair(2, curses.COLOR_GREEN, -1)     # Success
    curses.init_pair(3, curses.COLOR_YELLOW, -1)    # Warning
    curses.init_pair(4, curses.COLOR_CYAN, -1)      # Info
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)   # Highlight
    curses.init_pair(6, curses.COLOR_WHITE, -1)     # Normal
    curses.init_pair(7, curses.COLOR_BLUE, -1)      # Blue

    games = discover_games()
    if not games:
        stdscr.addstr(10, 10, "No games found!")
        stdscr.refresh()
        stdscr.getch()
        return None

    selected = 0

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        # Title
        title = "  N I G H T C L I M B  A R C A D E  "
        stdscr.addstr(2, max(0, (w - len(title)) // 2), title,
                      curses.color_pair(1) | curses.A_BOLD)

        # Subtitle
        sub = f"  Terminal Arcade Collection  •  {len(games)} Games  "
        stdscr.addstr(3, max(0, (w - len(sub)) // 2), sub,
                      curses.color_pair(6))

        # Game cards
        card_w = min(52, w - 4)
        start_y = 6
        for i, game in enumerate(games):
            y = start_y + i * 10
            x = max(2, (w - card_w) // 2)
            is_sel = (i == selected)

            # Card border
            border_color = game['color'] if is_sel else 6
            attr = curses.color_pair(border_color) | (curses.A_BOLD if is_sel else 0)

            # Top border
            stdscr.addstr(y, x, '╔' + '═' * (card_w - 2) + '╗', attr)
            # Title line
            title_line = f" {game['icon']}  {game['name']}  "
            subtitle = f" {game['subtitle']} "
            stdscr.addstr(y + 1, x, '║' + title_line.ljust(card_w - 2) + '║', attr)
            stdscr.addstr(y + 2, x, '║' + subtitle.center(card_w - 2) + '║',
                          curses.color_pair(game['color']))

            # Description
            desc_lines = game['desc'].split(' • ')
            for j, line in enumerate(desc_lines):
                stdscr.addstr(y + 3 + j, x, '║' + f"  {line}".ljust(card_w - 2) + '║',
                              curses.color_pair(6))

            # Bottom border
            stdscr.addstr(y + 6, x, '╚' + '═' * (card_w - 2) + '╝', attr)

            # Selection indicator
            if is_sel:
                stdscr.addstr(y, x + 1, '►', curses.color_pair(game['color']) | curses.A_BOLD)
                stdscr.addstr(y, x + card_w - 2, '◄', curses.color_pair(game['color']) | curses.A_BOLD)

        # Controls hint
        hint = "  ↑/↓ Navigate    Enter/Space Select    Q/Esc Quit  "
        stdscr.addstr(h - 3, max(0, (w - len(hint)) // 2), hint,
                      curses.color_pair(6))

        # Version
        ver = "  v2.1.0  •  Pure Python + Curses  •  Zero Dependencies  "
        stdscr.addstr(h - 1, max(0, (w - len(ver)) // 2), ver,
                      curses.color_pair(6) | curses.A_DIM)

        stdscr.refresh()

        key = stdscr.getch()
        if key in (curses.KEY_UP, ord('k'), ord('w')):
            selected = (selected - 1) % len(games)
        elif key in (curses.KEY_DOWN, ord('j'), ord('s')):
            selected = (selected + 1) % len(games)
        elif key in (curses.KEY_ENTER, 10, 13, ord(' ')):
            game_id = games[selected]['id']
            return game_id
        elif key in (ord('q'), 27):
            return None


def cli_main():
    """Entry point for pip-installed command."""
    try:
        game_id = curses.wrapper(main)
        if game_id:
            # Dynamic import
            games = discover_games()
            for g in games:
                if g['id'] == game_id:
                    module = importlib.import_module(g['module'])
                    entry_func = getattr(module, g['entry'])
                    curses.wrapper(entry_func)
                    break
    except KeyboardInterrupt:
        pass
    except ImportError as e:
        print(f"Game not found: {e}")
    except Exception as e:
        import traceback
        print(f"Fatal error: {e}")
        traceback.print_exc()


if __name__ == '__main__':
    cli_main()