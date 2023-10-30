Features
========

Supported TCOD features (at least for some terminals):

- Basic letter, digit, punctuation, and enter keys (anything received as an
  unescaped character; this set is safest for compatibility with untested
  terminals).
- Shift modifier for letter keys (but not digits etc.).
- Arrow, function, home, end, insert, delete, page up, page down keys.
- Keysyms for the above keys.
- Key down and key up events in immediate succession for the above keys, based
  on terminal input.
- Text input events for letter etc. keys.
- Terminal size checks for ``recommended_console_size()`` and
  ``new_console()``.
- Window position, pixel size, and character size as requests. The choice to
  honour them or not is up to the terminal and/or window manager.
- Window resize events for terminal resizes.
- Mouse motion, button, and wheel events.
- Window focus gained and lost events.
- Window title.
- Quit event on hangup and other exit signals. If in a windowing system, this
  might get produced when the window is closed but isn't guaranteed.

Other features:

- The terminal will be reset cleanly on exit.
- The cursor position can be set.
- Cursor visibility can be set.

Unsupported TCOD features:

- Shift modifier for non-letter key.
- Modifiers other than shift.
- Key scancodes (are all ``K_UNKNOWN``).
- Correct timing for key down/up events.
- ``tcod.event.get()``.
- Basically any other input/output feature that isn't mentioned above,
  especially things in ``tcod.context`` and ``tcod.event``.

Features that are not supported but could be later:

- Some support for other colour modes.
- Screenshots (with separate interface) to text files.
