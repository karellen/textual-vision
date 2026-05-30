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

from textual_vision.constants import Command, OptionFlag, StateFlag
from textual_vision.events import CommandMessage
from textual_vision.group import TVViewMixin


class InputLine(Widget, TVViewMixin):
    """Single-line text input with cursor, selection, and scroll.

    TV's TInputLine: fixed-width field with horizontal scrolling,
    character-level cursor, shift-select, and optional password masking.
    """

    COMPONENT_CLASSES = {
        "inputline--text",
        "inputline--focused",
        "inputline--selected",
        "inputline--cursor",
        "inputline--arrow",
    }

    DEFAULT_CSS = """
    InputLine {
        height: 1;
        width: 20;
    }
    InputLine .inputline--text {
        color: $input-fg;
        background: $input-bg;
    }
    InputLine .inputline--focused {
        color: $input-fg;
        background: $input-bg;
    }
    InputLine .inputline--selected {
        color: $input-selected-fg;
        background: $input-selected-bg;
    }
    InputLine .inputline--cursor {
        color: $input-bg;
        background: $input-fg;
    }
    InputLine .inputline--arrow {
        color: $input-arrow;
        background: $input-bg;
    }
    """

    data: reactive[str] = reactive("")

    def __init__(self, max_len: int = 255, password: bool = False,
                 read_only: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._max_len = max_len
        self._password = password
        self._read_only = read_only
        self._cursor_pos = 0
        self._first_pos = 0
        self._sel_start = -1
        self._sel_end = -1
        self._cursor_visible = True
        self._blink_timer = None
        self.tv_options = OptionFlag.SELECTABLE
        self.can_focus = True

    @property
    def tv_focused(self) -> bool:
        return bool(self.tv_state & StateFlag.FOCUSED)

    def on_tv_focus(self) -> None:
        self._cursor_visible = True
        self._start_blink()

    def on_tv_blur(self) -> None:
        self._stop_blink()
        self._cursor_visible = True

    def on_mount(self) -> None:
        if self.tv_focused:
            self._start_blink()

    def _start_blink(self) -> None:
        self._stop_blink()
        if not self.is_mounted:
            return
        self._blink_timer = self.set_interval(0.53, self._toggle_cursor, pause=False)

    def _stop_blink(self) -> None:
        if self._blink_timer is not None:
            self._blink_timer.stop()
            self._blink_timer = None

    def _toggle_cursor(self) -> None:
        self._cursor_visible = not self._cursor_visible
        self.refresh()

    def _reset_cursor_blink(self) -> None:
        self._cursor_visible = True
        if self.tv_focused:
            self._start_blink()
        self.refresh()

    @property
    def max_len(self) -> int:
        return self._max_len

    @property
    def password(self) -> bool:
        return self._password

    @property
    def read_only(self) -> bool:
        return self._read_only

    @read_only.setter
    def read_only(self, value: bool) -> None:
        self._read_only = value

    @property
    def cursor_pos(self) -> int:
        return self._cursor_pos

    @property
    def has_selection(self) -> bool:
        return self._sel_start >= 0 and self._sel_start != self._sel_end

    @property
    def _visible_width(self) -> int:
        return max(1, self.size.width - 2)

    @property
    def _display_text(self) -> str:
        if self._password:
            return "*" * len(self.data)
        return self.data

    def render_line(self, y: int) -> Strip:
        if y != 0:
            return Strip.blank(self.size.width)

        width = self.size.width
        focused = self.tv_focused
        text_style = self.get_component_rich_style(
            "inputline--focused" if focused else "inputline--text"
        )
        sel_style = self.get_component_rich_style("inputline--selected")
        cursor_style = self.get_component_rich_style("inputline--cursor")
        arrow_style = self.get_component_rich_style("inputline--arrow")

        display = self._display_text
        vis_w = self._visible_width
        fp = self._first_pos

        has_left = fp > 0
        has_right = fp + vis_w < len(display)

        visible = display[fp:fp + vis_w]
        if len(visible) < vis_w:
            visible += " " * (vis_w - len(visible))

        line = Text()
        line.append("◄" if has_left else " ", style=arrow_style if has_left else text_style)

        show_cursor = focused and self._cursor_visible

        for i, ch in enumerate(visible):
            abs_pos = fp + i
            in_sel = (self.has_selection and
                      min(self._sel_start, self._sel_end) <= abs_pos <
                      max(self._sel_start, self._sel_end))
            at_cursor = (abs_pos == self._cursor_pos)

            if at_cursor and show_cursor:
                style = cursor_style
            elif in_sel:
                style = sel_style
            else:
                style = text_style
            line.append(ch, style=style)

        line.append("►" if has_right else " ", style=arrow_style if has_right else text_style)

        remaining = width - len(line.plain)
        if remaining > 0:
            line.append(" " * remaining, style=text_style)

        return Strip(line.render(self.app.console))

    def _scroll_to_cursor(self) -> None:
        vis_w = self._visible_width
        if self._cursor_pos < self._first_pos:
            self._first_pos = self._cursor_pos
        elif self._cursor_pos >= self._first_pos + vis_w:
            self._first_pos = self._cursor_pos - vis_w + 1
        self._first_pos = max(0, self._first_pos)

    def _move_cursor(self, pos: int, extend_selection: bool = False) -> None:
        pos = max(0, min(pos, len(self.data)))
        if extend_selection:
            if self._sel_start < 0:
                self._sel_start = self._cursor_pos
            self._sel_end = pos
        else:
            self._sel_start = -1
            self._sel_end = -1
        self._cursor_pos = pos
        self._scroll_to_cursor()
        self._reset_cursor_blink()

    def _insert_char(self, ch: str) -> None:
        if self._read_only:
            return
        if self.has_selection:
            self._delete_selection()
        if len(self.data) >= self._max_len:
            return
        pos = self._cursor_pos
        self.data = self.data[:pos] + ch + self.data[pos:]
        self._cursor_pos = pos + 1
        self._scroll_to_cursor()
        self._reset_cursor_blink()
        self.post_message(InputLine.Changed(self.data))

    def _delete_selection(self) -> None:
        if self._read_only:
            return
        if not self.has_selection:
            return
        start = min(self._sel_start, self._sel_end)
        end = max(self._sel_start, self._sel_end)
        self.data = self.data[:start] + self.data[end:]
        self._cursor_pos = start
        self._sel_start = -1
        self._sel_end = -1
        self._scroll_to_cursor()
        self.post_message(InputLine.Changed(self.data))

    def _delete_char(self, forward: bool) -> None:
        if self._read_only:
            return
        if self.has_selection:
            self._delete_selection()
            return
        if forward:
            if self._cursor_pos < len(self.data):
                self.data = self.data[:self._cursor_pos] + self.data[self._cursor_pos + 1:]
                self.post_message(InputLine.Changed(self.data))
        else:
            if self._cursor_pos > 0:
                self._cursor_pos -= 1
                self.data = self.data[:self._cursor_pos] + self.data[self._cursor_pos + 1:]
                self._scroll_to_cursor()
                self.post_message(InputLine.Changed(self.data))

    def _word_left(self) -> int:
        pos = self._cursor_pos
        while pos > 0 and self.data[pos - 1] == " ":
            pos -= 1
        while pos > 0 and self.data[pos - 1] != " ":
            pos -= 1
        return pos

    def _word_right(self) -> int:
        pos = self._cursor_pos
        n = len(self.data)
        while pos < n and self.data[pos] != " ":
            pos += 1
        while pos < n and self.data[pos] == " ":
            pos += 1
        return pos

    def select_all(self) -> None:
        self._sel_start = 0
        self._sel_end = len(self.data)
        self._cursor_pos = len(self.data)
        self._scroll_to_cursor()
        self.refresh()

    def tv_handle_key(self, event: events.Key) -> bool:
        shift = event.key.startswith("shift+")
        key = event.key[6:] if shift else event.key

        if key == "left":
            self._move_cursor(self._cursor_pos - 1, shift)
            return True
        elif key == "right":
            self._move_cursor(self._cursor_pos + 1, shift)
            return True
        elif key == "home":
            self._move_cursor(0, shift)
            return True
        elif key == "end":
            self._move_cursor(len(self.data), shift)
            return True
        elif event.key == "ctrl+left":
            self._move_cursor(self._word_left())
            return True
        elif event.key == "ctrl+right":
            self._move_cursor(self._word_right())
            return True
        elif event.key == "ctrl+a":
            self.select_all()
            return True
        elif event.key == "backspace":
            self._delete_char(forward=False)
            return True
        elif event.key == "delete":
            self._delete_char(forward=True)
            return True
        elif event.character and len(event.character) == 1 and event.character.isprintable():
            self._insert_char(event.character)
            return True

        return False

    def on_mouse_down(self, event: events.MouseDown) -> None:
        if event.button != 1:
            return
        self.tv_select_self()
        pos = self._first_pos + event.x - 1
        pos = max(0, min(pos, len(self.data)))
        self._move_cursor(pos)
        event.stop()

    class Changed(CommandMessage):
        def __init__(self, value: str) -> None:
            super().__init__(Command.VALID)
            self.value = value
