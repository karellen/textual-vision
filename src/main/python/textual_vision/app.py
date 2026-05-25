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

from __future__ import annotations

from typing import Any

from textual import events
from textual.app import App, ComposeResult
from textual.screen import ModalScreen

from textual_vision.constants import Command
from textual_vision.desktop import DeskTop
from textual_vision.events import CommandMessage
from textual_vision.menus import Menu, MenuBar
from textual_vision.status_line import StatusDef, StatusLine
from textual_vision.themes import register_themes
from textual_vision.window import Window


class Program(App):
    """TV-style application composing MenuBar + DeskTop + StatusLine.

    Implements application-level three-phase dispatch:
    MenuBar (pre-process) -> focused widget -> StatusLine (post-process).

    Subclasses override init_menu_bar(), init_status_line(), and
    init_desktop() to customize the application's structure.
    """

    DEFAULT_CSS = """
    Program {
        layers: background windows menus;
    }
    """

    def __init__(self, theme: str = "turbo-pascal", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        register_themes(self)
        self.theme = theme
        self._menu_bar: MenuBar | None = None
        self._desktop: DeskTop | None = None
        self._status_line: StatusLine | None = None

    @property
    def menu_bar(self) -> MenuBar | None:
        return self._menu_bar

    @property
    def desktop(self) -> DeskTop | None:
        return self._desktop

    @property
    def status_line(self) -> StatusLine | None:
        return self._status_line

    def init_menu_bar(self) -> Menu | None:
        """Factory method for the menu bar's menu structure. Override in subclasses."""
        return None

    def init_status_line(self) -> list[StatusDef] | None:
        """Factory method for status line definitions. Override in subclasses."""
        return None

    def init_desktop(self) -> DeskTop:
        """Factory method for the desktop. Override to customize."""
        return DeskTop()

    def compose(self) -> ComposeResult:
        menu = self.init_menu_bar()
        if menu is not None:
            self._menu_bar = MenuBar(menu=menu)
            yield self._menu_bar

        self._desktop = self.init_desktop()
        yield self._desktop

        status_defs = self.init_status_line()
        if status_defs is not None:
            self._status_line = StatusLine(defs=status_defs)
            yield self._status_line

    async def on_key(self, event: events.Key) -> None:
        """Application-level three-phase dispatch.

        Phase 1: MenuBar (PRE_PROCESS) intercepts menu hotkeys
        Phase 2: Normal Textual key routing to focused widget
        Phase 3: StatusLine (POST_PROCESS) catches unbound hotkeys
        """
        if self._menu_bar is not None:
            if self._menu_bar.tv_handle_key(event):
                event.stop()
                event.prevent_default()
                return

        if self._status_line is not None:
            if self._status_line.tv_handle_key(event):
                event.stop()
                event.prevent_default()
                return

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Dismiss active menu when clicking outside menu widgets."""
        if self._menu_bar is not None and self._menu_bar.active:
            from textual_vision.menus import MenuBox
            widget = self.screen.get_widget_at(event.screen_x, event.screen_y)[0]
            if not isinstance(widget, (MenuBar, MenuBox)):
                self._menu_bar.deactivate()

    def on_menu_box_item_selected(self, message) -> None:
        """Dismiss menu bar when a dropdown item is selected."""
        if self._menu_bar is not None and self._menu_bar.active:
            self._menu_bar.deactivate()

    def on_menu_box_closed(self, message) -> None:
        """Dismiss menu bar when dropdown is closed via Escape."""
        if self._menu_bar is not None and self._menu_bar.active:
            self._menu_bar.deactivate()

    def on_command_message(self, message: CommandMessage) -> None:
        if message.command == Command.QUIT:
            self.exit()
            message.stop()

    def insert_window(self, window: Window) -> None:
        """Add a window to the desktop."""
        if self._desktop is not None:
            self._desktop.insert_window(window)

    async def execute_dialog(self, dialog: Any) -> Command:
        """Push a dialog wrapped in a ModalScreen and return its result.

        The dialog posts DialogClosed when done; the wrapper screen
        intercepts it and dismisses with the result command.
        """
        from textual_vision.dialogs import Dialog

        class _DialogScreen(ModalScreen[Command]):
            def compose(self) -> ComposeResult:
                yield dialog

            def on_dialog_dialog_closed(self, message: Dialog.DialogClosed) -> None:
                self.dismiss(message.result)

        return await self.push_screen_wait(_DialogScreen())

    def idle(self) -> None:
        """Virtual hook called when the event queue is empty. Override in subclasses."""
        pass


class Application(Program):
    """Top-level application class.

    Convenience subclass matching TV's TApplication = TProgram hierarchy.
    Identical to Program initially; exists for API compatibility.
    """
    pass
