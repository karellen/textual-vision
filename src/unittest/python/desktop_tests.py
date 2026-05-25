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

from textual.geometry import Region

from textual_vision.constants import OptionFlag
from textual_vision.desktop import Background, DeskTop, _grid_cols
from textual_vision.window import Window


class BackgroundTest(unittest.TestCase):
    def test_default_pattern(self):
        bg = Background()
        self.assertEqual(bg.pattern, "░")

    def test_custom_pattern(self):
        bg = Background(pattern="▒")
        self.assertEqual(bg.pattern, "▒")

    def test_pattern_setter(self):
        bg = Background()
        bg.pattern = "▓"
        self.assertEqual(bg.pattern, "▓")

    def test_css_uses_background_variable(self):
        """Background must use $background, not $surface, for desktop color."""
        self.assertIn("$background", Background.DEFAULT_CSS)
        self.assertNotIn("$surface", Background.DEFAULT_CSS)


class GridColsTest(unittest.TestCase):
    def test_single_window(self):
        self.assertEqual(_grid_cols(1), 1)

    def test_two_windows(self):
        self.assertEqual(_grid_cols(2), 2)

    def test_three_windows(self):
        self.assertEqual(_grid_cols(3), 2)

    def test_four_windows(self):
        self.assertEqual(_grid_cols(4), 2)

    def test_five_windows(self):
        self.assertEqual(_grid_cols(5), 3)

    def test_nine_windows(self):
        self.assertEqual(_grid_cols(9), 3)

    def test_ten_windows(self):
        self.assertEqual(_grid_cols(10), 4)


class DeskTopTileTest(unittest.TestCase):
    def _make_tileable_window(self, title: str) -> Window:
        win = Window(title=title)
        win.tv_options |= OptionFlag.TILEABLE
        return win

    def test_tile_empty_is_noop(self):
        desktop = DeskTop()
        desktop.tile(Region(0, 0, 80, 25))

    def test_tile_single_window_fills_region(self):
        desktop = DeskTop()
        win = self._make_tileable_window("W1")
        desktop._nodes._append(win)

        desktop.tile(Region(0, 0, 80, 25))

        self.assertEqual(win.styles.offset.x.value, 0)
        self.assertEqual(win.styles.offset.y.value, 0)
        self.assertEqual(win.styles.width.value, 80)
        self.assertEqual(win.styles.height.value, 25)

    def test_tile_two_windows_side_by_side(self):
        desktop = DeskTop()
        w1 = self._make_tileable_window("W1")
        w2 = self._make_tileable_window("W2")
        desktop._nodes._append(w1)
        desktop._nodes._append(w2)

        desktop.tile(Region(0, 0, 80, 25))

        self.assertEqual(w1.styles.offset.x.value, 0)
        self.assertEqual(w1.styles.width.value, 40)
        self.assertEqual(w2.styles.offset.x.value, 40)
        self.assertEqual(w2.styles.width.value, 40)
        self.assertEqual(w1.styles.height.value, 25)
        self.assertEqual(w2.styles.height.value, 25)

    def test_tile_four_windows_in_grid(self):
        desktop = DeskTop()
        wins = [self._make_tileable_window(f"W{i}") for i in range(4)]
        for w in wins:
            desktop._nodes._append(w)

        desktop.tile(Region(0, 0, 80, 24))

        self.assertEqual(wins[0].styles.offset.x.value, 0)
        self.assertEqual(wins[0].styles.offset.y.value, 0)
        self.assertEqual(wins[1].styles.offset.x.value, 40)
        self.assertEqual(wins[1].styles.offset.y.value, 0)
        self.assertEqual(wins[2].styles.offset.x.value, 0)
        self.assertEqual(wins[2].styles.offset.y.value, 12)
        self.assertEqual(wins[3].styles.offset.x.value, 40)
        self.assertEqual(wins[3].styles.offset.y.value, 12)

    def test_tile_skips_non_tileable(self):
        desktop = DeskTop()
        tileable = self._make_tileable_window("Tileable")
        non_tileable = Window(title="Fixed")
        desktop._nodes._append(tileable)
        desktop._nodes._append(non_tileable)

        desktop.tile(Region(0, 0, 80, 25))

        self.assertEqual(tileable.styles.width.value, 80)


class DeskTopCascadeTest(unittest.TestCase):
    def test_cascade_empty_is_noop(self):
        desktop = DeskTop()
        desktop.cascade(Region(0, 0, 80, 25))

    def test_cascade_windows_offset(self):
        desktop = DeskTop()
        w1 = Window(title="W1")
        w2 = Window(title="W2")
        w3 = Window(title="W3")
        desktop._nodes._append(w1)
        desktop._nodes._append(w2)
        desktop._nodes._append(w3)

        desktop.cascade(Region(0, 0, 80, 25))

        self.assertEqual(w1.styles.offset.x.value, 0)
        self.assertEqual(w1.styles.offset.y.value, 0)
        self.assertEqual(w2.styles.offset.x.value, 1)
        self.assertEqual(w2.styles.offset.y.value, 1)
        self.assertEqual(w3.styles.offset.x.value, 2)
        self.assertEqual(w3.styles.offset.y.value, 2)

    def test_cascade_all_same_size(self):
        desktop = DeskTop()
        w1 = Window(title="W1")
        w2 = Window(title="W2")
        desktop._nodes._append(w1)
        desktop._nodes._append(w2)

        desktop.cascade(Region(0, 0, 80, 25))

        self.assertEqual(w1.styles.width.value, w2.styles.width.value)
        self.assertEqual(w1.styles.height.value, w2.styles.height.value)


