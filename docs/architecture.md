# Textual Vision Architecture

How Turbo Vision's architecture maps onto Textual.

## Guiding Principle

Textual provides terminal I/O, rendering, CSS, and an async event loop.
Textual Vision adds what Textual lacks: the Turbo Vision application
architecture (desktop metaphor, movable windows, modal dialogs, menus,
status bars, three-phase event dispatch). We never reimplement what Textual
already does well; we build on top of it.

## What Is Dropped

TV's internals that Textual replaces outright:

| TV Concept | Textual Equivalent |
|---|---|
| TRect / TPoint geometry | CSS layout + Region / Offset / Size |
| DrawBuffer / ScreenCell | Strip / Segment + render() / render_line() |
| Color palette (indexed) | CSS variables + Theme ($primary, $surface, ...) |
| mapColor() owner-chain walk | CSS cascade + inheritance |
| growMode | CSS %, fr units, dock |
| setState(sfVisible/sfExposed) | display / visible CSS properties |
| Timer system | set_timer() / set_interval() |
| Clipboard | App.copy_to_clipboard() |
| Scrollbar / Scroller | ScrollableContainer + CSS overflow |

These are not ported. Textual's versions are used directly.

## What Is Adapted

TV concepts that have Textual analogs but need a thin bridge layer:

### Commands and Broadcasts

TV uses integer command constants in evCommand/evBroadcast events.
Textual uses typed Message subclasses.

**Decision:** Two Message subclasses bridge the gap:

- `CommandMessage(Message, bubble=True)` carries a `Command` enum value
  and optional `info` payload. It bubbles up the widget tree, matching
  TV's evCommand behavior where commands propagate up the owner chain.
- `BroadcastMessage(Message, bubble=False)` carries the same payload but
  does NOT bubble. TV's evBroadcast is not bottom-up; the originating
  Group iterates all children and posts to each one. The Group.broadcast()
  method does this explicitly.

The `Command` enum replaces TV's integer constants (cmQuit, cmClose, etc.)
with named Python values.

### Event Consumption

TV's `clearEvent()` mutates the event in-place (sets what to evNothing).
Textual's `message.stop()` sets a flag without mutating. Both prevent
further propagation. We use `message.stop()` everywhere and also call
`event.prevent_default()` to suppress Textual's built-in key handling
when TV dispatch consumes an event.

### State and Option Flags

TV's TView carries `state` and `options` bitfields that control visibility,
selectability, focus, and dispatch participation.

**Decision:** `TVViewMixin` adds `tv_state: StateFlag` and
`tv_options: OptionFlag` to any Textual Widget. The `tv_` prefix avoids
collisions with Textual's own Widget attributes. Group checks these flags
on children to determine dispatch participation and selectability.

Flags that have direct Textual equivalents are not duplicated:
- sfVisible/sfExposed map to Textual's `display`/`visible` CSS
- sfDisabled maps to Textual's `disabled` property
- ofSelectable maps to Textual's `can_focus`

The TV flags are still tracked because Group's three-phase dispatch needs
them for its own logic (e.g., checking DISABLED before allowing TV focus),
but the Textual-side equivalents handle the rendering/interaction effects.

### Focus

TV scopes focus per-Group: each Group tracks its own `current` child, and
Tab/Shift+Tab cycle within that Group's children only. Textual's
Screen-level focus_next/focus_previous cycles all focusable widgets on
the entire screen.

**Decision:** Group sets `can_focus = True` on itself, making Group the
widget that receives Textual focus. Group's children do NOT receive Textual
focus directly. Instead, Group maintains a `current` property pointing to
the TV-focused child and dispatches key events to it internally via
`tv_handle_key()`. Focus cycling (`select_next`) iterates only children
with `OptionFlag.SELECTABLE` and without `StateFlag.DISABLED`.

Setting `current` updates the child's `tv_state` flags (adds/removes
`FOCUSED | SELECTED`).

This means Textual's focus system and TV's focus system operate at different
levels: Textual focuses the Group container; TV focuses a child within it.

## What Is Built

Features Textual lacks entirely that must be constructed:

### Three-Phase Event Dispatch

