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

from textual_vision.constants import Command
from textual_vision.app import Application
from textual_vision.desktop import DeskTop
from textual_vision.menus import Menu, MenuItem, SubMenu
from textual_vision.status_line import StatusDef, StatusItem
from textual_vision.window import Window


class TestApp(Application):
    def init_menu_bar(self):
        return Menu(items=[
            SubMenu(
                "~F~ile",
                MenuItem("~N~ew", Command.NEW, key_code="Ctrl+N"),
                MenuItem("E~x~it", Command.QUIT, key_code="Alt+X"),
            ),
            SubMenu(
                "~H~elp",
                MenuItem("~A~bout", Command.HELP),
            ),
        ])

    def init_status_line(self):
        return [
            StatusDef(0, 99, [
                StatusItem("~F1~ Help", "f1", Command.HELP),
                StatusItem("~F10~ Menu", "f10", Command.MENU),
            ]),
        ]


class AppLifecycleTest(unittest.IsolatedAsyncioTestCase):
    async def test_app_composes_correctly(self):
        app = TestApp()
        async with app.run_test():
            self.assertIsNotNone(app.menu_bar)
            self.assertIsNotNone(app.desktop)
            self.assertIsNotNone(app.status_line)
            self.assertIsInstance(app.desktop, DeskTop)

    async def test_insert_window(self):
        app = TestApp()
        async with app.run_test() as pilot:
            win = Window(title="Test Window")
            app.insert_window(win)
            await pilot.pause()
            windows = app.desktop.query(Window)
            self.assertEqual(len(list(windows)), 1)

    async def test_f10_activates_menu(self):
        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.press("f10")
            await pilot.pause()
            self.assertTrue(app.menu_bar.active)

    async def test_f10_toggle_deactivates_menu(self):
        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.press("f10")
            await pilot.pause()
            self.assertTrue(app.menu_bar.active)
            await pilot.press("f10")
            await pilot.pause()
            self.assertFalse(app.menu_bar.active)


class MenuDismissTest(unittest.IsolatedAsyncioTestCase):
    async def test_enter_on_dropdown_item_dismisses_menu(self):
        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.press("f10")
            await pilot.pause()
            self.assertTrue(app.menu_bar.active)
            await pilot.press("enter")
            await pilot.pause()
            self.assertIsNotNone(app.menu_bar._menu_box)
            await pilot.press("enter")
            await pilot.pause()
            self.assertFalse(app.menu_bar.active)

    async def test_escape_on_dropdown_dismisses_menu(self):
        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.press("f10")
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            self.assertIsNotNone(app.menu_bar._menu_box)
            await pilot.press("escape")
            await pilot.pause()
            self.assertFalse(app.menu_bar.active)

    async def test_click_on_dropdown_item_dismisses_menu(self):
        from textual_vision.menus import MenuBox
        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.press("f10")
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            box = app.menu_bar._menu_box
            self.assertIsNotNone(box)
            await pilot.click(MenuBox, offset=(5, 1))
            await pilot.pause()
            self.assertFalse(app.menu_bar.active)


if __name__ == "__main__":
    unittest.main()
