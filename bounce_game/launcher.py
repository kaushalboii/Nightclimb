#!/usr/bin/env python3
"""
Nightclimb Arcade Launcher
Unified menu for Bounce + Snake games.
"""

import curses
import sys
import os

# Add game directories to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'games'))


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

    games = [
        {
            'id': 'bounce',
            'name': 'BOUNCE',
            'subtitle': 'Nokia Classic Recreation',
            'desc': 'Physics platformer • 12 levels • Power-ups • Auto-save',
            'color': 1,
            'icon': '●',
        },
        {
            'id': 'snake',
            'name': 'SNAKE',
            'subtitle': 'Retro Arcade Classic',
            'desc': '5 modes • Power-ups • Obstacles • High scores',
            'color': 2,
            'icon': '▲',
        },
    ]

    selected = 0

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        # Title
        title = "  N I G H T C L I M B  A R C A D E  "
        stdscr.addstr(2, max(0, (w - len(title)) // 2), title,
                      curses.color_pair(1) | curses.A_BOLD)

        # Subtitle
        sub = "  Terminal Arcade Collection  "
        stdscr.addstr(3, max(0, (w - len(sub)) // 2), sub,
                      curses.color_pair(6))

        # Game cards
        card_w = min(50, w - 4)
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
        ver = "  v2.0.0  •  Pure Python + Curses  •  Zero Dependencies  "
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


if __name__ == '__main__':
    try:
        game_id = curses.wrapper(main)
        if game_id == 'bounce':
            from games.bounce.main import main as bounce_main
            curses.wrapper(bounce_main)
        elif game_id == 'snake':
            from games.snake.main import main as snake_main
            curses.wrapper(snake_main)
    except KeyboardInterrupt:
        pass
    except ImportError as e:
        print(f"Game not found: {e}")
        print("Make sure games/bounce/ and games/snake/ exist")
    except Exception as e:
        import traceback
        print(f"Fatal error: {e}")
        traceback.print_exc()