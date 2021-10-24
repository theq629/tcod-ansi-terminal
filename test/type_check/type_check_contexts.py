from tcod.context import Context
from tcod_ansi_terminal.context import MinimalContext, TerminalContext

def _use_context(_context: MinimalContext) -> None:
    pass

def _use_tcod_context(context: Context) -> None:
    _use_context(context)

def _use_terminal_context(context: TerminalContext) -> None:
    _use_context(context)
