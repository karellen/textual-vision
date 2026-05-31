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
from textual_vision.dialogs import Dialog
from textual_vision.input_line import InputLine


from textual_vision.combo_box import ComboBox
from textual_vision.constants import StateFlag
from textual_vision.list_box import ListBox
from textual_vision.window import Window


class _MinimalApp(Application):
    def init_menu_bar(self):
        return None

    def init_status_line(self):
        return None


class _TwoInputDialog(Dialog):
    """Dialog with two InputLines to test Tab cycling."""

    def on_mount(self):
        super().on_mount()
        content = self.query_one(".tv-window-content")
        content.mount(InputLine(max_len=40, name="first"))
        content.mount(InputLine(max_len=40, name="second"))


class _ThreeInputDialog(Dialog):
    """Dialog with three InputLines to test repeated Tab cycling."""

    def on_mount(self):
        super().on_mount()
        content = self.query_one(".tv-window-content")
        content.mount(InputLine(max_len=40, name="first"))
        content.mount(InputLine(max_len=40, name="second"))
        content.mount(InputLine(max_len=40, name="third"))


class DialogFirstTabTest(unittest.IsolatedAsyncioTestCase):
    """Regression: first Tab press in a dialog must advance TV focus."""

    async def test_first_tab_advances_focus(self):
        app = _MinimalApp()
        async with app.run_test() as pilot:
            dlg = _TwoInputDialog(title="Test")
            dlg.styles.width = 40
            dlg.styles.height = 10
            app.insert_window(dlg)
            await pilot.pause()
            await pilot.pause()

            inputs = list(dlg.query(InputLine))
            self.assertEqual(len(inputs), 2)

            self.assertIs(dlg.current, inputs[0])
            self.assertTrue(inputs[0].tv_focused)

            await pilot.press("tab")
            await pilot.pause()

            self.assertIs(dlg.current, inputs[1],
                          "First Tab must advance from first to second input")
            self.assertTrue(inputs[1].tv_focused)
            self.assertFalse(inputs[0].tv_focused)

    async def test_second_tab_continues_cycling(self):
        app = _MinimalApp()
        async with app.run_test() as pilot:
            dlg = _ThreeInputDialog(title="Test")
            dlg.styles.width = 40
            dlg.styles.height = 12
            app.insert_window(dlg)
            await pilot.pause()
            await pilot.pause()

            inputs = list(dlg.query(InputLine))
            self.assertEqual(len(inputs), 3)
            self.assertIs(dlg.current, inputs[0])

            await pilot.press("tab")
            await pilot.pause()
            self.assertIs(dlg.current, inputs[1])

            await pilot.press("tab")
            await pilot.pause()
            self.assertIs(dlg.current, inputs[2])

    async def test_shift_tab_reverses_from_first(self):
        app = _MinimalApp()
        async with app.run_test() as pilot:
            dlg = _ThreeInputDialog(title="Test")
            dlg.styles.width = 40
            dlg.styles.height = 12
            app.insert_window(dlg)
            await pilot.pause()
            await pilot.pause()

            inputs = list(dlg.query(InputLine))
            self.assertIs(dlg.current, inputs[0])

            await pilot.press("shift+tab")
            await pilot.pause()
            self.assertIs(dlg.current, inputs[2],
                          "Shift+Tab from first must wrap to last input")

    async def test_textual_focus_follows_tv_focus(self):
        """Textual focus must be on the TV-focused child so events route correctly."""
        app = _MinimalApp()
        async with app.run_test() as pilot:
            dlg = _TwoInputDialog(title="Test")
            dlg.styles.width = 40
            dlg.styles.height = 10
            app.insert_window(dlg)
            await pilot.pause()
            await pilot.pause()

            inputs = list(dlg.query(InputLine))
            focused = app.screen.focused
            self.assertIs(focused, inputs[0],
                          "Textual focus must be on TV-focused InputLine after mount")

            await pilot.press("tab")
            await pilot.pause()

            focused = app.screen.focused
            self.assertIs(focused, inputs[1],
                          "Textual focus must follow TV focus after Tab")


class _ComboDialog(Dialog):
    """Dialog with InputLines and ComboBoxes for focus propagation tests."""

    def on_mount(self):
        super().on_mount()
        content = self.query_one(".tv-window-content")
        self._name_input = InputLine(max_len=40, name="name")
        self._pass_input = InputLine(max_len=20, name="pass")
        self._combo1 = ComboBox(items=["Alpha", "Beta", "Gamma"], name="combo1")
        self._combo2 = ComboBox(items=["Red", "Green", "Blue"], name="combo2")

        content.mount(self._name_input)
        content.mount(self._pass_input)
        content.mount(self._combo1)
        content.mount(self._combo2)


