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
        self.assertIsNone(sb.scroll_target)

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

    def test_thumb_size_no_range(self):
        sb = self._make(1, 10, min_val=0, max_val=0)
        self.assertEqual(sb._thumb_size, 0)

    def test_thumb_size_is_always_one(self):
        sb = self._make(1, 10, min_val=0, max_val=100)
        self.assertEqual(sb._thumb_size, 1)


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


class ScrollBarVerticalScrollingTest(unittest.TestCase):
    """Test scrolling back and forth through the full range on a vertical scrollbar."""

    def setUp(self):
        self.sb = ScrollBar(min_val=0, max_val=99, page_step=10, arrow_step=1)

    def test_arrow_step_forward_to_end(self):
        for i in range(100):
            self.assertEqual(self.sb.value, i)
            self.sb.tv_handle_key(Key("down", None))
        self.assertEqual(self.sb.value, 99)

    def test_arrow_step_backward_to_start(self):
        self.sb.set_value(99)
        for i in range(99, -1, -1):
            self.assertEqual(self.sb.value, i)
            self.sb.tv_handle_key(Key("up", None))
        self.assertEqual(self.sb.value, 0)

    def test_arrow_step_round_trip(self):
        for _ in range(50):
            self.sb.tv_handle_key(Key("down", None))
        self.assertEqual(self.sb.value, 50)
        for _ in range(50):
            self.sb.tv_handle_key(Key("up", None))
        self.assertEqual(self.sb.value, 0)

    def test_page_step_forward_and_back(self):
        self.sb.tv_handle_key(Key("pagedown", None))
        self.assertEqual(self.sb.value, 10)
        self.sb.tv_handle_key(Key("pagedown", None))
        self.assertEqual(self.sb.value, 20)
        self.sb.tv_handle_key(Key("pagedown", None))
        self.assertEqual(self.sb.value, 30)
        self.sb.tv_handle_key(Key("pageup", None))
        self.assertEqual(self.sb.value, 20)
        self.sb.tv_handle_key(Key("pageup", None))
        self.assertEqual(self.sb.value, 10)
        self.sb.tv_handle_key(Key("pageup", None))
        self.assertEqual(self.sb.value, 0)

    def test_page_step_clamps_at_boundaries(self):
        self.sb.set_value(95)
        self.sb.tv_handle_key(Key("pagedown", None))
        self.assertEqual(self.sb.value, 99)
        self.sb.set_value(5)
        self.sb.tv_handle_key(Key("pageup", None))
        self.assertEqual(self.sb.value, 0)

    def test_home_end_round_trip(self):
        self.sb.tv_handle_key(Key("end", None))
        self.assertEqual(self.sb.value, 99)
        self.sb.tv_handle_key(Key("home", None))
        self.assertEqual(self.sb.value, 0)
        self.sb.tv_handle_key(Key("end", None))
        self.assertEqual(self.sb.value, 99)

    def test_arrow_clamps_at_min(self):
        self.sb.set_value(0)
        self.sb.tv_handle_key(Key("up", None))
        self.assertEqual(self.sb.value, 0)

    def test_arrow_clamps_at_max(self):
        self.sb.set_value(99)
        self.sb.tv_handle_key(Key("down", None))
        self.assertEqual(self.sb.value, 99)

    def test_mixed_navigation(self):
        self.sb.tv_handle_key(Key("pagedown", None))
        self.assertEqual(self.sb.value, 10)
        self.sb.tv_handle_key(Key("down", None))
        self.sb.tv_handle_key(Key("down", None))
        self.assertEqual(self.sb.value, 12)
        self.sb.tv_handle_key(Key("pageup", None))
        self.assertEqual(self.sb.value, 2)
        self.sb.tv_handle_key(Key("home", None))
        self.assertEqual(self.sb.value, 0)
        self.sb.tv_handle_key(Key("end", None))
        self.assertEqual(self.sb.value, 99)
        self.sb.tv_handle_key(Key("up", None))
        self.assertEqual(self.sb.value, 98)


