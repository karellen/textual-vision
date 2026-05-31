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

from textual_vision.list_viewer import ListViewer


class ConcreteListViewer(ListViewer):
    """Test subclass that stores a fixed list of strings."""

    def __init__(self, items, **kwargs):
        super().__init__(**kwargs)
        self._items = list(items)
        self._range = len(self._items)

    def get_text(self, item):
        if 0 <= item < len(self._items):
            return self._items[item]
        return ""


class ListViewerRangeTest(unittest.TestCase):
    def test_initial_range(self):
        lv = ConcreteListViewer(["alpha", "beta", "gamma"])
        self.assertEqual(lv.range, 3)

    def test_set_range_shrinks_focus(self):
        lv = ConcreteListViewer(["a", "b", "c", "d", "e"])
        lv.focused = 4
        lv.set_range(3)
        self.assertEqual(lv.focused, 2)

    def test_set_range_zero(self):
        lv = ConcreteListViewer(["a", "b"])
        lv.set_range(0)
        self.assertEqual(lv.range, 0)
        self.assertEqual(lv.focused, 0)

    def test_set_range_preserves_valid_focus(self):
        lv = ConcreteListViewer(["a", "b", "c"])
        lv.focused = 1
        lv.set_range(3)
        self.assertEqual(lv.focused, 1)


class ListViewerFocusTest(unittest.TestCase):
    def test_focus_item_clamps_low(self):
        lv = ConcreteListViewer(["a", "b", "c"])
        lv.focus_item(-5)
        self.assertEqual(lv.focused, 0)

    def test_focus_item_clamps_high(self):
        lv = ConcreteListViewer(["a", "b", "c"])
        lv.focus_item(100)
        self.assertEqual(lv.focused, 2)

    def test_focus_item_noop_on_empty(self):
        lv = ConcreteListViewer([])
        lv.focus_item(0)
        self.assertEqual(lv.focused, 0)

    def test_focus_item_sets_value(self):
        lv = ConcreteListViewer(["a", "b", "c", "d"])
        lv.focus_item(2)
        self.assertEqual(lv.focused, 2)


class ListViewerScrollTest(unittest.TestCase):
    def test_scroll_to_focused_moves_down(self):
        lv = ConcreteListViewer([f"item{i}" for i in range(20)])
        lv._page_size = lambda: 5
        lv.focus_item(7)
        self.assertGreater(lv.top_item, 0)
        self.assertLessEqual(lv.top_item + 5, lv.focused + 1)

    def test_scroll_to_focused_moves_up(self):
        lv = ConcreteListViewer([f"item{i}" for i in range(20)])
        lv._page_size = lambda: 5
        lv._top_item = 10
        lv.focus_item(3)
        self.assertEqual(lv.top_item, 3)

    def test_initial_top_item_is_zero(self):
        lv = ConcreteListViewer(["a", "b", "c"])
        self.assertEqual(lv.top_item, 0)

    def test_page_size_default(self):
        lv = ConcreteListViewer(["a", "b"])
        self.assertEqual(lv._page_size(), 1)

    def test_scroll_to_focused_clamps_top_item_after_page_grows(self):
        """Simulates the ComboBox dropdown bug: focus_item with page=1 sets
        _top_item too high, then page grows but _top_item isn't corrected."""
        lv = ConcreteListViewer([f"item{i}" for i in range(8)])
        lv._page_size = lambda: 1
        lv.focus_item(5)
        self.assertEqual(lv.top_item, 5)

        lv._page_size = lambda: 8
        lv._scroll_to_focused()
        self.assertEqual(lv.top_item, 0,
                         "top_item must clamp down when page grows to fit all items")

    def test_scroll_to_focused_clamps_when_range_shrinks(self):
        """After set_list to a shorter list, top_item must not leave empty space."""
        lv = ConcreteListViewer([f"item{i}" for i in range(20)])
        lv._page_size = lambda: 5
        lv.focus_item(15)
        self.assertEqual(lv.top_item, 11)

        lv._items = [f"item{i}" for i in range(12)]
        lv._range = 12
        lv.focused = 11
        lv._scroll_to_focused()
        self.assertEqual(lv.top_item, 7,
                         "top_item must clamp to range - page when items shrink")


