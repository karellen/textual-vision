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
from textual.strip import Strip

from textual_vision.scroll_bar import ScrollBar


from textual_vision.themes import (
    CGA_BLUE, CGA_LIGHT_BLUE, CGA_LIGHT_CYAN,
    register_themes,
)


class VerticalScrollBarApp(App):
    CSS = """
    ScrollBar { width: 1; height: 12; }
    """

    def compose(self) -> ComposeResult:
        yield ScrollBar(min_val=0, max_val=100, page_step=10, arrow_step=1,
                        horizontal=False)


class HorizontalScrollBarApp(App):
    CSS = """
    ScrollBar { width: 20; height: 1; }
    """

    def compose(self) -> ComposeResult:
        yield ScrollBar(min_val=0, max_val=100, page_step=10, arrow_step=1,
                        horizontal=True)


class VerticalCornerScrollBarApp(App):
    CSS = """
    ScrollBar { width: 1; height: 12; }
    """

    def compose(self) -> ComposeResult:
        yield ScrollBar(min_val=0, max_val=100, page_step=10, arrow_step=1,
                        horizontal=False, corner_char="┘")


class HorizontalCornerScrollBarApp(App):
    CSS = """
    ScrollBar { width: 20; height: 1; }
    """

    def compose(self) -> ComposeResult:
        yield ScrollBar(min_val=0, max_val=100, page_step=10, arrow_step=1,
                        horizontal=True, left_chars="└─", corner_char="─")


class HorizontalOnlyCornerScrollBarApp(App):
    CSS = """
    ScrollBar { width: 20; height: 1; }
    """

    def compose(self) -> ComposeResult:
        yield ScrollBar(min_val=0, max_val=100, page_step=10, arrow_step=1,
                        horizontal=True, left_chars="└─", corner_char="─┘")


def strip_to_text(strip: Strip) -> str:
    return "".join(seg.text for seg in strip._segments)