class ScrollBarHorizontalScrollingTest(unittest.TestCase):
    """Test scrolling back and forth through the full range on a horizontal scrollbar."""

    def setUp(self):
        self.sb = ScrollBar(min_val=0, max_val=199, page_step=20, arrow_step=2,
                            horizontal=True)

    def test_arrow_step_forward_and_back(self):
        for _ in range(25):
            self.sb.tv_handle_key(Key("right", None))
        self.assertEqual(self.sb.value, 50)
        for _ in range(25):
            self.sb.tv_handle_key(Key("left", None))
        self.assertEqual(self.sb.value, 0)

    def test_page_step_forward_and_back(self):
        self.sb.tv_handle_key(Key("pagedown", None))
        self.assertEqual(self.sb.value, 20)
        self.sb.tv_handle_key(Key("pagedown", None))
        self.assertEqual(self.sb.value, 40)
        self.sb.tv_handle_key(Key("pageup", None))
        self.assertEqual(self.sb.value, 20)
        self.sb.tv_handle_key(Key("pageup", None))
        self.assertEqual(self.sb.value, 0)

    def test_home_end_round_trip(self):
        self.sb.tv_handle_key(Key("end", None))
        self.assertEqual(self.sb.value, 199)
        self.sb.tv_handle_key(Key("home", None))
        self.assertEqual(self.sb.value, 0)

    def test_arrow_clamps_at_boundaries(self):
        self.sb.set_value(0)
        self.sb.tv_handle_key(Key("left", None))
        self.assertEqual(self.sb.value, 0)
        self.sb.set_value(199)
        self.sb.tv_handle_key(Key("right", None))
        self.assertEqual(self.sb.value, 199)

    def test_mixed_navigation_round_trip(self):
        self.sb.tv_handle_key(Key("pagedown", None))
        self.sb.tv_handle_key(Key("right", None))
        self.sb.tv_handle_key(Key("right", None))
        self.assertEqual(self.sb.value, 24)
        self.sb.tv_handle_key(Key("pageup", None))
        self.assertEqual(self.sb.value, 4)
        self.sb.tv_handle_key(Key("left", None))
        self.sb.tv_handle_key(Key("left", None))
        self.assertEqual(self.sb.value, 0)


class ScrollBarNonZeroMinScrollingTest(unittest.TestCase):
    """Test scrolling with a non-zero min_val range."""

    def setUp(self):
        self.sb = ScrollBar(min_val=50, max_val=150, page_step=10, arrow_step=1)

    def test_home_goes_to_min(self):
        self.sb.set_value(100)
        self.sb.tv_handle_key(Key("home", None))
        self.assertEqual(self.sb.value, 50)

    def test_end_goes_to_max(self):
        self.sb.tv_handle_key(Key("end", None))
        self.assertEqual(self.sb.value, 150)

    def test_arrow_round_trip(self):
        self.sb.set_value(50)
        for _ in range(20):
            self.sb.tv_handle_key(Key("down", None))
        self.assertEqual(self.sb.value, 70)
        for _ in range(20):
            self.sb.tv_handle_key(Key("up", None))
        self.assertEqual(self.sb.value, 50)

    def test_page_clamps_at_min(self):
        self.sb.set_value(55)
        self.sb.tv_handle_key(Key("pageup", None))
        self.assertEqual(self.sb.value, 50)

    def test_page_clamps_at_max(self):
        self.sb.set_value(145)
        self.sb.tv_handle_key(Key("pagedown", None))
        self.assertEqual(self.sb.value, 150)


class ScrollBarSetValueScrollingTest(unittest.TestCase):
    """Test set_value-based scrolling with clamping at boundaries."""

    def test_sweep_forward_and_back(self):
        sb = ScrollBar(min_val=0, max_val=49)
        for i in range(50):
            sb.set_value(i)
            self.assertEqual(sb.value, i)
        for i in range(49, -1, -1):
            sb.set_value(i)
            self.assertEqual(sb.value, i)

    def test_set_value_beyond_max_clamps(self):
        sb = ScrollBar(min_val=0, max_val=49)
        sb.set_value(100)
        self.assertEqual(sb.value, 49)
        sb.set_value(25)
        self.assertEqual(sb.value, 25)

    def test_set_value_below_min_clamps(self):
        sb = ScrollBar(min_val=10, max_val=49)
        sb.set_value(-5)
        self.assertEqual(sb.value, 10)
        sb.set_value(30)
        self.assertEqual(sb.value, 30)

    def test_set_params_mid_scroll_clamps_and_continues(self):
        sb = ScrollBar(min_val=0, max_val=99, page_step=10)
        sb.set_value(80)
        sb.set_params(0, 50, page_step=10)
        self.assertEqual(sb.value, 50)
        sb.tv_handle_key(Key("pageup", None))
        self.assertEqual(sb.value, 40)
        sb.tv_handle_key(Key("pagedown", None))
        self.assertEqual(sb.value, 50)


