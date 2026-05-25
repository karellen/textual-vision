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

from textual.message import Message

from textual_vision.constants import Command


class CommandMessage(Message, bubble=True):
    def __init__(self, command: Command, info: Any = None) -> None:
        super().__init__()
        self.command = command
        self.info = info

    def __repr__(self) -> str:
        return f"CommandMessage({self.command!r}, info={self.info!r})"


class BroadcastMessage(Message, bubble=False):
    def __init__(self, command: Command, info: Any = None) -> None:
        super().__init__()
        self.command = command
        self.info = info

    def __repr__(self) -> str:
        return f"BroadcastMessage({self.command!r}, info={self.info!r})"


class CommandSet:
    def __init__(self, commands: set[Command] | None = None) -> None:
        self._commands: set[Command] = set(commands) if commands else set()

    def enable(self, *commands: Command) -> None:
        self._commands.update(commands)

    def disable(self, *commands: Command) -> None:
        self._commands.difference_update(commands)

    def has(self, command: Command) -> bool:
        return command in self._commands

    def enable_all(self, commands: set[Command]) -> None:
        self._commands.update(commands)

    def disable_all(self, commands: set[Command]) -> None:
        self._commands.difference_update(commands)

    def __contains__(self, command: Command) -> bool:
        return command in self._commands

    def __len__(self) -> int:
        return len(self._commands)

    def __repr__(self) -> str:
        return f"CommandSet({self._commands!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CommandSet):
            return self._commands == other._commands
        return NotImplemented

    def __iadd__(self, other: CommandSet) -> CommandSet:
        self._commands.update(other._commands)
        return self

    def __isub__(self, other: CommandSet) -> CommandSet:
        self._commands.difference_update(other._commands)
        return self
