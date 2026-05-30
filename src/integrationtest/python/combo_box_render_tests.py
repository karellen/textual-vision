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

from textual.app import App, ComposeResult

from textual_vision.combo_box import ComboBox, _DropDownButton, _DropDownPopup
from textual_vision.group import Group
from textual_vision.input_line import InputLine


COLORS = ["Black", "Blue", "Green", "Cyan",
          "Red", "Magenta", "Brown", "Light Gray"]


def strip_to_text(strip):
    return "".join(seg.text for seg in strip._segments)


class _ThemedApp(App):
    """Base test app that registers TV themes."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from textual_vision.themes import register_themes
        register_themes(self)
        self.theme = "turbo-pascal"


class ComboBoxInGroupApp(_ThemedApp):
    """Realistic setup: ComboBox inside a Group (like a Dialog)."""

    CSS = """
    Screen {
        layers: default menus;
    }
    Group {
        width: 1fr;
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        with Group():
            yield ComboBox(items=COLORS)


class SimpleComboBoxApp(_ThemedApp):
    """Minimal ComboBox without Group (tests standalone behavior)."""

    CSS = """
    Screen {
        layers: default menus;
    }
    ComboBox {
        width: 30;
        height: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield ComboBox(items=COLORS)


class ReadOnlyComboBoxApp(_ThemedApp):
    """ComboBox in read-only (drop-down only) mode inside a Group."""

    CSS = """
    Screen {
        layers: default menus;
    }
    Group {
        width: 1fr;
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        with Group():
            yield ComboBox(items=COLORS, editable=False)


class SimpleReadOnlyComboBoxApp(_ThemedApp):
    """Read-only ComboBox without Group."""

    CSS = """
    Screen {
        layers: default menus;
    }
    ComboBox {
        width: 30;
        height: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield ComboBox(items=COLORS, editable=False)


class ComboBoxCompositionTest(unittest.IsolatedAsyncioTestCase):
    """Test that ComboBox composes its children correctly."""

    async def test_has_input_line(self):
        app = SimpleComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            inputs = cb.query(InputLine)
            self.assertEqual(len(inputs), 1)

    async def test_has_dropdown_button(self):
        app = SimpleComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            buttons = cb.query(_DropDownButton)
            self.assertEqual(len(buttons), 1)

    async def test_input_line_reference(self):
        app = SimpleComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            self.assertIsNotNone(cb.input_line)
            self.assertIsInstance(cb.input_line, InputLine)

    async def test_combobox_height_is_one(self):
        app = SimpleComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            self.assertEqual(cb.size.height, 1)

    async def test_dropdown_button_renders_arrow(self):
        app = SimpleComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            btn = app.query_one(_DropDownButton)
            text = strip_to_text(btn.render_line(0))
            self.assertIn("▼", text)


class ComboBoxFocusTest(unittest.IsolatedAsyncioTestCase):
    """Test that TV focus chain reaches InputLine through ComboBox Group."""

    async def test_group_auto_focuses_combobox(self):
        """Parent Group should auto-select ComboBox as its current."""
        app = ComboBoxInGroupApp()
        async with app.run_test(size=(50, 20)) as pilot:
            await pilot.pause()
            groups = [w for w in app.screen.query(Group) if not isinstance(w, ComboBox)]
            group = groups[0]
            self.assertIsInstance(
                group.current, ComboBox,
                f"Group.current should be ComboBox, "
                f"got {type(group.current).__name__}")

    async def test_combobox_focuses_input_line(self):
        """ComboBox (as Group) should auto-select InputLine as its current."""
        app = ComboBoxInGroupApp()
        async with app.run_test(size=(50, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            self.assertIsInstance(
                cb.current, InputLine,
                f"ComboBox.current should be InputLine, "
                f"got {type(cb.current).__name__}")

    async def test_combobox_is_selectable(self):
        """ComboBox should be selectable as a Group in the parent."""
        app = ComboBoxInGroupApp()
        async with app.run_test(size=(50, 20)) as pilot:
            await pilot.pause()
            groups = [w for w in app.screen.query(Group) if not isinstance(w, ComboBox)]
            group = groups[0]
            selectable = group._selectable_children()
            self.assertTrue(
                any(isinstance(c, ComboBox) for c in selectable),
                "ComboBox should be in parent Group's selectable children")


class ComboBoxTypingTest(unittest.IsolatedAsyncioTestCase):
    """Test typing in the InputLine when ComboBox is inside a Group."""

    async def test_typing_updates_input_data(self):
        app = ComboBoxInGroupApp()
        async with app.run_test(size=(50, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            inp = cb.input_line
            await pilot.press("H", "e", "l", "l", "o")
            await pilot.pause()
            self.assertEqual(inp.data, "Hello",
                             f"InputLine.data should be 'Hello', got: {inp.data!r}")

    async def test_typing_updates_combobox_value(self):
        app = ComboBoxInGroupApp()
        async with app.run_test(size=(50, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            await pilot.press("T", "e", "s", "t")
            await pilot.pause()
            self.assertEqual(cb.value, "Test",
                             f"ComboBox.value should be 'Test', got: {cb.value!r}")


class ComboBoxPopupTest(unittest.IsolatedAsyncioTestCase):
    """Test popup open/close lifecycle."""

    async def test_no_popup_initially(self):
        app = SimpleComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            popups = app.screen.query(_DropDownPopup)
            self.assertEqual(len(popups), 0)

    async def test_click_button_opens_popup(self):
        app = SimpleComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            btn = app.query_one(_DropDownButton)
            await pilot.click(btn)
            await pilot.pause()
            popups = app.screen.query(_DropDownPopup)
            self.assertEqual(len(popups), 1)

    async def test_popup_has_all_items(self):
        app = SimpleComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            btn = app.query_one(_DropDownButton)
            await pilot.click(btn)
            await pilot.pause()
            popup = app.screen.query_one(_DropDownPopup)
            self.assertEqual(popup.range, len(COLORS))

    async def test_popup_positioned_below_combobox(self):
        app = SimpleComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            btn = app.query_one(_DropDownButton)
            await pilot.click(btn)
            await pilot.pause()
            popup = app.screen.query_one(_DropDownPopup)
            cb_region = cb.region
            self.assertEqual(popup.styles.offset.y.value,
                             cb_region.y + cb_region.height)

    async def test_popup_width_matches_combobox(self):
        app = SimpleComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            btn = app.query_one(_DropDownButton)
            await pilot.click(btn)
            await pilot.pause()
            popup = app.screen.query_one(_DropDownPopup)
            self.assertEqual(popup.styles.width.value, cb.region.width)

    async def test_click_button_again_closes_popup(self):
        app = SimpleComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            btn = app.query_one(_DropDownButton)
            await pilot.click(btn)
            await pilot.pause()
            self.assertEqual(len(app.screen.query(_DropDownPopup)), 1)
            await pilot.click(btn)
            await pilot.pause()
            self.assertEqual(len(app.screen.query(_DropDownPopup)), 0)

    async def test_popup_renders_first_item(self):
        app = SimpleComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            btn = app.query_one(_DropDownButton)
            await pilot.click(btn)
            await pilot.pause()
            popup = app.screen.query_one(_DropDownPopup)
            text = strip_to_text(popup.render_line(0))
            self.assertIn("Black", text)

    async def test_ctrl_down_opens_popup(self):
        """Ctrl+Down should open the popup (TV convention)."""
        app = ComboBoxInGroupApp()
        async with app.run_test(size=(50, 20)) as pilot:
            await pilot.pause()
            await pilot.press("ctrl+down")
            await pilot.pause()
            popups = app.screen.query(_DropDownPopup)
            self.assertEqual(len(popups), 1,
                             "Ctrl+Down should open the popup")


class ComboBoxSelectionTest(unittest.IsolatedAsyncioTestCase):
    """Test that selecting an item fills the InputLine."""

    async def test_select_item_fills_input(self):
        app = SimpleComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            btn = app.query_one(_DropDownButton)
            await pilot.click(btn)
            await pilot.pause()
            popup = app.screen.query_one(_DropDownPopup)
            popup.focus_item(2)
            popup.select_item(2)
            await pilot.pause()
            self.assertEqual(cb.input_line.data, "Green")

    async def test_select_item_updates_value(self):
        app = SimpleComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            btn = app.query_one(_DropDownButton)
            await pilot.click(btn)
            await pilot.pause()
            popup = app.screen.query_one(_DropDownPopup)
            popup.select_item(4)
            await pilot.pause()
            self.assertEqual(cb.value, "Red")

    async def test_select_item_closes_popup(self):
        app = SimpleComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            btn = app.query_one(_DropDownButton)
            await pilot.click(btn)
            await pilot.pause()
            popup = app.screen.query_one(_DropDownPopup)
            popup.select_item(0)
            await pilot.pause()
            self.assertEqual(len(app.screen.query(_DropDownPopup)), 0)


class ComboBoxKeyboardTest(unittest.IsolatedAsyncioTestCase):
    """Test keyboard interaction with the popup."""

    async def test_escape_closes_popup(self):
        app = SimpleComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            btn = app.query_one(_DropDownButton)
            await pilot.click(btn)
            await pilot.pause()
            self.assertEqual(len(app.screen.query(_DropDownPopup)), 1)
            await pilot.press("escape")
            await pilot.pause()
            self.assertEqual(len(app.screen.query(_DropDownPopup)), 0)

    async def test_enter_selects_and_closes(self):
        app = SimpleComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            btn = app.query_one(_DropDownButton)
            await pilot.click(btn)
            await pilot.pause()
            await pilot.press("down", "down")
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            self.assertEqual(len(app.screen.query(_DropDownPopup)), 0,
                             "Enter should close the popup")
            self.assertEqual(cb.value, "Green",
                             "Enter should select the focused item")

    async def test_arrow_keys_navigate_popup(self):
        app = SimpleComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            btn = app.query_one(_DropDownButton)
            await pilot.click(btn)
            await pilot.pause()
            popup = app.screen.query_one(_DropDownPopup)
            self.assertEqual(popup.focused, 0)
            await pilot.press("down")
            await pilot.pause()
            self.assertEqual(popup.focused, 1)
            await pilot.press("down")
            await pilot.pause()
            self.assertEqual(popup.focused, 2)
            await pilot.press("up")
            await pilot.pause()
            self.assertEqual(popup.focused, 1)

    async def test_arrow_keys_do_not_leak_to_parent(self):
        """Arrow keys in popup must not affect other ComboBoxes in the Group."""
        app = ComboBoxInGroupApp()
        async with app.run_test(size=(50, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            btn = cb.query_one(_DropDownButton)
            await pilot.click(btn)
            await pilot.pause()
            popup = app.screen.query_one(_DropDownPopup)
            self.assertEqual(popup.focused, 0)
            await pilot.press("down", "down", "down")
            await pilot.pause()
            self.assertEqual(popup.focused, 3,
                             "Arrow keys should navigate inside the popup")


class ComboBoxReadOnlyInitTest(unittest.IsolatedAsyncioTestCase):
    """Test read-only ComboBox construction and properties."""

    async def test_editable_default_true(self):
        app = SimpleComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            self.assertTrue(cb.editable)

    async def test_read_only_flag(self):
        app = SimpleReadOnlyComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            self.assertFalse(cb.editable)

    async def test_read_only_has_input_line(self):
        app = SimpleReadOnlyComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            self.assertIsNotNone(cb.input_line)

    async def test_read_only_has_button(self):
        app = SimpleReadOnlyComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            buttons = cb.query(_DropDownButton)
            self.assertEqual(len(buttons), 1)


class ComboBoxReadOnlyTypingTest(unittest.IsolatedAsyncioTestCase):
    """Test that typing is blocked in read-only mode."""

    async def test_typing_does_not_change_value(self):
        app = ReadOnlyComboBoxApp()
        async with app.run_test(size=(50, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            await pilot.press("H", "e", "l", "l", "o")
            await pilot.pause()
            self.assertEqual(cb.value, "",
                             "Read-only ComboBox should not accept typed input")

    async def test_typing_does_not_change_input_data(self):
        app = ReadOnlyComboBoxApp()
        async with app.run_test(size=(50, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            inp = cb.input_line
            await pilot.press("A", "B", "C")
            await pilot.pause()
            self.assertEqual(inp.data, "",
                             "Read-only InputLine should not accept typed input")


class ComboBoxReadOnlySelectionTest(unittest.IsolatedAsyncioTestCase):
    """Test that dropdown selection still works in read-only mode."""

    async def test_click_opens_popup(self):
        app = SimpleReadOnlyComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            btn = app.query_one(_DropDownButton)
            await pilot.click(btn)
            await pilot.pause()
            popups = app.screen.query(_DropDownPopup)
            self.assertEqual(len(popups), 1)

    async def test_select_fills_value(self):
        app = SimpleReadOnlyComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            btn = app.query_one(_DropDownButton)
            await pilot.click(btn)
            await pilot.pause()
            popup = app.screen.query_one(_DropDownPopup)
            popup.select_item(3)
            await pilot.pause()
            self.assertEqual(cb.value, "Cyan",
                             f"Should be 'Cyan', got: {cb.value!r}")

    async def test_select_fills_input_display(self):
        app = SimpleReadOnlyComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            btn = app.query_one(_DropDownButton)
            await pilot.click(btn)
            await pilot.pause()
            popup = app.screen.query_one(_DropDownPopup)
            popup.select_item(1)
            await pilot.pause()
            self.assertEqual(cb.input_line.data, "Blue",
                             f"Should be 'Blue', got: {cb.input_line.data!r}")

    async def test_typing_after_selection_does_not_change(self):
        """After selecting an item, typing should not alter the value."""
        app = ReadOnlyComboBoxApp()
        async with app.run_test(size=(50, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            btn = app.query_one(_DropDownButton)
            await pilot.click(btn)
            await pilot.pause()
            popup = app.screen.query_one(_DropDownPopup)
            popup.select_item(2)
            await pilot.pause()
            self.assertEqual(cb.value, "Green")
            await pilot.press("X", "Y", "Z")
            await pilot.pause()
            self.assertEqual(cb.value, "Green",
                             "Typing after selection should not change value")


class ComboBoxReadOnlyKeyboardNavTest(unittest.IsolatedAsyncioTestCase):
    """Test up/down keyboard navigation in read-only mode."""

    async def test_down_key_selects_first_item(self):
        """In read-only mode, Down arrow should select the first item."""
        app = ReadOnlyComboBoxApp()
        async with app.run_test(size=(50, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            await pilot.press("down")
            await pilot.pause()
            self.assertEqual(cb.value, "Black",
                             f"Down should select first item, got: {cb.value!r}")

    async def test_down_key_cycles_forward(self):
        app = ReadOnlyComboBoxApp()
        async with app.run_test(size=(50, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            await pilot.press("down")
            await pilot.pause()
            self.assertEqual(cb.value, "Black")
            await pilot.press("down")
            await pilot.pause()
            self.assertEqual(cb.value, "Blue",
                             f"Second Down should select 'Blue', got: {cb.value!r}")

    async def test_up_key_cycles_backward(self):
        app = ReadOnlyComboBoxApp()
        async with app.run_test(size=(50, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            await pilot.press("down", "down", "down")
            await pilot.pause()
            self.assertEqual(cb.value, "Green")
            await pilot.press("up")
            await pilot.pause()
            self.assertEqual(cb.value, "Blue",
                             f"Up should go back to 'Blue', got: {cb.value!r}")

    async def test_up_key_stops_at_first(self):
        app = ReadOnlyComboBoxApp()
        async with app.run_test(size=(50, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            await pilot.press("down")
            await pilot.pause()
            self.assertEqual(cb.value, "Black")
            await pilot.press("up")
            await pilot.pause()
            self.assertEqual(cb.value, "Black",
                             "Up at first item should stay at first")

    async def test_down_key_stops_at_last(self):
        app = ReadOnlyComboBoxApp()
        async with app.run_test(size=(50, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            for _ in range(len(COLORS) + 5):
                await pilot.press("down")
            await pilot.pause()
            self.assertEqual(cb.value, "Light Gray",
                             f"Should stop at last item, got: {cb.value!r}")


class ComboBoxInWindowApp(App):
    """ComboBox inside a Window on a DeskTop — tests lifecycle cleanup."""

    CSS = """
    Screen {
        layers: background windows menus;
    }
    """

    def __init__(self):
        super().__init__()
        from textual_vision.themes import register_themes
        register_themes(self)
        self.theme = "turbo-pascal"

    def compose(self) -> ComposeResult:
        from textual_vision.desktop import DeskTop
        yield DeskTop()

    def on_mount(self):
        from textual_vision.window import Window
        win = Window(title="Test")
        win.styles.width = 40
        win.styles.height = 10
        self.query_one("DeskTop").insert_window(win)

    def _mount_combo_in_window(self, items):
        from textual_vision.window import Window
        win = self.query_one(Window)
        content = win.query_one(".tv-window-content")
        cb = ComboBox(items=items)
        content.mount(cb)
        return cb


class ComboBoxSecondOpenTest(unittest.IsolatedAsyncioTestCase):
    """Regression: reopening popup after selecting a mid-list item must show all items.

    Root cause: _DropDownPopup.on_mount calls focus_item() when self.size is (0,0),
    causing _page_size()=1 and _top_item to be set to the focused index. render_line
    is called BEFORE on_resize corrects _top_item, so the user sees only the tail of
    the list.
    """

    async def test_reopen_first_render_top_item_correct(self):
        """Select 'Magenta' (index 5), reopen popup — the FIRST render must
        have top_item=0, not 5. Captures the value at render time, not after
        on_resize corrects it."""
        app = SimpleComboBoxApp()
        first_render_top_items = []

        orig_render = _DropDownPopup.render_line.__wrapped__ \
            if hasattr(_DropDownPopup.render_line, '__wrapped__') \
            else _DropDownPopup.render_line

        def capturing_render(self_popup, y):
            if y == 0 and not first_render_top_items:
                first_render_top_items.append(self_popup._top_item)
            return orig_render(self_popup, y)

        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            btn = app.query_one(_DropDownButton)

            await pilot.click(btn)
            await pilot.pause()
            popup = app.screen.query_one(_DropDownPopup)
            popup.select_item(5)
            await pilot.pause()
            self.assertEqual(cb.value, "Magenta")

            first_render_top_items.clear()
            _DropDownPopup.render_line = capturing_render
            try:
                await pilot.click(btn)
                await pilot.pause()
                self.assertTrue(len(first_render_top_items) > 0,
                                "render_line(0) should have been called")
                self.assertEqual(first_render_top_items[0], 0,
                                 f"First render must have top_item=0, "
                                 f"got top_item={first_render_top_items[0]}")
            finally:
                _DropDownPopup.render_line = orig_render

    async def test_reopen_after_selection_shows_all_items(self):
        """Select 'Magenta' (index 5), reopen popup — all 8 items must be visible."""
        app = SimpleComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            btn = app.query_one(_DropDownButton)

            await pilot.click(btn)
            await pilot.pause()
            popup = app.screen.query_one(_DropDownPopup)
            popup.select_item(5)
            await pilot.pause()
            self.assertEqual(cb.value, "Magenta")
            self.assertEqual(len(app.screen.query(_DropDownPopup)), 0,
                             "Popup should be closed after selection")

            await pilot.click(btn)
            await pilot.pause()
            popup2 = app.screen.query_one(_DropDownPopup)
            self.assertEqual(popup2.range, 8, "All 8 items must be in the popup")
            first_line = strip_to_text(popup2.render_line(0))
            self.assertIn("Black", first_line,
                          f"First rendered line should be 'Black', got: {first_line!r}")
            self.assertEqual(popup2.top_item, 0,
                             f"top_item must be 0 to show all items, got: {popup2.top_item}")

    async def test_reopen_after_last_item_shows_all(self):
        """Select 'Light Gray' (index 7), reopen — must still show from top."""
        app = SimpleComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            cb = app.query_one(ComboBox)
            btn = app.query_one(_DropDownButton)

            await pilot.click(btn)
            await pilot.pause()
            popup = app.screen.query_one(_DropDownPopup)
            popup.select_item(7)
            await pilot.pause()
            self.assertEqual(cb.value, "Light Gray")

            await pilot.click(btn)
            await pilot.pause()
            popup2 = app.screen.query_one(_DropDownPopup)
            first_line = strip_to_text(popup2.render_line(0))
            self.assertIn("Black", first_line,
                          f"First rendered line should be 'Black', got: {first_line!r}")
            self.assertEqual(popup2.top_item, 0,
                             f"top_item must be 0, got: {popup2.top_item}")


class ComboBoxPopupCleanupTest(unittest.IsolatedAsyncioTestCase):
    """Popup must be removed when ComboBox or parent Window is removed."""

    async def test_popup_removed_when_window_closed(self):
        app = ComboBoxInWindowApp()
        async with app.run_test(size=(60, 20)) as pilot:
            await pilot.pause()
            cb = app._mount_combo_in_window(COLORS)
            await pilot.pause()

            btn = cb.query_one(_DropDownButton)
            await pilot.click(btn)
            await pilot.pause()
            self.assertEqual(len(app.screen.query(_DropDownPopup)), 1,
                             "Popup should be open")

            from textual_vision.window import Window
            win = app.query_one(Window)
            win.close()
            await pilot.pause()
            self.assertEqual(len(app.screen.query(_DropDownPopup)), 0,
                             "Popup must be cleaned up when window is closed")

    async def test_popup_removed_when_combobox_unmounted(self):
        app = ComboBoxInWindowApp()
        async with app.run_test(size=(60, 20)) as pilot:
            await pilot.pause()
            cb = app._mount_combo_in_window(COLORS)
            await pilot.pause()

            btn = cb.query_one(_DropDownButton)
            await pilot.click(btn)
            await pilot.pause()
            self.assertEqual(len(app.screen.query(_DropDownPopup)), 1)

            cb.remove()
            await pilot.pause()
            self.assertEqual(len(app.screen.query(_DropDownPopup)), 0,
                             "Popup must be cleaned up when ComboBox is removed")

    async def test_no_error_closing_window_without_popup(self):
        app = ComboBoxInWindowApp()
        async with app.run_test(size=(60, 20)) as pilot:
            await pilot.pause()
            app._mount_combo_in_window(COLORS)
            await pilot.pause()

            from textual_vision.window import Window
            win = app.query_one(Window)
            win.close()
            await pilot.pause()


class ComboBoxPopupBlurTest(unittest.IsolatedAsyncioTestCase):
    """Popup should close when it loses focus."""

    async def test_popup_closes_on_blur(self):
        app = ComboBoxInWindowApp()
        async with app.run_test(size=(60, 20)) as pilot:
            await pilot.pause()
            cb = app._mount_combo_in_window(COLORS)
            await pilot.pause()

            btn = cb.query_one(_DropDownButton)
            await pilot.click(btn)
            await pilot.pause()
            self.assertEqual(len(app.screen.query(_DropDownPopup)), 1)

            cb.input_line.focus()
            await pilot.pause()
            self.assertEqual(len(app.screen.query(_DropDownPopup)), 0,
                             "Popup should close when it loses focus")


class ThemedComboBoxApp(_ThemedApp):
    """ComboBox with turbo-pascal theme for color testing."""

    CSS = """
    Screen {
        layers: default menus;
    }
    ComboBox {
        width: 30;
        height: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield ComboBox(items=COLORS)


class ComboBoxButtonContrastTest(unittest.IsolatedAsyncioTestCase):
    """Test dropdown button has distinct colors from InputLine."""

    async def test_arrow_bg_differs_from_inputline_bg(self):
        """Arrow background must differ from InputLine background."""
        app = ThemedComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            btn = app.query_one(_DropDownButton)
            inp = app.query_one(InputLine)
            arrow_style = btn.get_component_rich_style("combo--arrow")
            inp_style = inp.get_component_rich_style("inputline--text")
            arrow_bg = arrow_style.bgcolor
            inp_bg = inp_style.bgcolor
            self.assertIsNotNone(arrow_bg)
            self.assertIsNotNone(inp_bg)
            self.assertNotEqual(
                arrow_bg, inp_bg,
                f"Arrow bg ({arrow_bg}) must differ from InputLine bg ({inp_bg})")

    async def test_arrow_bg_is_green(self):
        """TV History arrow: BLACK on GREEN (BIOS 0x20)."""
        app = ThemedComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            from textual_vision.themes import CGA_GREEN
            btn = app.query_one(_DropDownButton)
            arrow_style = btn.get_component_rich_style("combo--arrow")
            bg = arrow_style.bgcolor
            self.assertIsNotNone(bg)
            bg_hex = f"#{bg.triplet.red:02x}{bg.triplet.green:02x}{bg.triplet.blue:02x}"
            self.assertEqual(bg_hex.lower(), CGA_GREEN.lower(),
                             f"Arrow bg should be CGA_GREEN, got {bg_hex}")

    async def test_arrow_fg_is_black(self):
        """TV History arrow: BLACK on GREEN (BIOS 0x20)."""
        app = ThemedComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            from textual_vision.themes import CGA_BLACK
            btn = app.query_one(_DropDownButton)
            arrow_style = btn.get_component_rich_style("combo--arrow")
            fg = arrow_style.color
            self.assertIsNotNone(fg)
            fg_hex = f"#{fg.triplet.red:02x}{fg.triplet.green:02x}{fg.triplet.blue:02x}"
            self.assertEqual(fg_hex.lower(), CGA_BLACK.lower(),
                             f"Arrow fg should be CGA_BLACK, got {fg_hex}")

    async def test_sides_bg_is_lightgray(self):
        """TV History sides: GREEN on LGRAY (BIOS 0x72)."""
        app = ThemedComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            from textual_vision.themes import CGA_LIGHT_GRAY
            btn = app.query_one(_DropDownButton)
            sides_style = btn.get_component_rich_style("combo--sides")
            bg = sides_style.bgcolor
            self.assertIsNotNone(bg)
            bg_hex = f"#{bg.triplet.red:02x}{bg.triplet.green:02x}{bg.triplet.blue:02x}"
            self.assertEqual(bg_hex.lower(), CGA_LIGHT_GRAY.lower(),
                             f"Sides bg should be CGA_LIGHT_GRAY, got {bg_hex}")

    async def test_sides_fg_is_green(self):
        """TV History sides: GREEN on LGRAY (BIOS 0x72)."""
        app = ThemedComboBoxApp()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            from textual_vision.themes import CGA_GREEN
            btn = app.query_one(_DropDownButton)
            sides_style = btn.get_component_rich_style("combo--sides")
            fg = sides_style.color
            self.assertIsNotNone(fg)
            fg_hex = f"#{fg.triplet.red:02x}{fg.triplet.green:02x}{fg.triplet.blue:02x}"
            self.assertEqual(fg_hex.lower(), CGA_GREEN.lower(),
                             f"Sides fg should be CGA_GREEN, got {fg_hex}")


if __name__ == "__main__":
    unittest.main()
