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

from textual.strip import Strip
from textual.widget import Widget

from textual_vision.events import BroadcastMessage
from textual_vision.group import TVViewMixin
from textual_vision.menus import parse_hotkey_text, render_tilde_text


class Label(Widget, TVViewMixin):
    """Text label with tilde-hotkey that focuses a linked view.

    TV's TLabel: not focusable itself, but Alt+hotkey focuses the
    linked widget via the owning Group's focus system. Highlights
    when the linked view has TV focus.
    """

    COMPONENT_CLASSES = {
        "label--text",
        "label--highlighted",
        "label--hotkey",
        "label--hotkey-highlighted",
        "label--disabled",
    }

    DEFAULT_CSS = """
    Label {
        height: 1;
        width: auto;
    }
    Label .label--text {
        color: $text;
    }
    Label .label--highlighted {
        color: $label-highlight;
    }
    Label .label--hotkey {
        color: $label-hotkey;
    }
    Label .label--hotkey-highlighted {
        color: $label-hotkey;
        text-style: underline;
    }
    Label .label--disabled {
        color: $text-muted;
    }
    """

    def __init__(self, text: str, link: Widget | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._text = text
        self._link = link
        self._plain, self._hotkey = parse_hotkey_text(text)
        self._light = False

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value
        self._plain, self._hotkey = parse_hotkey_text(value)
        self.refresh()

    @property
    def link(self) -> Widget | None:
        return self._link

    @link.setter
    def link(self, value: Widget | None) -> None:
        self._link = value

    @property
    def hotkey(self) -> str | None:
        return self._hotkey

    def get_content_width(self, container, viewport) -> int:
        return len(self._plain)

    def render_line(self, y: int) -> Strip:
        if y != 0:
            return Strip.blank(self.size.width)

        if self._light:
            text_style = self.get_component_rich_style("label--highlighted")
            hotkey_style = self.get_component_rich_style("label--hotkey-highlighted")
        else:
            text_style = self.get_component_rich_style("label--text")
            hotkey_style = self.get_component_rich_style("label--hotkey")

        line = render_tilde_text(self._text, str(text_style), str(hotkey_style))
        remaining = self.size.width - len(line.plain)
        if remaining > 0:
            padded = Text()
            padded.append(line)
            padded.append(" " * remaining, style=text_style)
            line = padded

        return Strip(line.render(self.app.console))

    def _is_linked(self, widget) -> bool:
        if self._link is None or widget is None:
            return False
        if widget is self._link:
            return True
        w = getattr(widget, "parent", None)
        while w is not None:
            if w is self._link:
                return True
            w = getattr(w, "parent", None)
        return False

    def on_broadcast_message(self, message: BroadcastMessage) -> None:
        from textual_vision.constants import Command
        if self._link is None:
            return
        if message.command == Command.RECEIVED_FOCUS and self._is_linked(message.info):
            self._light = True
            self.refresh()
        elif message.command == Command.RELEASED_FOCUS and self._is_linked(message.info):
            self._light = False
            self.refresh()

    def tv_get_hotkey(self) -> str | None:
        if self._hotkey and self._link is not None:
            return self._hotkey
        return None

    def tv_handle_hotkey(self) -> bool:
        if self._hotkey and self._link is not None:
            if isinstance(self._link, TVViewMixin):
                self._link.tv_select_self()
            return True
        return False
