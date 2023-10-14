"""
This is the internal context system.
"""

from typing import TypeVar, Any, Optional, Sequence, Tuple, List, BinaryIO
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal # type: ignore
from tcod.console import Console
from tcod.event import Event
from ._platform import Platform, make_platform
from ._internal_event import EventsManager
from ._abstract_context import TerminalCompatibleContext
from ._presenters import Presenter, NaivePresenter
from . import _ansi

E = TypeVar("E", bound=Event)

_context_stack: List["TerminalContext"] = []

class TerminalContext(TerminalCompatibleContext):
    """
    TCOD-compatible context that writes to a terminal.

    `recommended_console_size()` with no set minimum is the real size of the terminal, and
    `new_console()` with no set minimum will create a console that fits the terminal exactly.
    """

    _out_file: BinaryIO
    _platform: Platform
    _term_dim: Tuple[int, int]
    _events_manager: EventsManager

    def _on_resize(self, width: int, height: int) -> None:
        self._term_dim = (width, height)

    def _open(
        self,
        *,
        requested_window_pos: Optional[Tuple[int, int]],
        requested_pixels_dim: Optional[Tuple[int, int]],
        requested_chars_dim: Optional[Tuple[int, int]],
        title: Optional[str],
    ) -> None:
        _ansi.hide_cursor(self._out_file)
        _ansi.enable_mouse_tracking(self._out_file)
        _ansi.enable_focus_reporting(self._out_file)
        if requested_window_pos is not None:
            _ansi.request_terminal_window_pos(requested_window_pos, self._out_file)
        if requested_pixels_dim is not None:
            _ansi.request_terminal_pixels_dim(requested_pixels_dim, self._out_file)
        elif requested_chars_dim is not None:
            _ansi.request_terminal_chars_dim(requested_chars_dim, self._out_file)
        if title is not None:
            _ansi.request_terminal_title(title, self._out_file)
        self._out_file.flush()

    def __enter__(self) -> "TerminalContext":
        return self

    def close(self) -> None:
        global _context_stack
        _ansi.set_cursor_pos((0, 0), self._out_file)
        _ansi.clear_screen(self._out_file)
        _ansi.show_cursor(self._out_file)
        _ansi.disable_mouse_tracking(self._out_file)
        _ansi.disable_focus_reporting(self._out_file)
        _ansi.reset(self._out_file)
        self._out_file.flush()
        self._platform.close()
        _context_stack = [c for c in _context_stack if c is not self]

    def __exit__(self, *args: Any) -> None:
        self.close()

    def present(
        self,
        console: Console,
        *,
        clear_color: Tuple[int, int, int] = (0, 0, 0),
        align: Tuple[float, float] = (0.5, 0.5),
        presenter: Optional[Presenter] = None
    ) -> None:
        # pylint: disable=arguments-differ
        if presenter is None:
            presenter = NaivePresenter()
        presenter.present(
            console=console,
            term_dim=self._term_dim,
            align=align,
            clear_colour=clear_color,
            out_file=self._out_file
        )

    def pixel_to_tile(self, x: int, y: int) -> Tuple[int, int]:
        return x, y

    def pixel_to_subtile(self, x: int, y: int) -> Tuple[float, float]:
        return x, y

    def convert_event(self, event: E) -> E:
        return event

    def new_console(
        self,
        *,
        min_columns: int = 1,
        min_rows: int = 1,
        order: Literal['C', 'F'] = 'C'
    ) -> Console:
        width, height = max(min_columns, self._term_dim[0]), max(min_rows, self._term_dim[1])
        return Console(width, height, order=order)

    def recommended_console_size(self, min_columns: int = 1, min_rows: int = 1) -> Tuple[int, int]:
        return max(min_columns, self._term_dim[0]), max(min_rows, self._term_dim[1])

def get_terminal_context_stack() -> Sequence[TerminalContext]:
    return _context_stack

def get_events_manager(context: TerminalContext) -> EventsManager:
    # pylint: disable=protected-access
    return context._events_manager

def make_terminal_context(
    *,
    in_file: BinaryIO,
    out_file: BinaryIO,
    requested_window_pos: Optional[Tuple[int, int]] = None,
    requested_pixels_dim: Optional[Tuple[int, int]] = None,
    requested_chars_dim: Optional[Tuple[int, int]] = None,
    title: Optional[str] = None
) -> TerminalContext:
    # pylint: disable=protected-access
    new: TerminalContext = TerminalContext.__new__(TerminalContext)
    new._out_file = out_file
    new._platform = make_platform(in_file)
    new._platform.open()
    new._term_dim = (0, 0)
    new._events_manager = EventsManager(new._platform, new._out_file, new._on_resize)
    new._open(
        requested_window_pos=requested_window_pos,
        requested_pixels_dim=requested_pixels_dim,
        requested_chars_dim=requested_chars_dim,
        title=title,
    )
    new._events_manager.request_resize_event()
    _context_stack.append(new)
    return new
