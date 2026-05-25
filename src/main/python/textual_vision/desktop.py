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

from textual.app import ComposeResult
from textual.geometry import Region
from textual.widget import Widget

from textual_vision.constants import OptionFlag
from textual_vision.group import Group, TVViewMixin
from textual_vision.window import Window


class Background(Widget):
    """Desktop background fill widget."""

    DEFAULT_CSS = """
    Background {
        width: 1fr;
        height: 1fr;
        background: $background;
    }
    """

    def __init__(self, pattern: str = "░", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._pattern = pattern

    @property
    def pattern(self) -> str:
        return self._pattern

    @pattern.setter
    def pattern(self, value: str) -> None:
        self._pattern = value
        self.refresh()

    def render(self) -> str:
        width = self.size.width
        height = self.size.height
        line = (self._pattern * width)[:width]
        return "\n".join(line for _ in range(height))


class DeskTop(Group):
    """Desktop container that manages windows with tile, cascade, and Z-order.

    Contains a Background as the bottommost child, plus Window children
    that can be arranged, raised, and managed.
    """

    DEFAULT_CSS = """
    DeskTop {
        width: 1fr;
        height: 1fr;
        layers: background;
    }
    DeskTop > Background {
        layer: background;
    }
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._window_layer_counter = 0
        self._z_order: list[Window] = []

    def compose(self) -> ComposeResult:
        yield Background()

    def _get_windows(self) -> list[Window]:
        return list(self.query(Window))

    def _get_tileable_windows(self) -> list[Window]:
        return [w for w in self._get_windows()
                if isinstance(w, TVViewMixin) and OptionFlag.TILEABLE in w.tv_options]

    def _rebuild_layers(self) -> None:
        """Rebuild the DeskTop's layers CSS from the Z-order list."""
        layer_names = ["background"] + [w.styles.layer for w in self._z_order]
        self.styles.layers = tuple(layer_names)

    def insert_window(self, window: Window) -> None:
        for w in self._get_windows():
            if w.frame is not None:
                w.frame.active = False
        self._window_layer_counter += 1
        window.styles.layer = f"win-{self._window_layer_counter}"
        self._z_order.append(window)
        self._rebuild_layers()
        self.mount(window)
        self.current = window

    def remove_window(self, window: Window) -> None:
        """Remove a window from the desktop, cleaning up Z-order and layers."""
        if window in self._z_order:
            self._z_order.remove(window)
            self._rebuild_layers()
        if self.current is window:
            self.current = self._z_order[-1] if self._z_order else None
        if window.is_mounted:
            window.remove()

    def tile(self, region: Region | None = None) -> None:
        """Arrange tileable windows in a grid within the given region."""
        windows = self._get_tileable_windows()
        if not windows:
            return

        if region is None:
            region = Region(0, 0, self.size.width, self.size.height)

        n = len(windows)
        cols = _grid_cols(n)
        rows = (n + cols - 1) // cols

        col_width = region.width // cols
        row_height = region.height // rows

        for i, win in enumerate(windows):
            row = i // cols
            col = i % cols
            x = region.x + col * col_width
            y = region.y + row * row_height

            w = col_width
            h = row_height
            if col == cols - 1:
                w = region.width - col * col_width
            if row == rows - 1 and i >= n - (n % cols or cols):
                h = region.height - row * row_height

            win.styles.offset = (x, y)
            win.styles.width = w
            win.styles.height = h

    def cascade(self, region: Region | None = None) -> None:
        """Arrange windows staggered with overlap, offset by (1,1)."""
        windows = self._get_windows()
        if not windows:
            return

        if region is None:
            region = Region(0, 0, self.size.width, self.size.height)

        cascade_width = max(10, region.width * 2 // 3)
        cascade_height = max(5, region.height * 2 // 3)

        max_offset_x = region.width - cascade_width
        max_offset_y = region.height - cascade_height

        for i, win in enumerate(windows):
            x = region.x + (i % (max_offset_x + 1)) if max_offset_x > 0 else region.x
            y = region.y + (i % (max_offset_y + 1)) if max_offset_y > 0 else region.y

            win.styles.offset = (x, y)
            win.styles.width = cascade_width
            win.styles.height = cascade_height

    def raise_window(self, window: Window) -> None:
        """Bring a window to the top of the Z-order and activate it."""
        for w in self._get_windows():
            if w.frame is not None:
                w.frame.active = (w is window)
        if window in self._z_order:
            self._z_order.remove(window)
            self._z_order.append(window)
            self._rebuild_layers()
        self.current = window


def _grid_cols(n: int) -> int:
    """Choose number of columns for a tile grid of n windows."""
    if n <= 2:
        return n
    if n <= 4:
        return 2
    if n <= 9:
        return 3
    return 4
