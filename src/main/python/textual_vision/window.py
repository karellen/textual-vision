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
from textual.app import ComposeResult
from textual.containers import Container
from textual.geometry import Offset

from textual_vision.constants import (Command, OptionFlag, WindowFlag)
from textual_vision.events import CommandMessage
from textual_vision.frame import Frame
from textual_vision.group import Group


class Window(Group):
    """A movable, resizable, closable, zoomable window with TV-style chrome.

    Window is a Group that composes a Frame for border rendering and mouse
    interaction, plus a content container for child widgets.
    """

    DEFAULT_CSS = """
    Window {
        width: 50%;
        height: 60%;
        background: $background;
        layers: frame content;
    }
    Window > Frame {
        width: 1fr;
        height: 1fr;
        layer: frame;
    }
    Window > .tv-window-content {
        width: 1fr;
        height: 1fr;
        margin: 1;
        layer: content;
    }
    """

    def __init__(self, title: str = "",
                 flags: WindowFlag = WindowFlag.MOVE | WindowFlag.CLOSE | WindowFlag.ZOOM | WindowFlag.GROW,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._title = title
        self._window_flags = flags
        self._number: int = 0
        self._zoomed = False
        self._pre_zoom_offset: Offset | None = None
        self._pre_zoom_width: int | None = None
        self._pre_zoom_height: int | None = None
        self.tv_options |= OptionFlag.SELECTABLE

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value
        if self.frame is not None:
            self.frame.title = value

    @property
    def number(self) -> int:
        return self._number

    @number.setter
    def number(self, value: int) -> None:
        self._number = value

    @property
    def window_flags(self) -> WindowFlag:
        return self._window_flags

    @window_flags.setter
    def window_flags(self, value: WindowFlag) -> None:
        self._window_flags = value
        if self.frame is not None:
            self.frame.flags = value

    @property
    def zoomed(self) -> bool:
        return self._zoomed

    @property
    def frame(self) -> Frame | None:
        return self.query_one(Frame, Frame) if self.is_mounted else None

    @property
    def content(self) -> Container | None:
        return self.query_one(".tv-window-content", Container) if self.is_mounted else None

    def compose(self) -> ComposeResult:
        yield Frame(title=self._title, flags=self._window_flags, active=True)
        yield Container(classes="tv-window-content")

    def zoom(self) -> None:
        if self._zoomed:
            return
        self._pre_zoom_offset = Offset(
            self.styles.offset.x.value if self.styles.offset.x else 0,
            self.styles.offset.y.value if self.styles.offset.y else 0,
        )
        self._pre_zoom_width = str(self.styles.width) if self.styles.width else None
        self._pre_zoom_height = str(self.styles.height) if self.styles.height else None
        self.styles.offset = (0, 0)
        self.styles.width = "1fr"
        self.styles.height = "1fr"
        self._zoomed = True
        if self.frame is not None:
            self.frame.zoomed = True

    def unzoom(self) -> None:
        if not self._zoomed:
            return
        if self._pre_zoom_offset is not None:
            self.styles.offset = (self._pre_zoom_offset.x, self._pre_zoom_offset.y)
        if self._pre_zoom_width is not None:
            self.styles.width = self._pre_zoom_width
        if self._pre_zoom_height is not None:
            self.styles.height = self._pre_zoom_height
        self._zoomed = False
        if self.frame is not None:
            self.frame.zoomed = False

    def toggle_zoom(self) -> None:
        if self._zoomed:
            self.unzoom()
        else:
            self.zoom()

    def close(self) -> None:
        from textual_vision.desktop import DeskTop
        parent = self.parent
        if isinstance(parent, DeskTop):
            parent.remove_window(self)
        else:
            self.remove()

    def _raise_self(self) -> None:
        from textual_vision.desktop import DeskTop
        parent = self.parent
        if isinstance(parent, DeskTop):
            parent.raise_window(self)

    def on_mouse_down(self, event: events.MouseDown) -> None:
        self._raise_self()

    def on_frame_selected(self, message: Frame.Selected) -> None:
        self._raise_self()
        message.stop()

    def on_command_message(self, message: CommandMessage) -> None:
        if message.command == Command.CLOSE:
            self.close()
            message.stop()
        elif message.command == Command.ZOOM:
            self.toggle_zoom()
            message.stop()

    def on_frame_drag_move(self, message: Frame.DragMove) -> None:
        if WindowFlag.MOVE not in self._window_flags:
            return
        x = (self.styles.offset.x.value if self.styles.offset.x else 0) + message.delta_x
        y = (self.styles.offset.y.value if self.styles.offset.y else 0) + message.delta_y
        self.styles.offset = (int(x), int(y))
        self.screen.refresh()
        message.stop()

    def on_frame_resize_move(self, message: Frame.ResizeMove) -> None:
        if WindowFlag.GROW not in self._window_flags:
            return
        w = self.size.width + message.delta_x
        h = self.size.height + message.delta_y
        self.styles.width = max(10, int(w))
        self.styles.height = max(5, int(h))
        self.screen.refresh()
        message.stop()