class ScrollBarCornerRenderTest(unittest.IsolatedAsyncioTestCase):
    """Test rendered characters for scrollbars with corner_char and left_chars."""

    async def test_vertical_corner_bottom_row_is_corner_char(self):
        app = VerticalCornerScrollBarApp()
        async with app.run_test(size=(3, 14)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            h = sb.size.height
            text = strip_to_text(sb.render_line(h - 1))
            self.assertEqual(text[0], "┘",
                             f"Bottom row should be ┘, got: {text!r}")

    async def test_vertical_corner_down_arrow_moves_up(self):
        app = VerticalCornerScrollBarApp()
        async with app.run_test(size=(3, 14)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            h = sb.size.height
            text = strip_to_text(sb.render_line(h - 2))
            self.assertEqual(text[0], "▼",
                             f"Row h-2 should be ▼, got: {text!r}")

    async def test_vertical_corner_track_len_reduced_by_one(self):
        app = VerticalCornerScrollBarApp()
        async with app.run_test(size=(3, 14)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            self.assertEqual(sb._track_len, sb.size.height - 3)

    async def test_horizontal_left_chars_rendered_first(self):
        app = HorizontalCornerScrollBarApp()
        async with app.run_test(size=(22, 3)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            text = strip_to_text(sb.render_line(0))
            self.assertEqual(text[0], "└",
                             f"First char should be └, got: {text!r}")
            self.assertEqual(text[1], "─",
                             f"Second char should be ─, got: {text!r}")

    async def test_horizontal_left_arrow_after_left_chars(self):
        app = HorizontalCornerScrollBarApp()
        async with app.run_test(size=(22, 3)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            text = strip_to_text(sb.render_line(0))
            self.assertEqual(text[2], "◄",
                             f"Third char should be ◄, got: {text!r}")

    async def test_horizontal_corner_char_at_end(self):
        app = HorizontalCornerScrollBarApp()
        async with app.run_test(size=(22, 3)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            w = sb.size.width
            text = strip_to_text(sb.render_line(0))
            content = text[:w]
            self.assertEqual(content[-2], "►",
                             f"Second-to-last should be ►, got: {content!r}")
            self.assertEqual(content[-1], "─",
                             f"Last char should be ─, got: {content!r}")

    async def test_horizontal_full_layout_both_scrollbars(self):
        """Horizontal scrollbar for both-scrollbars case: └─◄[track]►─"""
        app = HorizontalCornerScrollBarApp()
        async with app.run_test(size=(22, 3)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            w = sb.size.width
            text = strip_to_text(sb.render_line(0))[:w]
            self.assertEqual(text[:3], "└─◄",
                             f"Left edge should be └─◄, got: {text!r}")
            self.assertEqual(text[-2:], "►─",
                             f"Right edge should be ►─, got: {text!r}")
            self.assertEqual(len(text), w,
                             f"Total width should be {w}, got {len(text)}")

    async def test_horizontal_full_layout_hscrollbar_only(self):
        """Horizontal scrollbar for h-only case: └─◄[track]►─┘"""
        app = HorizontalOnlyCornerScrollBarApp()
        async with app.run_test(size=(22, 3)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            w = sb.size.width
            text = strip_to_text(sb.render_line(0))[:w]
            self.assertEqual(text[:3], "└─◄",
                             f"Left edge should be └─◄, got: {text!r}")
            self.assertEqual(text[-3:], "►─┘",
                             f"Right edge should be ►─┘, got: {text!r}")
            self.assertEqual(len(text), w,
                             f"Total width should be {w}, got {len(text)}")

    async def test_horizontal_track_len_with_both_left_and_corner(self):
        app = HorizontalCornerScrollBarApp()
        async with app.run_test(size=(22, 3)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            expected = sb.size.width - 2 - 1 - 2
            self.assertEqual(sb._track_len, expected)


class ScrollBarVerticalRenderTest(unittest.IsolatedAsyncioTestCase):
    async def test_top_arrow_is_up_triangle(self):
        app = VerticalScrollBarApp()
        async with app.run_test(size=(3, 14)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            line = sb.render_line(0)
            text = strip_to_text(line)
            self.assertIn("▲", text,
                          f"Top arrow should be ▲, got: {text!r}")

    async def test_bottom_arrow_is_down_triangle(self):
        app = VerticalScrollBarApp()
        async with app.run_test(size=(3, 14)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            line = sb.render_line(sb.size.height - 1)
            text = strip_to_text(line)
            self.assertIn("▼", text,
                          f"Bottom arrow should be ▼, got: {text!r}")

    async def test_track_uses_medium_shade(self):
        app = VerticalScrollBarApp()
        async with app.run_test(size=(3, 14)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            sb.set_value(sb.max_val)
            track_text = strip_to_text(sb.render_line(2))
            self.assertIn("▒", track_text,
                          f"Track should use ▒ (medium shade), got: {track_text!r}")
            self.assertNotIn("░", track_text,
                             "Track should NOT use ░ (light shade)")
            self.assertNotIn("█", track_text,
                             "Track should NOT use █ (full block)")

    async def test_thumb_uses_black_square(self):
        app = VerticalScrollBarApp()
        async with app.run_test(size=(3, 14)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            sb.set_value(0)
            found_thumb = False
            for y in range(1, sb.size.height - 1):
                text = strip_to_text(sb.render_line(y))
                if "■" in text:
                    found_thumb = True
                    break
            self.assertTrue(found_thumb,
                            "Thumb should use ■ (black square) somewhere in the track")

    async def test_thumb_not_full_block(self):
        app = VerticalScrollBarApp()
        async with app.run_test(size=(3, 14)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            for y in range(1, sb.size.height - 1):
                text = strip_to_text(sb.render_line(y))
                self.assertNotIn("█", text,
                                 f"Thumb should NOT use █ (full block), at row {y}: {text!r}")


class ScrollBarHorizontalRenderTest(unittest.IsolatedAsyncioTestCase):
    async def test_left_arrow(self):
        app = HorizontalScrollBarApp()
        async with app.run_test(size=(22, 3)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            line = sb.render_line(0)
            text = strip_to_text(line)
            self.assertTrue(text.startswith("◄"),
                            f"Horizontal left arrow should be ◄, got: {text!r}")

    async def test_right_arrow(self):
        app = HorizontalScrollBarApp()
        async with app.run_test(size=(22, 3)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            line = sb.render_line(0)
            text = strip_to_text(line)
            content = text[:sb.size.width]
            self.assertIn("►", content,
                          f"Horizontal right arrow should be ►, got: {content!r}")

    async def test_track_uses_medium_shade(self):
        app = HorizontalScrollBarApp()
        async with app.run_test(size=(22, 3)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            sb.set_value(sb.max_val)
            line = sb.render_line(0)
            text = strip_to_text(line)
            self.assertIn("▒", text,
                          f"Horizontal track should use ▒ (medium shade), got: {text!r}")
            self.assertNotIn("░", text,
                             "Horizontal track should NOT use ░ (light shade)")

    async def test_thumb_uses_black_square(self):
        app = HorizontalScrollBarApp()
        async with app.run_test(size=(22, 3)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            sb.set_value(50)
            line = sb.render_line(0)
            text = strip_to_text(line)
            self.assertIn("■", text,
                          f"Horizontal thumb should use ■ (black square), got: {text!r}")
            self.assertNotIn("█", text,
                             "Horizontal thumb should NOT use █ (full block)")


class TVThemedScrollBarApp(App):
    CSS = """
    ScrollBar { width: 1; height: 12; }
    """

    def __init__(self):
        super().__init__()
        register_themes(self)
        self.theme = "turbo-pascal"

    def compose(self) -> ComposeResult:
        yield ScrollBar(min_val=0, max_val=100, page_step=10, arrow_step=1,
                        horizontal=False)


class ScrollBarThemeColorTest(unittest.IsolatedAsyncioTestCase):
    """Verify scrollbar colors resolve correctly under the turbo-pascal theme."""

    async def test_track_background_is_cga_blue(self):
        app = TVThemedScrollBarApp()
        async with app.run_test(size=(3, 14)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            track_style = sb.get_component_rich_style("scrollbar--track")
            bg = track_style.bgcolor
            self.assertIsNotNone(bg, "Track background should not be None")
            bg_hex = f"#{bg.triplet.red:02x}{bg.triplet.green:02x}{bg.triplet.blue:02x}"
            self.assertEqual(bg_hex.lower(), CGA_BLUE.lower(),
                             f"Track background should be CGA_BLUE ({CGA_BLUE}), got {bg_hex}")

    async def test_arrow_color_is_cga_light_blue(self):
        app = TVThemedScrollBarApp()
        async with app.run_test(size=(3, 14)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            arrow_style = sb.get_component_rich_style("scrollbar--arrow")
            fg = arrow_style.color
            self.assertIsNotNone(fg, "Arrow foreground should not be None")
            fg_hex = f"#{fg.triplet.red:02x}{fg.triplet.green:02x}{fg.triplet.blue:02x}"
            self.assertEqual(fg_hex.lower(), CGA_LIGHT_BLUE.lower(),
                             f"Arrow color should be CGA_LIGHT_BLUE ({CGA_LIGHT_BLUE}), got {fg_hex}")

    async def test_thumb_color_is_cga_light_cyan(self):
        app = TVThemedScrollBarApp()
        async with app.run_test(size=(3, 14)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            thumb_style = sb.get_component_rich_style("scrollbar--thumb")
            fg = thumb_style.color
            self.assertIsNotNone(fg, "Thumb foreground should not be None")
            fg_hex = f"#{fg.triplet.red:02x}{fg.triplet.green:02x}{fg.triplet.blue:02x}"
            self.assertEqual(fg_hex.lower(), CGA_LIGHT_CYAN.lower(),
                             f"Thumb color should be CGA_LIGHT_CYAN ({CGA_LIGHT_CYAN}), got {fg_hex}")

    async def test_scrollbar_background_is_cga_blue(self):
        app = TVThemedScrollBarApp()
        async with app.run_test(size=(3, 14)) as pilot:
            await pilot.pause()
            sb = app.query_one(ScrollBar)
            bg = sb.rich_style.bgcolor
            self.assertIsNotNone(bg, "ScrollBar background should not be None")
            bg_hex = f"#{bg.triplet.red:02x}{bg.triplet.green:02x}{bg.triplet.blue:02x}"
            self.assertEqual(bg_hex.lower(), CGA_BLUE.lower(),
                             f"ScrollBar background should be CGA_BLUE ({CGA_BLUE}), got {bg_hex}")


if __name__ == "__main__":
    unittest.main()
