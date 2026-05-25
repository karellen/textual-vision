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
from textual_vision.button import Button


class ButtonCreationTest(unittest.TestCase):
    def test_text_property(self):
        btn = Button("~O~K")
        self.assertEqual(btn.text, "~O~K")

    def test_plain_text(self):
        btn = Button("~O~K")
        self.assertEqual(btn._plain, "OK")

    def test_hotkey(self):
        btn = Button("~O~K")
        self.assertEqual(btn.hotkey, "o")

    def test_default_command(self):
        btn = Button("OK")
        self.assertEqual(btn.command, Command.OK)

    def test_custom_command(self):
        btn = Button("Cancel", command=Command.CANCEL)
        self.assertEqual(btn.command, Command.CANCEL)

    def test_is_default_false(self):
        btn = Button("OK")
        self.assertFalse(btn.is_default)

    def test_is_default_true(self):
        btn = Button("OK", is_default=True)
        self.assertTrue(btn.is_default)

    def test_selectable(self):
        btn = Button("OK")
        self.assertIn(OptionFlag.SELECTABLE, btn.tv_options)


class ButtonTextSetterTest(unittest.TestCase):
    def test_text_setter_updates_hotkey(self):
        btn = Button("~O~K")
        btn.text = "~C~ancel"
        self.assertEqual(btn.hotkey, "c")
        self.assertEqual(btn._plain, "Cancel")

    def test_command_setter(self):
        btn = Button("OK")
        btn.command = Command.CANCEL
        self.assertEqual(btn.command, Command.CANCEL)


class ButtonKeyHandlingTest(unittest.TestCase):
    def test_enter_presses(self):
        btn = Button("OK")
        result = btn.tv_handle_key(Key("enter", None))
        self.assertTrue(result)

    def test_space_presses(self):
        btn = Button("OK")
        result = btn.tv_handle_key(Key("space", " "))
        self.assertTrue(result)

    def test_alt_hotkey_presses(self):
        btn = Button("~O~K")
        result = btn.tv_handle_key(Key("alt+o", None))
        self.assertTrue(result)

    def test_non_matching_key_ignored(self):
        btn = Button("~O~K")
        result = btn.tv_handle_key(Key("alt+x", None))
        self.assertFalse(result)

    def test_no_hotkey_alt_ignored(self):
        btn = Button("OK")
        result = btn.tv_handle_key(Key("alt+o", None))
        self.assertFalse(result)


class ButtonSizingTest(unittest.TestCase):
    def test_face_width(self):
        btn = Button("OK")
        self.assertEqual(btn._face_width, len("OK") + 4)

    def test_content_width_includes_shadow_columns(self):
        btn = Button("OK")
        self.assertEqual(btn.get_content_width(None, None), btn._face_width + 2)

    def test_content_height_is_two(self):
        btn = Button("OK")
        self.assertEqual(btn.get_content_height(None, None, 20), 2)


class ButtonMouseBehaviorTest(unittest.TestCase):
    def test_down_state_tracks_mouse_pressed(self):
        """Mouse press should set down=True and _mouse_pressed=True."""
        btn = Button("OK")
        btn._mouse_pressed = True
        btn.down = True
        self.assertTrue(btn.down)
        self.assertTrue(btn._mouse_pressed)

    def test_release_when_down_clears_state(self):
        """Mouse release when down should clear state and return was_down=True."""
        btn = Button("OK")
        btn._mouse_pressed = True
        btn.down = True
        was_down = btn.down
        btn.down = False
        btn._mouse_pressed = False
        self.assertTrue(was_down)
        self.assertFalse(btn.down)

    def test_release_when_not_down_no_action(self):
        """Mouse release when cursor moved off button should not fire."""
        btn = Button("OK")
        btn._mouse_pressed = True
        btn.down = False
        was_down = btn.down
        btn._mouse_pressed = False
        self.assertFalse(was_down)


class ButtonDownStateTest(unittest.TestCase):
    def test_initial_not_down(self):
        btn = Button("OK")
        self.assertFalse(btn.down)


class ButtonCssTest(unittest.TestCase):
    def test_has_component_classes(self):
        self.assertIn("button--normal", Button.COMPONENT_CLASSES)
        self.assertIn("button--default", Button.COMPONENT_CLASSES)
        self.assertIn("button--hotkey", Button.COMPONENT_CLASSES)
        self.assertIn("button--shadow", Button.COMPONENT_CLASSES)
        self.assertIn("button--disabled", Button.COMPONENT_CLASSES)

    def test_normal_uses_panel_background(self):
        css = Button.DEFAULT_CSS
        section = css.split("button--normal")[1].split("}")[0]
        self.assertIn("$panel", section)

    def test_hotkey_uses_menu_hotkey(self):
        css = Button.DEFAULT_CSS
        section = css.split("button--hotkey")[1].split("}")[0]
        self.assertIn("$menu-hotkey", section)


if __name__ == "__main__":
    unittest.main()
