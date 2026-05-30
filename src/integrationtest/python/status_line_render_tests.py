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

from textual_vision.constants import Command
from textual_vision.status_line import StatusDef, StatusItem, StatusLine
from textual_vision.themes import (
    CGA_LIGHT_GRAY, CGA_BLACK, CGA_RED,
    register_themes,
)


def strip_to_text(strip):
    return "".join(seg.text for seg in strip._segments)


class StatusLineApp(App):
    CSS = """
    StatusLine { dock: bottom; width: 1fr; height: 1; }
    """

    def __init__(self):
        super().__init__()
        register_themes(self)
        self.theme = "turbo-pascal"

    def compose(self) -> ComposeResult:
        yield StatusLine(defs=[
            StatusDef(0, 0xFFFF, [
                StatusItem("~F1~ Help", "f1", Command.HELP),
                StatusItem("~F10~ Menu", "f10", Command.MENU),
                StatusItem("~Alt+X~ Exit", "alt+x", Command.QUIT),
            ]),
        ])


class StatusLineRenderTest(unittest.IsolatedAsyncioTestCase):
    """Test StatusLine renders with correct colors and visible text."""

    async def test_status_line_renders_text(self):
        """StatusLine should render status item text."""
        app = StatusLineApp()
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            sl = app.query_one(StatusLine)
            text = strip_to_text(sl.render_line(0))
            self.assertIn("Help", text,
                          f"StatusLine should render 'Help', got: {text!r}")

    async def test_status_line_renders_hotkey(self):
        """StatusLine should render hotkey labels."""
        app = StatusLineApp()
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            sl = app.query_one(StatusLine)
            text = strip_to_text(sl.render_line(0))
            self.assertIn("F1", text,
                          f"StatusLine should render 'F1', got: {text!r}")
            self.assertIn("F10", text)
            self.assertIn("Alt+X", text)

    async def test_status_line_background_is_lightgray(self):
        """StatusLine background should be CGA light gray (TV: BIOS 0x70)."""
        app = StatusLineApp()
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            sl = app.query_one(StatusLine)
            item_style = sl.get_component_rich_style("statusline--item")
            bg = item_style.bgcolor
            self.assertIsNotNone(bg, "StatusLine item bg should not be None")
            bg_hex = f"#{bg.triplet.red:02x}{bg.triplet.green:02x}{bg.triplet.blue:02x}"
            self.assertEqual(bg_hex.lower(), CGA_LIGHT_GRAY.lower(),
                             f"StatusLine bg should be CGA_LIGHT_GRAY "
                             f"({CGA_LIGHT_GRAY}), got {bg_hex}")

    async def test_status_line_text_color_is_dark(self):
        """StatusLine text should be dark (TV: black on lightgray)."""
        app = StatusLineApp()
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            sl = app.query_one(StatusLine)
            item_style = sl.get_component_rich_style("statusline--item")
            fg = item_style.color
            self.assertIsNotNone(fg, "StatusLine item fg should not be None")
            fg_hex = f"#{fg.triplet.red:02x}{fg.triplet.green:02x}{fg.triplet.blue:02x}"
            self.assertEqual(fg_hex.lower(), CGA_BLACK.lower(),
                             f"StatusLine text should be CGA_BLACK "
                             f"({CGA_BLACK}), got {fg_hex}")

    async def test_status_line_hotkey_color_is_red(self):
        """StatusLine hotkey should be red (TV: BIOS attr 4 = red)."""
        app = StatusLineApp()
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            sl = app.query_one(StatusLine)
            hotkey_style = sl.get_component_rich_style("statusline--hotkey")
            fg = hotkey_style.color
            self.assertIsNotNone(fg, "StatusLine hotkey fg should not be None")
            fg_hex = f"#{fg.triplet.red:02x}{fg.triplet.green:02x}{fg.triplet.blue:02x}"
            self.assertEqual(fg_hex.lower(), CGA_RED.lower(),
                             f"StatusLine hotkey should be CGA_RED "
                             f"({CGA_RED}), got {fg_hex}")

    async def test_status_line_full_width(self):
        """StatusLine rendered text should fill the full width."""
        app = StatusLineApp()
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            sl = app.query_one(StatusLine)
            text = strip_to_text(sl.render_line(0))
            self.assertEqual(len(text), sl.size.width,
                             f"StatusLine should fill width {sl.size.width}, "
                             f"got {len(text)}")

    async def test_status_line_height_is_one(self):
        app = StatusLineApp()
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            sl = app.query_one(StatusLine)
            self.assertEqual(sl.size.height, 1)


if __name__ == "__main__":
    unittest.main()
