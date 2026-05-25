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

import unittest

from textual_vision.constants import Command
from textual_vision.menus import (
    MenuItem, Separator, Menu, SubMenu, MenuBar, MenuBox,
    parse_hotkey_text, render_tilde_text,
)


class ParseHotkeyTextTest(unittest.TestCase):
    def test_simple_hotkey(self):
        plain, hotkey = parse_hotkey_text("~F~ile")
        self.assertEqual(plain, "File")
        self.assertEqual(hotkey, "f")

    def test_middle_hotkey(self):
        plain, hotkey = parse_hotkey_text("E~x~it")
        self.assertEqual(plain, "Exit")
        self.assertEqual(hotkey, "x")

    def test_no_hotkey(self):
        plain, hotkey = parse_hotkey_text("About")
        self.assertEqual(plain, "About")
        self.assertIsNone(hotkey)

    def test_hotkey_case_insensitive(self):
        _, hotkey = parse_hotkey_text("~N~ew")
        self.assertEqual(hotkey, "n")

    def test_first_highlighted_span_used(self):
        plain, hotkey = parse_hotkey_text("~A~dd ~B~ar")
        self.assertEqual(plain, "Add Bar")
        self.assertEqual(hotkey, "a")

    def test_multi_char_span(self):
        plain, hotkey = parse_hotkey_text("~F1~ Help")
        self.assertEqual(plain, "F1 Help")
        self.assertEqual(hotkey, "f")


class RenderTildeTextTest(unittest.TestCase):
    def test_renders_plain_and_highlight(self):
        text = render_tilde_text("~F~ile")
        self.assertEqual(text.plain, "File")
        self.assertTrue(len(text._spans) > 0)

    def test_no_tildes(self):
        text = render_tilde_text("About")
        self.assertEqual(text.plain, "About")

    def test_multi_char_highlight(self):
        text = render_tilde_text("~F1~ Help")
        self.assertEqual(text.plain, "F1 Help")

    def test_multi_char_alt_key(self):
        text = render_tilde_text("~Alt+X~ Exit")
        self.assertEqual(text.plain, "Alt+X Exit")


class MenuItemTest(unittest.TestCase):
    def test_plain_name(self):
        item = MenuItem("~N~ew", Command.NEW, key_code="Ctrl+N")
        self.assertEqual(item.plain_name, "New")

    def test_hotkey(self):
        item = MenuItem("~O~pen", Command.OPEN)
        self.assertEqual(item.hotkey, "o")

    def test_no_hotkey(self):
        item = MenuItem("About", Command.HELP)
        self.assertIsNone(item.hotkey)

    def test_is_separator_false(self):
        item = MenuItem("Test", Command.VALID)
        self.assertFalse(item.is_separator)

    def test_is_submenu_false(self):
        item = MenuItem("Test", Command.VALID)
        self.assertFalse(item.is_submenu)

    def test_is_submenu_true(self):
        item = SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW))
        self.assertTrue(item.is_submenu)


class SeparatorTest(unittest.TestCase):
    def test_is_separator(self):
        sep = Separator()
        self.assertTrue(sep.is_separator)

    def test_disabled(self):
        sep = Separator()
        self.assertTrue(sep.disabled)

    def test_is_submenu_false(self):
        sep = Separator()
        self.assertFalse(sep.is_submenu)


class SubMenuTest(unittest.TestCase):
    def test_creates_menuitem_with_submenu(self):
        item = SubMenu(
            "~F~ile",
            MenuItem("~N~ew", Command.NEW),
            MenuItem("~O~pen", Command.OPEN),
        )
        self.assertIsNotNone(item.sub_menu)
        self.assertEqual(len(item.sub_menu.items), 2)
        self.assertEqual(item.name, "~F~ile")

    def test_submenu_with_separator(self):
        item = SubMenu(
            "~E~dit",
            MenuItem("~U~ndo", Command.UNDO),
            Separator(),
            MenuItem("~C~ut", Command.CUT),
        )
        self.assertEqual(len(item.sub_menu.items), 3)


