"""
Windows platform support.

TODO: This is totally untested, and doesn't support some things!
"""

from typing import Callable, Optional, BinaryIO
import msvcrt # pylint: disable=import-error

class WindowsPlatform:
    # pylint: disable=no-self-use

    def __init__(self, in_file: BinaryIO):
        self.in_file = in_file

    def open(self) -> None:
        pass

    def close(self) -> None:
        pass

    def getch(self, timeout: Optional[float] = None) -> Optional[bytes]:
        # pylint: disable=unused-argument
        return msvcrt.getch() # type: ignore

    def watch_resize(self, callback: Callable[[], None]) -> None:
        pass

    def watch_quit(self, callback: Callable[[], None]) -> None:
        pass
