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

from textual_vision.app import Application
from textual_vision.menus import Menu, MenuItem, SubMenu
from textual_vision.status_line import StatusDef, StatusItem
from textual_vision.constants import Command
from textual_vision.themes import (
    CGA_BLUE, CGA_BLACK, CGA_LIGHT_GRAY, CGA_YELLOW,
    CGA_WHITE, CGA_RED,
)


CMD_THEME_TP = Command.USER + 10
CMD_THEME_TC = Command.USER + 11
CMD_THEME_TC_1X = Command.USER + 12
CMD_THEME_TC_TURQUOISE = Command.USER + 13


class ThemeSwitchApp(Application):
    CSS = """
    Screen {
        layers: background windows menus;
    }
    """

    def init_menu_bar(self):
        return Menu(items=[
            SubMenu(
                "~S~ettings",
                MenuItem("~T~urbo Pascal", CMD_THEME_TP),
                MenuItem("Turbo ~C~", CMD_THEME_TC),
                MenuItem("Turbo C ~1~.x", CMD_THEME_TC_1X),
                MenuItem("Turbo C T~u~rquoise", CMD_THEME_TC_TURQUOISE),
            ),
        ])

    def init_status_line(self):
        return [
            StatusDef(0, 0xFFFF, [
                StatusItem("~F10~ Menu", "f10", Command.MENU),
            ]),
        ]

    def on_command_message(self, message):
        if message.command == CMD_THEME_TP:
            self.theme = "turbo-pascal"
            message.stop()
        elif message.command == CMD_THEME_TC:
            self.theme = "turbo-c"
            message.stop()
        elif message.command == CMD_THEME_TC_1X:
            self.theme = "turbo-c-1x"
            message.stop()
        elif message.command == CMD_THEME_TC_TURQUOISE:
            self.theme = "turbo-c-turquoise"
            message.stop()
        else:
            super().on_command_message(message)


class ThemeSwitchTest(unittest.IsolatedAsyncioTestCase):

    async def test_default_theme_is_turbo_pascal(self):
        app = ThemeSwitchApp()
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            self.assertEqual(app.theme, "turbo-pascal")

    async def test_switch_to_all_themes(self):
        """All four themes can be activated without error."""
        app = ThemeSwitchApp()
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            for theme_name in ("turbo-c", "turbo-c-1x",
                               "turbo-c-turquoise", "turbo-pascal"):
                app.theme = theme_name
                await pilot.pause()
                self.assertEqual(app.theme, theme_name)

    async def test_turbo_pascal_background_is_blue(self):
        app = ThemeSwitchApp()
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            desktop = app.desktop
            bg_widget = desktop.query_one("Background")
            bg_style = bg_widget.rich_style
            bg = bg_style.bgcolor
            self.assertIsNotNone(bg)
            bg_hex = f"#{bg.triplet.red:02x}{bg.triplet.green:02x}{bg.triplet.blue:02x}"
            self.assertEqual(bg_hex.lower(), CGA_BLUE.lower())

    async def test_turbo_c_turquoise_background_is_black(self):
        app = ThemeSwitchApp()
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            app.theme = "turbo-c-turquoise"
            await pilot.pause()
            desktop = app.desktop
            bg_widget = desktop.query_one("Background")
            bg_style = bg_widget.rich_style
            bg = bg_style.bgcolor
            self.assertIsNotNone(bg)
            bg_hex = f"#{bg.triplet.red:02x}{bg.triplet.green:02x}{bg.triplet.blue:02x}"
            self.assertEqual(bg_hex.lower(), CGA_BLACK.lower())

    async def test_statusline_bg_follows_footer_background(self):
        """StatusLine bg uses $footer-background, varying per theme."""
        app = ThemeSwitchApp()
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            sl = app.query_one("StatusLine")

            style1 = sl.get_component_rich_style("statusline--item")
            bg1 = f"#{style1.bgcolor.triplet.red:02x}{style1.bgcolor.triplet.green:02x}{style1.bgcolor.triplet.blue:02x}"
            self.assertEqual(bg1.lower(), CGA_LIGHT_GRAY.lower(),
                             "TP status bg should be light gray")

            app.theme = "turbo-c-turquoise"
            await pilot.pause()
            style2 = sl.get_component_rich_style("statusline--item")
            bg2 = f"#{style2.bgcolor.triplet.red:02x}{style2.bgcolor.triplet.green:02x}{style2.bgcolor.triplet.blue:02x}"
            self.assertEqual(bg2.lower(), CGA_BLUE.lower(),
                             "TC Turquoise status bg should be blue")


class TurboCPaletteTest(unittest.IsolatedAsyncioTestCase):
    """TC 2.01 default: gray chrome, yellow editor, white-on-black hotkey."""

    async def test_tc_surface_is_gray(self):
        from textual_vision.themes import THEME_TURBO_C
        self.assertEqual(THEME_TURBO_C.surface.lower(), CGA_LIGHT_GRAY.lower())

    async def test_tc_foreground_is_yellow(self):
        from textual_vision.themes import THEME_TURBO_C
        self.assertEqual(THEME_TURBO_C.foreground.lower(), CGA_YELLOW.lower())

    async def test_tc_menu_hotkey_is_white_on_black(self):
        from textual_vision.themes import THEME_TURBO_C
        self.assertEqual(THEME_TURBO_C.variables["menu-hotkey"], CGA_WHITE)
        self.assertEqual(THEME_TURBO_C.variables["menu-hotkey-background"],
                         CGA_BLACK)

    async def test_tc_status_hotkey_is_red(self):
        from textual_vision.themes import THEME_TURBO_C
        self.assertEqual(THEME_TURBO_C.variables["footer-key-foreground"],
                         CGA_RED)


if __name__ == "__main__":
    unittest.main()