class MenuBarBuildTest(unittest.TestCase):
    def test_build_creates_menubar(self):
        bar = MenuBar.build(
            SubMenu(
                "~F~ile",
                MenuItem("~N~ew", Command.NEW, key_code="Ctrl+N"),
                MenuItem("~O~pen", Command.OPEN, key_code="Ctrl+O"),
            ),
            SubMenu(
                "~E~dit",
                MenuItem("~U~ndo", Command.UNDO, key_code="Ctrl+Z"),
            ),
        )
        self.assertIsInstance(bar, MenuBar)
        self.assertEqual(len(bar._top_items), 2)

    def test_find_by_hotkey(self):
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
            SubMenu("~E~dit", MenuItem("~U~ndo", Command.UNDO)),
        )
        self.assertEqual(bar.find_by_hotkey("f"), 0)
        self.assertEqual(bar.find_by_hotkey("e"), 1)
        self.assertEqual(bar.find_by_hotkey("z"), -1)

    def test_find_by_hotkey_skips_disabled(self):
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
        )
        bar._top_items[0].disabled = True
        self.assertEqual(bar.find_by_hotkey("f"), -1)

    def test_item_x_offset(self):
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
            SubMenu("~E~dit", MenuItem("~U~ndo", Command.UNDO)),
        )
        self.assertEqual(bar._item_x_offset(0), 1)
        self.assertEqual(bar._item_x_offset(1), 1 + len("File") + 2)


class MenuBarActivationTest(unittest.TestCase):
    def test_activate_sets_active(self):
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
        )
        bar.activate()
        self.assertTrue(bar.active)
        self.assertEqual(bar.selected_index, 0)

    def test_deactivate_clears(self):
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
        )
        bar.activate()
        bar.deactivate()
        self.assertFalse(bar.active)
        self.assertEqual(bar.selected_index, -1)

    def test_f10_toggles(self):
        from textual.events import Key
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
        )
        event = Key("f10", None)
        self.assertTrue(bar.tv_handle_key(event))
        self.assertTrue(bar.active)

        event2 = Key("f10", None)
        self.assertTrue(bar.tv_handle_key(event2))
        self.assertFalse(bar.active)


class MenuBarNavigationTest(unittest.TestCase):
    def test_left_right_navigation(self):
        from textual.events import Key
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
            SubMenu("~E~dit", MenuItem("~U~ndo", Command.UNDO)),
            SubMenu("~H~elp", MenuItem("~A~bout", Command.HELP)),
        )
        bar.activate()
        self.assertEqual(bar.selected_index, 0)

        bar.tv_handle_key(Key("right", None))
        self.assertEqual(bar.selected_index, 1)

        bar.tv_handle_key(Key("right", None))
        self.assertEqual(bar.selected_index, 2)

        bar.tv_handle_key(Key("right", None))
        self.assertEqual(bar.selected_index, 0)

        bar.tv_handle_key(Key("left", None))
        self.assertEqual(bar.selected_index, 2)

    def test_escape_deactivates(self):
        from textual.events import Key
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
        )
        bar.activate()
        bar.tv_handle_key(Key("escape", None))
        self.assertFalse(bar.active)

    def test_inactive_ignores_arrows(self):
        from textual.events import Key
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
        )
        self.assertFalse(bar.tv_handle_key(Key("right", None)))

    def test_alt_hotkey_activates_and_selects(self):
        from textual.events import Key
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
            SubMenu("~E~dit", MenuItem("~U~ndo", Command.UNDO)),
        )
        result = bar.tv_handle_key(Key("alt+e", None))
        self.assertTrue(result)
        self.assertTrue(bar.active)
        self.assertEqual(bar.selected_index, 1)


class MenuBarUnmountedTest(unittest.TestCase):
    def test_alt_hotkey_open_menu_box_safe_when_unmounted(self):
        """_open_menu_box must not crash when MenuBar is not mounted in an app."""
        from textual.events import Key
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
            SubMenu("~E~dit", MenuItem("~U~ndo", Command.UNDO)),
        )
        result = bar.tv_handle_key(Key("alt+e", None))
        self.assertTrue(result)
        self.assertTrue(bar.active)
        self.assertEqual(bar.selected_index, 1)
        self.assertIsNone(bar._menu_box)

    def test_enter_open_menu_box_safe_when_unmounted(self):
        """Down/Enter to open dropdown must not crash when unmounted."""
        from textual.events import Key
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
        )
        bar.activate()
        result = bar.tv_handle_key(Key("enter", None))
        self.assertTrue(result)
        self.assertIsNone(bar._menu_box)

    def test_navigate_with_open_box_safe_when_unmounted(self):
        """Arrow navigation re-opens menu box; must not crash when unmounted."""
        from textual.events import Key
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
            SubMenu("~E~dit", MenuItem("~U~ndo", Command.UNDO)),
        )
        bar.activate()
        bar.tv_handle_key(Key("right", None))
        self.assertEqual(bar.selected_index, 1)
        self.assertIsNone(bar._menu_box)


