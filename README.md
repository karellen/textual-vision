# Textual Vision

A Python implementation of [Turbo Vision](https://github.com/magiblot/tvision) built on top of [Textual](https://github.com/Textualize/textual).

Textual Vision brings the classic Turbo Vision desktop application architecture to modern Python terminals: movable/resizable windows with Z-order, modal dialogs, hierarchical dropdown menus, a context-sensitive status bar, three-phase event dispatch, and the full set of TV form controls. It uses Textual as its rendering and terminal I/O layer while faithfully porting TV's class hierarchy, event model, and visual style.

## Features

- **Desktop metaphor** with tiled/cascaded windows, Z-order management, and per-window focus
- **Window system** with double-line active / single-line passive frames, title bar, close/zoom icons, drag-to-move, drag-to-resize
- **Menu bar** with dropdown menus, sub-menus, keyboard navigation, mouse hover highlighting, and tilde-hotkey support
- **Status bar** with context-sensitive items that map key presses to commands
- **Three-phase event dispatch**: pre-process (menu bar), focused widget, post-process (status bar)
- **Modal and modeless dialogs** with OK/Cancel/Yes/No command handling and validation hooks
- **Form controls**: Button, Label, CheckBoxes, RadioButtons, InputLine (with password masking), ScrollBar
- **Two classic themes**: Turbo Pascal 7.0 (blue desktop, cyan highlights) and Turbo C (black desktop, yellow accents), both using the original CGA/VGA 16-color palette

## Screenshot

```
 File  Edit  Window  Help
╔[■]══════════════ Window 1 ══════════════[▲]╗
║This is window #1.                          ║
║                                            ║
║Drag the title bar to move.                 ║
║Drag bottom-right corner to resize.         ║
║Use frame icons to close/zoom.              ║
╚════════════════════════════════════════════╝
F1 Help  F10 Menu  Alt+X Exit
```

## Quick Start

### Requirements

- Python >= 3.10
- [Textual](https://pypi.org/project/textual/)

### Installation

```bash
pip install textual-vision
```

Or install from source:

```bash
git clone https://github.com/karellen/textual-vision.git
cd textual-vision
pip install -e .
```

### Run the Demo

```bash
PYTHONPATH=src/main/python python examples/demo.py
```

Keys: **F10** toggle menu, **Alt+F/E/W/H** open menus, **Ctrl+N** new window, **F1** controls dialog, **Alt+X** quit. **Tab** cycles between controls in dialogs.

## Architecture

Textual provides the terminal I/O, rendering engine, CSS styling, and async event loop. Textual Vision adds the Turbo Vision application architecture on top. See [docs/architecture.md](docs/architecture.md) for the full design.

### Class Hierarchy

```
Widget (Textual)
  +-- TVViewMixin               # tv_state, tv_options, tv_handle_key
  |
  +-- Group (Widget, TVViewMixin)     # three-phase dispatch, focus scoping
  |     +-- Window (Group)            # frame + content, drag/resize/zoom
  |     |     +-- Dialog (Window)     # modal/modeless dialog
  |     +-- DeskTop (Group)           # tile/cascade/Z-order
  |
  +-- App (Textual)
  |     +-- Program (App)             # MenuBar + DeskTop + StatusLine
  |           +-- Application         # top-level app
  |
  +-- Frame (Widget)                  # border rendering, mouse interaction
  +-- Background (Widget)             # desktop fill pattern
  +-- MenuBar (Widget, TVViewMixin)   # horizontal menu, PRE_PROCESS
  +-- MenuBox (Widget)                # dropdown menu
  +-- StatusLine (Widget, TVViewMixin)# status bar, POST_PROCESS
  +-- Label (Widget, TVViewMixin)     # linked text label with hotkey
  +-- Button (Widget, TVViewMixin)    # push button with shadow
  +-- Cluster (Widget, TVViewMixin)   # abstract toggle group
  |     +-- CheckBoxes (Cluster)      # [X]/[ ] multi-select
  |     +-- RadioButtons (Cluster)    # (•)/( ) single-select
  +-- InputLine (Widget, TVViewMixin) # single-line text editor
  +-- ScrollBar (Widget, TVViewMixin) # vertical/horizontal scrollbar
```

### Naming Conventions

TV names are adapted to Python conventions:

| Turbo Vision | Textual Vision | Rule |
|---|---|---|
| `TView` | `View` | Drop `T` prefix |
| `TWindow` | `Window` | Drop `T` prefix |
| `handleEvent` | `handle_event` | snake_case methods |
| `mapColor` | `map_color` | snake_case methods |
| `evMouseDown` | `EV_MOUSE_DOWN` | UPPER_SNAKE constants |
| `cmQuit` | `Command.QUIT` | IntEnum members |
| `ofSelectable` | `OptionFlag.SELECTABLE` | IntFlag members |

### Event System

TV's three-phase dispatch is preserved:

1. **Pre-process** -- `OptionFlag.PRE_PROCESS` widgets (e.g., MenuBar) intercept keys first
2. **Focused** -- the current (TV-focused) child handles the key
3. **Post-process** -- `OptionFlag.POST_PROCESS` widgets (e.g., StatusLine) catch unhandled keys

Commands flow via `CommandMessage(Message, bubble=True)`. Broadcasts use `BroadcastMessage(Message, bubble=False)` posted to each child individually.

### Themes

Two built-in themes use the original 16-color CGA/VGA BIOS palette:

| Theme | Desktop | Surface | Accent |
|---|---|---|---|
| `turbo-pascal` | Blue (#0000AA) | Light Gray (#AAAAAA) | Green (#00AA00) |
| `turbo-c` | Black (#000000) | Light Gray (#AAAAAA) | Yellow (#FFFF55) |

Set the theme in your Application subclass:

```python
class MyApp(Application):
    def __init__(self):
        super().__init__(theme="turbo-c")
```

## Example

```python
from textual_vision.app import Application
from textual_vision.button import Button
from textual_vision.cluster import CheckBoxes, RadioButtons
from textual_vision.constants import Command
from textual_vision.dialogs import Dialog
from textual_vision.input_line import InputLine
from textual_vision.label import Label
from textual_vision.menus import Menu, MenuItem, SubMenu
from textual_vision.status_line import StatusDef, StatusItem
from textual_vision.window import Window


class MyApp(Application):
    def init_menu_bar(self):
        return Menu(items=[
            SubMenu("~F~ile",
                MenuItem("~N~ew", Command.NEW),
                MenuItem("E~x~it", Command.QUIT, key_code="Alt+X"),
            ),
        ])

    def init_status_line(self):
        return [StatusDef(0, 0xFFFF, [
            StatusItem("~Alt+X~ Exit", "alt+x", Command.QUIT),
        ])]


if __name__ == "__main__":
    MyApp().run()
```

## Building

Textual Vision uses [PyBuilder](https://pybuilder.io/):

```bash
pip install pybuilder karellen-pyb-plugin
pyb -vX                       # Full build
pyb -vX run_unit_tests        # Unit tests only
pyb -vX run_integration_tests # Integration tests only
```

## Reference

The architectural guide is [magiblot/tvision](https://github.com/magiblot/tvision), the modern C++ port of Borland's Turbo Vision 2.0. Textual Vision ports the design and class hierarchy faithfully while adapting to Python conventions and building on Textual's rendering capabilities.

## License

Apache License, Version 2.0

Copyright 2026 Karellen, Inc.
