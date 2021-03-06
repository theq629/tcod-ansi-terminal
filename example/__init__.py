"""
Example and testing program.
"""

from typing import Any, NoReturn, Callable, Literal, Iterator, Mapping
import sys
import time
from random import Random
import argparse
import tcod.event
from tcod.event import Event, Quit, KeyDown
from tcod_ansi_terminal.context import MinimalContext
from ._world import World
from ._rendering import WorldRenderer
from ._sampling import Sampler

class GameUi:
    def __init__(
        self,
        context: MinimalContext,
        event_wait: Callable[[], Iterator[Event]],
        console_order: Literal['C', 'F'],
        console_scale: float,
        present_kwargs: Mapping[str, Any],
        verbose: bool
    ) -> None:
        self.context = context
        self.event_wait = event_wait
        self.verbose = verbose
        self.present_kwargs = present_kwargs

        term_dim = context.recommended_console_size()
        if verbose:
            print(f"TERMINAL SIZE {term_dim[0]}x{term_dim[1]}", file=sys.stderr)
        console_dim = int(term_dim[0] * console_scale), int(term_dim[1] * console_scale)

        rng = Random(0)
        self.world = World(console_dim, rng)
        self.world_renderer = WorldRenderer(self.world, console_order)

        self.root_console = tcod.Console(*console_dim, order=console_order)

        self.present_times = Sampler()

    def run(self) -> None:
        while True:
            self.world_renderer.render(self.root_console)
            present_start_time = time.time()
            self.context.present(self.root_console, clear_color=(64, 64, 0), **self.present_kwargs)
            self.present_times.sample(time.time() - present_start_time)
            self.root_console.clear()
            self._handle_events()

    def _handle_events(self) -> None:
        for event in self.event_wait():
            if event.type and self.verbose:
                print("EVENT", event, file=sys.stderr)
            if isinstance(event, Quit):
                self._quit()
            elif isinstance(event, KeyDown):
                key = event.sym
                if key == tcod.event.K_q:
                    self._quit()
                elif key in (tcod.event.K_UP, tcod.event.K_k):
                    self.world.move_player((0, -1))
                elif key in (tcod.event.K_DOWN, tcod.event.K_j):
                    self.world.move_player((0, 1))
                elif key in (tcod.event.K_LEFT, tcod.event.K_h):
                    self.world.move_player((-1, 0))
                elif key in (tcod.event.K_RIGHT, tcod.event.K_l):
                    self.world.move_player((1, 0))

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
