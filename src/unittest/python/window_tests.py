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

    def test_icon_uses_accent_color(self):
        """Frame icons must use $accent (green)."""
        css = Frame.DEFAULT_CSS
        icon_section = css.split("frame--icon")[1].split("}")[0]
        self.assertIn("$accent", icon_section)


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

    def test_css_uses_background_variable_for_blue(self):
        """Window background must be $background (blue), not $surface (gray)."""
        css = Window.DEFAULT_CSS
        self.assertIn("$background", css)
        self.assertNotIn("$surface", css)

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
    def test_resize_uses_computed_size_not_style_value(self):
        """on_frame_resize_move must use self.size (computed cells), not styles.width.value."""
        import inspect
        source = inspect.getsource(Window.on_frame_resize_move)
        self.assertIn("self.size.width", source)
        self.assertIn("self.size.height", source)
        self.assertNotIn("styles.width.value", source)
        self.assertNotIn("styles.height.value", source)


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