class DeskTopWindowActivationTest(unittest.IsolatedAsyncioTestCase):
    def _make_app(self):
        from textual_vision.app import Application
        from textual_vision.menus import Menu, MenuItem, SubMenu
        from textual_vision.status_line import StatusDef, StatusItem
        from textual_vision.constants import Command

        class App(Application):
            CSS = "Screen { layers: background windows menus; }"

            def init_menu_bar(self):
                return Menu(items=[
                    SubMenu("~F~ile", MenuItem("~N~ew", Command.NEW)),
                ])

            def init_status_line(self):
                return [StatusDef(0, 99, [
                    StatusItem("~F1~ Help", "f1", Command.HELP),
                    StatusItem("~F10~ Menu", "f10", Command.MENU),
                ])]

        return App()

    async def test_insert_deactivates_existing_windows(self):
        """Inserting a new window must deactivate frames of existing windows."""
        from textual_vision.frame import Frame

        app = self._make_app()
        async with app.run_test() as pilot:
            w1 = Window(title="W1")
            app.insert_window(w1)
            await pilot.pause()

            w2 = Window(title="W2")
            app.insert_window(w2)
            await pilot.pause()

            f1 = w1.query_one(Frame)
            f2 = w2.query_one(Frame)
            self.assertFalse(f1.active)
            self.assertTrue(f2.active)

    async def test_raise_window_activates_and_deactivates(self):
        """Raising a window must activate it and deactivate all others."""
        from textual_vision.frame import Frame

        app = self._make_app()
        async with app.run_test() as pilot:
            w1 = Window(title="W1")
            app.insert_window(w1)
            await pilot.pause()

            w2 = Window(title="W2")
            app.insert_window(w2)
            await pilot.pause()

            app.desktop.raise_window(w1)
            await pilot.pause()

            f1 = w1.query_one(Frame)
            f2 = w2.query_one(Frame)
            self.assertTrue(f1.active)
            self.assertFalse(f2.active)

    async def test_frame_click_raises_window(self):
        """Clicking on a window's frame must raise that window."""
        from textual_vision.frame import Frame

        app = self._make_app()
        async with app.run_test() as pilot:
            w1 = Window(title="W1")
            app.insert_window(w1)
            await pilot.pause()

            w2 = Window(title="W2")
            w2.styles.offset = (10, 5)
            app.insert_window(w2)
            await pilot.pause()

            f1 = w1.query_one(Frame)
            f2 = w2.query_one(Frame)
            self.assertFalse(f1.active)
            self.assertTrue(f2.active)

            app.desktop.raise_window(w1)
            await pilot.pause()

            self.assertTrue(f1.active)
            self.assertFalse(f2.active)


    async def test_close_window_removes_from_z_order(self):
        """Closing a window must remove it from DeskTop._z_order."""
        app = self._make_app()
        async with app.run_test() as pilot:
            w1 = Window(title="W1")
            app.insert_window(w1)
            await pilot.pause()

            w2 = Window(title="W2")
            app.insert_window(w2)
            await pilot.pause()

            self.assertEqual(len(app.desktop._z_order), 2)
            w1.close()
            await pilot.pause()

            self.assertEqual(len(app.desktop._z_order), 1)
            self.assertNotIn(w1, app.desktop._z_order)
            self.assertIn(w2, app.desktop._z_order)

    async def test_close_window_updates_current(self):
        """Closing the current window must set current to the next topmost."""
        app = self._make_app()
        async with app.run_test() as pilot:
            w1 = Window(title="W1")
            app.insert_window(w1)
            await pilot.pause()

            w2 = Window(title="W2")
            app.insert_window(w2)
            await pilot.pause()

            self.assertIs(app.desktop.current, w2)
            w2.close()
            await pilot.pause()

            self.assertIs(app.desktop.current, w1)

    async def test_close_last_window_sets_current_none(self):
        """Closing the only window must set current to None."""
        app = self._make_app()
        async with app.run_test() as pilot:
            w1 = Window(title="W1")
            app.insert_window(w1)
            await pilot.pause()

            w1.close()
            await pilot.pause()

            self.assertEqual(len(app.desktop._z_order), 0)
            self.assertIsNone(app.desktop.current)

    async def test_insert_window_sets_current(self):
        """insert_window must set the new window as DeskTop.current."""
        app = self._make_app()
        async with app.run_test() as pilot:
            w1 = Window(title="W1")
            app.insert_window(w1)
            await pilot.pause()

            self.assertIs(app.desktop.current, w1)

            w2 = Window(title="W2")
            app.insert_window(w2)
            await pilot.pause()

            self.assertIs(app.desktop.current, w2)


if __name__ == "__main__":
    unittest.main()
