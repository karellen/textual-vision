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
from textual_vision.desktop import DeskTop
from textual_vision.menus import Menu, MenuItem, SubMenu
from textual_vision.status_line import StatusDef, StatusItem
from textual_vision.app import Program, Application


class ProgramCompositionTest(unittest.TestCase):
    def test_program_is_app(self):
        from textual.app import App
        self.assertTrue(issubclass(Program, App))

    def test_application_is_program(self):
        self.assertTrue(issubclass(Application, Program))

    def test_default_factories_return_none(self):
        prog = Program()
        self.assertIsNone(prog.init_menu_bar())
        self.assertIsNone(prog.init_status_line())

    def test_default_desktop_factory(self):
        prog = Program()
        desktop = prog.init_desktop()
        self.assertIsInstance(desktop, DeskTop)


class CustomProgramTest(unittest.TestCase):
    def test_custom_menu_bar(self):
        class MyApp(Program):
            def init_menu_bar(self):
                return Menu(items=[
                    SubMenu("~F~ile",
                            MenuItem("~N~ew", Command.NEW),
                            MenuItem("E~x~it", Command.QUIT)),
                ])

        app = MyApp()
        menu = app.init_menu_bar()
        self.assertIsNotNone(menu)
        self.assertEqual(len(menu.items), 1)

    def test_custom_status_line(self):
        class MyApp(Program):
            def init_status_line(self):
                return [
                    StatusDef(0, 99, [
                        StatusItem("~F1~ Help", "f1", Command.HELP),
                        StatusItem("~F10~ Menu", "f10", Command.MENU),
                    ]),
                ]

        app = MyApp()
        defs = app.init_status_line()
        self.assertIsNotNone(defs)
        self.assertEqual(len(defs), 1)
        self.assertEqual(len(defs[0].items), 2)

    def test_custom_desktop(self):
        class MyDesktop(DeskTop):
            pass

        class MyApp(Program):
            def init_desktop(self):
                return MyDesktop()

        app = MyApp()
        desktop = app.init_desktop()
        self.assertIsInstance(desktop, MyDesktop)


class ProgramPropertiesTest(unittest.TestCase):
    def test_initial_properties_none(self):
        prog = Program()
        self.assertIsNone(prog.menu_bar)
        self.assertIsNone(prog.desktop)
        self.assertIsNone(prog.status_line)

    def test_idle_is_noop(self):
        prog = Program()
        prog.idle()


if __name__ == "__main__":
    unittest.main()
