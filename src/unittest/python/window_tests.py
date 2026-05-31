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

from textual_vision.constants import WindowFlag, OptionFlag
from textual_vision.frame import (Frame, FRAME_CHARS_ACTIVE, FRAME_CHARS_PASSIVE)
from textual_vision.window import Window


class FrameCharsTest(unittest.TestCase):
    def test_active_chars_double_line(self):
        self.assertEqual(FRAME_CHARS_ACTIVE["tl"], "╔")
        self.assertEqual(FRAME_CHARS_ACTIVE["tr"], "╗")
        self.assertEqual(FRAME_CHARS_ACTIVE["bl"], "╚")
        self.assertEqual(FRAME_CHARS_ACTIVE["br"], "╝")
        self.assertEqual(FRAME_CHARS_ACTIVE["h"], "═")
        self.assertEqual(FRAME_CHARS_ACTIVE["v"], "║")

    def test_passive_chars_single_line(self):
        self.assertEqual(FRAME_CHARS_PASSIVE["tl"], "┌")
        self.assertEqual(FRAME_CHARS_PASSIVE["tr"], "┐")
        self.assertEqual(FRAME_CHARS_PASSIVE["bl"], "└")
        self.assertEqual(FRAME_CHARS_PASSIVE["br"], "┘")
        self.assertEqual(FRAME_CHARS_PASSIVE["h"], "─")
        self.assertEqual(FRAME_CHARS_PASSIVE["v"], "│")

    def test_icon_chars_present(self):
        for chars in [FRAME_CHARS_ACTIVE, FRAME_CHARS_PASSIVE]:
            self.assertIn("close", chars)
            self.assertIn("zoom", chars)
            self.assertIn("unzoom", chars)


class FrameHitTestTest(unittest.TestCase):
    def test_close_icon_range(self):
        frame = Frame(flags=WindowFlag.CLOSE | WindowFlag.ZOOM)
        result = frame._close_icon_range(20)
        self.assertIsNotNone(result)
        self.assertEqual(result, (1, 4))

    def test_close_icon_range_no_close_flag(self):
        frame = Frame(flags=WindowFlag.ZOOM)
        result = frame._close_icon_range(20)
        self.assertIsNone(result)

    def test_zoom_icon_range(self):
        frame = Frame(flags=WindowFlag.CLOSE | WindowFlag.ZOOM)
        result = frame._zoom_icon_range(20)
        self.assertIsNotNone(result)
        self.assertEqual(result, (16, 19))

    def test_zoom_icon_range_no_zoom_flag(self):
        frame = Frame(flags=WindowFlag.CLOSE)
        result = frame._zoom_icon_range(20)
        self.assertIsNone(result)


class FrameResizeCornerHitTest(unittest.TestCase):
    """Frame must detect both bottom-left and bottom-right resize corners."""

    def _make_frame(self, width, height):
        from unittest.mock import PropertyMock, patch
        from textual.geometry import Size
        frame = Frame(flags=WindowFlag.GROW)
        patcher = patch.object(type(frame), 'size',
                               new_callable=PropertyMock,
                               return_value=Size(width, height))
        patcher.start()
        self.addCleanup(patcher.stop)
        return frame

    def test_hit_bottom_right_corner(self):
        frame = self._make_frame(20, 10)
        result = frame._hit_resize_corner(19, 9)
        self.assertTrue(result)
        self.assertEqual(result, "right")

    def test_hit_bottom_right_edge_cases(self):
        frame = self._make_frame(20, 10)
        self.assertTrue(frame._hit_resize_corner(18, 9))
        self.assertTrue(frame._hit_resize_corner(19, 8))

    def test_miss_interior(self):
        frame = self._make_frame(20, 10)
        self.assertFalse(frame._hit_resize_corner(10, 5))

    def test_no_grow_flag_no_hit(self):
        from unittest.mock import PropertyMock, patch
        from textual.geometry import Size
        frame = Frame(flags=WindowFlag.MOVE)
        with patch.object(type(frame), 'size',
                          new_callable=PropertyMock,
                          return_value=Size(20, 10)):
            self.assertFalse(frame._hit_resize_corner(19, 9))
            self.assertFalse(frame._hit_resize_corner(0, 9))

    def test_hit_bottom_left_corner(self):
        frame = self._make_frame(20, 10)
        result = frame._hit_resize_corner(0, 9)
        self.assertTrue(result)
        self.assertEqual(result, "left")

    def test_hit_bottom_left_edge_cases(self):
        frame = self._make_frame(20, 10)
        self.assertTrue(frame._hit_resize_corner(1, 9))
        self.assertTrue(frame._hit_resize_corner(0, 8))

    def test_miss_middle_bottom(self):
        frame = self._make_frame(20, 10)
        self.assertFalse(frame._hit_resize_corner(10, 9))


