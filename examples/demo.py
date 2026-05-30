#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   Copyright 2026 Karellen, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

"""Textual Vision demo application.

A minimal Turbo Vision-style application with menus, a status bar,
and windows on a desktop. Demonstrates the core architecture:
MenuBar (pre-process) + DeskTop + StatusLine (post-process).

Usage:
    python examples/demo.py

Keys:
    F10         Activate/deactivate menu bar
    Alt+F/E/W/H Open menu by hotkey
    F1          About dialog (via status bar)
    Alt+X       Quit
    Ctrl+N      New window
"""

from textual.containers import Horizontal, Vertical
from textual.widgets import Static

from textual_vision.app import Application
from textual_vision.button import Button
from textual_vision.cluster import CheckBoxes, RadioButtons
from textual_vision.combo_box import ComboBox
from textual_vision.constants import Command, OptionFlag
from textual_vision.dialogs import Dialog
from textual_vision.events import CommandMessage
from textual_vision.input_line import InputLine
from textual_vision.label import Label
from textual_vision.list_box import ListBox
from textual_vision.menus import Menu, MenuItem, Separator, SubMenu
from textual_vision.scroll_bar import ScrollBar
from textual_vision.status_line import StatusDef, StatusItem
from textual_vision.window import Window


class DemoWindow(Window):
    """A demo window that displays some text."""

    def __init__(self, title="", number=0, **kwargs):
        super().__init__(title=title, **kwargs)
        self.number = number
        self._body = Static(
            f"This is window #{number}.\n\n"
            f"Drag the title bar to move.\n"
            f"Drag bottom-right corner to resize.\n"
            f"Use frame icons to close/zoom."
        )

    def on_mount(self):
        super().on_mount()
        content = self.query_one(".tv-window-content")
        content.mount(self._body)