class MenuBarMouseHoverTest(unittest.TestCase):
    def test_hover_over_item_when_active_changes_selection(self):
        from textual.events import MouseMove
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
            SubMenu("~E~dit", MenuItem("~U~ndo", Command.UNDO)),
        )
        bar.activate()
        self.assertEqual(bar.selected_index, 0)
        offset = 1 + len("File") + 2
        event = MouseMove(bar, x=offset, y=0, delta_x=0, delta_y=0,
                          button=0, shift=False, meta=False, ctrl=False)
        bar.on_mouse_move(event)
        self.assertEqual(bar.selected_index, 1)

    def test_hover_ignored_when_inactive(self):
        from textual.events import MouseMove
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
            SubMenu("~E~dit", MenuItem("~U~ndo", Command.UNDO)),
        )
        offset = 1 + len("File") + 2
        event = MouseMove(bar, x=offset, y=0, delta_x=0, delta_y=0,
                          button=0, shift=False, meta=False, ctrl=False)
        bar.on_mouse_move(event)
        self.assertEqual(bar.selected_index, -1)


class MenuBoxMouseHoverTest(unittest.TestCase):
    def test_hover_highlights_item(self):
        from textual.events import MouseMove
        menu = Menu(items=[
            MenuItem("~N~ew", Command.NEW),
            MenuItem("~O~pen", Command.OPEN),
        ])
        box = MenuBox(menu=menu)
        self.assertEqual(box.selected_index, 0)
        event = MouseMove(box, x=5, y=2, delta_x=0, delta_y=0,
                          button=0, shift=False, meta=False, ctrl=False)
        box.on_mouse_move(event)
        self.assertEqual(box.selected_index, 1)

    def test_hover_skips_separator(self):
        from textual.events import MouseMove
        menu = Menu(items=[
            MenuItem("~N~ew", Command.NEW),
            Separator(),
            MenuItem("~O~pen", Command.OPEN),
        ])
        box = MenuBox(menu=menu)
        event = MouseMove(box, x=5, y=2, delta_x=0, delta_y=0,
                          button=0, shift=False, meta=False, ctrl=False)
        box.on_mouse_move(event)
        self.assertEqual(box.selected_index, 0)


class MenuBarCssTest(unittest.TestCase):
    def test_hotkey_uses_menu_hotkey_variable(self):
        """Menu bar hotkey letters must use $menu-hotkey (red), not $warning or other."""
        css = MenuBar.DEFAULT_CSS
        hotkey_section = css.split("menubar--hotkey")[1].split("}")[0]
        self.assertIn("$menu-hotkey", hotkey_section)

    def test_item_uses_text_color(self):
        """Menu bar normal items must use $text color."""
        css = MenuBar.DEFAULT_CSS
        item_section = css.split("menubar--item")[1].split("}")[0]
        self.assertIn("$text", item_section)

    def test_all_component_classes_have_background(self):
        """All menu bar component classes must set explicit background to prevent bleed-through."""
        css = MenuBar.DEFAULT_CSS
        for cc in ("menubar--item", "menubar--hotkey", "menubar--disabled"):
            section = css.split(cc)[1].split("}")[0]
            self.assertIn("background:", section, f"{cc} missing explicit background")


class MenuBarMouseTest(unittest.TestCase):
    def test_hit_test_item_first(self):
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
            SubMenu("~E~dit", MenuItem("~U~ndo", Command.UNDO)),
        )
        self.assertEqual(bar._hit_test_item(1), 0)
        self.assertEqual(bar._hit_test_item(2), 0)

    def test_hit_test_item_second(self):
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
            SubMenu("~E~dit", MenuItem("~U~ndo", Command.UNDO)),
        )
        offset = 1 + len("File") + 2
        self.assertEqual(bar._hit_test_item(offset), 1)

    def test_hit_test_item_miss(self):
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
        )
        self.assertEqual(bar._hit_test_item(100), -1)
        self.assertEqual(bar._hit_test_item(0), -1)


class MenuBarKeyForwardingTest(unittest.TestCase):
    def test_enter_forwarded_to_menu_box_selects_item(self):
        """When menu bar is active with an open MenuBox, Enter should be forwarded."""
        from textual.events import Key
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
        )
        bar.activate()
        bar._menu_box = MenuBox(
            menu=Menu(items=[
                MenuItem("~N~ew", Command.NEW),
                MenuItem("~O~pen", Command.OPEN),
            ]),
        )
        result = bar.tv_handle_key(Key("down", None))
        self.assertTrue(result)
        self.assertEqual(bar._menu_box.selected_index, 1)

    def test_up_down_forwarded_to_menu_box(self):
        from textual.events import Key
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
        )
        bar.activate()
        bar._menu_box = MenuBox(
            menu=Menu(items=[
                MenuItem("~N~ew", Command.NEW),
                MenuItem("~O~pen", Command.OPEN),
                MenuItem("~S~ave", Command.SAVE),
            ]),
        )
        bar.tv_handle_key(Key("down", None))
        self.assertEqual(bar._menu_box.selected_index, 1)
        bar.tv_handle_key(Key("up", None))
        self.assertEqual(bar._menu_box.selected_index, 0)


