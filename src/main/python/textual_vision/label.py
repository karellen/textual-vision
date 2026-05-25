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
from textual.strip import Strip
from textual.widget import Widget

from textual_vision.group import TVViewMixin
from textual_vision.menus import parse_hotkey_text, render_tilde_text


class Label(Widget, TVViewMixin):
    """Text label with tilde-hotkey that focuses a linked view.

    TV's TLabel: not focusable itself, but Alt+hotkey focuses the
    linked widget via the owning Group's focus system.
    """

    COMPONENT_CLASSES = {
        "label--text",
        "label--hotkey",
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
    Label .label--hotkey {
        color: $menu-hotkey;
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

    def tv_handle_key(self, event: events.Key) -> bool:
        if self._hotkey and self._link is not None:
            if event.key.startswith("alt+") and len(event.key) == 5:
                if event.key[4].lower() == self._hotkey:
                    from textual_vision.group import Group
                    parent = self.parent
                    if isinstance(parent, Group):
                        parent.current = self._link
                    return True
        return False
