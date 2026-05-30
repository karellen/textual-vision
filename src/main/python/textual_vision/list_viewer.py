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

from rich.text import Text

from textual import events
from textual.reactive import reactive
from textual.strip import Strip
from textual.widget import Widget

from textual_vision.constants import Command, OptionFlag
from textual_vision.events import CommandMessage
from textual_vision.group import TVViewMixin
from textual_vision.scroll_bar import ScrollBar


class ListViewer(Widget, TVViewMixin):
    """Abstract scrollable list display.

    Port of TV's TListViewer. Renders items in a scrollable list with
    keyboard/mouse navigation, focus tracking, and optional scrollbar
    integration. Subclasses must implement get_text().
    """

    COMPONENT_CLASSES = {
        "list-viewer--normal",
        "list-viewer--focused",
        "list-viewer--divider",
    }

    DEFAULT_CSS = """
    ListViewer {
        width: 1fr;
        height: 1fr;
        background: $surface;
    }
    ListViewer .list-viewer--normal {
        color: $text;
        background: $surface;
    }
    ListViewer .list-viewer--focused {
        color: $surface;
        background: $accent;
    }
    ListViewer .list-viewer--divider {
        color: $text;
    }
    """

    focused: reactive[int] = reactive(0)

    def __init__(self, num_cols: int = 1,
                 v_scroll_bar: ScrollBar | None = None,
                 h_scroll_bar: ScrollBar | None = None,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._num_cols = num_cols
        self._v_scroll_bar = None
        self._h_scroll_bar = None
        self._top_item = 0
        self._range = 0
        self.tv_options = OptionFlag.SELECTABLE
        if v_scroll_bar is not None:
            self.v_scroll_bar = v_scroll_bar
        if h_scroll_bar is not None:
            self.h_scroll_bar = h_scroll_bar

    @property
    def range(self) -> int:
        return self._range

    @property
    def top_item(self) -> int:
        return self._top_item

    @property
    def num_cols(self) -> int:
        return self._num_cols

    @property
    def v_scroll_bar(self) -> ScrollBar | None:
        return self._v_scroll_bar

    @v_scroll_bar.setter
    def v_scroll_bar(self, sb: ScrollBar | None) -> None:
        old = self._v_scroll_bar
        if old is not None:
            old.scroll_target = None
        self._v_scroll_bar = sb
        if sb is not None:
            sb.scroll_target = self
        self._update_scrollbars()

    @property
    def h_scroll_bar(self) -> ScrollBar | None:
        return self._h_scroll_bar

    @h_scroll_bar.setter
    def h_scroll_bar(self, sb: ScrollBar | None) -> None:
        self._h_scroll_bar = sb

    def get_text(self, item: int) -> str:
        raise NotImplementedError

    def is_selected(self, item: int) -> bool:
        return item == self.focused

    def set_range(self, count: int) -> None:
        self._range = count
        if count <= 0:
            self.focused = 0
            self._top_item = 0
        elif self.focused >= count:
            self.focused = count - 1
        self._update_scrollbars()
        self.refresh()

    def focus_item(self, item: int) -> None:
        if self._range <= 0:
            return
        item = max(0, min(item, self._range - 1))
        self.focused = item
        self._scroll_to_focused()
        self._sync_v_scrollbar()
        self.refresh()

    def select_item(self, item: int) -> None:
        self.focus_item(item)
        self.post_message(ListViewer.ItemSelected(item))

    def _page_size(self) -> int:
        return max(1, self.size.height)

    def _scroll_to_focused(self) -> None:
        page = self._page_size()
        if self.focused < self._top_item:
            self._top_item = self.focused
        elif self.focused >= self._top_item + page:
            self._top_item = self.focused - page + 1
        max_top = max(0, self._range - page)
        if self._top_item > max_top:
            self._top_item = max_top

    def _update_scrollbars(self) -> None:
        page = self._page_size()
        if self._v_scroll_bar is not None:
            max_val = max(0, self._range - 1)
            self._v_scroll_bar.set_params(0, max_val, page_step=page, arrow_step=1)

    def _sync_v_scrollbar(self) -> None:
        if self._v_scroll_bar is not None:
            if self._v_scroll_bar.value != self.focused:
                self._v_scroll_bar.set_value(self.focused)

    def scroll_to_value(self, value: int) -> None:
        if self.focused != value:
            self.focus_item(value)

    def render_line(self, y: int) -> Strip:
        width = self.size.width
        normal_style = self.get_component_rich_style("list-viewer--normal")
        focused_style = self.get_component_rich_style("list-viewer--focused")

        line = Text()

        if self._num_cols == 1:
            item_idx = self._top_item + y
            if 0 <= item_idx < self._range:
                text = self.get_text(item_idx)
                style = focused_style if item_idx == self.focused else normal_style
                if len(text) > width:
                    text = text[:width]
                else:
                    text += " " * (width - len(text))
                line.append(text, style=style)
            else:
                line.append(" " * width, style=normal_style)
        else:
            col_width = max(1, width // self._num_cols)
            page = self._page_size()
            divider_style = self.get_component_rich_style("list-viewer--divider")
            for col in range(self._num_cols):
                col_item = col * page + y + self._top_item
                avail = col_width
                if col > 0:
                    line.append("│", style=divider_style)
                    avail = max(0, avail - 1)

                if 0 <= col_item < self._range:
                    text = self.get_text(col_item)
                    style = focused_style if col_item == self.focused else normal_style
                    if len(text) > avail:
                        text = text[:avail]
                    else:
                        text += " " * (avail - len(text))
                    line.append(text, style=style)
                else:
                    line.append(" " * avail, style=normal_style)

            remaining = width - len(line.plain)
            if remaining > 0:
                line.append(" " * remaining, style=normal_style)

        return Strip(line.render(self.app.console))

    def tv_handle_key(self, event: events.Key) -> bool:
        page = self._page_size()
        key = event.key

        if key == "up":
            self.focus_item(self.focused - 1)
            return True
        elif key == "down":
            self.focus_item(self.focused + 1)
            return True
        elif key == "left" and self._num_cols > 1:
            self.focus_item(self.focused - page)
            return True
        elif key == "right" and self._num_cols > 1:
            self.focus_item(self.focused + page)
            return True
        elif key == "pageup":
            self.focus_item(self.focused - page)
            return True
        elif key == "pagedown":
            self.focus_item(self.focused + page)
            return True
        elif key == "home":
            self.focus_item(0)
            return True
        elif key == "end":
            self.focus_item(self._range - 1)
            return True
        elif key in ("enter", "space"):
            if self._range > 0:
                self.select_item(self.focused)
            return True

        return False

    def on_mouse_down(self, event: events.MouseDown) -> None:
        if event.button != 1:
            return
        self.tv_select_self()
        item = self._top_item + event.y
        if 0 <= item < self._range:
            self.focus_item(item)
        event.stop()

    def on_resize(self, event: events.Resize) -> None:
        self._update_scrollbars()
        self._scroll_to_focused()

    class ItemSelected(CommandMessage):
        def __init__(self, index: int) -> None:
            super().__init__(Command.LIST_ITEM_SELECTED)
            self.index = index