class FrameResizeStartMessageTest(unittest.TestCase):
    """Frame.ResizeStart must carry a 'left' flag."""

    def test_resize_start_has_left_attribute(self):
        msg = Frame.ResizeStart()
        self.assertTrue(hasattr(msg, "left"),
                        "ResizeStart must have a 'left' attribute")

    def test_resize_start_default_not_left(self):
        msg = Frame.ResizeStart()
        self.assertFalse(msg.left)

    def test_resize_start_left_true(self):
        msg = Frame.ResizeStart(left=True)
        self.assertTrue(msg.left)


class FrameBottomBorderTest(unittest.TestCase):
    """Test Frame.bottom_border_chars for all grow/active combinations and widths."""

    def test_active_no_grow_uses_double_line(self):
        result = Frame.bottom_border_chars(20, FRAME_CHARS_ACTIVE, has_grow=False)
        self.assertEqual(len(result), 20)
        self.assertEqual(result[0], "╚")
        self.assertEqual(result[-1], "╝")
        self.assertTrue(all(c == "═" for c in result[1:-1]))

    def test_passive_no_grow_uses_single_line(self):
        result = Frame.bottom_border_chars(20, FRAME_CHARS_PASSIVE, has_grow=False)
        self.assertEqual(len(result), 20)
        self.assertEqual(result[0], "└")
        self.assertEqual(result[-1], "┘")
        self.assertTrue(all(c == "─" for c in result[1:-1]))

    def test_active_grow_has_resize_indicators(self):
        result = Frame.bottom_border_chars(20, FRAME_CHARS_ACTIVE, has_grow=True)
        self.assertEqual(len(result), 20)
        self.assertEqual(result[0], "└")
        self.assertEqual(result[1], "─")
        self.assertEqual(result[-2], "─")
        self.assertEqual(result[-1], "┘")
        self.assertTrue(all(c == "═" for c in result[2:-2]))

    def test_grow_left_icon_is_single_line(self):
        result = Frame.bottom_border_chars(20, FRAME_CHARS_ACTIVE, has_grow=True)
        self.assertEqual(result[:2], "└─")

    def test_grow_right_icon_is_single_line(self):
        result = Frame.bottom_border_chars(20, FRAME_CHARS_ACTIVE, has_grow=True)
        self.assertEqual(result[-2:], "─┘")

    def test_grow_fill_uses_frame_h_char(self):
        result = Frame.bottom_border_chars(20, FRAME_CHARS_ACTIVE, has_grow=True)
        fill = result[2:-2]
        self.assertEqual(len(fill), 16)
        self.assertTrue(all(c == "═" for c in fill))

    def test_grow_width_4_minimal_fill(self):
        result = Frame.bottom_border_chars(4, FRAME_CHARS_ACTIVE, has_grow=True)
        self.assertEqual(result, "└──┘")

    def test_grow_width_3_single_middle(self):
        result = Frame.bottom_border_chars(3, FRAME_CHARS_ACTIVE, has_grow=True)
        self.assertEqual(result, "└─┘")

    def test_grow_width_2_just_corners(self):
        result = Frame.bottom_border_chars(2, FRAME_CHARS_ACTIVE, has_grow=True)
        self.assertEqual(result, "└┘")

    def test_no_grow_width_2(self):
        result = Frame.bottom_border_chars(2, FRAME_CHARS_ACTIVE, has_grow=False)
        self.assertEqual(result, "╚╝")

    def test_no_grow_width_3(self):
        result = Frame.bottom_border_chars(3, FRAME_CHARS_ACTIVE, has_grow=False)
        self.assertEqual(result, "╚═╝")

    def test_length_matches_width_no_grow(self):
        for width in range(2, 50):
            result = Frame.bottom_border_chars(width, FRAME_CHARS_ACTIVE, has_grow=False)
            self.assertEqual(len(result), width, f"width={width}")

    def test_length_matches_width_grow(self):
        for width in range(2, 50):
            result = Frame.bottom_border_chars(width, FRAME_CHARS_ACTIVE, has_grow=True)
            self.assertEqual(len(result), width, f"width={width}")

    def test_grow_uses_passive_fill_with_passive_chars(self):
        result = Frame.bottom_border_chars(10, FRAME_CHARS_PASSIVE, has_grow=True)
        fill = result[2:-2]
        self.assertTrue(all(c == "─" for c in fill))