class ComboDialogFocusTest(unittest.IsolatedAsyncioTestCase):
    """Regression: only the TV-focused InputLine should have StateFlag.FOCUSED."""

    async def test_only_dialog_focused_input_has_focused_state(self):
        app = _MinimalApp()
        async with app.run_test(size=(60, 25)) as pilot:
            dlg = _ComboDialog(title="Test")
            dlg.styles.width = 50
            dlg.styles.height = 20
            app.insert_window(dlg)
            await pilot.pause()
            await pilot.pause()

            name_input = dlg._name_input
            pass_input = dlg._pass_input
            combo1_input = dlg._combo1.input_line
            combo2_input = dlg._combo2.input_line

            self.assertIs(dlg.current, name_input,
                          "Dialog's current should be the first InputLine")
            self.assertTrue(bool(name_input.tv_state & StateFlag.FOCUSED),
                            "Dialog's focused InputLine must have FOCUSED state")

            self.assertFalse(bool(pass_input.tv_state & StateFlag.FOCUSED),
                             "Non-focused InputLine must NOT have FOCUSED state")
            self.assertFalse(bool(combo1_input.tv_state & StateFlag.FOCUSED),
                             "ComboBox InputLine must NOT have FOCUSED when ComboBox isn't focused")
            self.assertFalse(bool(combo2_input.tv_state & StateFlag.FOCUSED),
                             "ComboBox InputLine must NOT have FOCUSED when ComboBox isn't focused")

    async def test_tab_to_combobox_focuses_its_input(self):
        app = _MinimalApp()
        async with app.run_test(size=(60, 25)) as pilot:
            dlg = _ComboDialog(title="Test")
            dlg.styles.width = 50
            dlg.styles.height = 20
            app.insert_window(dlg)
            await pilot.pause()
            await pilot.pause()

            combo1_input = dlg._combo1.input_line

            for _ in range(2):
                await pilot.press("tab")
                await pilot.pause()

            self.assertIs(dlg.current, dlg._combo1,
                          "After 2 tabs, ComboBox should be current")
            self.assertTrue(bool(combo1_input.tv_state & StateFlag.FOCUSED),
                            "ComboBox's InputLine must have FOCUSED when ComboBox is focused")

    async def test_tab_away_from_combobox_clears_input_focus(self):
        app = _MinimalApp()
        async with app.run_test(size=(60, 25)) as pilot:
            dlg = _ComboDialog(title="Test")
            dlg.styles.width = 50
            dlg.styles.height = 20
            app.insert_window(dlg)
            await pilot.pause()
            await pilot.pause()

            combo1_input = dlg._combo1.input_line

            for _ in range(2):
                await pilot.press("tab")
                await pilot.pause()
            self.assertTrue(bool(combo1_input.tv_state & StateFlag.FOCUSED))

            await pilot.press("tab")
            await pilot.pause()

            self.assertFalse(bool(combo1_input.tv_state & StateFlag.FOCUSED),
                             "After tabbing away, ComboBox's InputLine must lose FOCUSED")


class _ListBoxWindow(Window):
    def on_mount(self):
        super().on_mount()
        content = self.query_one(".tv-window-content")
        items = [f"Item {i}" for i in range(1, 21)]
        self._listbox = ListBox(items=items, classes="list-area")
        content.mount(self._listbox)


class ChildClickActivatesWindowTest(unittest.IsolatedAsyncioTestCase):
    """Regression: clicking a child widget must activate its parent Window."""

    async def test_click_listbox_activates_window(self):
        app = _MinimalApp()
        async with app.run_test(size=(60, 25)) as pilot:
            win1 = _ListBoxWindow(title="Win1")
            win1.styles.width = 30
            win1.styles.height = 15
            win1.styles.offset = (0, 0)
            app.insert_window(win1)

            win2 = _ListBoxWindow(title="Win2")
            win2.styles.width = 30
            win2.styles.height = 15
            win2.styles.offset = (15, 5)
            app.insert_window(win2)
            await pilot.pause()
            await pilot.pause()

            desktop = app.desktop
            self.assertIs(desktop.current, win2,
                          "Win2 should be current after being inserted last")

            listbox1 = win1._listbox
            listbox1.tv_select_self()
            await pilot.pause()

            self.assertIs(desktop.current, win1,
                          "tv_select_self on ListBox in Win1 must activate Win1")
            self.assertTrue(win1.frame.active)
            self.assertFalse(win2.frame.active)

    async def test_tv_select_self_propagates_to_desktop(self):
        app = _MinimalApp()
        async with app.run_test(size=(60, 25)) as pilot:
            win1 = _ListBoxWindow(title="Win1")
            win1.styles.width = 30
            win1.styles.height = 15
            app.insert_window(win1)

            win2 = _ListBoxWindow(title="Win2")
            win2.styles.width = 30
            win2.styles.height = 15
            win2.styles.offset = (5, 3)
            app.insert_window(win2)
            await pilot.pause()
            await pilot.pause()

            listbox1 = win1._listbox
            listbox1.tv_select_self()
            await pilot.pause()

            self.assertIs(app.desktop.current, win1,
                          "tv_select_self must propagate up to DeskTop")


if __name__ == "__main__":
    unittest.main()