class MenuBoxFindByKeyCodeTest(unittest.TestCase):
    def test_find_by_key_code_match(self):
        menu = Menu(items=[
            MenuItem("~N~ew", Command.NEW, key_code="Ctrl+N"),
            MenuItem("~O~pen", Command.OPEN, key_code="Ctrl+O"),
        ])
        box = MenuBox(menu=menu)
        self.assertEqual(box.find_by_key_code("ctrl+n"), 0)
        self.assertEqual(box.find_by_key_code("ctrl+o"), 1)

    def test_find_by_key_code_case_insensitive(self):
        menu = Menu(items=[
            MenuItem("~N~ew", Command.NEW, key_code="Ctrl+N"),
        ])
        box = MenuBox(menu=menu)
        self.assertEqual(box.find_by_key_code("Ctrl+N"), 0)
        self.assertEqual(box.find_by_key_code("ctrl+n"), 0)

    def test_find_by_key_code_no_match(self):
        menu = Menu(items=[
            MenuItem("~N~ew", Command.NEW, key_code="Ctrl+N"),
        ])
        box = MenuBox(menu=menu)
        self.assertEqual(box.find_by_key_code("ctrl+s"), -1)

    def test_find_by_key_code_skips_disabled(self):
        menu = Menu(items=[
            MenuItem("~N~ew", Command.NEW, key_code="Ctrl+N", disabled=True),
        ])
        box = MenuBox(menu=menu)
        self.assertEqual(box.find_by_key_code("ctrl+n"), -1)


class MenuBarCloseSubMenuTest(unittest.TestCase):
    def test_close_menu_box_calls_close_sub_menu(self):
        """_close_menu_box must call _close_sub_menu on the MenuBox before removing it."""
        import inspect
        source = inspect.getsource(MenuBar._close_menu_box)
        self.assertIn("_close_sub_menu", source)

    def test_close_menu_box_clears_sub_menu_reference(self):
        """_close_menu_box must clear the sub-menu reference via _close_sub_menu."""
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
        )
        bar.activate()
        box = MenuBox(
            menu=Menu(items=[
                MenuItem("~N~ew", Command.NEW),
                MenuItem("~O~pen", Command.OPEN),
            ]),
        )
        sub_box = MenuBox(menu=Menu(items=[MenuItem("~S~ub", Command.VALID)]))
        box._sub_menu_box = sub_box
        bar._menu_box = box

        box._close_sub_menu()
        self.assertIsNone(box._sub_menu_box)


class MenuBarDismissOnUnhandledKeyTest(unittest.TestCase):
    def test_unhandled_key_deactivates_menu(self):
        """An unhandled key while menu is active must dismiss the menu."""
        from textual.events import Key
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
        )
        bar.activate()
        self.assertTrue(bar.active)
        result = bar.tv_handle_key(Key("ctrl+n", None))
        self.assertFalse(result)
        self.assertFalse(bar.active)

    def test_unhandled_key_returns_false_for_propagation(self):
        """Unhandled key must return False so Textual processes it normally."""
        from textual.events import Key
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
        )
        bar.activate()
        result = bar.tv_handle_key(Key("ctrl+s", None))
        self.assertFalse(result)


class MenuBarKeyForwardingToMenuBoxTest(unittest.TestCase):
    def test_keys_forwarded_when_box_open(self):
        """When MenuBox is open, up/down/enter/escape/chars forwarded to it."""
        from textual.events import Key
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
        )
        bar.activate()
        bar._menu_box = MenuBox(
            menu=Menu(items=[
                MenuItem("~N~ew", Command.NEW),
                MenuItem("~O~pen", Command.OPEN),
                MenuItem("~S~ave", Command.SAVE),
            ]),
        )
        bar.tv_handle_key(Key("down", None))
        self.assertEqual(bar._menu_box.selected_index, 1)

        bar.tv_handle_key(Key("down", None))
        self.assertEqual(bar._menu_box.selected_index, 2)

        bar.tv_handle_key(Key("up", None))
        self.assertEqual(bar._menu_box.selected_index, 1)

    def test_left_right_not_forwarded_without_box(self):
        """Without open MenuBox, left/right navigate the menu bar items."""
        from textual.events import Key
        bar = MenuBar.build(
            SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
            SubMenu("~E~dit", MenuItem("~U~ndo", Command.UNDO)),
        )
        bar.activate()
        self.assertEqual(bar.selected_index, 0)
        bar.tv_handle_key(Key("right", None))
        self.assertEqual(bar.selected_index, 1)


