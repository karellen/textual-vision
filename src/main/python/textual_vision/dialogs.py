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

from textual_vision.constants import Command, WindowFlag
from textual_vision.events import CommandMessage
from textual_vision.window import Window


class Dialog(Window):
    """A specialized Window for modal and modeless dialog interaction.

    Default flags: MOVE | CLOSE (no zoom/grow).
    Handles OK, Cancel, and Escape for modal completion.

    For modal use:  result = await app.execute_dialog(dialog)
    For modeless:   app.insert_window(dialog)
    """

    DEFAULT_CSS = """
    Dialog {
        width: 40;
        height: 12;
        background: $surface;
        layer: windows;
    }
    """

    def __init__(self, title: str = "",
                 flags: WindowFlag = WindowFlag.MOVE | WindowFlag.CLOSE,
                 **kwargs: Any) -> None:
        super().__init__(title=title, flags=flags, **kwargs)
        self._modal_result: Command | None = None

    @property
    def modal_result(self) -> Command | None:
        return self._modal_result

    def end_modal(self, command: Command) -> None:
        """End modal execution with the given result command.

        If valid() returns False for this command, the dialog stays open.
        Posts a DialogClosed message with the result, then schedules close
        so the message can be delivered before the widget is removed.
        """
        if not self.valid(command):
            return
        self._modal_result = command
        if self.is_mounted:
            self.post_message(Dialog.DialogClosed(command))
            self.call_later(self.close)
        else:
            self.close()

    def valid(self, command: Command) -> bool:
        """Validation hook. Return False to prevent the dialog from closing.

        Override in subclasses to add validation logic.
        """
        return True

    def on_command_message(self, message: CommandMessage) -> None:
        if message.command == Command.OK:
            self.end_modal(Command.OK)
            message.stop()
        elif message.command == Command.CANCEL:
            self.end_modal(Command.CANCEL)
            message.stop()
        elif message.command == Command.CLOSE:
            self.end_modal(Command.CANCEL)
            message.stop()
        elif message.command == Command.YES:
            self.end_modal(Command.YES)
            message.stop()
        elif message.command == Command.NO:
            self.end_modal(Command.NO)
            message.stop()
        else:
            super().on_command_message(message)

    def tv_handle_key(self, event: events.Key) -> bool:
        if event.key == "escape":
            self.end_modal(Command.CANCEL)
            return True
        return super().tv_handle_key(event)

    def close(self) -> None:
        if self.is_mounted:
            self.remove()

    class DialogClosed(CommandMessage):
        """Posted when a dialog closes with a result."""
        def __init__(self, result: Command) -> None:
            super().__init__(result)
            self.result = result