TV's defining event architecture. When a Group receives a key event, it
dispatches in three phases:

1. **PreProcess** -- children with `OptionFlag.PRE_PROCESS` get the event
   first. The canonical example is MenuBar intercepting F10.
2. **Focused** -- the `current` child handles the event.
3. **PostProcess** -- children with `OptionFlag.POST_PROCESS` get unhandled
   events. The canonical example is StatusLine catching unbound hotkeys.

If any phase returns True (handled), subsequent phases are skipped.

**Integration with Textual's key routing:** Textual sends key events to the
focused widget. Since Group has `can_focus = True`, it receives key events
via `_on_key()`. The override runs three-phase dispatch; if handled, it
calls `event.stop()` and `event.prevent_default()` to suppress further
Textual processing.

For nested Groups: a child Group's `tv_handle_key()` delegates to its own
`_three_phase_dispatch()`, so the three-phase model composes recursively.

Mouse events are NOT three-phase dispatched. Textual's positional mouse
routing (event goes to the widget under the cursor) matches TV's behavior.

### Window System

TV's TWindow = TGroup + TFrame + title + drag/resize/zoom/close.

**Decision:** Two classes:

- `Frame(Widget)` -- renders TV-style box-drawing borders and handles
  mouse interactions. Uses `render_line()` for per-row border rendering
  with a character buffer approach: build an array of characters and
  styles, stamp icons and title into it, then emit styled Text. Frame
  has `COMPONENT_CLASSES` for CSS-targetable styling (active/passive
  frame, icons, title). Active frames use double-line box drawing
  (╔═╗║╚═╝) in `$foreground` (white); passive frames use single-line
  (┌─┐│└─┘) in `$text`. Title and icons use `$foreground` and `$accent`
  respectively. Window's background is `$background` (blue) so the
  frame lines appear white-on-blue; Dialog overrides to `$surface`
  (gray).

- `Window(Group)` -- composes a Frame and a content Container. Frame
  renders the border chrome; content Container (with `margin: 1`) sits
  inside, leaving border edges visible. Frame posts `CommandMessage`
  (close, zoom) and `DragMove`/`ResizeMove` messages that bubble to
  Window. Window handles them to update `styles.offset` (move) and
  `styles.width`/`styles.height` (resize).

**Positioning model:** Windows use Textual's `styles.offset` for absolute
positioning within DeskTop and `styles.width`/`styles.height` for sizing.
DeskTop imposes no layout on Window children; each Window manages its own
position. This gives free-form window placement while using Textual's
rendering pipeline.

**Zoom:** Window stores pre-zoom offset/width/height, then sets offset to
(0,0) and size to 1fr/1fr to fill the parent. Unzoom restores the stored
values.

### DeskTop

`DeskTop(Group)` manages Window children:

- `Background(Widget)` fills the desktop area with a pattern character,
  on a separate CSS layer (`background`) below the `windows` layer.
- `tile(region)` arranges windows with `OptionFlag.TILEABLE` in a grid.
  Grid column count scales: 1-2 windows = N cols, 3-4 = 2, 5-9 = 3,
  10+ = 4. Last column/row absorb remainder width/height.
- `cascade(region)` staggers all windows at (i, i) offsets with 2/3
  region size, wrapping via modular arithmetic when hitting edges.
