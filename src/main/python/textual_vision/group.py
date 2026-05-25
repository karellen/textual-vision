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
        if old is not None and isinstance(old, TVViewMixin):
            old.tv_state &= ~(StateFlag.FOCUSED | StateFlag.SELECTED)
        if child is not None and isinstance(child, TVViewMixin):
            child.tv_state |= StateFlag.FOCUSED | StateFlag.SELECTED

    def _tv_children(self) -> list[Widget]:
        """Return children that participate in TV dispatch (have TVViewMixin)."""
        return [c for c in self.children if isinstance(c, TVViewMixin)]

    def _selectable_children(self) -> list[Widget]:
        """Return children that can receive TV focus."""
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

    def _dispatch_to_phase(self, event: events.Key, flag: OptionFlag) -> bool:
        """Dispatch a key event to children with the given option flag.

        Returns True if any child handled the event.
        """
        for child in self._tv_children():
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
        """Execute three-phase key dispatch.

        Phase 1: PreProcess children
        Phase 2: Current (focused) child
        Phase 3: PostProcess children

        Returns True if any phase handled the event.
        """
        if self._dispatch_to_phase(event, OptionFlag.PRE_PROCESS):
            return True

        if self._current is not None and isinstance(self._current, TVViewMixin):
            if self._current.tv_handle_key(event):
                return True

        if self._dispatch_to_phase(event, OptionFlag.POST_PROCESS):
            return True

        return False

    async def _on_key(self, event: events.Key) -> None:
        """Intercept Textual key events for three-phase dispatch.

        When Group has Textual focus, key events arrive here. We implement
        TV's three-phase dispatch before letting Textual's normal handling proceed.
        """
        if self._three_phase_dispatch(event):
            event.stop()
            event.prevent_default()

    def broadcast(self, command: Command, info: Any = None) -> None:
        """Post a BroadcastMessage to every child widget."""
        for child in self.children:
            child.post_message(BroadcastMessage(command, info))

    def on_mount(self) -> None:
        """Auto-select the first selectable child on mount if none is current."""
        if self._current is None:
            self.select_next()
