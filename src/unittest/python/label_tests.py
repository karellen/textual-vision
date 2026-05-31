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

from textual.widget import Widget

from textual_vision.label import Label


class LabelCreationTest(unittest.TestCase):
    def test_text_property(self):
        lbl = Label("~N~ame")
        self.assertEqual(lbl.text, "~N~ame")

    def test_plain_text_parsed(self):
        lbl = Label("~N~ame")
        self.assertEqual(lbl._plain, "Name")

    def test_hotkey_parsed(self):
        lbl = Label("~N~ame")
        self.assertEqual(lbl.hotkey, "n")

    def test_no_hotkey(self):
        lbl = Label("Name")
        self.assertIsNone(lbl.hotkey)

    def test_link_default_none(self):
        lbl = Label("Text")
        self.assertIsNone(lbl.link)

    def test_link_set(self):
        target = Widget()
        lbl = Label("~N~ame", link=target)
        self.assertIs(lbl.link, target)


class LabelTextSetterTest(unittest.TestCase):
    def test_text_setter_updates_hotkey(self):
        lbl = Label("~O~ld")
        self.assertEqual(lbl.hotkey, "o")
        lbl.text = "~N~ew"
        self.assertEqual(lbl.hotkey, "n")
        self.assertEqual(lbl._plain, "New")

    def test_text_setter_clears_hotkey(self):
        lbl = Label("~O~ld")
        lbl.text = "Plain"
        self.assertIsNone(lbl.hotkey)


class LabelLinkSetterTest(unittest.TestCase):
    def test_link_setter(self):
        lbl = Label("Text")
        target = Widget()
        lbl.link = target
        self.assertIs(lbl.link, target)

    def test_link_setter_none(self):
        target = Widget()
        lbl = Label("Text", link=target)
        lbl.link = None
        self.assertIsNone(lbl.link)


class LabelHotkeyTest(unittest.TestCase):
    def test_get_hotkey_with_link(self):
        target = Widget()
        lbl = Label("~N~ame", link=target)
        self.assertEqual(lbl.tv_get_hotkey(), "n")

    def test_get_hotkey_without_link_returns_none(self):
        lbl = Label("~N~ame")
        self.assertIsNone(lbl.tv_get_hotkey())

    def test_get_hotkey_no_tilde_returns_none(self):
        target = Widget()
        lbl = Label("Name", link=target)
        self.assertIsNone(lbl.tv_get_hotkey())

    def test_handle_hotkey_with_link_returns_true(self):
        from textual_vision.group import TVViewMixin

        class TVWidget(Widget, TVViewMixin):
            pass

        target = TVWidget()
        lbl = Label("~N~ame", link=target)
        self.assertTrue(lbl.tv_handle_hotkey())

    def test_handle_hotkey_without_link_returns_false(self):
        lbl = Label("~N~ame")
        self.assertFalse(lbl.tv_handle_hotkey())


class LabelNotSelectableTest(unittest.TestCase):
    def test_not_selectable(self):
        from textual_vision.constants import OptionFlag
        lbl = Label("Text")
        self.assertNotIn(OptionFlag.SELECTABLE, lbl.tv_options)


class LabelCssTest(unittest.TestCase):
    def test_has_component_classes(self):
        self.assertIn("label--text", Label.COMPONENT_CLASSES)
        self.assertIn("label--hotkey", Label.COMPONENT_CLASSES)
        self.assertIn("label--disabled", Label.COMPONENT_CLASSES)

    def test_hotkey_uses_label_hotkey_variable(self):
        css = Label.DEFAULT_CSS
        hotkey_section = css.split("label--hotkey")[1].split("}")[0]
        self.assertIn("$label-hotkey", hotkey_section)

    def test_highlight_uses_label_highlight_variable(self):
        css = Label.DEFAULT_CSS
        section = css.split("label--highlighted")[1].split("}")[0]
        self.assertIn("$label-highlight", section)


if __name__ == "__main__":
    unittest.main()
