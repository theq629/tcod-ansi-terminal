"""
Unix platform support.
"""

from typing import Union, Callable, Optional, List, BinaryIO
import os
import termios
import tty
import signal
import select

class UnixPlatform:
    def __init__(self, in_file: BinaryIO):
        self.old_attrs: Optional[List[Union[int, List[Union[bytes, int]]]]] = None
        self._pipe_r, self._pipe_w = os.pipe()
        os.set_blocking(self._pipe_w, False)
        self.in_file = in_file.fileno()
        signal.set_wakeup_fd(self._pipe_w, warn_on_full_buffer=False)

    def open(self) -> None:
        self.old_attrs = termios.tcgetattr(self.in_file)
        tty.setraw(self.in_file)

    def close(self) -> None:
        if self.old_attrs is not None:
            termios.tcsetattr(self.in_file, termios.TCSADRAIN, self.old_attrs)

    def getch(self, timeout: Optional[float] = None) -> Optional[bytes]:
        ready, _rw, _rx = select.select((self.in_file, self._pipe_r), (), (), timeout)
        if self._pipe_r in ready:
            os.read(self._pipe_r, 1)
        if self.in_file in ready:
            return os.read(self.in_file, 1)
        return None

    def watch_resize(self, callback: Callable[[], None]) -> None:
        signal.signal(signal.SIGWINCH, lambda sn, sf: callback())

    def watch_quit(self, callback: Callable[[], None]) -> None:
        signal.signal(signal.SIGTERM, lambda sn, sf: callback())
        signal.signal(signal.SIGINT, lambda sn, sf: callback())
        signal.signal(signal.SIGQUIT, lambda sn, sf: callback())
        signal.signal(signal.SIGHUP, lambda sn, sf: callback())
