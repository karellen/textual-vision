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
    THEME_TURBO_PASCAL, THEME_TURBO_C, THEME_TURBO_C_1X,
    THEME_TURBO_C_TURQUOISE, ALL_THEMES,
    CGA_BLUE, CGA_BLACK, CGA_WHITE, CGA_LIGHT_GRAY,
    CGA_GREEN, CGA_CYAN, CGA_RED, CGA_YELLOW,
    CGA_MAGENTA,
)


class ThemeDefinitionTest(unittest.TestCase):
    def test_all_are_themes(self):
        for theme in ALL_THEMES.values():
            self.assertIsInstance(theme, Theme)

    def test_theme_names_distinct(self):
        names = [t.name for t in ALL_THEMES.values()]
        self.assertEqual(len(names), len(set(names)))

    def test_all_themes_count(self):
        self.assertEqual(len(ALL_THEMES), 4)

    def test_all_themes_contains_all(self):
        self.assertIn("turbo-pascal", ALL_THEMES)
        self.assertIn("turbo-c", ALL_THEMES)
        self.assertIn("turbo-c-1x", ALL_THEMES)
        self.assertIn("turbo-c-turquoise", ALL_THEMES)


class TurboPascalThemeTest(unittest.TestCase):
    """TV cpAppColor palette: gray menus, blue desktop, green selection."""

    def test_name(self):
        self.assertEqual(THEME_TURBO_PASCAL.name, "turbo-pascal")

    def test_blue_background(self):
        self.assertEqual(THEME_TURBO_PASCAL.background, CGA_BLUE)

    def test_white_foreground(self):
        self.assertEqual(THEME_TURBO_PASCAL.foreground, CGA_WHITE)

    def test_gray_surface(self):
        self.assertEqual(THEME_TURBO_PASCAL.surface, CGA_LIGHT_GRAY)

    def test_green_accent(self):
        self.assertEqual(THEME_TURBO_PASCAL.accent, CGA_GREEN)

    def test_dark_mode(self):
        self.assertTrue(THEME_TURBO_PASCAL.dark)

    def test_text_is_black(self):
        self.assertEqual(THEME_TURBO_PASCAL.variables["text"], CGA_BLACK)

    def test_menu_hotkey_is_red(self):
        self.assertEqual(THEME_TURBO_PASCAL.variables["menu-hotkey"], CGA_RED)

    def test_menu_hotkey_background_matches_surface(self):
        self.assertEqual(THEME_TURBO_PASCAL.variables["menu-hotkey-background"],
                         CGA_LIGHT_GRAY)

    def test_footer_key_foreground_is_red(self):
        self.assertEqual(THEME_TURBO_PASCAL.variables["footer-key-foreground"],
                         CGA_RED)

    def test_window_content_background_is_blue(self):
        self.assertEqual(THEME_TURBO_PASCAL.variables["window-content-background"],
                         CGA_BLUE)

    def test_has_scrollbar_variables(self):
        self.assertIn("scrollbar", THEME_TURBO_PASCAL.variables)
        self.assertIn("scrollbar-background", THEME_TURBO_PASCAL.variables)


class TurboCThemeTest(unittest.TestCase):
    """TC 2.01 default: same gray chrome, yellow editor, white-on-black hotkey."""

    def test_name(self):
        self.assertEqual(THEME_TURBO_C.name, "turbo-c")

    def test_blue_background(self):
        self.assertEqual(THEME_TURBO_C.background, CGA_BLUE)

    def test_yellow_foreground(self):
        self.assertEqual(THEME_TURBO_C.foreground, CGA_YELLOW)

    def test_gray_surface(self):
        self.assertEqual(THEME_TURBO_C.surface, CGA_LIGHT_GRAY)

    def test_text_is_black(self):
        self.assertEqual(THEME_TURBO_C.variables["text"], CGA_BLACK)

    def test_menu_hotkey_is_white(self):
        self.assertEqual(THEME_TURBO_C.variables["menu-hotkey"], CGA_WHITE)

    def test_menu_hotkey_background_is_black(self):
        self.assertEqual(THEME_TURBO_C.variables["menu-hotkey-background"],
                         CGA_BLACK)

    def test_footer_key_foreground_is_red(self):
        self.assertEqual(THEME_TURBO_C.variables["footer-key-foreground"],
                         CGA_RED)

    def test_window_content_background_is_blue(self):
        self.assertEqual(THEME_TURBO_C.variables["window-content-background"],
                         CGA_BLUE)