class FramePropertyTest(unittest.TestCase):
    def test_title_property(self):
        frame = Frame(title="Test")
        self.assertEqual(frame.title, "Test")
        frame._title = "Changed"
        self.assertEqual(frame.title, "Changed")

    def test_flags_property(self):
        frame = Frame(flags=WindowFlag.MOVE | WindowFlag.CLOSE)
        self.assertEqual(frame.flags, WindowFlag.MOVE | WindowFlag.CLOSE)

    def test_chars_active(self):
        frame = Frame()
        frame.active = True
        self.assertEqual(frame._chars, FRAME_CHARS_ACTIVE)

    def test_chars_passive(self):
        frame = Frame()
        frame.active = False
        self.assertEqual(frame._chars, FRAME_CHARS_PASSIVE)

    def test_active_via_constructor(self):
        frame = Frame(active=True)
        self.assertTrue(frame.active)
        self.assertEqual(frame._chars, FRAME_CHARS_ACTIVE)

    def test_passive_by_default(self):
        frame = Frame()
        self.assertFalse(frame.active)
        self.assertEqual(frame._chars, FRAME_CHARS_PASSIVE)


class FrameCssTest(unittest.TestCase):
    def test_active_frame_uses_foreground_color(self):
        """Active frame border must be $foreground (white), not $primary."""
        css = Frame.DEFAULT_CSS
        active_section = css.split("frame--active")[1].split("}")[0]
        self.assertIn("$foreground", active_section)
        self.assertNotIn("$primary", active_section)

    def test_title_uses_foreground_color(self):
        """Frame title must be $foreground (white), not $primary."""
        css = Frame.DEFAULT_CSS
        title_section = css.split("frame--title")[1].split("}")[0]
        self.assertIn("$foreground", title_section)
        self.assertNotIn("$primary", title_section)

    def test_icon_uses_frame_icon_variable(self):
        css = Frame.DEFAULT_CSS
        icon_section = css.split("frame--icon")[1].split("}")[0]
        self.assertIn("$frame-icon", icon_section)


class FrameBottomBorderStyleTest(unittest.TestCase):
    """Regression: bottom border segments must carry explicit style (not None)."""

    def test_bottom_border_chars_not_using_text_base_style(self):
        """Text(text, style=style) loses style in render(); must use append()."""
        import inspect
        source = inspect.getsource(Frame._render_bottom_border)
        self.assertNotIn("Text(text", source)
        self.assertIn(".append(", source)

    def test_top_border_narrow_not_using_text_base_style(self):
        """Narrow top border also must use append(), not Text(text, style)."""
        import inspect
        source = inspect.getsource(Frame._render_top_border)
        self.assertNotIn("Text(chars", source)


class WindowPropertyTest(unittest.TestCase):
    def test_default_flags(self):
        win = Window(title="Test")
        expected = WindowFlag.MOVE | WindowFlag.CLOSE | WindowFlag.ZOOM | WindowFlag.GROW
        self.assertEqual(win.window_flags, expected)

    def test_custom_flags(self):
        win = Window(title="Test", flags=WindowFlag.MOVE | WindowFlag.CLOSE)
        self.assertEqual(win.window_flags, WindowFlag.MOVE | WindowFlag.CLOSE)

    def test_title(self):
        win = Window(title="My Window")
        self.assertEqual(win.title, "My Window")

    def test_number(self):
        win = Window(title="Test")
        self.assertEqual(win.number, 0)
        win.number = 5
        self.assertEqual(win.number, 5)

    def test_selectable_option(self):
        win = Window()
        self.assertIn(OptionFlag.SELECTABLE, win.tv_options)

    def test_initial_zoom_state(self):
        win = Window()
        self.assertFalse(win.zoomed)


