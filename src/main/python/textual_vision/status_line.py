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

from dataclasses import dataclass, field
from typing import Any

from rich.text import Text

from textual import events
from textual.strip import Strip
from textual.widget import Widget

from textual_vision.constants import Command, OptionFlag
from textual_vision.events import CommandMessage
from textual_vision.group import TVViewMixin
from textual_vision.menus import render_tilde_text


@dataclass
class StatusItem:
    text: str
    key_code: str
    command: Command


@dataclass
class StatusDef:
    min_help_ctx: int
    max_help_ctx: int
    items: list[StatusItem] = field(default_factory=list)

    def matches(self, help_ctx: int) -> bool:
        return self.min_help_ctx <= help_ctx <= self.max_help_ctx


class StatusLine(Widget, TVViewMixin):
    """Context-sensitive status bar at the bottom of the application.

    Has OptionFlag.POST_PROCESS to intercept unhandled keys in the
    post-process phase. Displays status items based on the current
    help context and maps key presses to commands.
    """

    COMPONENT_CLASSES = {
        "statusline--item",
        "statusline--hotkey",
        "statusline--hint",
    }

    DEFAULT_CSS = """
    StatusLine {
        dock: bottom;
        width: 1fr;
        height: 1;
        background: $footer-background;
    }
    StatusLine .statusline--item {
        color: $footer-foreground;
        background: $footer-background;
    }
    StatusLine .statusline--hotkey {
        color: $footer-key-foreground;
        background: $footer-background;
    }
    StatusLine .statusline--hint {
        color: $text-muted;
        background: $footer-background;
    }
    """

    def __init__(self, defs: list[StatusDef] | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._defs: list[StatusDef] = defs or []
        self._help_ctx: int = 0
        self._hint_text: str = ""
        self.tv_options = OptionFlag.POST_PROCESS

    @property
    def help_ctx(self) -> int:
        return self._help_ctx

    @property
    def current_items(self) -> list[StatusItem]:
        """Return the status items for the current help context."""
        for status_def in self._defs:
            if status_def.matches(self._help_ctx):
                return status_def.items
        return []

    def find_by_key(self, key_code: str) -> StatusItem | None:
        """Find a status item matching the given key code."""
        for item in self.current_items:
            if item.key_code == key_code:
                return item
        return None

    def update(self, help_ctx: int) -> None:
        """Update the status line for a new help context."""
        self._help_ctx = help_ctx
        self._hint_text = self.hint(help_ctx)
        self.refresh()

    def hint(self, help_ctx: int) -> str:
        """Return context-sensitive hint text. Override in subclasses."""
        return ""

    def render_line(self, y: int) -> Strip:
        if y != 0:
            return Strip.blank(self.size.width)

        item_style = self.get_component_rich_style("statusline--item")
        hotkey_style = self.get_component_rich_style("statusline--hotkey")
        hint_style = self.get_component_rich_style("statusline--hint")

        line = Text()
        line.append(" ", style=item_style)

        for item in self.current_items:
            text = render_tilde_text(item.text, str(item_style), str(hotkey_style))
            line.append(text)
            line.append("  ", style=item_style)

        if self._hint_text:
            line.append("│ ", style=item_style)
            line.append(self._hint_text, style=hint_style)

        remaining = self.size.width - len(line.plain)
        if remaining > 0:
            line.append(" " * remaining, style=item_style)

        return Strip(line.render(self.app.console))

    def tv_handle_key(self, event: events.Key) -> bool:
        item = self.find_by_key(event.key)
        if item is not None:
            self.post_message(CommandMessage(item.command))
            return True
        return False
