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

from textual.events import Key

from textual_vision.constants import OptionFlag
from textual_vision.scroll_bar import ScrollBar


class ScrollBarCreationTest(unittest.TestCase):
    def test_default_values(self):
        sb = ScrollBar()
        self.assertEqual(sb.min_val, 0)
        self.assertEqual(sb.max_val, 0)
        self.assertEqual(sb.value, 0)
        self.assertEqual(sb.page_step, 1)
        self.assertEqual(sb.arrow_step, 1)
        self.assertFalse(sb.horizontal)

    def test_custom_range(self):
        sb = ScrollBar(min_val=10, max_val=100, page_step=10, arrow_step=2)
        self.assertEqual(sb.min_val, 10)
        self.assertEqual(sb.max_val, 100)
        self.assertEqual(sb.page_step, 10)
        self.assertEqual(sb.arrow_step, 2)

    def test_horizontal(self):
        sb = ScrollBar(horizontal=True)
        self.assertTrue(sb.horizontal)

    def test_selectable(self):
        sb = ScrollBar()
        self.assertIn(OptionFlag.SELECTABLE, sb.tv_options)


class ScrollBarSetValueTest(unittest.TestCase):
    def test_set_value_clamps_min(self):
        sb = ScrollBar(min_val=0, max_val=100)
        sb.set_value(-10)
        self.assertEqual(sb.value, 0)

    def test_set_value_clamps_max(self):
        sb = ScrollBar(min_val=0, max_val=100)
        sb.set_value(200)
        self.assertEqual(sb.value, 100)

    def test_set_value_in_range(self):
        sb = ScrollBar(min_val=0, max_val=100)
        sb.set_value(50)
        self.assertEqual(sb.value, 50)

    def test_set_value_no_change_no_message(self):
        sb = ScrollBar(min_val=0, max_val=100)
        sb.value = 50
        sb.set_value(50)
        self.assertEqual(sb.value, 50)


class ScrollBarSetParamsTest(unittest.TestCase):
    def test_set_params_updates(self):
        sb = ScrollBar()
        sb.set_params(10, 200, page_step=20, arrow_step=5)
        self.assertEqual(sb.min_val, 10)
        self.assertEqual(sb.max_val, 200)
        self.assertEqual(sb.page_step, 20)
        self.assertEqual(sb.arrow_step, 5)

    def test_set_params_clamps_value(self):
        sb = ScrollBar(min_val=0, max_val=100)
        sb.value = 80
        sb.set_params(0, 50)
        self.assertEqual(sb.value, 50)

    def test_set_params_max_not_below_min(self):
        sb = ScrollBar()
        sb.set_params(50, 10)
        self.assertEqual(sb.max_val, 50)


class _SizedScrollBar(ScrollBar):
    """ScrollBar subclass with overridable size for unit testing."""
    _test_size = None

    @property
    def size(self):
        if self._test_size is not None:
            return self._test_size
        return super().size

    @size.setter
    def size(self, value):
        pass


class ScrollBarThumbTest(unittest.TestCase):
    def _make(self, width, height, **kwargs):
        from textual.geometry import Size
        sb = _SizedScrollBar(**kwargs)
        sb._test_size = Size(width, height)
        return sb

    def test_thumb_size_full_range(self):
        sb = self._make(1, 12, min_val=0, max_val=100, page_step=10)
        self.assertGreaterEqual(sb._thumb_size, 1)
        self.assertLessEqual(sb._thumb_size, sb._track_len)

    def test_thumb_pos_at_min(self):
        sb = self._make(1, 12, min_val=0, max_val=100, page_step=10)
        sb.value = 0
        self.assertEqual(sb._thumb_pos, 0)

    def test_thumb_pos_at_max(self):
        sb = self._make(1, 12, min_val=0, max_val=100, page_step=10)
        sb.value = 100
        expected = sb._track_len - sb._thumb_size
        self.assertEqual(sb._thumb_pos, expected)

    def test_track_len_vertical(self):
        sb = self._make(1, 10)
        self.assertEqual(sb._track_len, 8)

    def test_track_len_horizontal(self):
        sb = self._make(20, 1, horizontal=True)
        self.assertEqual(sb._track_len, 18)

    def test_thumb_size_equal_range(self):
        sb = self._make(1, 10, min_val=0, max_val=0)
        self.assertEqual(sb._thumb_size, sb._track_len)


