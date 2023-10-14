"""
Example and testing program.
"""

from typing import Any, NoReturn, Callable, Literal, Iterator, Mapping
import sys
import time
from random import Random
import argparse
import tcod.event
from tcod.console import Console
from tcod.event import Event, Quit, KeyDown, MouseMotion, WindowResized
from tcod_ansi_terminal.context import TerminalCompatibleContext, TerminalContext
from tcod_ansi_terminal.event import TerminalCompatibleEventWait
from ._world import World
from ._rendering import WorldRenderer
from ._sampling import Sampler

_WAIT_TIMEOUT = 0.1

class GameUi:
    def __init__(
        self,
        context: TerminalCompatibleContext,
        event_wait: TerminalCompatibleEventWait,
        console_order: Literal['C', 'F'],
        console_scale: float,
        present_kwargs: Mapping[str, Any],
        verbose: bool
    ) -> None:
        self.context = context
        self.event_wait = event_wait
        self.console_order = console_order
        self.console_scale = console_scale
        self.verbose = verbose
        self.present_kwargs = present_kwargs

        self.root_console = self._make_console()

        rng = Random(0)
        self.world = World((self.root_console.width, self.root_console.height), rng)
        self.world_renderer = WorldRenderer(self.world, console_order)

        self.present_times = Sampler()

    def run(self) -> None:
        while True:
            if isinstance(self.context, TerminalContext):
                self.context.cursor_position = self.world.player_pos
            self.world_renderer.render(self.root_console, self.context)
            present_start_time = time.time()
            self.context.present(self.root_console, clear_color=(64, 64, 0), **self.present_kwargs)
            self.present_times.sample(time.time() - present_start_time)
            self.root_console.clear()
            self._handle_events()

    def _make_console(self) -> Console:
        term_dim = self.context.recommended_console_size()
        if self.verbose:
            print(f"TERMINAL SIZE {term_dim[0]}x{term_dim[1]}", file=sys.stderr)
        console_dim = int(term_dim[0] * self.console_scale), int(term_dim[1] * self.console_scale)
        return Console(*console_dim, order=self.console_order)

    def _handle_events(self) -> None:
        for event in self.event_wait(_WAIT_TIMEOUT):
            if event.type and self.verbose:
                print("EVENT", event, file=sys.stderr)
            if isinstance(event, Quit):
                self._quit()
            elif isinstance(event, KeyDown):
                key = event.sym
                if key == tcod.event.KeySym.q:
                    self._quit()
                elif key in (tcod.event.KeySym.UP, tcod.event.KeySym.k):
                    self.world.move_player((0, -1))
                elif key in (tcod.event.KeySym.DOWN, tcod.event.KeySym.j):
                    self.world.move_player((0, 1))
                elif key in (tcod.event.KeySym.LEFT, tcod.event.KeySym.h):
                    self.world.move_player((-1, 0))
                elif key in (tcod.event.KeySym.RIGHT, tcod.event.KeySym.l):
                    self.world.move_player((1, 0))
            elif isinstance(event, MouseMotion):
                self.world_renderer.mouse_position = event.position
            elif isinstance(event, WindowResized):
                self.root_console = self._make_console()

    def _quit(self) -> NoReturn:
        if self.verbose:
            print(
                f"PRESENT TIME"
                f" min {self.present_times.minimum:0.4f}"
                f" max {self.present_times.maximum:0.4f}"
                f" mean {self.present_times.mean:0.4f}",
                file=sys.stderr
            )
        raise SystemExit()
