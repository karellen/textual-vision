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

from textual_vision.constants import OptionFlag
from textual_vision.input_line import InputLine


class InputLineCreationTest(unittest.TestCase):
    def test_default_empty(self):
        il = InputLine()
        self.assertEqual(il.data, "")

    def test_max_len(self):
        il = InputLine(max_len=10)
        self.assertEqual(il.max_len, 10)

    def test_password_mode(self):
        il = InputLine(password=True)
        self.assertTrue(il.password)

    def test_selectable(self):
        il = InputLine()
        self.assertIn(OptionFlag.SELECTABLE, il.tv_options)

    def test_initial_cursor_at_zero(self):
        il = InputLine()
        self.assertEqual(il.cursor_pos, 0)

    def test_no_initial_selection(self):
        il = InputLine()
        self.assertFalse(il.has_selection)


class InputLineInsertTest(unittest.TestCase):
    def test_insert_char(self):
        il = InputLine()
        il._insert_char("a")
        self.assertEqual(il.data, "a")
        self.assertEqual(il.cursor_pos, 1)

    def test_insert_multiple(self):
        il = InputLine()
        il._insert_char("h")
        il._insert_char("i")
        self.assertEqual(il.data, "hi")
        self.assertEqual(il.cursor_pos, 2)

    def test_insert_at_middle(self):
        il = InputLine()
        il.data = "ac"
        il._cursor_pos = 1
        il._insert_char("b")
        self.assertEqual(il.data, "abc")
        self.assertEqual(il.cursor_pos, 2)

    def test_insert_respects_max_len(self):
        il = InputLine(max_len=3)
        il.data = "abc"
        il._cursor_pos = 3
        il._insert_char("d")
        self.assertEqual(il.data, "abc")


class InputLineDeleteTest(unittest.TestCase):
    def test_backspace(self):
        il = InputLine()
        il.data = "abc"
        il._cursor_pos = 3
        il._delete_char(forward=False)
        self.assertEqual(il.data, "ab")
        self.assertEqual(il.cursor_pos, 2)

    def test_backspace_at_start(self):
        il = InputLine()
        il.data = "abc"
        il._cursor_pos = 0
        il._delete_char(forward=False)
        self.assertEqual(il.data, "abc")

    def test_delete_forward(self):
        il = InputLine()
        il.data = "abc"
        il._cursor_pos = 0
        il._delete_char(forward=True)
        self.assertEqual(il.data, "bc")
        self.assertEqual(il.cursor_pos, 0)

    def test_delete_at_end(self):
        il = InputLine()
        il.data = "abc"
        il._cursor_pos = 3
        il._delete_char(forward=True)
        self.assertEqual(il.data, "abc")


class InputLineSelectionTest(unittest.TestCase):
    def test_select_via_shift_right(self):
        il = InputLine()
        il.data = "hello"
        il._cursor_pos = 0
        il._move_cursor(3, extend_selection=True)
        self.assertTrue(il.has_selection)
        self.assertEqual(il._sel_start, 0)
        self.assertEqual(il._sel_end, 3)

    def test_delete_selection(self):
        il = InputLine()
        il.data = "hello"
        il._sel_start = 1
        il._sel_end = 4
        il._cursor_pos = 4
        il._delete_selection()
        self.assertEqual(il.data, "ho")
        self.assertEqual(il.cursor_pos, 1)
        self.assertFalse(il.has_selection)

    def test_insert_replaces_selection(self):
        il = InputLine()
        il.data = "hello"
        il._sel_start = 1
        il._sel_end = 4
        il._cursor_pos = 4
        il._insert_char("X")
        self.assertEqual(il.data, "hXo")

    def test_select_all(self):
        il = InputLine()
        il.data = "hello"
        il.select_all()
        self.assertEqual(il._sel_start, 0)
        self.assertEqual(il._sel_end, 5)
        self.assertEqual(il.cursor_pos, 5)


class InputLineCursorMovementTest(unittest.TestCase):
    def test_move_left(self):
        il = InputLine()
        il.data = "abc"
        il._cursor_pos = 2
        il._move_cursor(1)
        self.assertEqual(il.cursor_pos, 1)

    def test_move_right(self):
        il = InputLine()
        il.data = "abc"
        il._cursor_pos = 1
        il._move_cursor(2)
        self.assertEqual(il.cursor_pos, 2)

    def test_move_clamps_start(self):
        il = InputLine()
        il.data = "abc"
        il._move_cursor(-5)
        self.assertEqual(il.cursor_pos, 0)

    def test_move_clamps_end(self):
        il = InputLine()
        il.data = "abc"
        il._move_cursor(100)
        self.assertEqual(il.cursor_pos, 3)

    def test_move_clears_selection(self):
        il = InputLine()
        il.data = "abc"
        il._sel_start = 0
        il._sel_end = 2
        il._move_cursor(1)
        self.assertFalse(il.has_selection)


