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

    The size of the terminal can be requested but is not guaranteed, and may
    change at runtime after the context is created.
    `recommended_console_size()` is the actual size of the terminal and
    `new_console()` creates a console of that size.
    """

    _out_file: BinaryIO
    _platform: Platform
    _last_term_dim: Tuple[int, int]
    _cursor_visible: bool
    _cursor_position: Tuple[int, int]
    _events_manager: EventsManager

    def _open(
        self,
        *,
        requested_window_pos: Optional[Tuple[int, int]],
        requested_pixels_dim: Optional[Tuple[int, int]],
        requested_chars_dim: Optional[Tuple[int, int]],
        title: Optional[str],
    ) -> None:
        _ansi.hide_cursor(self._out_file)
        _ansi.set_cursor_pos((0, 0), self._out_file)
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
        """
        Present a console to this context’s display.

        `presenter` is the `Presenter` to use to control how the console is
        written to the terminal. In general the presenter instance should be
        reused between calls to `present()`. Other arguments are as for regular
        TCOD `present()`.
        """
        # pylint: disable=arguments-differ
        if presenter is None:
            presenter = NaivePresenter()
        presenter.present(
            console=console,
            term_dim=self._last_term_dim,
            align=align,
            clear_colour=clear_color,
            out_file=self._out_file
        )
        cur_x, cur_y = self._cursor_position
        _ansi.set_cursor_pos((cur_x + 1, cur_y + 1), self._out_file)
        self._out_file.flush()

    def pixel_to_tile(self, x: int, y: int) -> Tuple[int, int]:
        return x, y

    def pixel_to_subtile(self, x: int, y: int) -> Tuple[float, float]:
        return x, y

    def convert_event(self, event: E) -> E:
        return event

    def new_console(self, *, order: Literal['C', 'F'] = 'C') -> Console:
        """
        Return a new console sized for this context, that is with the actual
        size of the terminal.
        """
        width, height = self.recommended_console_size()
        return Console(width, height, order=order)

    def recommended_console_size(self) -> Tuple[int, int]:
        """
        Return the recommended size of a console for this context, which is
        always the actual size of the terminal.
        """
        new_term_dim = self._events_manager.get_terminal_dim()
        if new_term_dim is None:
            return (0, 0)
        self._last_term_dim = new_term_dim[0], new_term_dim[1]
        return self._last_term_dim

    def _on_resize(self, dim: Tuple[int, int]) -> None:
        self._last_term_dim = dim

    @property
    def cursor_position(self) -> Tuple[int, int]:
        """
        The current position of the terminal cursor.
        """
        return self._cursor_position

    @cursor_position.setter
    def cursor_position(self, value: Tuple[int, int]) -> None:
        self._cursor_position = value

    @property
    def cursor_visible(self) -> bool:
        return self._cursor_visible

    @cursor_visible.setter
    def cursor_visible(self, value: bool) -> None:
        if value:
            _ansi.show_cursor(self._out_file)
        else:
            _ansi.hide_cursor(self._out_file)
        self._cursor_visible = value

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
    new._last_term_dim = (0, 0)
    new._cursor_visible = False
    new._cursor_position = (0, 0)
    new._events_manager = EventsManager(new._platform, new._out_file, new._on_resize)
    new._open(
        requested_window_pos=requested_window_pos,
        requested_pixels_dim=requested_pixels_dim,
        requested_chars_dim=requested_chars_dim,
        title=title,
    )
    _context_stack.append(new)
    return new
