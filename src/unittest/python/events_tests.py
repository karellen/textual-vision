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
from textual_vision.events import CommandMessage, BroadcastMessage, CommandSet


class CommandMessageTest(unittest.TestCase):
    def test_creation(self):
        msg = CommandMessage(Command.QUIT)
        self.assertEqual(msg.command, Command.QUIT)
        self.assertIsNone(msg.info)

    def test_creation_with_info(self):
        msg = CommandMessage(Command.OPEN, info="/path/to/file")
        self.assertEqual(msg.command, Command.OPEN)
        self.assertEqual(msg.info, "/path/to/file")

    def test_bubbles(self):
        self.assertTrue(CommandMessage.bubble)

    def test_repr(self):
        msg = CommandMessage(Command.CLOSE, info=42)
        self.assertIn("CommandMessage", repr(msg))
        self.assertIn("CLOSE", repr(msg))


class BroadcastMessageTest(unittest.TestCase):
    def test_creation(self):
        msg = BroadcastMessage(Command.SCREEN_CHANGED)
        self.assertEqual(msg.command, Command.SCREEN_CHANGED)
        self.assertIsNone(msg.info)

    def test_creation_with_info(self):
        msg = BroadcastMessage(Command.SCROLL_BAR_CHANGED, info={"position": 50})
        self.assertEqual(msg.command, Command.SCROLL_BAR_CHANGED)
        self.assertEqual(msg.info, {"position": 50})

    def test_does_not_bubble(self):
        self.assertFalse(BroadcastMessage.bubble)

    def test_repr(self):
        msg = BroadcastMessage(Command.TIMER_EXPIRED)
        self.assertIn("BroadcastMessage", repr(msg))
        self.assertIn("TIMER_EXPIRED", repr(msg))


class CommandSetTest(unittest.TestCase):
    def test_empty_set(self):
        cs = CommandSet()
        self.assertEqual(len(cs), 0)
        self.assertFalse(cs.has(Command.QUIT))

    def test_initial_commands(self):
        cs = CommandSet({Command.QUIT, Command.CLOSE})
        self.assertTrue(cs.has(Command.QUIT))
        self.assertTrue(cs.has(Command.CLOSE))
        self.assertFalse(cs.has(Command.OPEN))

    def test_enable(self):
        cs = CommandSet()
        cs.enable(Command.CUT, Command.COPY)
        self.assertTrue(cs.has(Command.CUT))
        self.assertTrue(cs.has(Command.COPY))
        self.assertFalse(cs.has(Command.PASTE))

    def test_disable(self):
        cs = CommandSet({Command.CUT, Command.COPY, Command.PASTE})
        cs.disable(Command.CUT, Command.COPY)
        self.assertFalse(cs.has(Command.CUT))
        self.assertFalse(cs.has(Command.COPY))
        self.assertTrue(cs.has(Command.PASTE))

    def test_contains(self):
        cs = CommandSet({Command.OK, Command.CANCEL})
        self.assertIn(Command.OK, cs)
        self.assertIn(Command.CANCEL, cs)
        self.assertNotIn(Command.QUIT, cs)

    def test_enable_all(self):
        cs = CommandSet()
        cs.enable_all({Command.NEW, Command.OPEN, Command.SAVE})
        self.assertTrue(cs.has(Command.NEW))
        self.assertTrue(cs.has(Command.OPEN))
        self.assertTrue(cs.has(Command.SAVE))

    def test_disable_all(self):
        cs = CommandSet({Command.NEW, Command.OPEN, Command.SAVE})
        cs.disable_all({Command.NEW, Command.SAVE})
        self.assertFalse(cs.has(Command.NEW))
        self.assertTrue(cs.has(Command.OPEN))
        self.assertFalse(cs.has(Command.SAVE))

    def test_equality(self):
        cs1 = CommandSet({Command.OK, Command.CANCEL})
        cs2 = CommandSet({Command.OK, Command.CANCEL})
        cs3 = CommandSet({Command.OK})
        self.assertEqual(cs1, cs2)
        self.assertNotEqual(cs1, cs3)

    def test_iadd(self):
        cs1 = CommandSet({Command.CUT, Command.COPY})
        cs2 = CommandSet({Command.PASTE, Command.UNDO})
        cs1 += cs2
        self.assertTrue(cs1.has(Command.CUT))
        self.assertTrue(cs1.has(Command.PASTE))
        self.assertTrue(cs1.has(Command.UNDO))
        self.assertEqual(len(cs1), 4)

    def test_isub(self):
        cs1 = CommandSet({Command.CUT, Command.COPY, Command.PASTE})
        cs2 = CommandSet({Command.CUT, Command.COPY})
        cs1 -= cs2
        self.assertFalse(cs1.has(Command.CUT))
        self.assertFalse(cs1.has(Command.COPY))
        self.assertTrue(cs1.has(Command.PASTE))
        self.assertEqual(len(cs1), 1)

    def test_repr(self):
        cs = CommandSet({Command.QUIT})
        self.assertIn("CommandSet", repr(cs))

    def test_disable_nonexistent_is_noop(self):
        cs = CommandSet({Command.OK})
        cs.disable(Command.CANCEL)
        self.assertTrue(cs.has(Command.OK))
        self.assertEqual(len(cs), 1)


if __name__ == "__main__":
    unittest.main()
