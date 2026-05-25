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
from textual_vision.constants import Command, OptionFlag
from textual_vision.dialogs import Dialog
from textual_vision.events import CommandMessage
from textual_vision.input_line import InputLine
from textual_vision.label import Label
from textual_vision.menus import Menu, MenuItem, Separator, SubMenu
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
                MenuItem("~T~ile", Command.TILE),
                MenuItem("C~a~scade", Command.CASCADE),
                MenuItem("Close ~a~ll", Command.CLOSE_ALL),
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
        groups = Horizontal(
            Vertical(Static("Options:"), options, classes="group-box"),
            Vertical(Static("Direction:"), direction, classes="group-box"),
            classes="groups-row",
        )
        buttons = Horizontal(ok_btn, cancel_btn, classes="button-row")

        content.mount(name_row)
        content.mount(pass_row)
        content.mount(groups)
        content.mount(buttons)


if __name__ == "__main__":
    app = DemoApp()
    app.run()
