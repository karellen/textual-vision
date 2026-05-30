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

from rich.style import Style
from rich.text import Text

from textual import events
from textual.reactive import reactive
from textual.strip import Strip
from textual.widget import Widget

from textual_vision.constants import Command, WindowFlag
from textual_vision.events import CommandMessage

# Box-drawing characters for TV-style frame
FRAME_CHARS_ACTIVE = {
    "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝",
    "h": "═", "v": "║",
    "close": "[■]", "zoom": "[▲]", "unzoom": "[▼]",
}

FRAME_CHARS_PASSIVE = {
    "tl": "┌", "tr": "┐", "bl": "└", "br": "┘",
    "h": "─", "v": "│",
    "close": "[■]", "zoom": "[▲]", "unzoom": "[▼]",
}


class Frame(Widget):
    """TV-style window frame with border, title, close/zoom icons, and drag support."""

    COMPONENT_CLASSES = {
        "frame--active",
        "frame--passive",
        "frame--icon",
        "frame--title",
    }

    DEFAULT_CSS = """
    Frame {
        width: 1fr;
        height: 1fr;
        background: transparent;
    }
    Frame .frame--active {
        color: $foreground;
    }
    Frame .frame--passive {
        color: $text;
    }
    Frame .frame--icon {
        color: $frame-icon;
    }
    Frame .frame--title {
        color: $foreground;
    }
    """

    active: reactive[bool] = reactive(False)
    zoomed: reactive[bool] = reactive(False)

    def __init__(self, title: str = "", flags: WindowFlag = WindowFlag(0),
                 active: bool = False,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self._title = title
        self._flags = flags
        self._dragging = False
        self._drag_offset_x = 0
        self._drag_offset_y = 0
        self.active = active

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value
        self.refresh()

    @property
    def flags(self) -> WindowFlag:
        return self._flags

    @flags.setter
    def flags(self, value: WindowFlag) -> None:
        self._flags = value
        self.refresh()

    @property
    def _chars(self) -> dict[str, str]:
        return FRAME_CHARS_ACTIVE if self.active else FRAME_CHARS_PASSIVE

    def _close_icon_range(self, width: int) -> tuple[int, int] | None:
        if WindowFlag.CLOSE not in self._flags:
            return None
        return (1, 4)

    def _zoom_icon_range(self, width: int) -> tuple[int, int] | None:
        if WindowFlag.ZOOM not in self._flags:
            return None
        icon_len = 3
        return (width - 1 - icon_len, width - 1)

    def render_line(self, y: int) -> Strip:
        width = self.size.width
        height = self.size.height
        chars = self._chars

        if width < 2 or height < 2:
            return Strip.blank(width)

        style = self.get_component_rich_style(
            "frame--active" if self.active else "frame--passive"
        )
        icon_style = self.get_component_rich_style("frame--icon")
        title_style = self.get_component_rich_style("frame--title")

        if y == 0:
            return self._render_top_border(width, chars, style, icon_style, title_style)
        elif y == height - 1:
            return self._render_bottom_border(width, chars, style)
        else:
            return self._render_side_borders(width, chars, style)

    def _render_top_border(self, width: int, chars: dict[str, str],
                           style: Style, icon_style: Style,
                           title_style: Style) -> Strip:
        inner_width = width - 2
        if inner_width <= 0:
            line = Text()
            line.append(chars["tl"] + chars["tr"], style=style)
            return Strip(line.render(self.app.console))

        buf = list(chars["h"] * inner_width)
        buf_styles: list[Style] = [style] * inner_width

        close_range = self._close_icon_range(width)
        if close_range is not None:
            icon = chars["close"]
            start = close_range[0] - 1
            for i, ch in enumerate(icon):
                if start + i < inner_width:
                    buf[start + i] = ch
                    buf_styles[start + i] = icon_style

        zoom_range = self._zoom_icon_range(width)
        if zoom_range is not None:
            icon = chars["unzoom"] if self.zoomed else chars["zoom"]
            start = zoom_range[0] - 1
            for i, ch in enumerate(icon):
                if 0 <= start + i < inner_width:
                    buf[start + i] = ch
                    buf_styles[start + i] = icon_style

        if self._title:
            title_display = f" {self._title} "
            center = (inner_width - len(title_display)) // 2
            if center >= 0 and center + len(title_display) <= inner_width:
                for i, ch in enumerate(title_display):
                    pos = center + i
                    if buf_styles[pos] is not icon_style:
                        buf[pos] = ch
                        buf_styles[pos] = title_style

        line = Text()
        line.append(chars["tl"], style=style)
        current_style = buf_styles[0]
        current_text = buf[0]
        for i in range(1, inner_width):
            if buf_styles[i] is current_style:
                current_text += buf[i]
            else:
                line.append(current_text, style=current_style)
                current_style = buf_styles[i]
                current_text = buf[i]
        line.append(current_text, style=current_style)
        line.append(chars["tr"], style=style)
        return Strip(line.render(self.app.console))

    @staticmethod
    def bottom_border_chars(width: int, chars: dict[str, str],
                            has_grow: bool) -> str:
        inner_width = width - 2
        if has_grow:
            result = "└"
            if inner_width >= 2:
                result += "─" + chars["h"] * (inner_width - 2) + "─"
            elif inner_width == 1:
                result += "─"
            result += "┘"
        else:
            result = chars["bl"] + chars["h"] * max(0, inner_width) + chars["br"]
        return result

    def _render_bottom_border(self, width: int, chars: dict[str, str],
                              style: Style) -> Strip:
        has_grow = self.active and WindowFlag.GROW in self._flags
        text = self.bottom_border_chars(width, chars, has_grow)
        line = Text()
        line.append(text, style=style)
        return Strip(line.render(self.app.console))

    def _render_side_borders(self, width: int, chars: dict[str, str],
                             style: Style) -> Strip:
        inner_width = width - 2
        bg = self.visual_style.rich_style
        line = Text()
        line.append(chars["v"], style=style)
        line.append(" " * max(0, inner_width), style=bg)
        line.append(chars["v"], style=style)
        return Strip(line.render(self.app.console))

    def _hit_close(self, x: int) -> bool:
        cr = self._close_icon_range(self.size.width)
        return cr is not None and cr[0] <= x < cr[1]

    def _hit_zoom(self, x: int) -> bool:
        zr = self._zoom_icon_range(self.size.width)
        return zr is not None and zr[0] <= x < zr[1]

    def _hit_title_bar(self, y: int) -> bool:
        return y == 0

    def _hit_resize_corner(self, x: int, y: int) -> str | bool:
        if y < self.size.height - 2 or WindowFlag.GROW not in self._flags:
            return False
        if x >= self.size.width - 2:
            return "right"
        if x < 2:
            return "left"
        return False

    def on_mouse_down(self, event: events.MouseDown) -> None:
        if event.button != 1:
            return

        self.post_message(Frame.Selected())

        if self._hit_title_bar(event.y):
            if self._hit_close(event.x):
                self.post_message(CommandMessage(Command.CLOSE))
                event.stop()
                return
            if self._hit_zoom(event.x):
                self.post_message(CommandMessage(Command.ZOOM))
                event.stop()
                return
            if WindowFlag.MOVE in self._flags:
                self._dragging = True
                self._drag_offset_x = event.x
                self._drag_offset_y = event.y
                self.capture_mouse()
                event.stop()
                return

        corner = self._hit_resize_corner(event.x, event.y)
        if corner:
            self.post_message(Frame.ResizeStart(left=(corner == "left")))
            event.stop()

    def on_mouse_move(self, event: events.MouseMove) -> None:
        if self._dragging:
            self.post_message(Frame.DragMove(
                delta_x=event.delta_x,
                delta_y=event.delta_y,
            ))
            event.stop()

    def on_mouse_up(self, event: events.MouseUp) -> None:
        if self._dragging:
            self._dragging = False
            self.release_mouse()
            event.stop()

    class Selected(CommandMessage):
        def __init__(self) -> None:
            super().__init__(Command.VALID)

    class DragMove(CommandMessage):
        def __init__(self, delta_x: int, delta_y: int) -> None:
            super().__init__(Command.RESIZE)
            self.delta_x = delta_x
            self.delta_y = delta_y

    class ResizeStart(CommandMessage):
        """Posted when a resize corner is clicked. Window handles capture."""
        def __init__(self, left: bool = False) -> None:
            super().__init__(Command.RESIZE)
            self.left = left