class ScrollBarKeyHandlingTest(unittest.TestCase):
    def test_up_decreases_vertical(self):
        sb = ScrollBar(min_val=0, max_val=100, arrow_step=5)
        sb.value = 50
        result = sb.tv_handle_key(Key("up", None))
        self.assertTrue(result)
        self.assertEqual(sb.value, 45)

    def test_down_increases_vertical(self):
        sb = ScrollBar(min_val=0, max_val=100, arrow_step=5)
        sb.value = 50
        result = sb.tv_handle_key(Key("down", None))
        self.assertTrue(result)
        self.assertEqual(sb.value, 55)

    def test_left_decreases_horizontal(self):
        sb = ScrollBar(min_val=0, max_val=100, arrow_step=5, horizontal=True)
        sb.value = 50
        result = sb.tv_handle_key(Key("left", None))
        self.assertTrue(result)
        self.assertEqual(sb.value, 45)

    def test_right_increases_horizontal(self):
        sb = ScrollBar(min_val=0, max_val=100, arrow_step=5, horizontal=True)
        sb.value = 50
        result = sb.tv_handle_key(Key("right", None))
        self.assertTrue(result)
        self.assertEqual(sb.value, 55)

    def test_pageup(self):
        sb = ScrollBar(min_val=0, max_val=100, page_step=20)
        sb.value = 50
        result = sb.tv_handle_key(Key("pageup", None))
        self.assertTrue(result)
        self.assertEqual(sb.value, 30)

    def test_pagedown(self):
        sb = ScrollBar(min_val=0, max_val=100, page_step=20)
        sb.value = 50
        result = sb.tv_handle_key(Key("pagedown", None))
        self.assertTrue(result)
        self.assertEqual(sb.value, 70)

    def test_home(self):
        sb = ScrollBar(min_val=0, max_val=100)
        sb.value = 50
        result = sb.tv_handle_key(Key("home", None))
        self.assertTrue(result)
        self.assertEqual(sb.value, 0)

    def test_end(self):
        sb = ScrollBar(min_val=0, max_val=100)
        sb.value = 50
        result = sb.tv_handle_key(Key("end", None))
        self.assertTrue(result)
        self.assertEqual(sb.value, 100)

    def test_unhandled_key(self):
        sb = ScrollBar()
        result = sb.tv_handle_key(Key("a", "a"))
        self.assertFalse(result)

    def test_vertical_ignores_left_right(self):
        sb = ScrollBar(min_val=0, max_val=100)
        sb.value = 50
        self.assertFalse(sb.tv_handle_key(Key("left", None)))
        self.assertFalse(sb.tv_handle_key(Key("right", None)))
        self.assertEqual(sb.value, 50)

    def test_horizontal_ignores_up_down(self):
        sb = ScrollBar(min_val=0, max_val=100, horizontal=True)
        sb.value = 50
        self.assertFalse(sb.tv_handle_key(Key("up", None)))
        self.assertFalse(sb.tv_handle_key(Key("down", None)))
        self.assertEqual(sb.value, 50)


class ScrollBarCssTest(unittest.TestCase):
    def test_has_component_classes(self):
        self.assertIn("scrollbar--arrow", ScrollBar.COMPONENT_CLASSES)
        self.assertIn("scrollbar--track", ScrollBar.COMPONENT_CLASSES)
        self.assertIn("scrollbar--thumb", ScrollBar.COMPONENT_CLASSES)

    def test_uses_scrollbar_theme_variables(self):
        css = ScrollBar.DEFAULT_CSS
        self.assertIn("$scrollbar", css)
        self.assertIn("$scrollbar-background", css)
        self.assertIn("$scrollbar-active", css)


if __name__ == "__main__":
    unittest.main()
