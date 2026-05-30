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
from textual.containers import Container

from textual_vision.scroll_bar import ScrollBar


class BothScrollbarsWindow(Container):
    """Minimal window-like container with both scrollbars and corner chars."""

    DEFAULT_CSS = """
    BothScrollbarsWindow {
        width: 40;
        height: 20;
        background: blue;
    }
    BothScrollbarsWindow .vscrollbar {
        width: 1;
        dock: right;
        margin: 1 0 0 0;
        layer: default;
    }
    BothScrollbarsWindow .hscrollbar {
        height: 1;
        dock: bottom;
        margin: 0 1 0 0;
        layer: default;
    }
    """

    def compose(self) -> ComposeResult:
        yield ScrollBar(min_val=0, max_val=100, page_step=10, arrow_step=1,
                        horizontal=False, corner_char="┘",
                        classes="vscrollbar")
        yield ScrollBar(min_val=0, max_val=100, page_step=10, arrow_step=1,
                        horizontal=True, left_chars="└─", corner_char="─",
                        classes="hscrollbar")


class BothScrollbarsApp(App):
    CSS = """
    BothScrollbarsWindow {
        width: 40;
        height: 20;
    }
    """

    def compose(self) -> ComposeResult:
        yield BothScrollbarsWindow()


def strip_to_text(strip):
    return "".join(seg.text for seg in strip._segments)


class WindowCornerLayoutTest(unittest.IsolatedAsyncioTestCase):
    """Test the actual composed layout of scrollbars inside a container."""

    async def test_vscrollbar_actual_height(self):
        app = BothScrollbarsApp()
        async with app.run_test(size=(42, 22)) as pilot:
            await pilot.pause()
            vbar = app.query_one(".vscrollbar", ScrollBar)
            hbar = app.query_one(".hscrollbar", ScrollBar)
            print(f"vbar size: {vbar.size}, hbar size: {hbar.size}")
            print(f"vbar region: {vbar.region}, hbar region: {hbar.region}")
            self.assertGreater(vbar.size.height, 0,
                               "VScrollbar should have non-zero height")

    async def test_hscrollbar_actual_width(self):
        app = BothScrollbarsApp()
        async with app.run_test(size=(42, 22)) as pilot:
            await pilot.pause()
            hbar = app.query_one(".hscrollbar", ScrollBar)
            self.assertGreater(hbar.size.width, 0,
                               "HScrollbar should have non-zero width")

    async def test_vscrollbar_bottom_renders_corner(self):
        """The bottom cell of the vscrollbar should render ┘."""
        app = BothScrollbarsApp()
        async with app.run_test(size=(42, 22)) as pilot:
            await pilot.pause()
            vbar = app.query_one(".vscrollbar", ScrollBar)
            h = vbar.size.height
            text = strip_to_text(vbar.render_line(h - 1))
            self.assertEqual(text[0], "┘",
                             f"VBar bottom should render ┘, got: {text!r} "
                             f"(vbar height={h}, region={vbar.region})")

    async def test_hscrollbar_last_char_renders_corner(self):
        """The last character of the hscrollbar should render ─."""
        app = BothScrollbarsApp()
        async with app.run_test(size=(42, 22)) as pilot:
            await pilot.pause()
            hbar = app.query_one(".hscrollbar", ScrollBar)
            w = hbar.size.width
            text = strip_to_text(hbar.render_line(0))[:w]
            self.assertEqual(text[-1], "─",
                             f"HBar last char should be ─, got: {text!r} "
                             f"(hbar width={w}, region={hbar.region})")

    async def test_hscrollbar_first_chars_render_left_border(self):
        """The first two characters should be └─."""
        app = BothScrollbarsApp()
        async with app.run_test(size=(42, 22)) as pilot:
            await pilot.pause()
            hbar = app.query_one(".hscrollbar", ScrollBar)
            text = strip_to_text(hbar.render_line(0))
            self.assertEqual(text[:2], "└─",
                             f"HBar first 2 chars should be └─, got: {text!r}")

    async def test_vbar_and_hbar_adjacent_at_corner(self):
        """VBar ┘ must be immediately to the right of HBar ─ at the bottom row."""
        app = BothScrollbarsApp()
        async with app.run_test(size=(42, 22)) as pilot:
            await pilot.pause()
            vbar = app.query_one(".vscrollbar", ScrollBar)
            hbar = app.query_one(".hscrollbar", ScrollBar)
            vbar_region = vbar.region
            hbar_region = hbar.region
            hbar_right_edge = hbar_region.x + hbar_region.width
            vbar_left_edge = vbar_region.x
            self.assertEqual(hbar_right_edge, vbar_left_edge,
                             f"HBar right edge ({hbar_right_edge}) must equal "
                             f"VBar left edge ({vbar_left_edge}). "
                             f"hbar region={hbar_region}, vbar region={vbar_region}")

    async def test_corner_row_alignment(self):
        """Both scrollbars must share the same bottom row for the corner."""
        app = BothScrollbarsApp()
        async with app.run_test(size=(42, 22)) as pilot:
            await pilot.pause()
            vbar = app.query_one(".vscrollbar", ScrollBar)
            hbar = app.query_one(".hscrollbar", ScrollBar)
            vbar_bottom = vbar.region.y + vbar.size.height - 1
            hbar_row = hbar.region.y
            self.assertEqual(vbar_bottom, hbar_row,
                             f"VBar bottom row ({vbar_bottom}) must equal "
                             f"HBar row ({hbar_row}). "
                             f"vbar region={vbar.region}, hbar region={hbar.region}")