- `raise_window(window)` brings the window to the top of the Z-order
  (by reordering its layer in the DeskTop's `layers` CSS), activates
  its frame (double-line border), deactivates all others, and sets it
  as `current`.

Z-order is managed by assigning each window its own CSS layer (e.g.,
`win-1`, `win-2`). Each layer has its own layout context, so every
window's natural position is (0,0) within its layer — making `offset`
effectively absolute. DeskTop maintains a `_z_order` list and rebuilds
its `layers` CSS property to reflect the stacking order. This avoids
using `move_child`, which would change natural layout positions since
Textual's `offset` is relative.

### Menu System

TV's TMenuBar + TMenuBox ported as two widgets plus data structures.

**Data model:** `MenuItem` (dataclass with name, command, key_code,
sub_menu, disabled, param), `Separator`, `Menu` (list of items).
`SubMenu()` helper creates a MenuItem with a nested Menu.

**Hotkey markup:** TV's `~X~` convention marks hotkey characters.
`parse_hotkey_text("~F~ile")` returns `("File", "f")`.
`render_hotkey_text()` produces Rich Text with underline styling on
the hotkey character.

**`MenuBar(Widget, TVViewMixin)`:**
- `OptionFlag.PRE_PROCESS` — intercepts F10 and Alt+hotkey in the
  pre-process phase of three-phase dispatch
- `tv_handle_key()` handles activation (F10 toggle), arrow navigation,
  Enter/Down to open dropdown, Escape to close, Alt+letter for hotkeys
- Renders items horizontally with hotkey highlighting via `render_line()`
- Opens `MenuBox` as a child of the Screen (positioned absolutely)
- `MenuBar.build(*items)` class method for ergonomic construction

**`MenuBox(Widget)`:**
- Renders vertical dropdown with single-line box-drawing border
- Up/Down navigate (skipping separators and disabled items), Enter
  selects, Escape closes, Right opens sub-menus, single-letter hotkeys
- Sub-menu items show `►` indicator; opening mounts a nested MenuBox
- Posts `CommandMessage(item.command)` and `ItemSelected` on selection
- `get_content_width`/`get_content_height` auto-size to fit items

**Menu box mounting:** MenuBox is mounted on the Screen, not inside the
MenuBar. This avoids layout conflicts — the dropdown floats over other
content using absolute positioning on the `menus` CSS layer.

### StatusLine

TV's TStatusLine ported as a context-sensitive status bar.

**Data model:** `StatusItem(text, key_code, command)` — one entry.
`StatusDef(min_help_ctx, max_help_ctx, items)` — defines which items
are shown for a range of help context values.

**`StatusLine(Widget, TVViewMixin)`:**
- `OptionFlag.POST_PROCESS` — catches unhandled keys in the post-process
  phase
- `tv_handle_key()` checks if the pressed key matches any current item's
  `key_code`; if so, posts `CommandMessage(item.command)`
- `update(help_ctx)` switches to the matching StatusDef's items
- `hint(help_ctx)` virtual method for context-sensitive hint text
- Renders items horizontally with hotkey highlighting via `render_line()`
- Docked to the bottom (`dock: bottom; height: 1`)

### Application

TV's TProgram/TApplication ported as `Program(App)`.

**`Program(App)`:**
- `compose()` yields MenuBar (top) + DeskTop (middle) + StatusLine (bottom)
- Factory methods `init_menu_bar()`, `init_status_line()`,
  `init_desktop()` — subclasses override to customize
- `on_key()` implements application-level dispatch: MenuBar pre-process
  first, then StatusLine post-process (the focused widget phase is
  Textual's normal key routing between the two)
- `on_command_message()` handles `Command.QUIT` by calling `self.exit()`
- `insert_window(window)` delegates to `self.desktop.insert_window()`
- `execute_dialog(dialog)` wraps the Dialog in a `ModalScreen` and
  uses `push_screen_wait()` to await the result

**Application-level dispatch vs Group-level dispatch:** The Program's
`on_key()` provides the top-level three-phase dispatch (MenuBar as
pre-process, StatusLine as post-process). This is separate from Group's
`_on_key()` which provides per-container three-phase dispatch. Both
operate on the same event: Program's handler fires first (during
Textual's bubble phase), and if it consumes the event, Group never
sees it.

**`Application(Program)`:** Convenience subclass matching TV's class
hierarchy. Currently identical to Program.

### Dialog

TV's TDialog ported as `Dialog(Window)`.

- Default flags: `WindowFlag.MOVE | WindowFlag.CLOSE` (no zoom/grow)
- `on_command_message()` handles OK, Cancel, Yes, No, Close commands
  by calling `end_modal()`
- `end_modal(command)` checks `valid(command)` — if validation fails,
  the dialog stays open. Otherwise posts `DialogClosed` message and
  closes.
- `valid(command)` virtual hook for subclass validation logic
- `tv_handle_key()` maps Escape to `end_modal(Command.CANCEL)`
- `DialogClosed(CommandMessage)` message carries the result command

**Modal execution:** `Program.execute_dialog(dialog)` wraps the Dialog
widget in a `ModalScreen`, mounts the dialog inside it, and awaits
`push_screen_wait()`. When the dialog posts `DialogClosed`, the
ModalScreen intercepts it and calls `self.dismiss(result)`, which
resolves the awaited future.

### Shadow (Not Yet Implemented)

TV's 1-character drop shadow on windows. Textual has no built-in shadow.
This will be a custom visual effect, likely rendered by Window as extra
characters on the right and bottom edges outside the frame border.

## Class Hierarchy

```
Widget (Textual)
  +-- TVViewMixin               # adds tv_state, tv_options, tv_handle_key
  |
  +-- Group (Widget, TVViewMixin)     # three-phase dispatch, focus scoping
  |     +-- Window (Group)            # Frame + content, drag/resize/zoom
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
  +-- StatusLine (Widget, TVViewMixin)# context-sensitive status bar, POST_PROCESS
```

## Message Flow

```
Frame click on [■]
  --> Frame.post_message(CommandMessage(CLOSE))
  --> bubbles to Window
  --> Window.on_command_message() calls self.close()

Frame drag on title bar
  --> Frame captures mouse
  --> Frame.post_message(DragMove(delta_x, delta_y))
  --> bubbles to Window
  --> Window.on_frame_drag_move() updates styles.offset

Key press (application level)
  --> Program.on_key()
  --> MenuBar.tv_handle_key() checks F10, Alt+hotkeys
  --> If not handled: normal Textual key routing to focused widget
  --> StatusLine.tv_handle_key() checks unbound hotkeys
  --> If handled: event.stop() + event.prevent_default()

Key press (Group level, when Group has Textual focus)
  --> Group._on_key()
  --> Phase 1: PreProcess children
  --> Phase 2: current child's tv_handle_key()
  --> Phase 3: PostProcess children
  --> If handled: event.stop() + event.prevent_default()

Menu selection
  --> MenuBar activates (F10 or Alt+hotkey)
  --> Arrow keys navigate, Enter/Down opens MenuBox
  --> MenuBox item selected
  --> MenuBox.post_message(CommandMessage(item.command))
  --> Bubbles to application

Dialog modal flow
  --> Program.execute_dialog(dialog)
  --> Wraps dialog in ModalScreen, pushes screen
  --> User interacts, dialog calls end_modal(OK/CANCEL)
  --> Dialog posts DialogClosed, ModalScreen intercepts
  --> ModalScreen.dismiss(result) resolves the awaited future

Group.broadcast(command)
  --> Creates BroadcastMessage (bubble=False)
  --> Posts to every child via post_message()
```

## Rendering

All `render_line()` implementations use Rich `Text` objects to build
styled content, then pass the generator from `text.render(console)` to
`Strip()`. The generator yields `rich.segment.Segment` tuples which
Strip expects — wrapping it in a list (e.g., `Strip([text.render(...)])`)
is incorrect and causes unpacking errors at compositing time.

## Open Questions

1. **Frame vs content mouse event routing.** Frame covers the full Window
   area; content Container sits inside with margin:1. Clicks in the
   interior should reach content, not Frame. Textual routes mouse events
   to the most specific widget at (x,y), so content Container (smaller,
   overlapping interior) should receive interior clicks while Frame
   receives border clicks. This needs validation with a running app.

2. **Shadow rendering.** How to render the 1-char shadow outside the
   Window's own bounds. Options: Window requests extra space; use a
   sibling shadow widget; use CSS outline.

3. **Nested Group focus and Textual's focus_next.** If multiple Groups
   have `can_focus = True`, Textual's screen-level focus cycling will
   visit each Group. TV expects only one Group to be active at a time
   (the modal one, or the focused window). This needs focus trapping
   or coordination at the Program/Screen level.

4. **Async broadcast.** `Group.broadcast()` uses `post_message()`, which
   is async (messages are queued). TV's broadcast is synchronous (the
   Group iterates children in the same call frame). If ordering or
   synchronous completion matters, broadcast may need to call handlers
   directly instead of posting.