class MenuBoxTest(unittest.TestCase):
    def test_navigation(self):
        menu = Menu(items=[
            MenuItem("~N~ew", Command.NEW),
            Separator(),
            MenuItem("~O~pen", Command.OPEN),
        ])
        box = MenuBox(menu=menu)
        self.assertEqual(box.selected_index, 0)

        box.navigate(1)
        self.assertEqual(box.selected_index, 2)

        box.navigate(1)
        self.assertEqual(box.selected_index, 0)

    def test_navigate_skips_disabled(self):
        menu = Menu(items=[
            MenuItem("~N~ew", Command.NEW),
            MenuItem("Disabled", Command.VALID, disabled=True),
            MenuItem("~O~pen", Command.OPEN),
        ])
        box = MenuBox(menu=menu)
        box.navigate(1)
        self.assertEqual(box.selected_index, 2)

    def test_select_current(self):
        menu = Menu(items=[
            MenuItem("~N~ew", Command.NEW),
            MenuItem("~O~pen", Command.OPEN),
        ])
        box = MenuBox(menu=menu)
        item = box.select_current()
        self.assertIsNotNone(item)
        self.assertEqual(item.command, Command.NEW)

    def test_select_disabled_returns_none(self):
        menu = Menu(items=[
            MenuItem("Disabled", Command.VALID, disabled=True),
            MenuItem("~O~pen", Command.OPEN),
        ])
        box = MenuBox(menu=menu)
        box.selected_index = 0
        item = box.select_current()
        self.assertIsNone(item)

    def test_find_by_hotkey(self):
        menu = Menu(items=[
            MenuItem("~N~ew", Command.NEW),
            Separator(),
            MenuItem("~O~pen", Command.OPEN),
        ])
        box = MenuBox(menu=menu)
        self.assertEqual(box.find_by_hotkey("n"), 0)
        self.assertEqual(box.find_by_hotkey("o"), 2)
        self.assertEqual(box.find_by_hotkey("z"), -1)

    def test_box_width(self):
        menu = Menu(items=[
            MenuItem("~N~ew", Command.NEW, key_code="Ctrl+N"),
            MenuItem("~O~pen", Command.OPEN, key_code="Ctrl+O"),
        ])
        box = MenuBox(menu=menu)
        width = box._box_width
        self.assertGreater(width, len("Open") + len("Ctrl+O"))

    def test_skip_to_first_selectable(self):
        menu = Menu(items=[
            Separator(),
            MenuItem("Disabled", Command.VALID, disabled=True),
            MenuItem("~O~pen", Command.OPEN),
        ])
        box = MenuBox(menu=menu)
        self.assertEqual(box.selected_index, 2)


class MenuBoxMouseTest(unittest.TestCase):
    def test_click_on_item_selects(self):
        from textual.events import MouseDown
        menu = Menu(items=[
            MenuItem("~N~ew", Command.NEW),
            MenuItem("~O~pen", Command.OPEN),
        ])
        box = MenuBox(menu=menu)
        event = MouseDown(box, x=5, y=2, delta_x=0, delta_y=0,
                          button=1, shift=False, meta=False, ctrl=False)
        box.on_mouse_down(event)
        self.assertEqual(box.selected_index, 1)

    def test_click_on_separator_ignored(self):
        from textual.events import MouseDown
        menu = Menu(items=[
            MenuItem("~N~ew", Command.NEW),
            Separator(),
            MenuItem("~O~pen", Command.OPEN),
        ])
        box = MenuBox(menu=menu)
        event = MouseDown(box, x=5, y=2, delta_x=0, delta_y=0,
                          button=1, shift=False, meta=False, ctrl=False)
        box.on_mouse_down(event)
        self.assertEqual(box.selected_index, 0)

    def test_click_on_border_ignored(self):
        from textual.events import MouseDown
        menu = Menu(items=[
            MenuItem("~N~ew", Command.NEW),
            MenuItem("~O~pen", Command.OPEN),
        ])
        box = MenuBox(menu=menu)
        event = MouseDown(box, x=5, y=0, delta_x=0, delta_y=0,
                          button=1, shift=False, meta=False, ctrl=False)
        box.on_mouse_down(event)
        self.assertEqual(box.selected_index, 0)


if __name__ == "__main__":
    unittest.main()
