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

from textual.events import Key

from textual_vision.constants import Command, OptionFlag
from textual_vision.status_line import StatusItem, StatusDef, StatusLine


class StatusItemTest(unittest.TestCase):
    def test_creation(self):
        item = StatusItem("~F1~ Help", "f1", Command.HELP)
        self.assertEqual(item.text, "~F1~ Help")
        self.assertEqual(item.key_code, "f1")
        self.assertEqual(item.command, Command.HELP)


class StatusDefTest(unittest.TestCase):
    def test_matches_in_range(self):
        sd = StatusDef(0, 100, [
            StatusItem("~F1~ Help", "f1", Command.HELP),
            StatusItem("~F10~ Menu", "f10", Command.MENU),
        ])
        self.assertTrue(sd.matches(0))
        self.assertTrue(sd.matches(50))
        self.assertTrue(sd.matches(100))

    def test_does_not_match_out_of_range(self):
        sd = StatusDef(10, 20)
        self.assertFalse(sd.matches(9))
        self.assertFalse(sd.matches(21))

    def test_single_value_range(self):
        sd = StatusDef(5, 5)
        self.assertTrue(sd.matches(5))
        self.assertFalse(sd.matches(4))
        self.assertFalse(sd.matches(6))


class StatusLineItemSelectionTest(unittest.TestCase):
    def _make_status_line(self):
        return StatusLine(defs=[
            StatusDef(0, 49, [
                StatusItem("~F1~ Help", "f1", Command.HELP),
                StatusItem("~F10~ Menu", "f10", Command.MENU),
            ]),
            StatusDef(50, 99, [
                StatusItem("~F1~ Help", "f1", Command.HELP),
                StatusItem("~F2~ Save", "f2", Command.SAVE),
                StatusItem("~Esc~ Cancel", "escape", Command.CANCEL),
            ]),
        ])

    def test_current_items_default_context(self):
        sl = self._make_status_line()
        items = sl.current_items
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].command, Command.HELP)
        self.assertEqual(items[1].command, Command.MENU)

    def test_current_items_after_update(self):
        sl = self._make_status_line()
        sl.update(50)
        items = sl.current_items
        self.assertEqual(len(items), 3)
        self.assertEqual(items[1].command, Command.SAVE)
        self.assertEqual(items[2].command, Command.CANCEL)

    def test_current_items_no_match(self):
        sl = self._make_status_line()
        sl.update(200)
        items = sl.current_items
        self.assertEqual(len(items), 0)

    def test_find_by_key(self):
        sl = self._make_status_line()
        item = sl.find_by_key("f1")
        self.assertIsNotNone(item)
        self.assertEqual(item.command, Command.HELP)

    def test_find_by_key_not_found(self):
        sl = self._make_status_line()
        item = sl.find_by_key("f5")
        self.assertIsNone(item)

    def test_find_by_key_changes_with_context(self):
        sl = self._make_status_line()
        self.assertIsNone(sl.find_by_key("f2"))

        sl.update(60)
        item = sl.find_by_key("f2")
        self.assertIsNotNone(item)
        self.assertEqual(item.command, Command.SAVE)


class StatusLineKeyHandlingTest(unittest.TestCase):
    def test_handles_matching_key(self):
        sl = StatusLine(defs=[
            StatusDef(0, 99, [
                StatusItem("~F1~ Help", "f1", Command.HELP),
                StatusItem("~F10~ Menu", "f10", Command.MENU),
            ]),
        ])
        event = Key("f1", None)
        result = sl.tv_handle_key(event)
        self.assertTrue(result)

    def test_ignores_non_matching_key(self):
        sl = StatusLine(defs=[
            StatusDef(0, 99, [
                StatusItem("~F1~ Help", "f1", Command.HELP),
            ]),
        ])
        event = Key("f5", None)
        result = sl.tv_handle_key(event)
        self.assertFalse(result)


class StatusLineOptionsTest(unittest.TestCase):
    def test_has_post_process(self):
        sl = StatusLine()
        self.assertIn(OptionFlag.POST_PROCESS, sl.tv_options)


class StatusLineHintTest(unittest.TestCase):
    def test_default_hint_empty(self):
        sl = StatusLine()
        self.assertEqual(sl.hint(0), "")

    def test_custom_hint(self):
        class CustomStatusLine(StatusLine):
            def hint(self, help_ctx):
                if help_ctx == 1:
                    return "Press F1 for help"
                return ""

        sl = CustomStatusLine()
        sl.update(1)
        self.assertEqual(sl._hint_text, "Press F1 for help")

    def test_hint_separator(self):
        """Hint text must be preceded by a │ separator."""
        class HintStatusLine(StatusLine):
            def hint(self, help_ctx):
                return "some hint"

        sl = HintStatusLine(defs=[
            StatusDef(0, 99, [
                StatusItem("~F1~ Help", "f1", Command.HELP),
            ]),
        ])
        sl.update(0)
        self.assertEqual(sl._hint_text, "some hint")


class StatusLineCssTest(unittest.TestCase):
    def test_hotkey_uses_menu_hotkey_variable(self):
        """Status line hotkey text must use $menu-hotkey (red), not $foreground or other."""
        css = StatusLine.DEFAULT_CSS
        hotkey_section = css.split("statusline--hotkey")[1].split("}")[0]
        self.assertIn("$menu-hotkey", hotkey_section)

    def test_item_uses_text_color(self):
        """Status line normal items must use $text color."""
        css = StatusLine.DEFAULT_CSS
        item_section = css.split("statusline--item")[1].split("}")[0]
        self.assertIn("$text", item_section)

    def test_all_component_classes_have_background(self):
        """All status line component classes must set explicit background."""
        css = StatusLine.DEFAULT_CSS
        for cc in ("statusline--item", "statusline--hotkey", "statusline--hint"):
            section = css.split(cc)[1].split("}")[0]
            self.assertIn("background:", section, f"{cc} missing explicit background")


class StatusLineTildeRenderingTest(unittest.TestCase):
    def test_item_text_uses_tilde_toggle(self):
        """StatusLine must use render_tilde_text, not render raw text with literal tildes."""
        from textual_vision.menus import render_tilde_text
        text = render_tilde_text("~F1~ Help")
        self.assertEqual(text.plain, "F1 Help")
        self.assertNotIn("~", text.plain)

    def test_multi_char_key_span(self):
        from textual_vision.menus import render_tilde_text
        text = render_tilde_text("~Alt+X~ Exit")
        self.assertEqual(text.plain, "Alt+X Exit")
        self.assertNotIn("~", text.plain)


if __name__ == "__main__":
    unittest.main()
