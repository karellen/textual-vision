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

from textual_vision.list_box import ListBox


class ListBoxInitTest(unittest.TestCase):
    def test_default_empty(self):
        lb = ListBox()
        self.assertEqual(lb.items, [])
        self.assertEqual(lb.range, 0)

    def test_with_items(self):
        lb = ListBox(items=["alpha", "beta", "gamma"])
        self.assertEqual(lb.items, ["alpha", "beta", "gamma"])
        self.assertEqual(lb.range, 3)

    def test_items_are_copied(self):
        original = ["a", "b", "c"]
        lb = ListBox(items=original)
        original.append("d")
        self.assertEqual(lb.range, 3)


class ListBoxGetTextTest(unittest.TestCase):
    def test_get_text_valid(self):
        lb = ListBox(items=["hello", "world"])
        self.assertEqual(lb.get_text(0), "hello")
        self.assertEqual(lb.get_text(1), "world")

    def test_get_text_out_of_bounds(self):
        lb = ListBox(items=["hello"])
        self.assertEqual(lb.get_text(-1), "")
        self.assertEqual(lb.get_text(5), "")


class ListBoxSetListTest(unittest.TestCase):
    def test_set_list_replaces(self):
        lb = ListBox(items=["a", "b"])
        lb.set_list(["x", "y", "z"])
        self.assertEqual(lb.items, ["x", "y", "z"])
        self.assertEqual(lb.range, 3)
        self.assertEqual(lb.focused, 0)

    def test_set_list_empty(self):
        lb = ListBox(items=["a", "b", "c"])
        lb.set_list([])
        self.assertEqual(lb.range, 0)
        self.assertEqual(lb.focused, 0)

    def test_set_list_copies_input(self):
        data = ["p", "q"]
        lb = ListBox()
        lb.set_list(data)
        data.append("r")
        self.assertEqual(lb.range, 2)


class ListBoxFocusTest(unittest.TestCase):
    def test_initial_focus(self):
        lb = ListBox(items=["a", "b", "c"])
        self.assertEqual(lb.focused, 0)

    def test_focus_item(self):
        lb = ListBox(items=["a", "b", "c", "d"])
        lb.focus_item(2)
        self.assertEqual(lb.focused, 2)
        self.assertEqual(lb.get_text(lb.focused), "c")

    def test_focus_clamped(self):
        lb = ListBox(items=["a", "b"])
        lb.focus_item(99)
        self.assertEqual(lb.focused, 1)


class ListBoxInheritanceTest(unittest.TestCase):
    def test_is_list_viewer(self):
        from textual_vision.list_viewer import ListViewer
        lb = ListBox()
        self.assertIsInstance(lb, ListViewer)

    def test_is_selected(self):
        lb = ListBox(items=["a", "b", "c"])
        lb.focused = 1
        self.assertTrue(lb.is_selected(1))
        self.assertFalse(lb.is_selected(0))


class ListBoxScrollBarInitTest(unittest.TestCase):
    """Regression: scrollbar must have correct max_val after ListBox init."""

    def test_scrollbar_max_val_matches_item_count(self):
        from textual_vision.scroll_bar import ScrollBar
        sb = ScrollBar()
        ListBox(items=["a", "b", "c", "d", "e"], v_scroll_bar=sb)
        self.assertEqual(sb.max_val, 4,
                         "ScrollBar max_val must equal len(items)-1 after ListBox init")

    def test_scrollbar_max_val_with_large_list(self):
        from textual_vision.scroll_bar import ScrollBar
        sb = ScrollBar()
        items = [f"Item {i}" for i in range(100)]
        ListBox(items=items, v_scroll_bar=sb)
        self.assertEqual(sb.max_val, 99,
                         "ScrollBar max_val must be 99 for 100-item list")

    def test_scrollbar_max_val_empty(self):
        from textual_vision.scroll_bar import ScrollBar
        sb = ScrollBar()
        ListBox(items=[], v_scroll_bar=sb)
        self.assertEqual(sb.max_val, 0)


if __name__ == "__main__":
    unittest.main()
