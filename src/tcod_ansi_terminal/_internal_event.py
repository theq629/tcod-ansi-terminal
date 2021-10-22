"""
This is the internal event system including hooks for the context.
"""

from typing import Optional, Iterator, Tuple
from tcod.event import Event, KeyDown, KeyUp, TextInput, Quit, WindowResized, KMOD_NONE, \
    KMOD_SHIFT, K_UNKNOWN
from ._platform import Platform

class EventsManager:
    def __init__(self, platform: Platform):
        self._platform = platform
        self._resize_waiting: Optional[Tuple[int, int]] = None
        self._quit_waiting = False

    def on_resize(self, new_dim: Tuple[int, int]) -> None:
        self._resize_waiting = new_dim

    def on_quit(self) -> None:
        self._quit_waiting = True

    def wait(self, timeout: Optional[float] = None) -> Iterator[Event]:
        key = self._platform.getch(timeout)
        if self._quit_waiting:
            yield Quit()
            self._quit_waiting = False
        if self._resize_waiting is not None:
            yield WindowResized(
                type='WINDOWRESIZED',
                width=self._resize_waiting[0],
                height=self._resize_waiting[1]
            )
            self._resize_waiting = None
        if key is not None:
            key_text = key.decode('ascii')
            if key.isupper():
                key = key.lower()
                mod = KMOD_SHIFT
            else:
                mod = KMOD_NONE
            key_sym = ord(key)
            yield KeyDown(sym=key_sym, scancode=K_UNKNOWN, mod=mod)
            yield TextInput(text=key_text)
            yield KeyUp(sym=key_sym, scancode=K_UNKNOWN, mod=mod)