class ScrollBarCornerCharVerticalTest(unittest.TestCase):
    """Test corner_char geometry for vertical scrollbars."""

    def _make(self, width, height, **kwargs):
        from textual.geometry import Size
        sb = _SizedScrollBar(**kwargs)
        sb._test_size = Size(width, height)
        return sb

    def test_no_corner_track_len(self):
        sb = self._make(1, 10, min_val=0, max_val=100)
        self.assertEqual(sb._corner_len, 0)
        self.assertEqual(sb._track_len, 8)

    def test_single_corner_char_track_len(self):
        sb = self._make(1, 10, min_val=0, max_val=100, corner_char="┘")
        self.assertEqual(sb._corner_len, 1)
        self.assertEqual(sb._track_len, 7)

    def test_multi_corner_char_track_len(self):
        sb = self._make(1, 10, min_val=0, max_val=100, corner_char="║┘")
        self.assertEqual(sb._corner_len, 2)
        self.assertEqual(sb._track_len, 6)

    def test_thumb_still_works_with_corner(self):
        sb = self._make(1, 10, min_val=0, max_val=100, corner_char="┘")
        self.assertEqual(sb._thumb_size, 1)
        sb.value = 0
        self.assertEqual(sb._thumb_pos, 0)
        sb.value = 100
        self.assertEqual(sb._thumb_pos, sb._track_len - 1)

    def test_thumb_works_with_multi_corner(self):
        sb = self._make(1, 10, min_val=0, max_val=100, corner_char="║┘")
        self.assertEqual(sb._thumb_size, 1)
        sb.value = 100
        self.assertEqual(sb._thumb_pos, sb._track_len - 1)


class ScrollBarCornerCharHorizontalTest(unittest.TestCase):
    """Test corner_char geometry for horizontal scrollbars."""

    def _make(self, width, height, **kwargs):
        from textual.geometry import Size
        sb = _SizedScrollBar(**kwargs)
        sb._test_size = Size(width, height)
        return sb

    def test_no_corner_track_len(self):
        sb = self._make(20, 1, min_val=0, max_val=100, horizontal=True)
        self.assertEqual(sb._corner_len, 0)
        self.assertEqual(sb._left_len, 0)
        self.assertEqual(sb._track_len, 18)

    def test_single_corner_char_track_len(self):
        sb = self._make(20, 1, min_val=0, max_val=100, horizontal=True, corner_char="─")
        self.assertEqual(sb._corner_len, 1)
        self.assertEqual(sb._track_len, 17)

    def test_multi_corner_char_track_len(self):
        sb = self._make(20, 1, min_val=0, max_val=100, horizontal=True, corner_char="─┘")
        self.assertEqual(sb._corner_len, 2)
        self.assertEqual(sb._track_len, 16)

    def test_left_chars_track_len(self):
        sb = self._make(20, 1, min_val=0, max_val=100, horizontal=True, left_chars="└─")
        self.assertEqual(sb._left_len, 2)
        self.assertEqual(sb._track_len, 16)

    def test_both_left_and_corner_track_len(self):
        sb = self._make(20, 1, min_val=0, max_val=100, horizontal=True,
                        left_chars="└─", corner_char="─")
        self.assertEqual(sb._left_len, 2)
        self.assertEqual(sb._corner_len, 1)
        self.assertEqual(sb._track_len, 15)

    def test_thumb_still_works_with_corner(self):
        sb = self._make(20, 1, min_val=0, max_val=100, horizontal=True, corner_char="─")
        self.assertEqual(sb._thumb_size, 1)
        sb.value = 0
        self.assertEqual(sb._thumb_pos, 0)
        sb.value = 100
        self.assertEqual(sb._thumb_pos, sb._track_len - 1)

    def test_thumb_works_with_multi_corner(self):
        sb = self._make(20, 1, min_val=0, max_val=100, horizontal=True, corner_char="─┘")
        self.assertEqual(sb._thumb_size, 1)
        sb.value = 100
        self.assertEqual(sb._thumb_pos, sb._track_len - 1)

    def test_thumb_works_with_both_left_and_corner(self):
        sb = self._make(20, 1, min_val=0, max_val=100, horizontal=True,
                        left_chars="└─", corner_char="─")
        self.assertEqual(sb._thumb_size, 1)
        sb.value = 0
        self.assertEqual(sb._thumb_pos, 0)
        sb.value = 100
        self.assertEqual(sb._thumb_pos, sb._track_len - 1)


