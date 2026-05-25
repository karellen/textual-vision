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

from textual.theme import Theme

from textual_vision.themes import (
    THEME_TURBO_PASCAL, THEME_TURBO_C, ALL_THEMES,
    CGA_BLUE, CGA_BLACK, CGA_YELLOW, CGA_WHITE, CGA_LIGHT_GRAY,
    CGA_LIGHT_CYAN, CGA_CYAN, CGA_GREEN, CGA_RED,
)


class ThemeDefinitionTest(unittest.TestCase):
    def test_turbo_pascal_is_theme(self):
        self.assertIsInstance(THEME_TURBO_PASCAL, Theme)

    def test_turbo_c_is_theme(self):
        self.assertIsInstance(THEME_TURBO_C, Theme)

    def test_theme_names_distinct(self):
        self.assertNotEqual(THEME_TURBO_PASCAL.name, THEME_TURBO_C.name)

    def test_all_themes_contains_both(self):
        self.assertIn("turbo-pascal", ALL_THEMES)
        self.assertIn("turbo-c", ALL_THEMES)
        self.assertEqual(len(ALL_THEMES), 2)


class TurboPascalThemeTest(unittest.TestCase):
    def test_name(self):
        self.assertEqual(THEME_TURBO_PASCAL.name, "turbo-pascal")

    def test_blue_background(self):
        self.assertEqual(THEME_TURBO_PASCAL.background, CGA_BLUE)

    def test_white_foreground(self):
        self.assertEqual(THEME_TURBO_PASCAL.foreground, CGA_WHITE)

    def test_gray_surface(self):
        self.assertEqual(THEME_TURBO_PASCAL.surface, CGA_LIGHT_GRAY)

    def test_cyan_primary(self):
        self.assertEqual(THEME_TURBO_PASCAL.primary, CGA_LIGHT_CYAN)

    def test_green_accent(self):
        self.assertEqual(THEME_TURBO_PASCAL.accent, CGA_GREEN)

    def test_dark_mode(self):
        self.assertTrue(THEME_TURBO_PASCAL.dark)

    def test_has_scrollbar_variables(self):
        self.assertIn("scrollbar", THEME_TURBO_PASCAL.variables)
        self.assertIn("scrollbar-background", THEME_TURBO_PASCAL.variables)

    def test_has_footer_variables(self):
        self.assertIn("footer-foreground", THEME_TURBO_PASCAL.variables)
        self.assertIn("footer-background", THEME_TURBO_PASCAL.variables)

    def test_has_menu_hotkey_variable(self):
        self.assertIn("menu-hotkey", THEME_TURBO_PASCAL.variables)

    def test_menu_hotkey_is_red(self):
        self.assertEqual(THEME_TURBO_PASCAL.variables["menu-hotkey"], CGA_RED)


class TurboCThemeTest(unittest.TestCase):
    def test_name(self):
        self.assertEqual(THEME_TURBO_C.name, "turbo-c")

    def test_black_background(self):
        self.assertEqual(THEME_TURBO_C.background, CGA_BLACK)

    def test_yellow_foreground(self):
        self.assertEqual(THEME_TURBO_C.foreground, CGA_YELLOW)

    def test_gray_surface(self):
        self.assertEqual(THEME_TURBO_C.surface, CGA_LIGHT_GRAY)

    def test_cyan_primary(self):
        self.assertEqual(THEME_TURBO_C.primary, CGA_CYAN)

    def test_dark_mode(self):
        self.assertTrue(THEME_TURBO_C.dark)

    def test_has_scrollbar_variables(self):
        self.assertIn("scrollbar", THEME_TURBO_C.variables)
        self.assertIn("scrollbar-background", THEME_TURBO_C.variables)

    def test_has_menu_hotkey_variable(self):
        self.assertIn("menu-hotkey", THEME_TURBO_C.variables)

    def test_menu_hotkey_is_red(self):
        self.assertEqual(THEME_TURBO_C.variables["menu-hotkey"], CGA_RED)


class CgaConstantsTest(unittest.TestCase):
    def test_all_colors_are_hex_strings(self):
        from textual_vision import themes
        cga_names = [n for n in dir(themes) if n.startswith("CGA_")]
        self.assertGreaterEqual(len(cga_names), 16)
        for name in cga_names:
            value = getattr(themes, name)
            self.assertTrue(value.startswith("#"), f"{name} = {value}")
            self.assertEqual(len(value), 7, f"{name} = {value}")

    def test_black_and_white_endpoints(self):
        self.assertEqual(CGA_BLACK, "#000000")
        self.assertEqual(CGA_WHITE, "#FFFFFF")


if __name__ == "__main__":
    unittest.main()
