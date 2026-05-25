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
from textual.reactive import reactive
from textual.strip import Strip
from textual.widget import Widget

from textual_vision.constants import Command, OptionFlag
from textual_vision.events import CommandMessage
from textual_vision.group import TVViewMixin


def parse_hotkey_text(label: str) -> tuple[str, str | None]:
    """Parse TV tilde markup from a label to extract the hotkey character.

    In TV, tildes toggle highlighting. For menu items like '~F~ile',
    the first highlighted character ('F') is the hotkey.

    Returns (plain_text, hotkey_char_lower).
    """
    parts = label.split("~")
    plain = "".join(parts)
    if len(parts) >= 3:
        hotkey_span = parts[1]
        if hotkey_span:
            return plain, hotkey_span[0].lower()
    return plain, None


def render_tilde_text(label: str, normal_style: str = "",
                      highlight_style: str = "underline") -> Text:
    """Render TV tilde-toggle markup into Rich Text.

    Tildes toggle between normal and highlight style. Text between
    the first and second tilde is highlighted, between second and
    third is normal, etc. Supports multi-character spans like '~F1~'.
    """
    text = Text()
    parts = label.split("~")
    for i, part in enumerate(parts):
        if part:
            style = highlight_style if i % 2 == 1 else normal_style
            text.append(part, style=style)
    return text


@dataclass
class MenuItem:
    name: str
    command: Command = Command.VALID
    key_code: str = ""
    help_ctx: int = 0
    sub_menu: Menu | None = None
    disabled: bool = False
    param: Any = None

    @property
    def plain_name(self) -> str:
        return parse_hotkey_text(self.name)[0]

    @property
    def hotkey(self) -> str | None:
        return parse_hotkey_text(self.name)[1]

    @property
    def is_separator(self) -> bool:
        return False

    @property
    def is_submenu(self) -> bool:
        return self.sub_menu is not None


@dataclass
class Separator:
    @property
    def is_separator(self) -> bool:
        return True

    @property
    def disabled(self) -> bool:
        return True

    @property
    def is_submenu(self) -> bool:
        return False


@dataclass
class Menu:
    items: list[MenuItem | Separator] = field(default_factory=list)
    default: MenuItem | None = None


def SubMenu(name: str, *items: MenuItem | Separator) -> MenuItem:
    """Create a MenuItem that opens a sub-menu."""
    return MenuItem(name=name, sub_menu=Menu(items=list(items)))