class ScrollBarFullLayoutTest(unittest.TestCase):
    """Test all four scrollbar+resize-corner combinations from the TV layout table."""

    def _make(self, width, height, **kwargs):
        from textual.geometry import Size
        sb = _SizedScrollBar(**kwargs)
        sb._test_size = Size(width, height)
        return sb

    def test_both_scrollbars_geometry(self):
        vbar = self._make(1, 20, min_val=0, max_val=100, corner_char="┘")
        hbar = self._make(39, 1, min_val=0, max_val=100, horizontal=True,
                          left_chars="└─", corner_char="─")
        self.assertEqual(vbar._corner_len, 1)
        self.assertEqual(vbar._track_len, 17)
        self.assertEqual(hbar._left_len, 2)
        self.assertEqual(hbar._corner_len, 1)
        self.assertEqual(hbar._track_len, 34)

    def test_vscrollbar_only_geometry(self):
        vbar = self._make(1, 20, min_val=0, max_val=100, corner_char="┘")
        self.assertEqual(vbar._corner_len, 1)
        self.assertEqual(vbar._track_len, 17)

    def test_hscrollbar_only_geometry(self):
        hbar = self._make(40, 1, min_val=0, max_val=100, horizontal=True,
                          left_chars="└─", corner_char="─┘")
        self.assertEqual(hbar._left_len, 2)
        self.assertEqual(hbar._corner_len, 2)
        self.assertEqual(hbar._track_len, 34)

    def test_no_scrollbars_no_corner(self):
        vbar = self._make(1, 20, min_val=0, max_val=100)
        hbar = self._make(40, 1, min_val=0, max_val=100, horizontal=True)
        self.assertEqual(vbar._corner_len, 0)
        self.assertEqual(vbar._left_len, 0)
        self.assertEqual(vbar._track_len, 18)
        self.assertEqual(hbar._corner_len, 0)
        self.assertEqual(hbar._left_len, 0)
        self.assertEqual(hbar._track_len, 38)


class ScrollBarLeftCornerTest(unittest.TestCase):
    """Left corner must post CornerPressed(left=True) for left-side resize."""

    def test_left_chars_posts_corner_pressed_with_left_flag(self):
        import inspect
        source = inspect.getsource(ScrollBar.on_mouse_down)
        lines = source.split('\n')
        in_left_branch = False
        for line in lines:
            stripped = line.strip()
            if 'pos < ll' in stripped:
                in_left_branch = True
            elif in_left_branch:
                if 'CornerPressed' in stripped:
                    self.assertIn('left=True', stripped,
                                  "left_chars CornerPressed must pass left=True")
                    break
                if 'return' in stripped or 'elif' in stripped:
                    self.fail("left_chars branch must post CornerPressed(left=True)")

    def test_right_corner_posts_corner_pressed_without_left(self):
        import inspect
        source = inspect.getsource(ScrollBar.on_mouse_down)
        lines = source.split('\n')
        in_right_branch = False
        for line in lines:
            stripped = line.strip()
            if 'pos > arrow_end' in stripped:
                in_right_branch = True
            elif in_right_branch:
                if 'CornerPressed' in stripped:
                    self.assertNotIn('left=True', stripped,
                                     "right corner CornerPressed must not pass left=True")
                    break
                if 'return' in stripped or 'elif' in stripped:
                    self.fail("right corner branch must post CornerPressed")


class ScrollBarCssTest(unittest.TestCase):
    def test_has_component_classes(self):
        self.assertIn("scrollbar--arrow", ScrollBar.COMPONENT_CLASSES)
        self.assertIn("scrollbar--track", ScrollBar.COMPONENT_CLASSES)
        self.assertIn("scrollbar--thumb", ScrollBar.COMPONENT_CLASSES)

    def test_uses_theme_variables(self):
        css = ScrollBar.DEFAULT_CSS
        self.assertIn("$scrollbar-background", css)
        self.assertIn("$scrollbar", css)
        self.assertIn("$scrollbar-active", css)


if __name__ == "__main__":
    unittest.main()
