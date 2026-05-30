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

from __future__ import annotations

from typing import Any

from textual import events
from textual.widget import Widget

from textual_vision.constants import StateFlag, OptionFlag, Command
from textual_vision.events import BroadcastMessage


class TVViewMixin:
    """Mixin providing Turbo Vision state, options, and event handling to Textual Widgets.

    Widgets that participate in TV's three-phase dispatch should include this mixin
    and override tv_handle_key to process key events.
    """

    tv_state: StateFlag = StateFlag(0)
    tv_options: OptionFlag = OptionFlag(0)
    help_ctx: int = 0

    def tv_handle_key(self, event: events.Key) -> bool:
        """Handle a key event dispatched by the owning Group.

        Returns True if the event was consumed, False to pass to the next phase.
        """
        return False

    def tv_get_hotkey(self) -> str | None:
        """Return the Alt+letter hotkey for this view, or None."""
        return None

    def tv_handle_hotkey(self) -> bool:
        """Activate this view's hotkey action. Returns True if handled."""
        return False

    def on_tv_focus(self) -> None:
        """Called when this view receives TV focus. Override to update appearance."""
        pass

    def on_tv_blur(self) -> None:
        """Called when this view loses TV focus. Override to update appearance."""
        pass

    def tv_select_self(self) -> None:
        """Transfer TV focus to this widget, propagating up through all ancestor Groups.

        Mirrors TV's TView::select: each Group in the chain sets its current
        to the child that contains this widget, ensuring the full focus chain
        is correct (e.g., a widget click activates its parent Window in the DeskTop).
        """
        if not isinstance(self, Widget):
            return
        widget: Widget = self  # type: ignore[assignment]
        parent = self.parent
        while parent is not None:
            if isinstance(parent, Group):
                parent.current = widget
                widget = parent
            parent = getattr(parent, "parent", None)