class MenuBar(Widget, TVViewMixin):
    """Horizontal menu bar with dropdown menus and keyboard navigation.

    Has OptionFlag.PRE_PROCESS to intercept F10 in the pre-process phase.
    """

    COMPONENT_CLASSES = {
        "menubar--item",
        "menubar--item-active",
        "menubar--hotkey",
        "menubar--disabled",
    }

    DEFAULT_CSS = """
    MenuBar {
        dock: top;
        width: 1fr;
        height: 1;
        background: $surface;
    }
    MenuBar .menubar--item {
        color: $text;
        background: $surface;
    }
    MenuBar .menubar--item-active {
        color: $text;
        background: $accent;
    }
    MenuBar .menubar--hotkey {
        color: $menu-hotkey;
        background: $surface;
    }
    MenuBar .menubar--disabled {
        color: $text-muted;
        background: $surface;
    }
    """

    active: reactive[bool] = reactive(False)
    selected_index: reactive[int] = reactive(-1)

    def __init__(self, menu: Menu | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._menu = menu or Menu()
        self.tv_options = OptionFlag.PRE_PROCESS
        self._menu_box: MenuBox | None = None

    @property
    def menu(self) -> Menu:
        return self._menu

    @menu.setter
    def menu(self, value: Menu) -> None:
        self._menu = value
        self.refresh()

    @property
    def _top_items(self) -> list[MenuItem]:
        return [item for item in self._menu.items if isinstance(item, MenuItem)]

    def find_by_hotkey(self, key: str) -> int:
        """Find the index of the top-level item with the given hotkey. Returns -1 if not found."""
        key_lower = key.lower()
        for i, item in enumerate(self._top_items):
            if item.hotkey == key_lower and not item.disabled:
                return i
        return -1

    def render_line(self, y: int) -> Strip:
        if y != 0:
            return Strip.blank(self.size.width)

        item_style = self.get_component_rich_style("menubar--item")
        active_style = self.get_component_rich_style("menubar--item-active")
        hotkey_style = self.get_component_rich_style("menubar--hotkey")
        disabled_style = self.get_component_rich_style("menubar--disabled")

        line = Text()
        line.append(" ", style=item_style)

        for i, item in enumerate(self._top_items):
            is_selected = self.active and i == self.selected_index
            if item.disabled:
                text = render_tilde_text(item.name, str(disabled_style), str(disabled_style))
            elif is_selected:
                text = render_tilde_text(item.name, str(active_style), str(active_style))
            else:
                text = render_tilde_text(item.name, str(item_style), str(hotkey_style))

            if is_selected:
                line.append(" ", style=active_style)
                line.append(text)
                line.append(" ", style=active_style)
            else:
                line.append(" ", style=item_style)
                line.append(text)
                line.append(" ", style=item_style)

        remaining = self.size.width - len(line.plain)
        if remaining > 0:
            line.append(" " * remaining, style=item_style)

        return Strip(line.render(self.app.console))

    def activate(self) -> None:
        self.active = True
        if self.selected_index < 0 and self._top_items:
            self.selected_index = 0

    def deactivate(self) -> None:
        self.active = False
        self.selected_index = -1
        self._close_menu_box()

    def _close_menu_box(self) -> None:
        if self._menu_box is not None:
            self._menu_box._close_sub_menu()
            if self._menu_box.is_mounted:
                self._menu_box.remove()
            self._menu_box = None

    def _open_menu_box(self) -> None:
        self._close_menu_box()
        if not self.is_mounted:
            return
        items = self._top_items
        if 0 <= self.selected_index < len(items):
            item = items[self.selected_index]
            if item.sub_menu:
                x = self._item_x_offset(self.selected_index)
                self._menu_box = MenuBox(menu=item.sub_menu)
                self._menu_box.styles.offset = (x, 1)
                self.app.screen.mount(self._menu_box)

    def _item_x_offset(self, index: int) -> int:
        """Calculate the x offset of a top-level item for positioning the dropdown."""
        offset = 1
        for i, item in enumerate(self._top_items):
            if i == index:
                return offset
            offset += len(item.plain_name) + 2
        return offset

    def _hit_test_item(self, x: int) -> int:
        """Return the index of the top-level item at screen x, or -1."""
        offset = 1
        for i, item in enumerate(self._top_items):
            item_width = len(item.plain_name) + 2
            if offset <= x < offset + item_width:
                return i
            offset += item_width
        return -1

    def on_mouse_move(self, event: events.MouseMove) -> None:
        if not self.active or event.y != 0:
            return
        idx = self._hit_test_item(event.x)
        if idx >= 0 and not self._top_items[idx].disabled and idx != self.selected_index:
            self.selected_index = idx
            self._open_menu_box()

    def on_mouse_down(self, event: events.MouseDown) -> None:
        if event.button != 1 or event.y != 0:
            return
        idx = self._hit_test_item(event.x)
        if idx >= 0 and not self._top_items[idx].disabled:
            if self.active and idx == self.selected_index:
                self.deactivate()
            else:
                self.activate()
                self.selected_index = idx
                self._open_menu_box()
            event.stop()

    def tv_handle_key(self, event: events.Key) -> bool:
        if event.key == "f10":
            if self.active:
                self.deactivate()
            else:
                self.activate()
            return True

        if not self.active:
            if event.key.startswith("alt+") and len(event.key) == 5:
                letter = event.key[4]
                idx = self.find_by_hotkey(letter)
                if idx >= 0:
                    self.activate()
                    self.selected_index = idx
                    self._open_menu_box()
                    return True
            return False

        if self._menu_box is not None:
            idx = self._menu_box.find_by_key_code(event.key)
            if idx >= 0:
                self._menu_box.selected_index = idx
                item = self._menu_box.select_current()
                if item:
                    self._menu_box.post_message(CommandMessage(item.command, info=item.param))
                    self._menu_box.post_message(MenuBox.ItemSelected(item))
                return True
            if event.key in ("up", "down", "enter", "escape", "right") or len(event.key) == 1:
                self._menu_box.on_key(event)
                return True

        if event.key == "left":
            self._navigate(-1)
            return True
        elif event.key == "right":
            self._navigate(1)
            return True
        elif event.key in ("down", "enter"):
            self._open_menu_box()
            return True
        elif event.key == "escape":
            self.deactivate()
            return True

        self.deactivate()
        return False

    def _navigate(self, direction: int) -> None:
        items = self._top_items
        if not items:
            return
        n = len(items)
        new_index = (self.selected_index + direction) % n
        self.selected_index = new_index
        if self._menu_box is not None:
            self._open_menu_box()

    @classmethod
    def build(cls, *items: MenuItem, **kwargs: Any) -> MenuBar:
        """Construct a MenuBar from top-level MenuItems (typically SubMenu items)."""
        return cls(menu=Menu(items=list(items)), **kwargs)


class MenuBox(Widget):
    """Vertical dropdown menu with borders, keyboard navigation, and sub-menu support."""

    COMPONENT_CLASSES = {
        "menubox--border",
        "menubox--item",
        "menubox--item-active",
        "menubox--hotkey",
        "menubox--disabled",
        "menubox--separator",
        "menubox--shortcut",
    }

    DEFAULT_CSS = """
    MenuBox {
        layer: menus;
        width: auto;
        height: auto;
        background: $surface;
    }
    MenuBox .menubox--border {
        color: $text;
    }
    MenuBox .menubox--item {
        color: $text;
    }
    MenuBox .menubox--item-active {
        color: $text;
        background: $accent;
    }
    MenuBox .menubox--hotkey {
        color: $accent;
    }
    MenuBox .menubox--disabled {
        color: $text-muted;
    }
    MenuBox .menubox--separator {
        color: $text-muted;
    }
    MenuBox .menubox--shortcut {
        color: $text-muted;
    }
    """

    selected_index: reactive[int] = reactive(0)

    def __init__(self, menu: Menu | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._menu = menu or Menu()
        self._sub_menu_box: MenuBox | None = None
        self._skip_to_first_selectable()

    @property
    def menu(self) -> Menu:
        return self._menu

    @property
    def _item_count(self) -> int:
        return len(self._menu.items)

    @property
    def _box_width(self) -> int:
        max_name = 0
        max_key = 0
        for item in self._menu.items:
            if isinstance(item, MenuItem):
                max_name = max(max_name, len(item.plain_name))
                max_key = max(max_key, len(item.key_code))
        gap = 2 if max_key > 0 else 0
        return max_name + max_key + gap + 4

    def get_content_width(self, container, viewport):
        return self._box_width

    def get_content_height(self, container, viewport, width):
        return self._item_count + 2

    def _skip_to_first_selectable(self) -> None:
        for i, item in enumerate(self._menu.items):
            if not item.is_separator and not item.disabled:
                self.selected_index = i
                return

    def render_line(self, y: int) -> Strip:
        width = self._box_width
        border_style = self.get_component_rich_style("menubox--border")
        item_style = self.get_component_rich_style("menubox--item")
        active_style = self.get_component_rich_style("menubox--item-active")
        hotkey_style = self.get_component_rich_style("menubox--hotkey")
        disabled_style = self.get_component_rich_style("menubox--disabled")
        sep_style = self.get_component_rich_style("menubox--separator")
        shortcut_style = self.get_component_rich_style("menubox--shortcut")

        inner_width = width - 2

        if y == 0:
            line = Text()
            line.append("┌" + "─" * inner_width + "┐", style=border_style)
            return Strip(line.render(self.app.console))

        if y == self._item_count + 1:
            line = Text()
            line.append("└" + "─" * inner_width + "┘", style=border_style)
            return Strip(line.render(self.app.console))

        item_idx = y - 1
        if item_idx < 0 or item_idx >= self._item_count:
            return Strip.blank(width)

        item = self._menu.items[item_idx]
        is_selected = item_idx == self.selected_index
        line = Text()
        line.append("│", style=border_style)

        if item.is_separator:
            line.append("─" * inner_width, style=sep_style)
        else:
            menu_item: MenuItem = item  # type: ignore[assignment]
            base_style = active_style if is_selected else (disabled_style if menu_item.disabled else item_style)
            hk_style = active_style if is_selected else (disabled_style if menu_item.disabled else hotkey_style)

            line.append(" ", style=base_style)
            name_text = render_tilde_text(menu_item.name, str(base_style), str(hk_style))
            line.append(name_text)

            name_len = len(menu_item.plain_name) + 1
            if menu_item.key_code:
                gap = inner_width - name_len - len(menu_item.key_code) - 1
                if gap > 0:
                    line.append(" " * gap, style=base_style)
                sc_style = active_style if is_selected else shortcut_style
                line.append(menu_item.key_code, style=sc_style)
                line.append(" ", style=base_style)
            elif menu_item.is_submenu:
                gap = inner_width - name_len - 2
                if gap > 0:
                    line.append(" " * gap, style=base_style)
                line.append("►", style=base_style)
                line.append(" ", style=base_style)
            else:
                remaining = inner_width - name_len
                if remaining > 0:
                    line.append(" " * remaining, style=base_style)

        line.append("│", style=border_style)
        return Strip(line.render(self.app.console))

    def navigate(self, direction: int) -> None:
        """Move selection up or down, skipping separators and disabled items."""
        n = self._item_count
        if n == 0:
            return
        idx = self.selected_index
        for _ in range(n):
            idx = (idx + direction) % n
            item = self._menu.items[idx]
            if not item.is_separator and not item.disabled:
                self.selected_index = idx
                return

    def select_current(self) -> MenuItem | None:
        """Select the current item. Returns the MenuItem or None if separator/disabled."""
        if 0 <= self.selected_index < self._item_count:
            item = self._menu.items[self.selected_index]
            if isinstance(item, MenuItem) and not item.disabled:
                return item
        return None

    def find_by_key_code(self, key: str) -> int:
        """Find index of item whose key_code shortcut matches. Returns -1 if not found."""
        key_lower = key.lower()
        for i, item in enumerate(self._menu.items):
            if isinstance(item, MenuItem) and item.key_code and item.key_code.lower() == key_lower and not item.disabled:
                return i
        return -1

    def find_by_hotkey(self, key: str) -> int:
        """Find index of item with given hotkey. Returns -1 if not found."""
        key_lower = key.lower()
        for i, item in enumerate(self._menu.items):
            if isinstance(item, MenuItem) and item.hotkey == key_lower and not item.disabled:
                return i
        return -1

    def on_mouse_move(self, event: events.MouseMove) -> None:
        item_idx = event.y - 1
        if 0 <= item_idx < self._item_count:
            item = self._menu.items[item_idx]
            if not item.is_separator and not item.disabled:
                self.selected_index = item_idx

    def on_mouse_down(self, event: events.MouseDown) -> None:
        if event.button != 1:
            return
        item_idx = event.y - 1
        if 0 <= item_idx < self._item_count:
            item = self._menu.items[item_idx]
            if not item.is_separator and not item.disabled:
                self.selected_index = item_idx
                menu_item: MenuItem = item  # type: ignore[assignment]
                if menu_item.is_submenu:
                    self._open_sub_menu(menu_item)
                else:
                    self.post_message(CommandMessage(menu_item.command, info=menu_item.param))
                    self.post_message(MenuBox.ItemSelected(menu_item))
        event.stop()

    def on_key(self, event: events.Key) -> None:
        if event.key == "up":
            self.navigate(-1)
            event.stop()
        elif event.key == "down":
            self.navigate(1)
            event.stop()
        elif event.key == "enter":
            item = self.select_current()
            if item:
                if item.is_submenu:
                    self._open_sub_menu(item)
                else:
                    self.post_message(CommandMessage(item.command, info=item.param))
                    self.post_message(MenuBox.ItemSelected(item))
            event.stop()
        elif event.key == "right":
            item = self.select_current()
            if item and item.is_submenu:
                self._open_sub_menu(item)
                event.stop()
        elif event.key == "left":
            self._close_sub_menu()
            event.stop()
        elif event.key == "escape":
            self._close_sub_menu()
            self.post_message(MenuBox.Closed())
            event.stop()
        elif len(event.key) == 1:
            idx = self.find_by_hotkey(event.key)
            if idx >= 0:
                self.selected_index = idx
                item = self.select_current()
                if item:
                    if item.is_submenu:
                        self._open_sub_menu(item)
                    else:
                        self.post_message(CommandMessage(item.command, info=item.param))
                        self.post_message(MenuBox.ItemSelected(item))
                event.stop()

    def _open_sub_menu(self, item: MenuItem) -> None:
        self._close_sub_menu()
        if item.sub_menu:
            self._sub_menu_box = MenuBox(menu=item.sub_menu)
            self._sub_menu_box.styles.offset = (self._box_width - 1, self.selected_index)
            self.app.screen.mount(self._sub_menu_box)

    def _close_sub_menu(self) -> None:
        if self._sub_menu_box is not None:
            if self._sub_menu_box.is_mounted:
                self._sub_menu_box.remove()
            self._sub_menu_box = None

    class ItemSelected(CommandMessage):
        def __init__(self, item: MenuItem) -> None:
            super().__init__(item.command, info=item.param)
            self.item = item

    class Closed(CommandMessage):
        def __init__(self) -> None:
            super().__init__(Command.VALID)