class ListViewerIsSelectedTest(unittest.TestCase):
    def test_is_selected_for_focused(self):
        lv = ConcreteListViewer(["a", "b", "c"])
        lv.focused = 1
        self.assertTrue(lv.is_selected(1))
        self.assertFalse(lv.is_selected(0))
        self.assertFalse(lv.is_selected(2))


class ListViewerGetTextTest(unittest.TestCase):
    def test_get_text_abstract(self):
        lv = ListViewer()
        with self.assertRaises(NotImplementedError):
            lv.get_text(0)

    def test_concrete_get_text(self):
        lv = ConcreteListViewer(["hello", "world"])
        self.assertEqual(lv.get_text(0), "hello")
        self.assertEqual(lv.get_text(1), "world")

    def test_get_text_out_of_range(self):
        lv = ConcreteListViewer(["hello"])
        self.assertEqual(lv.get_text(-1), "")
        self.assertEqual(lv.get_text(5), "")


class ListViewerNumColsTest(unittest.TestCase):
    def test_default_single_column(self):
        lv = ConcreteListViewer(["a"])
        self.assertEqual(lv.num_cols, 1)

    def test_multi_column(self):
        lv = ConcreteListViewer(["a"], num_cols=3)
        self.assertEqual(lv.num_cols, 3)


class MockScrollBar:
    def __init__(self):
        self.value = 0
        self._min = 0
        self._max = 0
        self._page = 1
        self._arrow = 1

    def set_params(self, min_val, max_val, page_step=1, arrow_step=1):
        self._min = min_val
        self._max = max_val
        self._page = page_step
        self._arrow = arrow_step

    def set_value(self, val):
        self.value = val


class ListViewerScrollBarTest(unittest.TestCase):
    def test_scroll_bar_properties(self):
        lv = ConcreteListViewer(["a", "b"])
        self.assertIsNone(lv.v_scroll_bar)
        self.assertIsNone(lv.h_scroll_bar)

    def test_v_scroll_bar_setter(self):
        lv = ConcreteListViewer(["a", "b"])
        sb = MockScrollBar()
        lv.v_scroll_bar = sb
        self.assertIs(lv.v_scroll_bar, sb)

    def test_v_scroll_bar_setter_updates_params(self):
        lv = ConcreteListViewer(["a", "b", "c"])
        sb = MockScrollBar()
        lv.v_scroll_bar = sb
        self.assertEqual(sb._max, 2)

    def test_h_scroll_bar_setter(self):
        lv = ConcreteListViewer(["a", "b"])
        lv.h_scroll_bar = "mock_hsb"
        self.assertEqual(lv.h_scroll_bar, "mock_hsb")

    def test_sync_v_scrollbar_on_focus(self):
        lv = ConcreteListViewer(["a", "b", "c", "d"])
        sb = MockScrollBar()
        lv.v_scroll_bar = sb
        lv.focus_item(2)
        self.assertEqual(sb.value, 2)


class ListViewerScrollTargetTest(unittest.TestCase):
    """Tests for the scrollbar-to-viewer auto-linkage."""

    def test_v_scroll_bar_setter_registers_scroll_target(self):
        from textual_vision.scroll_bar import ScrollBar
        lv = ConcreteListViewer([f"item{i}" for i in range(20)])
        sb = ScrollBar()
        lv.v_scroll_bar = sb
        self.assertIs(sb.scroll_target, lv,
                      "Setting v_scroll_bar must register the ListViewer as scroll_target")

    def test_v_scroll_bar_setter_unregisters_old_target(self):
        from textual_vision.scroll_bar import ScrollBar
        lv = ConcreteListViewer([f"item{i}" for i in range(20)])
        sb1 = ScrollBar()
        sb2 = ScrollBar()
        lv.v_scroll_bar = sb1
        lv.v_scroll_bar = sb2
        self.assertIsNone(sb1.scroll_target,
                          "Old scrollbar must lose its scroll_target")
        self.assertIs(sb2.scroll_target, lv,
                      "New scrollbar must be linked to the ListViewer")

    def test_v_scroll_bar_none_unregisters(self):
        from textual_vision.scroll_bar import ScrollBar
        lv = ConcreteListViewer([f"item{i}" for i in range(20)])
        sb = ScrollBar()
        lv.v_scroll_bar = sb
        lv.v_scroll_bar = None
        self.assertIsNone(sb.scroll_target,
                          "Setting v_scroll_bar to None must unregister the target")


if __name__ == "__main__":
    unittest.main()
