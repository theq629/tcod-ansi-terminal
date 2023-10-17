from tcod.event import wait as tcod_wait
from tcod_ansi_terminal.event import TerminalCompatibleEventWait, wait as terminal_wait

def _use_wait(wait: TerminalCompatibleEventWait) -> None:
    pass

def _use_tcod_wait() -> None:
    _use_wait(tcod_wait)

def _use_terminal_wait() -> None:
    _use_wait(terminal_wait)