class WindowUnmountedTest(unittest.TestCase):
    def test_frame_returns_none_when_unmounted(self):
        win = Window()
        self.assertIsNone(win.frame)

    def test_content_returns_none_when_unmounted(self):
        win = Window()
        self.assertIsNone(win.content)

    def test_css_uses_layers_for_frame_and_content(self):
        """Frame and content must be on separate CSS layers to overlap."""
        css = Window.DEFAULT_CSS
        self.assertIn("layers: frame content", css)
        self.assertIn("layer: frame", css)
        self.assertIn("layer: content", css)

    def test_css_uses_percentage_sizing(self):
        """Window default size must be proportional, not fixed."""
        css = Window.DEFAULT_CSS
        self.assertIn("%", css)

    def test_css_uses_window_content_background_variable(self):
        """Window background must be $window-content-background for per-theme control."""
        css = Window.DEFAULT_CSS
        self.assertIn("$window-content-background", css)

    def test_title_setter_safe_when_unmounted(self):
        """Setting title when not mounted must not crash (no Frame to update)."""
        win = Window(title="Original")
        win.title = "Changed"
        self.assertEqual(win.title, "Changed")

    def test_window_flags_setter_safe_when_unmounted(self):
        """Setting flags when not mounted must not crash."""
        win = Window()
        win.window_flags = WindowFlag.MOVE | WindowFlag.CLOSE
        self.assertEqual(win.window_flags, WindowFlag.MOVE | WindowFlag.CLOSE)

    def test_zoom_safe_when_unmounted(self):
        """zoom() must not crash when Frame is not composed yet."""
        win = Window()
        win.zoom()
        self.assertTrue(win.zoomed)

    def test_unzoom_safe_when_unmounted(self):
        """unzoom() must not crash when Frame is not composed yet."""
        win = Window()
        win.zoom()
        win.unzoom()
        self.assertFalse(win.zoomed)


class WindowZoomCssUnitTest(unittest.TestCase):
    def test_zoom_saves_width_as_css_string(self):
        """zoom() must save width as CSS string (e.g. '50w'), not bare float."""
        win = Window()
        win.styles.width = "50%"
        win.zoom()
        self.assertIsNotNone(win._pre_zoom_width)
        self.assertIsInstance(win._pre_zoom_width, str)
        self.assertEqual(win._pre_zoom_width, "50w")

    def test_zoom_saves_height_as_css_string(self):
        """zoom() must save height as CSS string (e.g. '60h'), not bare float."""
        win = Window()
        win.styles.height = "60%"
        win.zoom()
        self.assertIsNotNone(win._pre_zoom_height)
        self.assertIsInstance(win._pre_zoom_height, str)
        self.assertEqual(win._pre_zoom_height, "60h")

    def test_unzoom_restores_percentage_width(self):
        """unzoom() must restore percentage unit, not convert to cells."""
        win = Window()
        win.styles.width = "50%"
        win.styles.height = "60%"
        original_w = str(win.styles.width)
        original_h = str(win.styles.height)
        win.zoom()
        win.unzoom()
        self.assertEqual(str(win.styles.width), original_w)
        self.assertEqual(str(win.styles.height), original_h)

    def test_zoom_saves_cell_width(self):
        """zoom() preserves cell-based widths too."""
        win = Window()
        win.styles.width = 40
        win.zoom()
        self.assertIsNotNone(win._pre_zoom_width)
        self.assertEqual(win._pre_zoom_width, "40")


class WindowResizeUnitTest(unittest.TestCase):
    def test_resize_uses_tracked_targets(self):
        """_apply_resize_delta must accumulate onto tracked targets, not re-read self.size."""
        import inspect
        source = inspect.getsource(Window._apply_resize_delta)
        self.assertIn("_resize_target_w", source)
        self.assertIn("_resize_target_h", source)
        self.assertNotIn("styles.width.value", source)
        self.assertNotIn("styles.height.value", source)

    def test_resize_target_initialized_from_size(self):
        """_apply_resize_delta initializes targets from self.size on first call."""
        import inspect
        source = inspect.getsource(Window._apply_resize_delta)
        self.assertIn("self.size.width", source)
        self.assertIn("self.size.height", source)

    def test_end_resize_clears_targets(self):
        win = Window()
        win._resize_target_w = 50
        win._resize_target_h = 30
        win._end_resize()
        self.assertIsNone(win._resize_target_w)
        self.assertIsNone(win._resize_target_h)


class WindowZoomTest(unittest.TestCase):
    def test_zoom_sets_state(self):
        win = Window()
        win.zoom()
        self.assertTrue(win.zoomed)

    def test_unzoom_clears_state(self):
        win = Window()
        win.zoom()
        win.unzoom()
        self.assertFalse(win.zoomed)

    def test_zoom_when_already_zoomed_is_noop(self):
        win = Window()
        win.zoom()
        win.zoom()
        self.assertTrue(win.zoomed)

    def test_unzoom_when_not_zoomed_is_noop(self):
        win = Window()
        win.unzoom()
        self.assertFalse(win.zoomed)

    def test_toggle_zoom(self):
        win = Window()
        win.toggle_zoom()
        self.assertTrue(win.zoomed)
        win.toggle_zoom()
        self.assertFalse(win.zoomed)


if __name__ == "__main__":
    unittest.main()
