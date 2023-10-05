"""
Abstract context type to cover both regular TCOD and terminals.
"""

from typing import TypeVar, Type, Optional, Tuple
from types import TracebackType
try:
    from typing import Literal, Protocol # pylint: disable=ungrouped-imports
except ImportError:
    from typing_extensions import Literal, Protocol # type: ignore
from tcod.console import Console
from tcod.event import Event

C = TypeVar('C', bound="MinimalContext")
E = TypeVar("E", bound=Event)

class MinimalContext(Protocol):
    """
    Protocol for contexts which covers basic functionality that can be supported on terminals.

    Has slightly limited features compared to a regular TCOD context.

    A regular `tcod.context.Context` should satisfy this protocol, as does `TerminalContext`.
    """

    def __enter__(self: C) -> "C":
        ...

    def __exit__(
        self,
        type_: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType]
    ) -> None:
        ...

    def close(self) -> None:
        ...

    def present(
        self,
        console: Console,
        *,
        clear_color: Tuple[int, int, int] = (0, 0, 0),
        align: Tuple[float, float] = (0.5, 0.5)
    ) -> None:
        ...

    def pixel_to_tile(self, x: int, y: int) -> Tuple[int, int]:
        ...

    def pixel_to_subtile(self, x: int, y: int) -> Tuple[float, float]:
        ...

    def convert_event(self, event: E) -> E:
        ...

    def new_console(
        self,
        *,
        min_columns: int = 1,
        min_rows: int = 1,
        order: Literal['C', 'F'] = 'C'
    ) -> Console:
        ...

    def recommended_console_size(self, min_columns: int = 1, min_rows: int = 1) -> Tuple[int, int]:
        ...
