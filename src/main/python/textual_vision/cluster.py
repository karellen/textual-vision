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

import math
from typing import Any

from rich.text import Text

from textual import events
from textual.reactive import reactive
from textual.strip import Strip
from textual.widget import Widget

from textual_vision.constants import Command, OptionFlag, StateFlag
from textual_vision.events import CommandMessage
from textual_vision.group import TVViewMixin
from textual_vision.menus import parse_hotkey_text, render_tilde_text


class Cluster(Widget, TVViewMixin):
    """Abstract base for grouped toggle controls (checkboxes, radio buttons).

    TV's TCluster: manages N items with tilde-hotkey labels, arranged in
    columns. Selection is tracked as a bitmask. Subclasses define the
    marker glyph and toggle behavior.
    """

    COMPONENT_CLASSES = {
        "cluster--item",
        "cluster--item-focused",
        "cluster--hotkey",
        "cluster--mark",
    }

    DEFAULT_CSS = """
    Cluster {
        height: auto;
        width: auto;
        background: $cluster-bg;
    }
    Cluster .cluster--item {
        color: $cluster-fg;
        background: $cluster-bg;
    }
    Cluster .cluster--item-focused {
        color: $cluster-focused-fg;
        background: $cluster-focused-bg;
    }
    Cluster .cluster--hotkey {
        color: $cluster-hotkey;
        background: $cluster-bg;
    }
    Cluster .cluster--mark {
        color: $cluster-fg;
        background: $cluster-bg;
    }
    """

    value: reactive[int] = reactive(0)
    sel: reactive[int] = reactive(0)

    def __init__(self, items: list[str], columns: int = 1, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._items = items
        self._columns = max(1, columns)
        self._parsed = [parse_hotkey_text(item) for item in items]
        self.tv_options = OptionFlag.SELECTABLE
        self.can_focus = True

    @property
    def items(self) -> list[str]:
        return self._items

    @property
    def columns(self) -> int:
        return self._columns

    @property
    def _rows(self) -> int:
        return math.ceil(len(self._items) / self._columns) if self._items else 0

    def _item_at(self, row: int, col: int) -> int | None:
        idx = col * self._rows + row
        if 0 <= idx < len(self._items):
            return idx
        return None

    def _item_row_col(self, idx: int) -> tuple[int, int]:
        rows = self._rows
        if rows == 0:
            return 0, 0
        return idx % rows, idx // rows

    def _col_width(self) -> int:
        if not self._parsed:
            return 0
        mark_len = len(self.mark(0))
        max_label = max(len(plain) for plain, _ in self._parsed)
        return mark_len + max_label + 2

    def mark(self, item_index: int) -> str:
        raise NotImplementedError

    def press(self, item_index: int) -> None:
        raise NotImplementedError

    def get_content_width(self, container, viewport) -> int:
        return self._col_width() * self._columns

    def get_content_height(self, container, viewport, width) -> int:
        return self._rows

    def render_line(self, y: int) -> Strip:
        width = self.size.width
        if y >= self._rows:
            return Strip.blank(width)

        tv_focused = bool(self.tv_state & StateFlag.FOCUSED)
        item_style = self.get_component_rich_style("cluster--item")
        focused_style = self.get_component_rich_style("cluster--item-focused")
        hotkey_style = self.get_component_rich_style("cluster--hotkey")
        mark_style = self.get_component_rich_style("cluster--mark")

        col_w = self._col_width()
        line = Text()

        for col in range(self._columns):
            idx = self._item_at(y, col)
            if idx is None:
                line.append(" " * col_w, style=item_style)
                continue

            is_focused = tv_focused and (idx == self.sel)
            base = focused_style if is_focused else item_style
            hk = focused_style if is_focused else hotkey_style
            mk = focused_style if is_focused else mark_style

            marker = self.mark(idx)
            line.append(marker, style=mk)
            label = render_tilde_text(self._items[idx], str(base), str(hk))
            line.append(label)

            cell_used = len(marker) + len(self._parsed[idx][0])
            pad = col_w - cell_used
            if pad > 0:
                line.append(" " * pad, style=base)

        remaining = width - len(line.plain)
        if remaining > 0:
            line.append(" " * remaining, style=item_style)

        return Strip(line.render(self.app.console))

    def tv_handle_key(self, event: events.Key) -> bool:
        if event.key == "space":
            if 0 <= self.sel < len(self._items):
                self.press(self.sel)
                self.post_message(Cluster.Changed(self.value))
            return True

        rows = self._rows
        if rows == 0:
            return False

        if event.key == "up":
            self._move_sel(-1)
            return True
        elif event.key == "down":
            self._move_sel(1)
            return True
        elif event.key == "left":
            self._move_sel(-rows)
            return True
        elif event.key == "right":
            self._move_sel(rows)
            return True

        if len(event.key) == 1:
            key_lower = event.key.lower()
            for i, (_, hotkey) in enumerate(self._parsed):
                if hotkey == key_lower:
                    self.sel = i
                    self.press(i)
                    self.post_message(Cluster.Changed(self.value))
                    return True

        return False

    def _move_sel(self, delta: int) -> None:
        n = len(self._items)
        if n == 0:
            return
        self.sel = (self.sel + delta) % n

    def on_mouse_down(self, event: events.MouseDown) -> None:
        if event.button != 1:
            return
        self.tv_select_self()
        col_w = self._col_width()
        if col_w == 0:
            return
        col = event.x // col_w
        row = event.y
        idx = self._item_at(row, col)
        if idx is not None:
            self.sel = idx
            self.press(idx)
            self.post_message(Cluster.Changed(self.value))
            event.stop()

    class Changed(CommandMessage):
        def __init__(self, value: int) -> None:
            super().__init__(Command.VALID)
            self.value = value


class CheckBoxes(Cluster):
    """Multi-select toggle group with [X]/[ ] markers."""

    def mark(self, item_index: int) -> str:
        checked = bool(self.value & (1 << item_index))
        return "[X] " if checked else "[ ] "

    def press(self, item_index: int) -> None:
        self.value ^= (1 << item_index)


class RadioButtons(Cluster):
    """Single-select toggle group with (•)/( ) markers."""

    def mark(self, item_index: int) -> str:
        selected = bool(self.value & (1 << item_index))
        return "(•) " if selected else "( ) "

    def press(self, item_index: int) -> None:
        self.value = 1 << item_index
