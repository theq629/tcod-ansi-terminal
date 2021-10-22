"""
Protocol for platform support.
"""

from typing import Callable, Optional
try:
    from typing import Protocol # pylint: disable=ungrouped-imports
except ImportError:
    from typing_extensions import Protocol # type: ignore

class Platform(Protocol):
    def open(self) -> None:
        ...

    def close(self) -> None:
        ...

    def getch(self, timeout: Optional[float] = None) -> Optional[bytes]:
        ...

    def watch_resize(self, callback: Callable[[], None]) -> None:
        ...

    def watch_quit(self, callback: Callable[[], None]) -> None:
        ...
