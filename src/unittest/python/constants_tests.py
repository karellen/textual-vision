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

from textual_vision.constants import (StateFlag, OptionFlag, Command,
                                      WindowFlag, DragMode)


class StateFlagTest(unittest.TestCase):
    def test_individual_flags(self):
        self.assertEqual(StateFlag.VISIBLE, 0x001)
        self.assertEqual(StateFlag.SHADOW, 0x008)
        self.assertEqual(StateFlag.MODAL, 0x200)
        self.assertEqual(StateFlag.EXPOSED, 0x800)

    def test_flag_combinations(self):
        combined = StateFlag.VISIBLE | StateFlag.ACTIVE | StateFlag.FOCUSED
        self.assertIn(StateFlag.VISIBLE, combined)
        self.assertIn(StateFlag.ACTIVE, combined)
        self.assertIn(StateFlag.FOCUSED, combined)
        self.assertNotIn(StateFlag.DISABLED, combined)

    def test_flag_removal(self):
        combined = StateFlag.VISIBLE | StateFlag.ACTIVE | StateFlag.SELECTED
        reduced = combined & ~StateFlag.ACTIVE
        self.assertIn(StateFlag.VISIBLE, reduced)
        self.assertNotIn(StateFlag.ACTIVE, reduced)
        self.assertIn(StateFlag.SELECTED, reduced)

    def test_all_flags_distinct(self):
        all_flags = [f for f in StateFlag if f.value != 0]
        values = [f.value for f in all_flags]
        self.assertEqual(len(values), len(set(values)))


class OptionFlagTest(unittest.TestCase):
    def test_individual_flags(self):
        self.assertEqual(OptionFlag.SELECTABLE, 0x001)
        self.assertEqual(OptionFlag.PRE_PROCESS, 0x010)
        self.assertEqual(OptionFlag.POST_PROCESS, 0x020)
        self.assertEqual(OptionFlag.TILEABLE, 0x080)

    def test_centered_is_combination(self):
        self.assertEqual(OptionFlag.CENTERED,
                         OptionFlag.CENTER_X | OptionFlag.CENTER_Y)
        self.assertIn(OptionFlag.CENTER_X, OptionFlag.CENTERED)
        self.assertIn(OptionFlag.CENTER_Y, OptionFlag.CENTERED)

    def test_pre_post_process_distinct(self):
        combined = OptionFlag.PRE_PROCESS | OptionFlag.POST_PROCESS
        self.assertIn(OptionFlag.PRE_PROCESS, combined)
        self.assertIn(OptionFlag.POST_PROCESS, combined)
        self.assertNotEqual(OptionFlag.PRE_PROCESS, OptionFlag.POST_PROCESS)


class CommandTest(unittest.TestCase):
    def test_standard_commands(self):
        self.assertEqual(Command.VALID, 0)
        self.assertEqual(Command.QUIT, 1)
        self.assertEqual(Command.OK, 10)
        self.assertEqual(Command.CANCEL, 11)

    def test_edit_commands(self):
        self.assertEqual(Command.CUT, 20)
        self.assertEqual(Command.COPY, 21)
        self.assertEqual(Command.PASTE, 22)

    def test_file_commands(self):
        self.assertEqual(Command.NEW, 30)
        self.assertEqual(Command.OPEN, 31)
        self.assertEqual(Command.SAVE, 32)

    def test_notification_commands(self):
        self.assertEqual(Command.RECEIVED_FOCUS, 50)
        self.assertEqual(Command.RELEASED_FOCUS, 51)
        self.assertEqual(Command.SCREEN_CHANGED, 57)

    def test_all_commands_unique(self):
        values = [c.value for c in Command]
        self.assertEqual(len(values), len(set(values)))


class WindowFlagTest(unittest.TestCase):
    def test_individual_flags(self):
        self.assertEqual(WindowFlag.MOVE, 0x01)
        self.assertEqual(WindowFlag.GROW, 0x02)
        self.assertEqual(WindowFlag.CLOSE, 0x04)
        self.assertEqual(WindowFlag.ZOOM, 0x08)

    def test_typical_window_flags(self):
        all_flags = WindowFlag.MOVE | WindowFlag.GROW | WindowFlag.CLOSE | WindowFlag.ZOOM
        self.assertIn(WindowFlag.MOVE, all_flags)
        self.assertIn(WindowFlag.ZOOM, all_flags)


class DragModeTest(unittest.TestCase):
    def test_individual_flags(self):
        self.assertEqual(DragMode.LIMIT_LO_X, 0x01)
        self.assertEqual(DragMode.LIMIT_LO_Y, 0x02)
        self.assertEqual(DragMode.LIMIT_HI_X, 0x04)
        self.assertEqual(DragMode.LIMIT_HI_Y, 0x08)

    def test_limit_all_is_combination(self):
        self.assertEqual(DragMode.LIMIT_ALL,
                         DragMode.LIMIT_LO_X | DragMode.LIMIT_LO_Y |
                         DragMode.LIMIT_HI_X | DragMode.LIMIT_HI_Y)
        self.assertEqual(DragMode.LIMIT_ALL, 0x0F)


if __name__ == "__main__":
    unittest.main()
