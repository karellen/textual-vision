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


class ScrollBar(Widget, TVViewMixin):
    """TV-style scrollbar with arrows, track, and draggable thumb.

    Can be vertical (width=1, height=N) or horizontal (width=N, height=1).
    Posts ScrollBar.Changed when the value changes via user interaction.
    """

    COMPONENT_CLASSES = {
        "scrollbar--arrow",
        "scrollbar--track",
        "scrollbar--thumb",
    }

    DEFAULT_CSS = """
    ScrollBar {
        background: $scrollbar-background;
    }
    ScrollBar .scrollbar--arrow {
        color: $scrollbar;
        background: $scrollbar-background;
    }
    ScrollBar .scrollbar--track {
        color: $scrollbar-background;
        background: $scrollbar-background;
    }
    ScrollBar .scrollbar--thumb {
        color: $scrollbar;
        background: $scrollbar-active;
    }
    """

    value: reactive[int] = reactive(0)

    def __init__(self, min_val: int = 0, max_val: int = 0,
                 page_step: int = 1, arrow_step: int = 1,
                 horizontal: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._min_val = min_val
        self._max_val = max_val
        self._page_step = page_step
        self._arrow_step = arrow_step
        self._horizontal = horizontal
        self._dragging = False
        self._drag_start_pos = 0
        self._drag_start_value = 0
        self.tv_options = OptionFlag.SELECTABLE

    @property
    def min_val(self) -> int:
        return self._min_val

    @property
    def max_val(self) -> int:
        return self._max_val

    @property
    def page_step(self) -> int:
        return self._page_step

    @property
    def arrow_step(self) -> int:
        return self._arrow_step

    @property
    def horizontal(self) -> bool:
        return self._horizontal

    @property
    def _track_len(self) -> int:
        total = self.size.width if self._horizontal else self.size.height
        return max(0, total - 2)

    @property
    def _thumb_size(self) -> int:
        track = self._track_len
        if track <= 0 or self._max_val <= self._min_val:
            return track
        range_val = self._max_val - self._min_val + self._page_step
        return max(1, track * self._page_step // range_val)

    @property
    def _thumb_pos(self) -> int:
        track = self._track_len
        thumb = self._thumb_size
        movable = track - thumb
        if movable <= 0 or self._max_val <= self._min_val:
            return 0
        return (self.value - self._min_val) * movable // (self._max_val - self._min_val)

    def set_params(self, min_val: int, max_val: int,
                   page_step: int = 1, arrow_step: int = 1) -> None:
        self._min_val = min_val
        self._max_val = max(min_val, max_val)
        self._page_step = max(1, page_step)
        self._arrow_step = max(1, arrow_step)
        self.set_value(self.value)

    def set_value(self, val: int) -> None:
        clamped = max(self._min_val, min(val, self._max_val))
        if clamped != self.value:
            self.value = clamped
            self.post_message(ScrollBar.Changed(clamped))

    def render_line(self, y: int) -> Strip:
        if self._horizontal:
            return self._render_horizontal(y)
        return self._render_vertical(y)

    def _render_vertical(self, y: int) -> Strip:
        width = self.size.width
        height = self.size.height
        arrow_style = self.get_component_rich_style("scrollbar--arrow")
        track_style = self.get_component_rich_style("scrollbar--track")
        thumb_style = self.get_component_rich_style("scrollbar--thumb")

        line = Text()

        if y == 0:
            line.append("▲", style=arrow_style)
        elif y == height - 1:
            line.append("▼", style=arrow_style)
        else:
            track_pos = y - 1
            tp = self._thumb_pos
            ts = self._thumb_size
            if tp <= track_pos < tp + ts:
                line.append("█", style=thumb_style)
            else:
                line.append("░", style=track_style)

        remaining = width - len(line.plain)
        if remaining > 0:
            line.append(" " * remaining, style=track_style)

        return Strip(line.render(self.app.console))

    def _render_horizontal(self, y: int) -> Strip:
        if y != 0:
            return Strip.blank(self.size.width)

        width = self.size.width
        arrow_style = self.get_component_rich_style("scrollbar--arrow")
        track_style = self.get_component_rich_style("scrollbar--track")
        thumb_style = self.get_component_rich_style("scrollbar--thumb")

        line = Text()
        line.append("◄", style=arrow_style)

        track = self._track_len
        tp = self._thumb_pos
        ts = self._thumb_size

        for i in range(track):
            if tp <= i < tp + ts:
                line.append("█", style=thumb_style)
            else:
                line.append("░", style=track_style)

        line.append("►", style=arrow_style)

        remaining = width - len(line.plain)
        if remaining > 0:
            line.append(" " * remaining, style=track_style)

        return Strip(line.render(self.app.console))

    def tv_handle_key(self, event: events.Key) -> bool:
        if self._horizontal:
            if event.key == "left":
                self.set_value(self.value - self._arrow_step)
                return True
            elif event.key == "right":
                self.set_value(self.value + self._arrow_step)
                return True
        else:
            if event.key == "up":
                self.set_value(self.value - self._arrow_step)
                return True
            elif event.key == "down":
                self.set_value(self.value + self._arrow_step)
                return True

        if event.key == "pageup":
            self.set_value(self.value - self._page_step)
            return True
        elif event.key == "pagedown":
            self.set_value(self.value + self._page_step)
            return True
        elif event.key == "home":
            self.set_value(self._min_val)
            return True
        elif event.key == "end":
            self.set_value(self._max_val)
            return True

        return False

    def on_mouse_down(self, event: events.MouseDown) -> None:
        if event.button != 1:
            return

        pos = event.x if self._horizontal else event.y
        total = self.size.width if self._horizontal else self.size.height

        if pos == 0:
            self.set_value(self.value - self._arrow_step)
        elif pos == total - 1:
            self.set_value(self.value + self._arrow_step)
        else:
            track_pos = pos - 1
            tp = self._thumb_pos
            ts = self._thumb_size
            if tp <= track_pos < tp + ts:
                self._dragging = True
                self._drag_start_pos = track_pos
                self._drag_start_value = self.value
                self.capture_mouse()
            elif track_pos < tp:
                self.set_value(self.value - self._page_step)
            else:
                self.set_value(self.value + self._page_step)

        event.stop()

    def on_mouse_move(self, event: events.MouseMove) -> None:
        if not self._dragging:
            return

        pos = event.x if self._horizontal else event.y
        track_pos = pos - 1
        delta = track_pos - self._drag_start_pos

        movable = self._track_len - self._thumb_size
        if movable > 0 and self._max_val > self._min_val:
            val_delta = delta * (self._max_val - self._min_val) // movable
            self.set_value(self._drag_start_value + val_delta)

        event.stop()

    def on_mouse_up(self, event: events.MouseUp) -> None:
        if self._dragging:
            self._dragging = False
            self.release_mouse()
            event.stop()

    class Changed(CommandMessage):
        def __init__(self, value: int) -> None:
            super().__init__(Command.SCROLL_BAR_CHANGED)
            self.value = value