class TurboC1xThemeTest(unittest.TestCase):
    """TC 2.01 'Version 1.x' preset: cyan-dominant, blue-on-cyan menu."""

    def test_name(self):
        self.assertEqual(THEME_TURBO_C_1X.name, "turbo-c-1x")

    def test_cyan_surface(self):
        self.assertEqual(THEME_TURBO_C_1X.surface, CGA_CYAN)

    def test_text_is_blue(self):
        self.assertEqual(THEME_TURBO_C_1X.variables["text"], CGA_BLUE)

    def test_menu_hotkey_is_yellow(self):
        self.assertEqual(THEME_TURBO_C_1X.variables["menu-hotkey"], CGA_YELLOW)

    def test_menu_hotkey_background_is_blue(self):
        self.assertEqual(THEME_TURBO_C_1X.variables["menu-hotkey-background"],
                         CGA_BLUE)

    def test_footer_foreground_is_yellow(self):
        self.assertEqual(THEME_TURBO_C_1X.variables["footer-foreground"],
                         CGA_YELLOW)

    def test_footer_background_is_cyan(self):
        self.assertEqual(THEME_TURBO_C_1X.variables["footer-background"],
                         CGA_CYAN)

    def test_magenta_accent(self):
        self.assertEqual(THEME_TURBO_C_1X.accent, CGA_MAGENTA)


class TurboCTurquoiseThemeTest(unittest.TestCase):
    """TC 2.01 'Turquoise' preset: black editor bg, yellow text, magenta sel."""

    def test_name(self):
        self.assertEqual(THEME_TURBO_C_TURQUOISE.name, "turbo-c-turquoise")

    def test_black_background(self):
        self.assertEqual(THEME_TURBO_C_TURQUOISE.background, CGA_BLACK)

    def test_yellow_foreground(self):
        self.assertEqual(THEME_TURBO_C_TURQUOISE.foreground, CGA_YELLOW)

    def test_gray_surface(self):
        self.assertEqual(THEME_TURBO_C_TURQUOISE.surface, CGA_LIGHT_GRAY)

    def test_magenta_accent(self):
        self.assertEqual(THEME_TURBO_C_TURQUOISE.accent, CGA_MAGENTA)

    def test_window_content_background_is_black(self):
        self.assertEqual(
            THEME_TURBO_C_TURQUOISE.variables["window-content-background"],
            CGA_BLACK)

    def test_footer_background_is_blue(self):
        self.assertEqual(
            THEME_TURBO_C_TURQUOISE.variables["footer-background"],
            CGA_BLUE)

    def test_menu_hotkey_background_is_magenta(self):
        self.assertEqual(
            THEME_TURBO_C_TURQUOISE.variables["menu-hotkey-background"],
            CGA_MAGENTA)


class AllThemesHaveRequiredVariablesTest(unittest.TestCase):
    """Every theme must define all custom variables used by widget CSS."""

    REQUIRED_VARS = [
        "text", "text-muted", "window-content-background",
        "menu-hotkey", "menu-hotkey-background",
        "footer-foreground", "footer-background",
        "footer-key-foreground", "footer-key-background",
        "desktop-pattern-color",
        "scrollbar", "scrollbar-background",
        "input-fg", "input-bg", "input-selected-fg", "input-selected-bg",
        "input-arrow",
        "button-face-fg", "button-face-bg", "button-default-fg",
        "button-focused-fg", "button-focused-bg",
        "button-disabled-fg", "button-disabled-bg",
        "button-hotkey", "button-shadow-fg", "button-shadow-bg",
        "label-highlight", "label-hotkey",
        "cluster-fg", "cluster-bg",
        "cluster-focused-fg", "cluster-focused-bg",
        "cluster-hotkey", "cluster-disabled-fg", "cluster-disabled-bg",
        "frame-icon",
        "combo-arrow-fg", "combo-arrow-bg",
        "combo-sides-fg", "combo-sides-bg",
    ]

    def test_all_themes_have_required_variables(self):
        for name, theme in ALL_THEMES.items():
            for var in self.REQUIRED_VARS:
                self.assertIn(var, theme.variables,
                              f"Theme '{name}' missing variable '{var}'")


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
