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

from textual_vision.constants import Command, WindowFlag
from textual_vision.dialogs import Dialog


class DialogDefaultsTest(unittest.TestCase):
    def test_default_flags(self):
        dlg = Dialog(title="Test")
        self.assertEqual(dlg.window_flags, WindowFlag.MOVE | WindowFlag.CLOSE)

    def test_no_zoom_flag(self):
        dlg = Dialog()
        self.assertNotIn(WindowFlag.ZOOM, dlg.window_flags)

    def test_no_grow_flag(self):
        dlg = Dialog()
        self.assertNotIn(WindowFlag.GROW, dlg.window_flags)

    def test_custom_flags(self):
        dlg = Dialog(flags=WindowFlag.MOVE | WindowFlag.CLOSE | WindowFlag.ZOOM)
        self.assertIn(WindowFlag.ZOOM, dlg.window_flags)

    def test_title(self):
        dlg = Dialog(title="My Dialog")
        self.assertEqual(dlg.title, "My Dialog")


class DialogModalResultTest(unittest.TestCase):
    def test_initial_result_is_none(self):
        dlg = Dialog()
        self.assertIsNone(dlg.modal_result)


class DialogValidationTest(unittest.TestCase):
    def test_default_valid_returns_true(self):
        dlg = Dialog()
        self.assertTrue(dlg.valid(Command.OK))
        self.assertTrue(dlg.valid(Command.CANCEL))

    def test_custom_validation_can_reject(self):
        class StrictDialog(Dialog):
            def valid(self, command):
                return command != Command.OK

        dlg = StrictDialog()
        self.assertFalse(dlg.valid(Command.OK))
        self.assertTrue(dlg.valid(Command.CANCEL))


class DialogEndModalTest(unittest.TestCase):
    def test_end_modal_sets_result(self):
        dlg = Dialog()
        dlg.end_modal(Command.OK)
        self.assertEqual(dlg.modal_result, Command.OK)

    def test_end_modal_cancel_sets_result(self):
        dlg = Dialog()
        dlg.end_modal(Command.CANCEL)
        self.assertEqual(dlg.modal_result, Command.CANCEL)

    def test_end_modal_safe_when_unmounted(self):
        """end_modal must not crash when dialog is not mounted."""
        dlg = Dialog()
        dlg.end_modal(Command.OK)
        self.assertEqual(dlg.modal_result, Command.OK)

    def test_end_modal_rejected_by_validation(self):
        """valid() returning False must prevent modal_result from being set."""
        class StrictDialog(Dialog):
            def valid(self, command):
                return command != Command.OK

        dlg = StrictDialog()
        dlg.end_modal(Command.OK)
        self.assertIsNone(dlg.modal_result)

    def test_end_modal_accepted_after_rejection(self):
        """After rejecting OK, CANCEL should still work."""
        class StrictDialog(Dialog):
            def valid(self, command):
                return command != Command.OK

        dlg = StrictDialog()
        dlg.end_modal(Command.OK)
        self.assertIsNone(dlg.modal_result)
        dlg.end_modal(Command.CANCEL)
        self.assertEqual(dlg.modal_result, Command.CANCEL)


class DialogEndModalOrderTest(unittest.TestCase):
    def test_end_modal_uses_call_later_when_mounted(self):
        """end_modal must use call_later for close to let the message deliver first."""
        import inspect
        source = inspect.getsource(Dialog.end_modal)
        self.assertIn("call_later", source)

    def test_end_modal_closes_directly_when_unmounted(self):
        """end_modal must close directly when not mounted (no message to deliver)."""
        dlg = Dialog()
        dlg.end_modal(Command.OK)
        self.assertEqual(dlg.modal_result, Command.OK)


class DialogCloseTest(unittest.TestCase):
    def test_close_safe_when_unmounted(self):
        """close() must not crash when dialog is not mounted."""
        dlg = Dialog()
        dlg.close()


class DialogEscapeTest(unittest.TestCase):
    def test_escape_returns_true_and_sets_cancel(self):
        dlg = Dialog()
        event = Key("escape", None)
        result = dlg.tv_handle_key(event)
        self.assertTrue(result)
        self.assertEqual(dlg.modal_result, Command.CANCEL)

    def test_other_key_returns_false(self):
        dlg = Dialog()
        event = Key("a", "a")
        result = dlg.tv_handle_key(event)
        self.assertFalse(result)
        self.assertIsNone(dlg.modal_result)


class DialogCssTest(unittest.TestCase):
    def test_dialog_uses_surface_background(self):
        """Dialog must use $surface (gray), not $background (blue) like Window."""
        css = Dialog.DEFAULT_CSS
        self.assertIn("$surface", css)

    def test_dialog_overrides_window_background(self):
        """Dialog's CSS must override Window's $background with $surface."""
        from textual_vision.window import Window
        self.assertIn("$background", Window.DEFAULT_CSS)
        self.assertIn("$surface", Dialog.DEFAULT_CSS)


class DialogIsWindowTest(unittest.TestCase):
    def test_dialog_is_window_subclass(self):
        from textual_vision.window import Window
        self.assertTrue(issubclass(Dialog, Window))

    def test_dialog_inherits_group(self):
        from textual_vision.group import Group
        self.assertTrue(issubclass(Dialog, Group))


if __name__ == "__main__":
    unittest.main()
