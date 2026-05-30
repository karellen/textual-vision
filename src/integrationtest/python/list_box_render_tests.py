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

from textual_vision.list_box import ListBox


def strip_to_text(strip):
    return "".join(seg.text for seg in strip._segments)


class ListBoxApp(App):
    CSS = """
    ListBox { width: 30; height: 10; }
    """

    def compose(self) -> ComposeResult:
        yield ListBox(items=[f"Item {i}" for i in range(1, 21)])


class EmptyListBoxApp(App):
    CSS = """
    ListBox { width: 20; height: 5; }
    """

    def compose(self) -> ComposeResult:
        yield ListBox()


class ListBoxRenderTest(unittest.IsolatedAsyncioTestCase):
    async def test_first_row_shows_first_item(self):
        app = ListBoxApp()
        async with app.run_test(size=(32, 12)) as pilot:
            await pilot.pause()
            lb = app.query_one(ListBox)
            text = strip_to_text(lb.render_line(0))
            self.assertIn("Item 1", text)

    async def test_focused_item_is_first_by_default(self):
        app = ListBoxApp()
        async with app.run_test(size=(32, 12)) as pilot:
            await pilot.pause()
            lb = app.query_one(ListBox)
            self.assertEqual(lb.focused, 0)

    async def test_second_row_shows_second_item(self):
        app = ListBoxApp()
        async with app.run_test(size=(32, 12)) as pilot:
            await pilot.pause()
            lb = app.query_one(ListBox)
            text = strip_to_text(lb.render_line(1))
            self.assertIn("Item 2", text)

    async def test_row_width_matches_widget_width(self):
        app = ListBoxApp()
        async with app.run_test(size=(32, 12)) as pilot:
            await pilot.pause()
            lb = app.query_one(ListBox)
            text = strip_to_text(lb.render_line(0))
            self.assertEqual(len(text), lb.size.width)

    async def test_focus_item_changes_focused(self):
        app = ListBoxApp()
        async with app.run_test(size=(32, 12)) as pilot:
            await pilot.pause()
            lb = app.query_one(ListBox)
            lb.focus_item(5)
            self.assertEqual(lb.focused, 5)

    async def test_empty_list_renders_blanks(self):
        app = EmptyListBoxApp()
        async with app.run_test(size=(22, 7)) as pilot:
            await pilot.pause()
            lb = app.query_one(ListBox)
            text = strip_to_text(lb.render_line(0))
            self.assertEqual(text.strip(), "")

    async def test_set_list_updates_items(self):
        app = ListBoxApp()
        async with app.run_test(size=(32, 12)) as pilot:
            await pilot.pause()
            lb = app.query_one(ListBox)
            lb.set_list(["New A", "New B", "New C"])
            self.assertEqual(lb.range, 3)
            text = strip_to_text(lb.render_line(0))
            self.assertIn("New A", text)


class ListBoxScrollTest(unittest.IsolatedAsyncioTestCase):
    async def test_focus_past_page_scrolls_down(self):
        app = ListBoxApp()
        async with app.run_test(size=(32, 12)) as pilot:
            await pilot.pause()
            lb = app.query_one(ListBox)
            lb.focus_item(15)
            self.assertGreater(lb.top_item, 0)
            text = strip_to_text(lb.render_line(0))
            self.assertNotIn("Item 1", text)

    async def test_focus_back_scrolls_up(self):
        app = ListBoxApp()
        async with app.run_test(size=(32, 12)) as pilot:
            await pilot.pause()
            lb = app.query_one(ListBox)
            lb.focus_item(15)
            lb.focus_item(0)
            self.assertEqual(lb.top_item, 0)
            text = strip_to_text(lb.render_line(0))
            self.assertIn("Item 1", text)


class ListBoxWithScrollBarApp(App):
    CSS = """
    ListBox { width: 30; height: 5; }
    ScrollBar { width: 1; height: 5; dock: right; }
    """

    def compose(self) -> ComposeResult:
        from textual_vision.scroll_bar import ScrollBar
        self._vbar = ScrollBar(min_val=0, max_val=19, page_step=5, arrow_step=1)
        self._listbox = ListBox(items=[f"Item {i}" for i in range(1, 21)],
                                v_scroll_bar=self._vbar)
        yield self._listbox
        yield self._vbar


class ListBoxScrollBarIntegrationTest(unittest.IsolatedAsyncioTestCase):
    """Regression: scrollbar value changes must update the linked ListBox."""

    async def test_scrollbar_set_value_updates_listbox_focus(self):
        app = ListBoxWithScrollBarApp()
        async with app.run_test(size=(32, 7)) as pilot:
            await pilot.pause()
            lb = app._listbox
            sb = app._vbar
            self.assertEqual(lb.focused, 0)

            sb.set_value(10)
            await pilot.pause()

            self.assertEqual(lb.focused, 10,
                             "ScrollBar.set_value must update the linked ListBox focused item")

    async def test_scrollbar_set_value_scrolls_top_item(self):
        app = ListBoxWithScrollBarApp()
        async with app.run_test(size=(32, 7)) as pilot:
            await pilot.pause()
            lb = app._listbox
            sb = app._vbar

            sb.set_value(15)
            await pilot.pause()

            self.assertGreater(lb.top_item, 0,
                               "ScrollBar value change must scroll the ListBox view")
            self.assertGreaterEqual(lb.top_item, 2,
                                    "top_item must advance past initial items")


if __name__ == "__main__":
    unittest.main()