class ScrollBarWindow(Window):
    """A window demonstrating vertical and horizontal scroll bars.

    Scrollbars overlay the frame borders, matching TV's convention where
    the right border becomes the vertical scrollbar and the bottom border
    becomes the horizontal scrollbar.
    """

    TOTAL_LINES = 50
    TOTAL_COLS = 120

    DEFAULT_CSS = """
    ScrollBarWindow .scroll-viewport {
        width: 1fr;
        height: 1fr;
        overflow: hidden;
    }
    ScrollBarWindow .vscrollbar {
        width: 1;
        dock: right;
        margin: 1 0 0 0;
        layer: content;
    }
    ScrollBarWindow .hscrollbar {
        height: 1;
        dock: bottom;
        margin: 0 1 0 0;
        layer: content;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._lines = [f"Line {i:3d}: {'·' * 100} end" for i in range(1, self.TOTAL_LINES + 1)]
        self._scroll_y = 0
        self._scroll_x = 0
        self._viewport: Static | None = None
        self._vbar: ScrollBar | None = None
        self._hbar: ScrollBar | None = None

    def on_mount(self):
        super().on_mount()
        content = self.query_one(".tv-window-content")

        self._viewport = Static("", classes="scroll-viewport")
        content.mount(self._viewport)

        self._vbar = ScrollBar(min_val=0, max_val=self.TOTAL_LINES - 1,
                               page_step=10, arrow_step=1,
                               horizontal=False, corner_char="┘",
                               classes="vscrollbar")
        self._hbar = ScrollBar(min_val=0, max_val=self.TOTAL_COLS - 1,
                               page_step=20, arrow_step=1,
                               horizontal=True,
                               left_chars="└─", corner_char="─",
                               classes="hscrollbar")
        self.mount(self._vbar)
        self.mount(self._hbar)
        self._update_viewport()

    def _update_viewport(self):
        if not self._viewport:
            return
        visible_h = max(1, self._viewport.size.height or 15)
        visible_w = max(1, self._viewport.size.width or 40)
        start = self._scroll_y
        visible = self._lines[start:start + visible_h]
        clipped = [line[self._scroll_x:self._scroll_x + visible_w] for line in visible]
        self._viewport.update("\n".join(clipped))

    def on_scroll_bar_changed(self, message: ScrollBar.Changed):
        if self._vbar:
            self._scroll_y = self._vbar.value
        if self._hbar:
            self._scroll_x = self._hbar.value
        self._update_viewport()
        message.stop()

    def on_resize(self, event):
        self._update_viewport()


CMD_SCROLLBAR_DEMO = Command.USER
CMD_LISTBOX_DEMO = Command.USER + 1
CMD_THEME_TP = Command.USER + 10
CMD_THEME_TC = Command.USER + 11
CMD_THEME_TC_1X = Command.USER + 12
CMD_THEME_TC_TURQUOISE = Command.USER + 13


class ListBoxWindow(Window):
    """A window demonstrating a ListBox with a vertical scrollbar."""

    DEFAULT_CSS = """
    ListBoxWindow .list-area {
        width: 1fr;
        height: 1fr;
    }
    ListBoxWindow .vscrollbar {
        width: 1;
        dock: right;
        margin: 1 0 0 0;
        layer: content;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._listbox: ListBox | None = None
        self._vbar: ScrollBar | None = None

    def on_mount(self):
        super().on_mount()
        content = self.query_one(".tv-window-content")

        items = [f"Item {i:3d} — Sample list entry" for i in range(1, 101)]

        self._vbar = ScrollBar(min_val=0, max_val=len(items) - 1,
                               page_step=10, arrow_step=1,
                               horizontal=False, corner_char="┘",
                               classes="vscrollbar")
        self._listbox = ListBox(items=items, v_scroll_bar=self._vbar,
                                classes="list-area")

        content.mount(self._listbox)
        self.mount(self._vbar)

    def on_scroll_bar_changed(self, message: ScrollBar.Changed):
        message.stop()

    def on_list_viewer_item_selected(self, message):
        if self._listbox is not None:
            selected_text = self._listbox.get_text(message.index)
            self.title = f"List Box Demo — {selected_text}"
        message.stop()


class DemoApp(Application):
    CSS = """
    Screen {
        layers: background windows menus;
    }
    """

    BINDINGS = [
        ("ctrl+n", "new_window", "New Window"),
        ("alt+x", "quit", "Quit"),
    ]

    _window_counter = 0

    def action_new_window(self):
        self._new_window()

    def action_quit(self):
        self.exit()

    def init_menu_bar(self):
        return Menu(items=[
            SubMenu(
                "~F~ile",
                MenuItem("~N~ew", Command.NEW, key_code="Ctrl+N"),
                MenuItem("~O~pen...", Command.OPEN, key_code="Ctrl+O"),
                MenuItem("~S~ave", Command.SAVE, key_code="Ctrl+S"),
                MenuItem("S~a~ve as...", Command.SAVE_AS),
                Separator(),
                MenuItem("E~x~it", Command.QUIT, key_code="Alt+X"),
            ),
            SubMenu(
                "~E~dit",
                MenuItem("~U~ndo", Command.UNDO, key_code="Ctrl+Z"),
                MenuItem("~R~edo", Command.REDO),
                Separator(),
                MenuItem("Cu~t~", Command.CUT, key_code="Ctrl+X"),
                MenuItem("~C~opy", Command.COPY, key_code="Ctrl+C"),
                MenuItem("~P~aste", Command.PASTE, key_code="Ctrl+V"),
            ),
            SubMenu(
                "~W~indow",
                MenuItem("~S~croll bar demo", CMD_SCROLLBAR_DEMO),
                MenuItem("~L~ist box demo", CMD_LISTBOX_DEMO),
                Separator(),
                MenuItem("~T~ile", Command.TILE),
                MenuItem("C~a~scade", Command.CASCADE),
                MenuItem("Close ~a~ll", Command.CLOSE_ALL),
            ),
            SubMenu(
                "~S~ettings",
                MenuItem("Turbo ~P~ascal", CMD_THEME_TP),
                MenuItem("Turbo ~C~", CMD_THEME_TC),
                MenuItem("Turbo C ~1~.x", CMD_THEME_TC_1X),
                MenuItem("Turbo C T~u~rquoise", CMD_THEME_TC_TURQUOISE),
            ),
            SubMenu(
                "~H~elp",
                MenuItem("~A~bout...", Command.HELP),
            ),
        ])

    def init_status_line(self):
        return [
            StatusDef(0, 0xFFFF, [
                StatusItem("~F1~ Help", "f1", Command.HELP),
                StatusItem("~F10~ Menu", "f10", Command.MENU),
                StatusItem("~Alt+X~ Exit", "alt+x", Command.QUIT),
            ]),
        ]

    def on_command_message(self, message: CommandMessage) -> None:
        if message.command == Command.NEW:
            self._new_window()
            message.stop()
        elif message.command == Command.HELP:
            self._show_about()
            message.stop()
        elif message.command == Command.TILE:
            if self.desktop:
                self.desktop.tile()
            message.stop()
        elif message.command == Command.CASCADE:
            if self.desktop:
                self.desktop.cascade()
            message.stop()
        elif message.command == CMD_SCROLLBAR_DEMO:
            self._show_scrollbar_demo()
            message.stop()
        elif message.command == CMD_LISTBOX_DEMO:
            self._show_listbox_demo()
            message.stop()
        elif message.command == CMD_THEME_TP:
            self.theme = "turbo-pascal"
            message.stop()
        elif message.command == CMD_THEME_TC:
            self.theme = "turbo-c"
            message.stop()
        elif message.command == CMD_THEME_TC_1X:
            self.theme = "turbo-c-1x"
            message.stop()
        elif message.command == CMD_THEME_TC_TURQUOISE:
            self.theme = "turbo-c-turquoise"
            message.stop()
        elif message.command == Command.CLOSE_ALL:
            self._close_all_windows()
            message.stop()
        else:
            super().on_command_message(message)

    def _new_window(self):
        self._window_counter += 1
        n = self._window_counter
        win = DemoWindow(title=f"Window {n}", number=n)
        win.tv_options |= OptionFlag.TILEABLE
        step_x = max(2, self.size.width // 30)
        step_y = max(1, self.size.height // 15)
        win.styles.offset = (step_x * ((n - 1) % 10), step_y * ((n - 1) % 8))
        self.insert_window(win)

    def _show_about(self):
        if self.desktop and self.desktop.query("Dialog"):
            return
        dlg = ControlsDialog(title="Controls Demo")
        dlg.styles.width = "60%"
        dlg.styles.height = "70%"
        cx = max(0, (self.size.width - self.size.width * 60 // 100) // 2)
        cy = max(0, (self.size.height - self.size.height * 70 // 100) // 2)
        dlg.styles.offset = (cx, cy)
        self.insert_window(dlg)

    def _show_scrollbar_demo(self):
        win = ScrollBarWindow(title="Scroll Bar Demo")
        win.styles.width = "60%"
        win.styles.height = "50%"
        cx = max(0, (self.size.width - self.size.width * 60 // 100) // 2)
        cy = max(0, (self.size.height - self.size.height * 50 // 100) // 2)
        win.styles.offset = (cx, cy)
        self.insert_window(win)

    def _show_listbox_demo(self):
        win = ListBoxWindow(title="List Box Demo")
        win.styles.width = "40%"
        win.styles.height = "50%"
        cx = max(0, (self.size.width - self.size.width * 40 // 100) // 2)
        cy = max(0, (self.size.height - self.size.height * 50 // 100) // 2)
        win.styles.offset = (cx, cy)
        self.insert_window(win)

    def _close_all_windows(self):
        if self.desktop:
            for win in list(self.desktop.query(Window)):
                win.close()


class ControlsDialog(Dialog):
    """Dialog showcasing TV-style form controls."""

    DEFAULT_CSS = """
    ControlsDialog {
        width: 60%;
        height: 70%;
        background: $surface;
    }
    ControlsDialog .tv-window-content {
        padding: 1;
    }
    ControlsDialog .form-row {
        height: auto;
        width: 1fr;
        margin-bottom: 1;
    }
    ControlsDialog .form-row > Label {
        width: 12;
    }
    ControlsDialog .form-row > InputLine {
        width: 1fr;
    }
    ControlsDialog .form-row > ComboBox {
        width: 1fr;
    }
    ControlsDialog .groups-row {
        height: auto;
        width: 1fr;
        margin-bottom: 1;
    }
    ControlsDialog .group-box {
        width: 1fr;
        height: auto;
        padding: 0 1;
    }
    ControlsDialog .button-row {
        height: auto;
        width: 1fr;
        align-horizontal: center;
    }
    ControlsDialog .button-row > Button {
        margin: 0 1;
    }
    """

    def on_mount(self):
        super().on_mount()
        content = self.query_one(".tv-window-content")

        name_input = InputLine(max_len=40)
        name_label = Label("~N~ame", link=name_input)

        pass_input = InputLine(max_len=20, password=True)
        pass_label = Label("~P~assword", link=pass_input)

        color_combo = ComboBox(items=[
            "Black", "Blue", "Green", "Cyan",
            "Red", "Magenta", "Brown", "Light Gray",
        ])
        color_label = Label("~C~olor", link=color_combo)

        size_combo = ComboBox(items=[
            "Small", "Medium", "Large", "Extra Large",
        ], editable=False)
        size_label = Label("~S~ize", link=size_combo)

        options = CheckBoxes([
            "~C~ase sensitive",
            "~W~hole words only",
            "~R~egular expression",
        ])

        direction = RadioButtons([
            "~F~orward",
            "~B~ackward",
        ])

        ok_btn = Button("~O~K", command=Command.OK, is_default=True)
        cancel_btn = Button("~C~ancel", command=Command.CANCEL)

        name_row = Horizontal(name_label, name_input, classes="form-row")
        pass_row = Horizontal(pass_label, pass_input, classes="form-row")
        color_row = Horizontal(color_label, color_combo, classes="form-row")
        size_row = Horizontal(size_label, size_combo, classes="form-row")
        options_label = Label("Options", link=options)
        direction_label = Label("Direction", link=direction)

        groups = Horizontal(
            Vertical(options_label, options, classes="group-box"),
            Vertical(direction_label, direction, classes="group-box"),
            classes="groups-row",
        )
        buttons = Horizontal(ok_btn, cancel_btn, classes="button-row")

        content.mount(name_row)
        content.mount(pass_row)
        content.mount(color_row)
        content.mount(size_row)
        content.mount(groups)
        content.mount(buttons)


if __name__ == "__main__":
    app = DemoApp()
    app.run()
