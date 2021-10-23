"""
Main for example.
"""

from pathlib import Path
import argparse
import tcod
import tcod_ansi_terminal
from tcod_ansi_terminal.context import NaivePresenter
from . import GameUi

_presenters = {
    'naive': NaivePresenter,
}

def main() -> None:
    title = "Test"
    default_term_width = 80
    default_term_height = 50

    argparser = argparse.ArgumentParser(description="tcod terminal test")
    argparser.add_argument(
        '--terminal',
        '-t',
        dest='use_terminal',
        default=False,
        action='store_true',
        help="Use the terminal instead of opening a new window."
    )
    argparser.add_argument(
        '--console-order',
        '-o',
        dest='console_order',
        type=str,
        choices=['C', 'F'],
        default='C',
        help="The order for the TCOD console."
    )
    argparser.add_argument(
        '--console-scale',
        '-s',
        dest='console_scale',
        type=float,
        default=1.0,
        help="The size of the TCOD console as a fraction of the terminal size."
    )
    argparser.add_argument(
        '--presenter',
        '-p',
        dest='presenter',
        type=str,
        choices=set(_presenters),
        default='naive',
        help="The type of presenter to use in terminal mode."
    )
    argparser.add_argument(
        '--verbose',
        '-v',
        dest='verbose',
        default=False,
        action='store_true',
        help="Log more info to stderr."
    )
    args = argparser.parse_args()

    if args.use_terminal:
        with tcod_ansi_terminal.context.new(
            columns=default_term_width,
            rows=default_term_height,
            title=title
        ) as regular_context:
            GameUi(
                context=regular_context,
                event_wait=tcod_ansi_terminal.event.wait,
                console_order=args.console_order,
                console_scale=args.console_scale,
                present_kwargs={
                    'presenter': _presenters[args.presenter]()
                },
                verbose=args.verbose
            ).run()

    else:
        tileset = tcod.tileset.load_tilesheet(
            Path(__file__).parent / "resources" / "terminal10x10_gs_tc.png",
            32,
            8,
            tcod.tileset.CHARMAP_TCOD
        )
        with tcod.context.new_terminal(
            default_term_width,
            default_term_height,
            tileset=tileset,
            title=title,
            vsync=True,
        ) as terminal_context:
            GameUi(
                context=terminal_context,
                event_wait=tcod.event.wait,
                console_order=args.console_order,
                console_scale=args.console_scale,
                present_kwargs={
                    'keep_aspect': True
                },
                verbose=args.verbose
            ).run()

if __name__ == "__main__":
    main()