class InputLineWordMovementTest(unittest.TestCase):
    def test_word_right(self):
        il = InputLine()
        il.data = "hello world"
        il._cursor_pos = 0
        pos = il._word_right()
        self.assertEqual(pos, 6)

    def test_word_left(self):
        il = InputLine()
        il.data = "hello world"
        il._cursor_pos = 8
        pos = il._word_left()
        self.assertEqual(pos, 6)

    def test_word_right_at_end(self):
        il = InputLine()
        il.data = "hello"
        il._cursor_pos = 5
        pos = il._word_right()
        self.assertEqual(pos, 5)

    def test_word_left_at_start(self):
        il = InputLine()
        il.data = "hello"
        il._cursor_pos = 0
        pos = il._word_left()
        self.assertEqual(pos, 0)


class InputLineScrollTest(unittest.TestCase):
    def test_scroll_to_cursor_right(self):
        il = InputLine()
        il.data = "a" * 50
        il._cursor_pos = 30
        from textual.geometry import Size
        il._size = Size(20, 1)
        il._scroll_to_cursor()
        self.assertGreater(il._first_pos, 0)
        self.assertLessEqual(il._first_pos, 30)

    def test_scroll_to_cursor_left(self):
        il = InputLine()
        il.data = "a" * 50
        il._first_pos = 20
        il._cursor_pos = 5
        from textual.geometry import Size
        il._size = Size(20, 1)
        il._scroll_to_cursor()
        self.assertEqual(il._first_pos, 5)


class InputLineKeyHandlingTest(unittest.TestCase):
    def test_left_key(self):
        il = InputLine()
        il.data = "abc"
        il._cursor_pos = 2
        result = il.tv_handle_key(Key("left", None))
        self.assertTrue(result)
        self.assertEqual(il.cursor_pos, 1)

    def test_right_key(self):
        il = InputLine()
        il.data = "abc"
        il._cursor_pos = 1
        result = il.tv_handle_key(Key("right", None))
        self.assertTrue(result)
        self.assertEqual(il.cursor_pos, 2)

    def test_home_key(self):
        il = InputLine()
        il.data = "abc"
        il._cursor_pos = 2
        result = il.tv_handle_key(Key("home", None))
        self.assertTrue(result)
        self.assertEqual(il.cursor_pos, 0)

    def test_end_key(self):
        il = InputLine()
        il.data = "abc"
        il._cursor_pos = 0
        result = il.tv_handle_key(Key("end", None))
        self.assertTrue(result)
        self.assertEqual(il.cursor_pos, 3)

    def test_backspace_key(self):
        il = InputLine()
        il.data = "abc"
        il._cursor_pos = 3
        result = il.tv_handle_key(Key("backspace", None))
        self.assertTrue(result)
        self.assertEqual(il.data, "ab")

    def test_delete_key(self):
        il = InputLine()
        il.data = "abc"
        il._cursor_pos = 0
        result = il.tv_handle_key(Key("delete", None))
        self.assertTrue(result)
        self.assertEqual(il.data, "bc")

    def test_printable_char(self):
        il = InputLine()
        result = il.tv_handle_key(Key("a", "a"))
        self.assertTrue(result)
        self.assertEqual(il.data, "a")

    def test_ctrl_a_selects_all(self):
        il = InputLine()
        il.data = "hello"
        result = il.tv_handle_key(Key("ctrl+a", None))
        self.assertTrue(result)
        self.assertTrue(il.has_selection)

    def test_unhandled_key(self):
        il = InputLine()
        result = il.tv_handle_key(Key("f1", None))
        self.assertFalse(result)


class InputLinePasswordTest(unittest.TestCase):
    def test_display_text_masked(self):
        il = InputLine(password=True)
        il.data = "secret"
        self.assertEqual(il._display_text, "******")

    def test_display_text_normal(self):
        il = InputLine()
        il.data = "hello"
        self.assertEqual(il._display_text, "hello")


class InputLineCssTest(unittest.TestCase):
    def test_has_component_classes(self):
        self.assertIn("inputline--text", InputLine.COMPONENT_CLASSES)
        self.assertIn("inputline--selected", InputLine.COMPONENT_CLASSES)
        self.assertIn("inputline--cursor", InputLine.COMPONENT_CLASSES)
        self.assertIn("inputline--arrow", InputLine.COMPONENT_CLASSES)

    def test_text_uses_panel_background(self):
        css = InputLine.DEFAULT_CSS
        section = css.split("inputline--text")[1].split("}")[0]
        self.assertIn("$panel", section)


if __name__ == "__main__":
    unittest.main()