class Group(Widget, TVViewMixin):
    """Container widget implementing TV-style three-phase event dispatch and focus scoping.

    Group dispatches key events in three phases:
    1. PreProcess: children with OptionFlag.PRE_PROCESS
    2. Focused: the current (TV-focused) child
    3. PostProcess: children with OptionFlag.POST_PROCESS

    Focus is scoped to the Group's children -- cycling does not escape to the Screen.
    """

    can_focus = True

    DEFAULT_CSS = """
    Group {
        width: 1fr;
        height: 1fr;
    }
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._current: Widget | None = None

    @property
    def current(self) -> Widget | None:
        return self._current

    @current.setter
    def current(self, child: Widget | None) -> None:
        if self._current is child:
            return
        old = self._current
        self._current = child
        in_chain = self._is_focus_chain()
        if old is not None and isinstance(old, TVViewMixin):
            old.tv_state &= ~StateFlag.SELECTED
            if in_chain:
                old.tv_state &= ~StateFlag.FOCUSED
                old.on_tv_blur()
                self.broadcast(Command.RELEASED_FOCUS, old)
            if isinstance(old, Widget):
                old.refresh()
        if child is not None and isinstance(child, TVViewMixin):
            child.tv_state |= StateFlag.SELECTED
            if in_chain:
                child.tv_state |= StateFlag.FOCUSED
                child.on_tv_focus()
                self.broadcast(Command.RECEIVED_FOCUS, child)
            if isinstance(child, Widget):
                child.refresh()
                if child.is_mounted and in_chain:
                    Group._focus_deepest(child)

    @staticmethod
    def _focus_deepest(widget: Widget) -> None:
        """Give Textual focus to the deepest TV-focused descendant.

        Walks down the _current chain so that activating a Window in the
        DeskTop gives Textual focus to the Window's internally focused child,
        not the Window itself.
        """
        while isinstance(widget, Group) and widget._current is not None:
            current = widget._current
            if isinstance(current, Widget) and current.is_mounted:
                widget = current
            else:
                break
        widget.focus()

    def _is_focus_chain(self) -> bool:
        """Check if this Group is in the active TV focus chain.

        A Group is in the focus chain if it has StateFlag.FOCUSED (set by its
        parent Group's current setter) or if it has no ancestor Group (i.e.,
        it is the topmost TV Group, like DeskTop).
        """
        if self.tv_state & StateFlag.FOCUSED:
            return True
        parent = self.parent
        while parent is not None:
            if isinstance(parent, Group):
                return False
            parent = getattr(parent, "parent", None)
        return True

    def on_tv_focus(self) -> None:
        """Propagate FOCUSED down to the current child when this Group gains focus."""
        if self._current is not None and isinstance(self._current, TVViewMixin):
            self._current.tv_state |= StateFlag.FOCUSED
            self._current.on_tv_focus()

    def on_tv_blur(self) -> None:
        """Clear FOCUSED from the current child when this Group loses focus."""
        if self._current is not None and isinstance(self._current, TVViewMixin):
            self._current.tv_state &= ~StateFlag.FOCUSED
            self._current.on_tv_blur()

    def _tv_children(self) -> list[Widget]:
        """Return all descendants that participate in TV dispatch (have TVViewMixin)."""
        result: list[Widget] = []
        self._collect_tv_children(self, result)
        return result

    def _collect_tv_children(self, widget: Widget, result: list[Widget]) -> None:
        for c in widget.children:
            if isinstance(c, TVViewMixin):
                result.append(c)
            if c.children and not isinstance(c, Group):
                self._collect_tv_children(c, result)

    def _selectable_children(self) -> list[Widget]:
        """Return descendants that can receive TV focus."""
        result = []
        for c in self._tv_children():
            mixin: TVViewMixin = c  # type: ignore[assignment]
            if OptionFlag.SELECTABLE in mixin.tv_options and not (StateFlag.DISABLED in mixin.tv_state):
                result.append(c)
        return result

    def select_next(self, forward: bool = True) -> bool:
        """Cycle TV focus to the next selectable child. Returns True if focus changed."""
        selectable = self._selectable_children()
        if not selectable:
            return False

        if self._current is None or self._current not in selectable:
            self.current = selectable[0] if forward else selectable[-1]
            return True

        idx = selectable.index(self._current)
        if forward:
            new_idx = (idx + 1) % len(selectable)
        else:
            new_idx = (idx - 1) % len(selectable)

        if selectable[new_idx] is self._current:
            return False

        self.current = selectable[new_idx]
        return True

    def _dispatch_to_phase(self, event: events.Key, flag: OptionFlag,
                           children: list[Widget] | None = None) -> bool:
        """Dispatch a key event to children with the given option flag.

        Returns True if any child handled the event.
        """
        for child in (children if children is not None else self._tv_children()):
            mixin: TVViewMixin = child  # type: ignore[assignment]
            if flag in mixin.tv_options:
                if mixin.tv_handle_key(event):
                    return True
        return False

    def tv_handle_key(self, event: events.Key) -> bool:
        """Handle key event using three-phase dispatch.

        Called when this Group is a child of another Group and receives
        a dispatched key event.
        """
        return self._three_phase_dispatch(event)

    def _three_phase_dispatch(self, event: events.Key) -> bool:
        """Execute four-phase key dispatch.

        Phase 1: PreProcess children
        Phase 2: Current (focused) child
        Phase 3: PostProcess children
        Phase 4: Hotkey scan — Alt+letter matched against all children

        Returns True if any phase handled the event.
        """
        children = self._tv_children()

        if self._dispatch_to_phase(event, OptionFlag.PRE_PROCESS, children):
            return True

        if self._current is not None and isinstance(self._current, TVViewMixin):
            if self._current.tv_handle_key(event):
                return True

        if self._dispatch_to_phase(event, OptionFlag.POST_PROCESS, children):
            return True

        if self._dispatch_hotkey(event, children):
            return True

        return False

    def _dispatch_hotkey(self, event: events.Key,
                         children: list[Widget] | None = None) -> bool:
        """Scan all TV children for an Alt+letter hotkey match."""
        if not (event.key.startswith("alt+") and len(event.key) == 5):
            return False
        letter = event.key[4].lower()
        for child in (children if children is not None else self._tv_children()):
            mixin: TVViewMixin = child  # type: ignore[assignment]
            if mixin.tv_get_hotkey() == letter:
                if mixin.tv_handle_hotkey():
                    return True
        return False

    def on_key(self, event: events.Key) -> None:
        """Intercept Textual key events for three-phase dispatch.

        Tab/Shift+Tab cycle TV focus before three-phase dispatch, matching
        TGroup::handleEvent which intercepts kbTab/kbShiftTab.
        Uses on_key (not _on_key) so it receives bubbled events from
        focused children.
        """
        self._ensure_current()

        if event.key == "tab":
            if self.select_next(forward=True):
                event.stop()
                event.prevent_default()
                return
        elif event.key == "shift+tab":
            if self.select_next(forward=False):
                event.stop()
                event.prevent_default()
                return

        if self._three_phase_dispatch(event):
            event.stop()
            event.prevent_default()

    def broadcast(self, command: Command, info: Any = None) -> None:
        """Post a BroadcastMessage to every descendant widget."""
        self._broadcast_to(self, command, info)

    def _broadcast_to(self, widget: Widget, command: Command, info: Any) -> None:
        for child in widget.children:
            child.post_message(BroadcastMessage(command, info))
            if child.children and not isinstance(child, Group):
                self._broadcast_to(child, command, info)

    def on_mount(self) -> None:
        """Auto-select the first selectable child on mount if none is current.

        Uses call_later so subclass on_mount can finish mounting children first.
        """
        if self._current is None:
            self.call_later(self._deferred_initial_select)

    def _deferred_initial_select(self) -> None:
        if self._current is None:
            self.select_next()

    def _ensure_current(self) -> None:
        """Silently initialize _current to the first selectable child.

        Called before Tab/key dispatch so the first Tab actually advances
        instead of being consumed by initialization. Only sets FOCUSED if
        this Group is in the active focus chain.
        """
        if self._current is not None:
            return
        selectable = self._selectable_children()
        if selectable:
            child = selectable[0]
            self._current = child
            in_chain = self._is_focus_chain()
            if isinstance(child, TVViewMixin):
                child.tv_state |= StateFlag.SELECTED
                if in_chain:
                    child.tv_state |= StateFlag.FOCUSED
                    child.on_tv_focus()
            if in_chain and isinstance(child, Widget) and child.is_mounted:
                Group._focus_deepest(child)
