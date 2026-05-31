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

from textual_vision.combo_box import ComboBox
from textual_vision.constants import OptionFlag


class ComboBoxInitTest(unittest.TestCase):
    def test_default_empty_items(self):
        cb = ComboBox()
        self.assertEqual(cb.items, [])

    def test_with_items(self):
        cb = ComboBox(items=["Red", "Green", "Blue"])
        self.assertEqual(cb.items, ["Red", "Green", "Blue"])

    def test_items_are_copied(self):
        original = ["a", "b"]
        cb = ComboBox(items=original)
        original.append("c")
        self.assertEqual(len(cb.items), 2)


class ComboBoxItemsPropertyTest(unittest.TestCase):
    def test_set_items(self):
        cb = ComboBox(items=["old"])
        cb.items = ["new1", "new2"]
        self.assertEqual(cb.items, ["new1", "new2"])

    def test_set_items_copies(self):
        data = ["x", "y"]
        cb = ComboBox()
        cb.items = data
        data.append("z")
        self.assertEqual(len(cb.items), 2)


class ComboBoxOptionFlagsTest(unittest.TestCase):
    def test_is_selectable(self):
        cb = ComboBox()
        self.assertTrue(OptionFlag.SELECTABLE in cb.tv_options,
                        "ComboBox should be SELECTABLE")

    def test_not_post_process(self):
        cb = ComboBox()
        self.assertFalse(OptionFlag.POST_PROCESS in cb.tv_options,
                         "ComboBox should not be POST_PROCESS")


class ComboBoxEditableTest(unittest.TestCase):
    def test_default_editable(self):
        cb = ComboBox()
        self.assertTrue(cb.editable)

    def test_editable_false(self):
        cb = ComboBox(editable=False)
        self.assertFalse(cb.editable)

    def test_editable_true_explicit(self):
        cb = ComboBox(editable=True)
        self.assertTrue(cb.editable)

    def test_read_only_selected_index_initial(self):
        cb = ComboBox(items=["a", "b", "c"], editable=False)
        self.assertEqual(cb._selected_index, -1)


class ComboBoxValueTest(unittest.TestCase):
    def test_initial_value_empty(self):
        cb = ComboBox()
        self.assertEqual(cb.value, "")


class ComboBoxClosePopupGuardTest(unittest.TestCase):
    def test_close_popup_noop_when_none(self):
        cb = ComboBox(items=["a", "b"])
        cb._close_popup()
        self.assertIsNone(cb._popup)

    def test_close_popup_clears_reference(self):
        from unittest.mock import MagicMock
        cb = ComboBox(items=["a", "b"])
        popup = MagicMock()
        popup.is_mounted = True
        cb._popup = popup
        cb._close_popup()
        self.assertIsNone(cb._popup)
        popup.remove.assert_called_once()

    def test_close_popup_skips_remove_when_not_mounted(self):
        from unittest.mock import MagicMock
        cb = ComboBox(items=["a", "b"])
        popup = MagicMock()
        popup.is_mounted = False
        cb._popup = popup
        cb._close_popup()
        self.assertIsNone(cb._popup)
        popup.remove.assert_not_called()


class ComboBoxFindCurrentTest(unittest.TestCase):
    """Popup must pre-select the item matching the current input value."""

    def test_finds_exact_match(self):
        cb = ComboBox(items=["Red", "Green", "Blue"])
        from unittest.mock import MagicMock
        cb._input = MagicMock()
        cb._input.data = "Green"
        self.assertEqual(cb._find_current_in_items(), 1)

    def test_finds_first_item_match(self):
        cb = ComboBox(items=["Alpha", "Beta", "Gamma"])
        from unittest.mock import MagicMock
        cb._input = MagicMock()
        cb._input.data = "Alpha"
        self.assertEqual(cb._find_current_in_items(), 0)

    def test_no_match_falls_back_to_selected_index(self):
        cb = ComboBox(items=["Red", "Green", "Blue"])
        cb._selected_index = 2
        from unittest.mock import MagicMock
        cb._input = MagicMock()
        cb._input.data = "custom text"
        self.assertEqual(cb._find_current_in_items(), 2)

    def test_no_match_no_selection_returns_zero(self):
        cb = ComboBox(items=["Red", "Green", "Blue"])
        from unittest.mock import MagicMock
        cb._input = MagicMock()
        cb._input.data = "custom text"
        self.assertEqual(cb._find_current_in_items(), 0)

    def test_empty_input_uses_selected_index(self):
        cb = ComboBox(items=["Red", "Green", "Blue"])
        cb._selected_index = 1
        from unittest.mock import MagicMock
        cb._input = MagicMock()
        cb._input.data = ""
        self.assertEqual(cb._find_current_in_items(), 1)

    def test_empty_input_no_selection_returns_zero(self):
        cb = ComboBox(items=["Red", "Green", "Blue"])
        from unittest.mock import MagicMock
        cb._input = MagicMock()
        cb._input.data = ""
        self.assertEqual(cb._find_current_in_items(), 0)


if __name__ == "__main__":
    unittest.main()
