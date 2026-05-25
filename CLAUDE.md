# Textual Vision — Project Instructions

Python implementation of Turbo Vision extending the Textual framework.
Brings the full Turbo Vision architecture (views, groups, dialogs, menus, palettes,
event handling) to Python/Textual while Pythonizing names and conventions.

## Reference Implementation

The modern C++ Turbo Vision at https://github.com/magiblot/tvision is the
architectural guide. Port the design and class hierarchy faithfully, but adapt
names to Python conventions:

- Class names: keep PascalCase but drop the `T` prefix where it would be
  unidiomatic (e.g., `TView` → `View`, `TRect` → `Rect`). Use judgement —
  if the `T`-prefixed name is iconic and avoids shadowing Python builtins or
  Textual classes, it may be kept.
- Methods/attributes: `snake_case` (e.g., `handleEvent` → `handle_event`,
  `mapColor` → `map_color`, `setState` → `set_state`).
- Constants: `UPPER_SNAKE_CASE` (e.g., `evMouseDown` → `EV_MOUSE_DOWN`,
  `cmQuit` → `CM_QUIT`, `kbEnter` → `KB_ENTER`).
- Enum-like constant groups: use `IntEnum` or `IntFlag` where semantics match.

## Architecture Overview

### Core Class Hierarchy (from tvision)

```
View                          # Fundamental UI element
  Frame                       # Window frame/border
  ScrollBar                   # Scrollbar control
  Scroller                    # Scrollable view with H/V scrollbars
    ListViewer                # Abstract list display
  StaticText                  # Read-only text display
    Label                     # Text label linked to another view
  Button                      # Push button
  Cluster                     # Group of toggles
    RadioButtons              # Single-selection
    CheckBoxes                # Multi-selection
  InputLine                   # Text input field
  StatusLine                  # Status bar at bottom
  MenuView                    # Base for menu rendering
    MenuBar                   # Horizontal menu bar
    MenuBox                   # Dropdown menu box
  Group                       # Container for child views
    Window                    # Titled, framed window
      Dialog                  # Modal/modeless dialog
    DeskTop                   # Desktop area manager
    Program                   # Application program core
      Application             # Top-level application
  Background                  # Desktop background fill
```

### Key Primitives

- **Point**: `(x, y)` with arithmetic operators
- **Rect**: Two Points `(a, b)` — top-left and bottom-right. Methods: `move()`,
  `grow()`, `intersect()`, `union()`, `contains()`, `is_empty()`
- **DrawBuffer**: Array of screen cells for efficient rendering
- **ScreenCell**: Character + color attribute pair
- **DrawSurface**: 2D grid of ScreenCells for off-screen rendering

### Event System

- **Event**: Tagged union with `what` (event type) + payload
- Event types: `EV_MOUSE_DOWN`, `EV_MOUSE_UP`, `EV_MOUSE_MOVE`, `EV_KEY_DOWN`,
  `EV_COMMAND`, `EV_BROADCAST`
- Event masks: `EV_MOUSE`, `EV_KEYBOARD`, `EV_MESSAGE`
- Flow: Application → Group dispatches to focused/child views → views call
  `clear_event()` to consume

### Color/Palette System

- Legacy indexed palette: each view class provides `get_palette()`, colors
  referenced by 1-based index, `map_color(index)` walks owner chain
- Extended colors: `ColorDesired` (tagged: default/BIOS/RGB/XTerm256),
  `ColorAttr` (fg + bg + style), `AttrPair` (normal + highlighted)
- Styles: bold, italic, underline, blink, reverse, strikethrough

## Relationship to Textual

This project **extends** Textual, not replaces it. Textual provides the terminal
I/O layer, rendering engine, CSS styling, and async event loop. Textual Vision adds
the Turbo Vision application architecture on top:

- Turbo Vision's view/group/owner hierarchy maps onto Textual's widget tree
- Turbo Vision's event dispatch integrates with Textual's message system
- Turbo Vision's palette system can layer over Textual's CSS theming
- The goal is to make building classic TV-style UIs (menus, dialogs, desktop
  metaphor) natural within Textual

## Project Layout (PyBuilder)

```
build.py                      # PyBuilder build script
setup.py                      # pip install shim (delegates to PyBuilder)
src/
  main/python/
    textual_vision/           # Main package
      __init__.py
      primitives.py           # Point, Rect
      views.py                # View base, Group, Window
      dialogs.py              # Dialog, standard dialogs
      menus.py                # MenuItem, MenuBar, MenuBox, StatusLine
      events.py               # Event, event types, handling
      colors.py               # Palette, ColorAttr, ColorDesired
      draw_buffer.py          # DrawBuffer, ScreenCell, DrawSurface
      app.py                  # Program, Application, DeskTop
      ...
  unittest/python/            # Unit tests (*_tests.py)
  integrationtest/python/     # Integration tests
```

## Build / Test

PyBuilder project. Always use `pyb -vX` for all build invocations.

```bash
pyb -vX                       # Full build (analyze + publish)
pyb -vX run_unit_tests        # Unit tests only
pyb -vX run_integration_tests # Integration tests only
```

Dependencies:
- `textual` — terminal UI framework (primary dependency)
- `karellen_pyb_plugin` — PyBuilder plugin for Karellen projects

## Conventions

- Apache-2.0 license, Karellen Inc. copyright
- Python ≥ 3.10
- File headers follow Karellen convention (see kubernator for reference)
- Test files: `*_tests.py` in the appropriate test directory
- Package name: `textual_vision` (underscore in Python, hyphen in distribution name)

## Design Principles

1. **Faithful architecture**: Port Turbo Vision's class hierarchy and
   design patterns accurately. Don't simplify away architectural elements
   that enable the full TV feature set.
2. **Pythonic API**: Names, patterns, and idioms should feel natural to
   Python developers. Use properties, context managers, dataclasses,
   protocols, and type hints where appropriate.
3. **Textual integration**: Build on Textual's strengths (async, CSS,
   rich rendering) rather than reimplementing what it already provides well.
4. **Incremental buildout**: Start with core primitives and the view/group
   hierarchy, then layer on events, palettes, menus, and dialogs.
