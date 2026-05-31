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

from textual import events
from textual.widget import Widget

from textual_vision.constants import StateFlag, OptionFlag, Command
from textual_vision.events import BroadcastMessage
from textual_vision.group import TVViewMixin, Group


class MockTVWidget(Widget, TVViewMixin):
    """A minimal TV-aware widget for testing dispatch."""

    def __init__(self, name: str, options: OptionFlag = OptionFlag(0),
                 handle_keys: set[str] | None = None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.tv_options = options
        self._handle_keys = handle_keys or set()
        self.received_keys: list[str] = []
        self.received_broadcasts: list[Command] = []

    def tv_handle_key(self, event: events.Key) -> bool:
        self.received_keys.append(event.key)
        return event.key in self._handle_keys

    def on_broadcast_message(self, message: BroadcastMessage) -> None:
        self.received_broadcasts.append(message.command)


class ThreePhaseDispatchTest(unittest.TestCase):
    def _make_key(self, key: str) -> events.Key:
        return events.Key(key, key if len(key) == 1 else None)

    def test_preprocess_receives_first(self):
        group = Group()
        pre = MockTVWidget("pre", OptionFlag.PRE_PROCESS | OptionFlag.SELECTABLE,
                           handle_keys={"a"})
        focused = MockTVWidget("focused", OptionFlag.SELECTABLE, handle_keys={"a"})
        post = MockTVWidget("post", OptionFlag.POST_PROCESS | OptionFlag.SELECTABLE,
                            handle_keys={"a"})

        group._nodes._append(pre)
        group._nodes._append(focused)
        group._nodes._append(post)
        group.current = focused

        event = self._make_key("a")
        result = group._three_phase_dispatch(event)

        self.assertTrue(result)
        self.assertEqual(pre.received_keys, ["a"])
        self.assertEqual(focused.received_keys, [])
        self.assertEqual(post.received_keys, [])

    def test_focused_receives_after_preprocess_passes(self):
        group = Group()
        pre = MockTVWidget("pre", OptionFlag.PRE_PROCESS | OptionFlag.SELECTABLE,
                           handle_keys=set())
        focused = MockTVWidget("focused", OptionFlag.SELECTABLE, handle_keys={"b"})
        post = MockTVWidget("post", OptionFlag.POST_PROCESS | OptionFlag.SELECTABLE,
                            handle_keys={"b"})

        group._nodes._append(pre)
        group._nodes._append(focused)
        group._nodes._append(post)
        group.current = focused

        event = self._make_key("b")
        result = group._three_phase_dispatch(event)

        self.assertTrue(result)
        self.assertEqual(pre.received_keys, ["b"])
        self.assertEqual(focused.received_keys, ["b"])
        self.assertEqual(post.received_keys, [])

    def test_postprocess_receives_last(self):
        group = Group()
        pre = MockTVWidget("pre", OptionFlag.PRE_PROCESS | OptionFlag.SELECTABLE,
                           handle_keys=set())
        focused = MockTVWidget("focused", OptionFlag.SELECTABLE, handle_keys=set())
        post = MockTVWidget("post", OptionFlag.POST_PROCESS | OptionFlag.SELECTABLE,
                            handle_keys={"c"})

        group._nodes._append(pre)
        group._nodes._append(focused)
        group._nodes._append(post)
        group.current = focused

        event = self._make_key("c")
        result = group._three_phase_dispatch(event)

        self.assertTrue(result)
        self.assertEqual(pre.received_keys, ["c"])
        self.assertEqual(focused.received_keys, ["c"])
        self.assertEqual(post.received_keys, ["c"])

    def test_unhandled_returns_false(self):
        group = Group()
        pre = MockTVWidget("pre", OptionFlag.PRE_PROCESS | OptionFlag.SELECTABLE,
                           handle_keys=set())
        focused = MockTVWidget("focused", OptionFlag.SELECTABLE, handle_keys=set())

        group._nodes._append(pre)
        group._nodes._append(focused)
        group.current = focused

        event = self._make_key("x")
        result = group._three_phase_dispatch(event)

        self.assertFalse(result)
        self.assertEqual(pre.received_keys, ["x"])
        self.assertEqual(focused.received_keys, ["x"])

    def test_no_current_skips_focused_phase(self):
        group = Group()
        pre = MockTVWidget("pre", OptionFlag.PRE_PROCESS | OptionFlag.SELECTABLE,
                           handle_keys=set())
        post = MockTVWidget("post", OptionFlag.POST_PROCESS | OptionFlag.SELECTABLE,
                            handle_keys={"d"})

        group._nodes._append(pre)
        group._nodes._append(post)

        event = self._make_key("d")
        result = group._three_phase_dispatch(event)

        self.assertTrue(result)
        self.assertEqual(pre.received_keys, ["d"])
        self.assertEqual(post.received_keys, ["d"])


class FocusScopingTest(unittest.TestCase):
    def test_select_next_forward(self):
        group = Group()
        w1 = MockTVWidget("w1", OptionFlag.SELECTABLE)
        w2 = MockTVWidget("w2", OptionFlag.SELECTABLE)
        w3 = MockTVWidget("w3", OptionFlag.SELECTABLE)

        group._nodes._append(w1)
        group._nodes._append(w2)
        group._nodes._append(w3)

        group.current = w1
        group.select_next(forward=True)
        self.assertIs(group.current, w2)

        group.select_next(forward=True)
        self.assertIs(group.current, w3)

        group.select_next(forward=True)
        self.assertIs(group.current, w1)

    def test_select_next_backward(self):
        group = Group()
        w1 = MockTVWidget("w1", OptionFlag.SELECTABLE)
        w2 = MockTVWidget("w2", OptionFlag.SELECTABLE)
        w3 = MockTVWidget("w3", OptionFlag.SELECTABLE)

        group._nodes._append(w1)
        group._nodes._append(w2)
        group._nodes._append(w3)

        group.current = w1
        group.select_next(forward=False)
        self.assertIs(group.current, w3)

    def test_select_next_skips_disabled(self):
        group = Group()
        w1 = MockTVWidget("w1", OptionFlag.SELECTABLE)
        w2 = MockTVWidget("w2", OptionFlag.SELECTABLE)
        w3 = MockTVWidget("w3", OptionFlag.SELECTABLE)
        w2.tv_state |= StateFlag.DISABLED

        group._nodes._append(w1)
        group._nodes._append(w2)
        group._nodes._append(w3)

        group.current = w1
        group.select_next(forward=True)
        self.assertIs(group.current, w3)

    def test_select_next_skips_non_selectable(self):
        group = Group()
        w1 = MockTVWidget("w1", OptionFlag.SELECTABLE)
        w2 = MockTVWidget("w2", OptionFlag(0))
        w3 = MockTVWidget("w3", OptionFlag.SELECTABLE)

        group._nodes._append(w1)
        group._nodes._append(w2)
        group._nodes._append(w3)

        group.current = w1
        group.select_next(forward=True)
        self.assertIs(group.current, w3)

    def test_select_next_no_selectable_returns_false(self):
        group = Group()
        w1 = MockTVWidget("w1", OptionFlag(0))

        group._nodes._append(w1)

        result = group.select_next()
        self.assertFalse(result)
        self.assertIsNone(group.current)

    def test_select_next_single_selectable_returns_false(self):
        group = Group()
        w1 = MockTVWidget("w1", OptionFlag.SELECTABLE)

        group._nodes._append(w1)
        group.current = w1

        result = group.select_next()
        self.assertFalse(result)
        self.assertIs(group.current, w1)

    def test_select_next_from_none(self):
        group = Group()
        w1 = MockTVWidget("w1", OptionFlag.SELECTABLE)
        w2 = MockTVWidget("w2", OptionFlag.SELECTABLE)

        group._nodes._append(w1)
        group._nodes._append(w2)

        group.select_next(forward=True)
        self.assertIs(group.current, w1)

    def test_select_next_backward_from_none(self):
        group = Group()
        w1 = MockTVWidget("w1", OptionFlag.SELECTABLE)
        w2 = MockTVWidget("w2", OptionFlag.SELECTABLE)

        group._nodes._append(w1)
        group._nodes._append(w2)

        group.select_next(forward=False)
        self.assertIs(group.current, w2)


class CurrentPropertyTest(unittest.TestCase):
    def test_setting_current_updates_state_flags(self):
        group = Group()
        w1 = MockTVWidget("w1", OptionFlag.SELECTABLE)
        w2 = MockTVWidget("w2", OptionFlag.SELECTABLE)

        group._nodes._append(w1)
        group._nodes._append(w2)

        group.current = w1
        self.assertIn(StateFlag.FOCUSED, w1.tv_state)
        self.assertIn(StateFlag.SELECTED, w1.tv_state)

        group.current = w2
        self.assertNotIn(StateFlag.FOCUSED, w1.tv_state)
        self.assertNotIn(StateFlag.SELECTED, w1.tv_state)
        self.assertIn(StateFlag.FOCUSED, w2.tv_state)
        self.assertIn(StateFlag.SELECTED, w2.tv_state)

    def test_setting_current_to_none(self):
        group = Group()
        w1 = MockTVWidget("w1", OptionFlag.SELECTABLE)

        group._nodes._append(w1)

        group.current = w1
        self.assertIn(StateFlag.FOCUSED, w1.tv_state)

        group.current = None
        self.assertNotIn(StateFlag.FOCUSED, w1.tv_state)

    def test_setting_same_current_is_noop(self):
        group = Group()
        w1 = MockTVWidget("w1", OptionFlag.SELECTABLE)

        group._nodes._append(w1)

        group.current = w1
        w1.tv_state |= StateFlag.ACTIVE
        group.current = w1
        self.assertIn(StateFlag.ACTIVE, w1.tv_state)
        self.assertIn(StateFlag.FOCUSED, w1.tv_state)


class TVViewMixinTest(unittest.TestCase):
    def test_default_state(self):
        w = MockTVWidget("test")
        self.assertEqual(w.tv_state, StateFlag(0))
        self.assertEqual(w.tv_options, OptionFlag(0))
        self.assertEqual(w.help_ctx, 0)

    def test_default_handle_key_returns_false(self):
        mixin = TVViewMixin()
        event = events.Key("a", "a")
        self.assertFalse(mixin.tv_handle_key(event))


class NestedGroupTest(unittest.TestCase):
    def test_nested_group_dispatch(self):
        """Inner Group's tv_handle_key triggers its own three-phase dispatch."""
        outer = Group()
        inner = Group(name="inner")
        inner.tv_options = OptionFlag.SELECTABLE

        child = MockTVWidget("child", OptionFlag.SELECTABLE, handle_keys={"e"})
        inner._nodes._append(child)
        inner.current = child

        outer._nodes._append(inner)
        outer.current = inner

        event = events.Key("e", "e")
        result = outer._three_phase_dispatch(event)

        self.assertTrue(result)
        self.assertEqual(child.received_keys, ["e"])


class FocusChainTest(unittest.TestCase):
    """Tests for Group._is_focus_chain and FOCUSED propagation."""

    def test_standalone_group_is_in_focus_chain(self):
        group = Group()
        self.assertTrue(group._is_focus_chain())

    def test_group_with_focused_flag_is_in_chain(self):
        group = Group()
        group.tv_state |= StateFlag.FOCUSED
        self.assertTrue(group._is_focus_chain())

    def test_child_group_not_focused_is_not_in_chain(self):
        outer = Group(name="outer")
        inner = Group(name="inner")
        inner.tv_options = OptionFlag.SELECTABLE
        outer._nodes._append(inner)
        inner._parent = outer
        self.assertFalse(inner._is_focus_chain())

    def test_child_group_with_focused_is_in_chain(self):
        outer = Group(name="outer")
        inner = Group(name="inner")
        inner.tv_options = OptionFlag.SELECTABLE
        inner.tv_state |= StateFlag.FOCUSED
        outer._nodes._append(inner)
        inner._parent = outer
        self.assertTrue(inner._is_focus_chain())

    def test_current_setter_sets_focused_when_in_chain(self):
        group = Group()
        w = MockTVWidget("w1", OptionFlag.SELECTABLE)
        group._nodes._append(w)
        group.current = w
        self.assertIn(StateFlag.FOCUSED, w.tv_state)

    def test_current_setter_no_focused_when_not_in_chain(self):
        outer = Group(name="outer")
        inner = Group(name="inner")
        inner.tv_options = OptionFlag.SELECTABLE
        outer._nodes._append(inner)
        inner._parent = outer

        w = MockTVWidget("w1", OptionFlag.SELECTABLE)
        inner._nodes._append(w)

        inner.current = w
        self.assertIn(StateFlag.SELECTED, w.tv_state)
        self.assertNotIn(StateFlag.FOCUSED, w.tv_state)

    def test_on_tv_focus_propagates_to_current(self):
        group = Group()
        w = MockTVWidget("w1", OptionFlag.SELECTABLE)
        group._nodes._append(w)
        group._current = w
        w.tv_state |= StateFlag.SELECTED

        group.on_tv_focus()
        self.assertIn(StateFlag.FOCUSED, w.tv_state)

    def test_on_tv_blur_clears_from_current(self):
        group = Group()
        w = MockTVWidget("w1", OptionFlag.SELECTABLE)
        group._nodes._append(w)
        group._current = w
        w.tv_state |= StateFlag.SELECTED | StateFlag.FOCUSED

        group.on_tv_blur()
        self.assertNotIn(StateFlag.FOCUSED, w.tv_state)

    def test_on_tv_focus_noop_when_no_current(self):
        group = Group()
        group.on_tv_focus()

    def test_on_tv_blur_noop_when_no_current(self):
        group = Group()
        group.on_tv_blur()


class BroadcastMessageIsolationTest(unittest.TestCase):
    def test_broadcast_creates_separate_messages(self):
        """Each child must receive its own BroadcastMessage instance."""
        group = Group()
        c1 = MockTVWidget("c1")
        c2 = MockTVWidget("c2")
        group._nodes._append(c1)
        group._nodes._append(c2)

        received_ids: list[int] = []
        original_post = Widget.post_message

        def tracking_post(self_widget, msg):
            if isinstance(msg, BroadcastMessage):
                received_ids.append(id(msg))
            return original_post(self_widget, msg)

        Widget.post_message = tracking_post
        try:
            group.broadcast(Command.VALID)
        finally:
            Widget.post_message = original_post

        self.assertEqual(len(received_ids), 2)
        self.assertNotEqual(received_ids[0], received_ids[1])


if __name__ == "__main__":
    unittest.main()
