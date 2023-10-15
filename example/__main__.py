"""
Main for example.
"""

from pathlib import Path
import logging
import argparse
import tcod
import tcod_ansi_terminal
from tcod_ansi_terminal.context import NaivePresenter, SparsePresenter
from . import GameUi

_presenters = {
    'naive': NaivePresenter,
    'sparse': SparsePresenter,
}

def main() -> None:
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
        help="The size of the TCOD console as a fraction of the terminal size. This is just for"
             " testing with different console sizes relative to the terminal."
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
        '--x',
        dest='window_x',
        type=int,
        default=None,
        help="The requested x position of the console window in pixels."
    )
    argparser.add_argument(
        '--y',
        dest='window_y',
        type=int,
        default=None,
        help="The requested y position of the console window in pixels."
    )
    argparser.add_argument(
        '--width',
        dest='width',
        type=int,
        default=None,
        help="The requested width of the console in pixels."
    )
    argparser.add_argument(
        '--height',
        dest='height',
        type=int,
        default=None,
        help="The requested height of the console in pixels."
    )
    argparser.add_argument(
        '--columns',
        dest='columns',
        type=int,
        default=80,
        help="The requested width of the console in characters."
    )
    argparser.add_argument(
        '--rows',
        dest='rows',
        type=int,
        default=50,
        help="The requested height of the console in characters."
    )
    argparser.add_argument(
        '--log',
        '-l',
        dest='log_path',
        type=Path,
        default=None,
        help="Path for log file.",
    )
    argparser.add_argument(
        '--verbose',
        '-v',
        dest='log_level',
        type=lambda s: s.upper(),
        default='info',
        help="Set Python log level."
    )
    args = argparser.parse_args()

    if args.log_path is not None:
        logging.basicConfig(
            filename=args.log_path,
            filemode='a',
            level=args.log_level,
        )

    context_kwargs = dict(
        title="Test",
        x=args.window_x,
        y=args.window_y,
        width=args.width,
        height=args.height,
        columns=args.columns,
        rows=args.rows,
    )
    game_ui_kwargs = dict(
        console_order=args.console_order,
        console_scale=args.console_scale,
    )

    if args.use_terminal:
        with tcod_ansi_terminal.context.new(**context_kwargs) as terminal_context:
            GameUi(
                context=terminal_context,
                event_wait=tcod_ansi_terminal.event.wait,
                present_kwargs={
                    'presenter': _presenters[args.presenter]()
                },
                **game_ui_kwargs
            ).run()

    else:
        tileset = tcod.tileset.load_tilesheet(
            Path(__file__).parent / "resources" / "terminal10x10_gs_tc.png",
            32,
            8,
            tcod.tileset.CHARMAP_TCOD
        )
        with tcod.context.new(
            tileset=tileset,
            vsync=True,
            **context_kwargs
        ) as regular_context:
            GameUi(
                context=regular_context,
                event_wait=tcod.event.wait,
                present_kwargs={
                    'keep_aspect': True
                },
                **game_ui_kwargs
            ).run()

if __name__ == "__main__":
    main()
