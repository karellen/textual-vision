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
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.strip import Strip
from textual.widget import Widget

from textual_vision.constants import Command, OptionFlag
from textual_vision.events import CommandMessage
from textual_vision.group import Group
from textual_vision.input_line import InputLine
from textual_vision.list_box import ListBox


MAX_POPUP_HEIGHT = 8


class _DropDownButton(Widget):
    """Small arrow button that triggers the dropdown popup."""

    COMPONENT_CLASSES = {
        "combo--arrow",
        "combo--sides",
    }

    DEFAULT_CSS = """
    _DropDownButton {
        width: 3;
        height: 1;
    }
    _DropDownButton .combo--arrow {
        color: $combo-arrow-fg;
        background: $combo-arrow-bg;
    }
    _DropDownButton .combo--sides {
        color: $combo-sides-fg;
        background: $combo-sides-bg;
    }
    """

    def render_line(self, y: int) -> Strip:
        if y != 0:
            return Strip.blank(self.size.width)
        arrow_style = self.get_component_rich_style("combo--arrow")
        sides_style = self.get_component_rich_style("combo--sides")
        line = Text()
        line.append("▐", style=sides_style)
        line.append("▼", style=arrow_style)
        line.append("▌", style=sides_style)
        return Strip(line.render(self.app.console))

    def on_mouse_down(self, event: events.MouseDown) -> None:
        if event.button == 1:
            self.post_message(_DropDownButton.Pressed())
            event.stop()

    class Pressed(CommandMessage):
        def __init__(self) -> None:
            super().__init__(Command.VALID)


class _DropDownPopup(ListBox):
    """Floating popup list for ComboBox."""

    DEFAULT_CSS = """
    _DropDownPopup {
        layer: menus;
        border: solid $accent;
        background: $surface;
    }
    """

    def __init__(self, items: list[str], owner: ComboBox,
                 initial_focus: int = 0, **kwargs: Any) -> None:
        super().__init__(items=items, **kwargs)
        self._owner = owner
        self._initial_focus = initial_focus
        self.can_focus = True

    def on_mount(self) -> None:
        self.focus()

    def on_resize(self, event: events.Resize) -> None:
        super().on_resize(event)
        if self._initial_focus >= 0:
            self.focus_item(self._initial_focus)
            self._initial_focus = -1

    def on_blur(self, event: events.Blur) -> None:
        self._owner._close_popup()

    def tv_handle_key(self, event: events.Key) -> bool:
        if event.key == "escape":
            self._owner._close_popup()
            return True
        return super().tv_handle_key(event)

    def on_key(self, event: events.Key) -> None:
        if self.tv_handle_key(event):
            event.stop()
            event.prevent_default()

    def on_mouse_move(self, event: events.MouseMove) -> None:
        item = self._top_item + event.y
        if 0 <= item < self._range:
            self.focus_item(item)
            self.refresh()

    def on_mouse_down(self, event: events.MouseDown) -> None:
        if event.button != 1:
            return
        item = self._top_item + event.y
        if 0 <= item < self._range:
            self.select_item(item)
        event.stop()

    def on_list_viewer_item_selected(self, message: ListBox.ItemSelected) -> None:
        self._owner._on_popup_selection(message.index)
        message.stop()


class ComboBox(Group):
    """Input line with a dropdown list.

    Inspired by TV's THistory + TInputLine pattern. Combines an InputLine
    with a dropdown button that opens a popup list of selectable items.
    ComboBox is a Group that manages InputLine focus via Group.current.
    """

    can_focus = False

    DEFAULT_CSS = """
    ComboBox {
        width: 1fr;
        height: 1;
        layout: horizontal;
    }
    ComboBox > InputLine {
        width: 1fr;
    }
    ComboBox > _DropDownButton {
        width: 3;
    }
    """

    value: reactive[str] = reactive("")

    def __init__(self, items: list[str] | None = None,
                 max_len: int = 128, editable: bool = True,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._items: list[str] = list(items) if items else []
        self._max_len = max_len
        self._editable = editable
        self._selected_index: int = -1
        self._input: InputLine | None = None
        self._popup: _DropDownPopup | None = None
        self.tv_options = OptionFlag.SELECTABLE

    @property
    def editable(self) -> bool:
        return self._editable

    @property
    def items(self) -> list[str]:
        return self._items

    @items.setter
    def items(self, value: list[str]) -> None:
        self._items = list(value)

    @property
    def input_line(self) -> InputLine | None:
        return self._input

    def compose(self) -> ComposeResult:
        self._input = InputLine(max_len=self._max_len,
                                read_only=not self._editable)
        yield self._input
        yield _DropDownButton()

    def on_key(self, event: events.Key) -> None:
        if event.key == "ctrl+down":
            if self._popup is None:
                self._open_popup()
            else:
                self._close_popup()
            event.stop()
            event.prevent_default()
            return
        if self._popup is not None:
            super().on_key(event)
            return
        if self._editable and self._items and event.key == "down":
            self._open_popup()
            event.stop()
            event.prevent_default()
            return
        if not self._editable and self._items:
            if event.key == "down":
                self._select_by_offset(1)
                event.stop()
                event.prevent_default()
                return
            elif event.key == "up":
                self._select_by_offset(-1)
                event.stop()
                event.prevent_default()
                return
        super().on_key(event)

    def on_mount(self) -> None:
        super().on_mount()
        if self._input is not None:
            self._input.data = self.value

    def on_unmount(self) -> None:
        self._close_popup()

    def on__drop_down_button_pressed(self, message: _DropDownButton.Pressed) -> None:
        if self._popup is not None:
            self._close_popup()
        else:
            self._open_popup()
        message.stop()

    def on_input_line_changed(self, message: InputLine.Changed) -> None:
        self.value = message.value

    def _find_current_in_items(self) -> int:
        """Find the index of the current input value in the items list."""
        current = self._input.data if self._input is not None else self.value
        if current:
            try:
                return self._items.index(current)
            except ValueError:
                pass
        if 0 <= self._selected_index < len(self._items):
            return self._selected_index
        return 0

    def _open_popup(self) -> None:
        if self._popup is not None or not self._items:
            return
        self.current = None
        region = self.region
        initial = self._find_current_in_items()
        popup = _DropDownPopup(items=self._items, owner=self,
                               initial_focus=initial)
        popup.styles.offset = (region.x, region.y + region.height)
        popup.styles.width = region.width
        popup.styles.height = min(len(self._items) + 2, MAX_POPUP_HEIGHT + 2)
        self.app.screen.mount(popup)
        self._popup = popup

    def _close_popup(self) -> None:
        if self._popup is not None:
            popup = self._popup
            self._popup = None
            if popup.is_mounted:
                popup.remove()
            if self._input is not None and self.is_mounted:
                self.current = self._input

    def _select_by_offset(self, delta: int) -> None:
        if not self._items:
            return
        new_idx = max(0, min(self._selected_index + delta,
                             len(self._items) - 1))
        self._apply_selection(new_idx)

    def _apply_selection(self, index: int) -> None:
        if 0 <= index < len(self._items):
            self._selected_index = index
            selected = self._items[index]
            if self._input is not None:
                self._input.data = selected
                self._input.select_all()
            self.value = selected
            self.post_message(ComboBox.Changed(selected, index))

    def _on_popup_selection(self, index: int) -> None:
        if 0 <= index < len(self._items):
            self._apply_selection(index)
        self._close_popup()

    class Changed(CommandMessage):
        def __init__(self, value: str, index: int) -> None:
            super().__init__(Command.LIST_ITEM_SELECTED)
            self.value = value
            self.index = index