class _ThemedApp(App):
    """Base test app that registers TV themes."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from textual_vision.themes import register_themes
        register_themes(self)
        self.theme = "turbo-pascal"


class FrameDialogApp(_ThemedApp):
    CSS = """
    Screen {
        layers: background windows menus;
    }
    """

    def compose(self) -> ComposeResult:
        from textual_vision.desktop import DeskTop
        yield DeskTop()


class FrameBorderStyleTest(unittest.IsolatedAsyncioTestCase):
    """Regression: Frame border Segments must have explicit style, not None."""

    async def test_bottom_border_segments_have_style(self):
        from textual_vision.dialogs import Dialog
        from textual_vision.frame import Frame
        from textual_vision.input_line import InputLine

        class _Dlg(Dialog):
            def on_mount(self):
                super().on_mount()
                content = self.query_one(".tv-window-content")
                content.mount(InputLine(max_len=40, name="first"))
                content.mount(InputLine(max_len=40, name="second"))

        app = FrameDialogApp()
        async with app.run_test(size=(60, 20)) as pilot:
            dlg = _Dlg(title="Test")
            dlg.styles.width = 40
            dlg.styles.height = 10
            app.query_one("DeskTop").insert_window(dlg)
            await pilot.pause()
            await pilot.pause()

            frame = dlg.query_one(Frame)
            bottom_strip = frame.render_line(frame.size.height - 1)
            for seg in bottom_strip._segments:
                if seg.text.strip():
                    self.assertIsNotNone(seg.style,
                                         f"Bottom border segment {seg.text!r} has style=None "
                                         f"(BLACK background)")

    async def test_bottom_border_has_correct_background(self):
        from textual_vision.dialogs import Dialog
        from textual_vision.frame import Frame
        from textual_vision.input_line import InputLine

        class _Dlg(Dialog):
            def on_mount(self):
                super().on_mount()
                content = self.query_one(".tv-window-content")
                content.mount(InputLine(max_len=40, name="first"))

        app = FrameDialogApp()
        async with app.run_test(size=(60, 20)) as pilot:
            dlg = _Dlg(title="Test")
            dlg.styles.width = 40
            dlg.styles.height = 10
            app.query_one("DeskTop").insert_window(dlg)
            await pilot.pause()
            await pilot.pause()

            frame = dlg.query_one(Frame)
            bottom_strip = frame.render_line(frame.size.height - 1)
            for seg in bottom_strip._segments:
                if seg.text.strip() and seg.style is not None:
                    self.assertIsNotNone(seg.style.bgcolor,
                                         "Bottom border must have explicit bgcolor")


class FrameResizeCornerTest(unittest.IsolatedAsyncioTestCase):
    """Integration: clicking bottom-left corner must start left-resize."""

    async def test_bottom_left_resize_starts(self):
        """Mouse-down on the bottom-left corner must enter left-resize mode."""
        from textual_vision.window import Window
        from textual_vision.frame import Frame

        app = FrameDialogApp()
        async with app.run_test(size=(80, 30)) as pilot:
            win = Window(title="ResizeTest")
            win.styles.width = 40
            win.styles.height = 15
            win.styles.offset = (10, 5)
            app.query_one("DeskTop").insert_window(win)
            await pilot.pause()
            await pilot.pause()

            frame = win.query_one(Frame)
            self.assertGreater(frame.size.height, 2, "Frame must have rendered")

            fr = frame.region
            await pilot.mouse_down(offset=(fr.x, fr.y + fr.height - 1))
            await pilot.pause()
            self.assertTrue(win._resizing,
                            "Window should be in resize mode after mouse-down on bottom-left")
            self.assertTrue(win._resize_left,
                            "Resize should be in left mode after bottom-left corner")

    async def test_bottom_right_resize_not_left(self):
        """Mouse-down on the bottom-right corner must enter right-resize mode."""
        from textual_vision.window import Window
        from textual_vision.frame import Frame

        app = FrameDialogApp()
        async with app.run_test(size=(80, 30)) as pilot:
            win = Window(title="ResizeTest")
            win.styles.width = 40
            win.styles.height = 15
            win.styles.offset = (10, 5)
            app.query_one("DeskTop").insert_window(win)
            await pilot.pause()
            await pilot.pause()

            frame = win.query_one(Frame)
            fr = frame.region
            await pilot.mouse_down(offset=(fr.x + fr.width - 1, fr.y + fr.height - 1))
            await pilot.pause()
            self.assertTrue(win._resizing,
                            "Window should be in resize mode after mouse-down on bottom-right")
            self.assertFalse(win._resize_left,
                             "Resize should NOT be left mode for bottom-right corner")


if __name__ == "__main__":
    unittest.main()
