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
from textual_vision.menus import parse_hotkey_text, render_tilde_text

SHADOW_TOP_RIGHT = "▄"
SHADOW_MID_RIGHT = "█"
SHADOW_BOTTOM = "▀"


class Button(Widget, TVViewMixin):
    """TV-style push button with shadow and hotkey support.

    Shadow is cast to the right and bottom (light from top-left).
    Column 0 is a shadow-colored space. The face occupies columns
    1..width-2. The last column has shadow characters (▄/█). The
    bottom row has ▀ shadow characters.

    When pressed, the face shifts right by 1 and the shadow disappears,
    creating a depress effect. Mouse click fires on release (not press).
    """

    COMPONENT_CLASSES = {
        "button--normal",
        "button--default",
        "button--focused",
        "button--hotkey",
        "button--hotkey-focused",
        "button--shadow",
        "button--disabled",
    }

    DEFAULT_CSS = """
    Button {
        height: 2;
        width: auto;
    }
    Button .button--normal {
        color: $button-face-fg;
        background: $button-face-bg;
    }
    Button .button--default {
        color: $button-default-fg;
        background: $button-face-bg;
    }
    Button .button--focused {
        color: $button-focused-fg;
        background: $button-focused-bg;
    }
    Button .button--hotkey {
        color: $button-hotkey;
        background: $button-face-bg;
    }
    Button .button--hotkey-focused {
        color: $button-hotkey;
        background: $button-focused-bg;
    }
    Button .button--shadow {
        color: $button-shadow-fg;
        background: $button-shadow-bg;
    }
    Button .button--disabled {
        color: $button-disabled-fg;
        background: $button-disabled-bg;
    }
    """

    is_default: reactive[bool] = reactive(False)
    down: reactive[bool] = reactive(False)

    def __init__(self, text: str, command: Command = Command.OK,
                 is_default: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._text = text
        self._command = command
        self._plain, self._hotkey = parse_hotkey_text(text)
        self.tv_options = OptionFlag.SELECTABLE
        self.can_focus = True
        self.is_default = is_default
        self._mouse_pressed = False

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value
        self._plain, self._hotkey = parse_hotkey_text(value)
        self.refresh()

    @property
    def command(self) -> Command:
        return self._command

    @command.setter
    def command(self, value: Command) -> None:
        self._command = value

    @property
    def hotkey(self) -> str | None:
        return self._hotkey

    @property
    def _face_width(self) -> int:
        return len(self._plain) + 4

    def get_content_width(self, container, viewport) -> int:
        return self._face_width + 2

    def get_content_height(self, container, viewport, width) -> int:
        return 2

    def render_line(self, y: int) -> Strip:
        width = self.size.width
        height = self.size.height

        focused = bool(self.tv_state & StateFlag.FOCUSED)

        if self.disabled:
            face_style = self.get_component_rich_style("button--disabled")
            hotkey_style = face_style
        elif focused:
            face_style = self.get_component_rich_style("button--focused")
            hotkey_style = self.get_component_rich_style("button--hotkey-focused")
        elif self.is_default:
            face_style = self.get_component_rich_style("button--default")
            hotkey_style = self.get_component_rich_style("button--hotkey")
        else:
            face_style = self.get_component_rich_style("button--normal")
            hotkey_style = self.get_component_rich_style("button--hotkey")
        shadow_style = self.get_component_rich_style("button--shadow")

        s = width - 1
        is_down = self.down
        line = Text()

        if y < height - 1:
            if is_down:
                line.append(" ", style=shadow_style)
                line.append(" ", style=shadow_style)
                face_start = 2
            else:
                line.append(" ", style=shadow_style)
                face_start = 1

            face_chars = width - face_start - (0 if is_down else 1)
            label = render_tilde_text(self._text, str(face_style), str(hotkey_style))
            label_plain_len = len(self._plain)
            pad_left = max(0, (face_chars - label_plain_len - 2) // 2)
            pad_right = max(0, face_chars - label_plain_len - 2 - pad_left)

            line.append(" " * pad_left, style=face_style)
            line.append(" ", style=face_style)
            line.append(label)
            line.append(" ", style=face_style)
            line.append(" " * pad_right, style=face_style)

            if not is_down:
                if y == 0:
                    line.append(SHADOW_TOP_RIGHT, style=shadow_style)
                else:
                    line.append(SHADOW_MID_RIGHT, style=shadow_style)
        elif y == height - 1:
            line.append(" ", style=shadow_style)
            if is_down:
                line.append(" " * s, style=shadow_style)
            else:
                line.append(" ", style=shadow_style)
                line.append(SHADOW_BOTTOM * (s - 1), style=shadow_style)
        else:
            return Strip.blank(width)

        remaining = width - len(line.plain)
        if remaining > 0:
            line.append(" " * remaining, style=shadow_style)

        return Strip(line.render(self.app.console))

    def press(self) -> None:
        if not self.disabled:
            self.post_message(CommandMessage(self._command))
            self.post_message(Button.Pressed(self._command))

    def tv_get_hotkey(self) -> str | None:
        return self._hotkey

    def tv_handle_hotkey(self) -> bool:
        if self._hotkey:
            self.tv_select_self()
            self.press()
            return True
        return False

    def tv_handle_key(self, event: events.Key) -> bool:
        if event.key in ("enter", "space"):
            self.press()
            return True
        return False

    def on_mouse_down(self, event: events.MouseDown) -> None:
        if event.button == 1 and not self.disabled:
            self.tv_select_self()
            self._mouse_pressed = True
            self.down = True
            self.capture_mouse()
            event.stop()

    def on_mouse_move(self, event: events.MouseMove) -> None:
        if not self._mouse_pressed:
            return
        inside = (0 <= event.x < self.size.width and
                  0 <= event.y < self.size.height - 1)
        self.down = inside

    def on_mouse_up(self, event: events.MouseUp) -> None:
        if not self._mouse_pressed:
            return
        self._mouse_pressed = False
        was_down = self.down
        self.down = False
        self.release_mouse()
        if was_down:
            self.press()
        event.stop()

    class Pressed(CommandMessage):
        pass
