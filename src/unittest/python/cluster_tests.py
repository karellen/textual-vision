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
from textual_vision.cluster import CheckBoxes, RadioButtons


class CheckBoxesCreationTest(unittest.TestCase):
    def test_items(self):
        cb = CheckBoxes(["~A~lpha", "~B~eta"])
        self.assertEqual(cb.items, ["~A~lpha", "~B~eta"])

    def test_initial_value_zero(self):
        cb = CheckBoxes(["A", "B"])
        self.assertEqual(cb.value, 0)

    def test_selectable(self):
        cb = CheckBoxes(["A"])
        self.assertIn(OptionFlag.SELECTABLE, cb.tv_options)

    def test_default_columns(self):
        cb = CheckBoxes(["A", "B"])
        self.assertEqual(cb.columns, 1)


class CheckBoxesMarkTest(unittest.TestCase):
    def test_unchecked_mark(self):
        cb = CheckBoxes(["A", "B"])
        self.assertEqual(cb.mark(0), "[ ] ")

    def test_checked_mark(self):
        cb = CheckBoxes(["A", "B"])
        cb.value = 0b01
        self.assertEqual(cb.mark(0), "[X] ")
        self.assertEqual(cb.mark(1), "[ ] ")

    def test_both_checked(self):
        cb = CheckBoxes(["A", "B"])
        cb.value = 0b11
        self.assertEqual(cb.mark(0), "[X] ")
        self.assertEqual(cb.mark(1), "[X] ")


class CheckBoxesPressTest(unittest.TestCase):
    def test_toggle_on(self):
        cb = CheckBoxes(["A", "B"])
        cb.press(0)
        self.assertEqual(cb.value, 0b01)

    def test_toggle_off(self):
        cb = CheckBoxes(["A", "B"])
        cb.value = 0b01
        cb.press(0)
        self.assertEqual(cb.value, 0b00)

    def test_toggle_independent(self):
        cb = CheckBoxes(["A", "B", "C"])
        cb.press(0)
        cb.press(2)
        self.assertEqual(cb.value, 0b101)
        cb.press(0)
        self.assertEqual(cb.value, 0b100)


class RadioButtonsCreationTest(unittest.TestCase):
    def test_items(self):
        rb = RadioButtons(["~O~ne", "~T~wo"])
        self.assertEqual(rb.items, ["~O~ne", "~T~wo"])

    def test_initial_value_zero(self):
        rb = RadioButtons(["A", "B"])
        self.assertEqual(rb.value, 0)


class RadioButtonsMarkTest(unittest.TestCase):
    def test_unselected_mark(self):
        rb = RadioButtons(["A", "B"])
        self.assertEqual(rb.mark(0), "( ) ")

    def test_selected_mark(self):
        rb = RadioButtons(["A", "B"])
        rb.value = 0b01
        self.assertEqual(rb.mark(0), "(•) ")
        self.assertEqual(rb.mark(1), "( ) ")


class RadioButtonsPressTest(unittest.TestCase):
    def test_select_first(self):
        rb = RadioButtons(["A", "B"])
        rb.press(0)
        self.assertEqual(rb.value, 0b01)

    def test_select_second_deselects_first(self):
        rb = RadioButtons(["A", "B"])
        rb.press(0)
        rb.press(1)
        self.assertEqual(rb.value, 0b10)

    def test_exclusive_selection(self):
        rb = RadioButtons(["A", "B", "C"])
        rb.press(2)
        self.assertEqual(rb.value, 0b100)
        rb.press(0)
        self.assertEqual(rb.value, 0b001)


class ClusterNavigationTest(unittest.TestCase):
    def test_down_moves_sel(self):
        cb = CheckBoxes(["A", "B", "C"])
        self.assertEqual(cb.sel, 0)
        cb.tv_handle_key(Key("down", None))
        self.assertEqual(cb.sel, 1)

    def test_up_wraps(self):
        cb = CheckBoxes(["A", "B", "C"])
        cb.tv_handle_key(Key("up", None))
        self.assertEqual(cb.sel, 2)

    def test_space_toggles(self):
        cb = CheckBoxes(["A", "B"])
        cb.tv_handle_key(Key("space", " "))
        self.assertEqual(cb.value, 0b01)

    def test_hotkey_selects_and_toggles(self):
        cb = CheckBoxes(["~A~lpha", "~B~eta"])
        result = cb.tv_handle_key(Key("b", "b"))
        self.assertTrue(result)
        self.assertEqual(cb.sel, 1)
        self.assertEqual(cb.value, 0b10)


class ClusterLayoutTest(unittest.TestCase):
    def test_single_column_rows(self):
        cb = CheckBoxes(["A", "B", "C"])
        self.assertEqual(cb._rows, 3)

    def test_two_columns_rows(self):
        cb = CheckBoxes(["A", "B", "C", "D"], columns=2)
        self.assertEqual(cb._rows, 2)

    def test_two_columns_odd_rows(self):
        cb = CheckBoxes(["A", "B", "C"], columns=2)
        self.assertEqual(cb._rows, 2)

    def test_item_at_single_column(self):
        cb = CheckBoxes(["A", "B", "C"])
        self.assertEqual(cb._item_at(0, 0), 0)
        self.assertEqual(cb._item_at(1, 0), 1)
        self.assertEqual(cb._item_at(2, 0), 2)

    def test_item_at_two_columns(self):
        cb = CheckBoxes(["A", "B", "C", "D"], columns=2)
        self.assertEqual(cb._item_at(0, 0), 0)
        self.assertEqual(cb._item_at(1, 0), 1)
        self.assertEqual(cb._item_at(0, 1), 2)
        self.assertEqual(cb._item_at(1, 1), 3)

    def test_item_at_out_of_range(self):
        cb = CheckBoxes(["A", "B", "C"], columns=2)
        self.assertIsNone(cb._item_at(1, 1))

    def test_content_height(self):
        cb = CheckBoxes(["A", "B", "C"])
        self.assertEqual(cb.get_content_height(None, None, 40), 3)

    def test_content_height_multicolumn(self):
        cb = CheckBoxes(["A", "B", "C", "D"], columns=2)
        self.assertEqual(cb.get_content_height(None, None, 40), 2)


class ClusterMultiColumnNavigationTest(unittest.TestCase):
    def test_right_moves_to_next_column(self):
        cb = CheckBoxes(["A", "B", "C", "D"], columns=2)
        self.assertEqual(cb.sel, 0)
        cb.tv_handle_key(Key("right", None))
        self.assertEqual(cb.sel, 2)

    def test_left_moves_to_prev_column(self):
        cb = CheckBoxes(["A", "B", "C", "D"], columns=2)
        cb.sel = 2
        cb.tv_handle_key(Key("left", None))
        self.assertEqual(cb.sel, 0)


if __name__ == "__main__":
    unittest.main()
