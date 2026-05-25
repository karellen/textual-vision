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

from enum import IntEnum, IntFlag


class StateFlag(IntFlag):
    VISIBLE = 0x001
    CURSOR_VIS = 0x002
    CURSOR_INS = 0x004
    SHADOW = 0x008
    ACTIVE = 0x010
    SELECTED = 0x020
    FOCUSED = 0x040
    DRAGGING = 0x080
    DISABLED = 0x100
    MODAL = 0x200
    DEFAULT = 0x400
    EXPOSED = 0x800


class OptionFlag(IntFlag):
    SELECTABLE = 0x001
    TOP_SELECT = 0x002
    FIRST_CLICK = 0x004
    FRAMED = 0x008
    PRE_PROCESS = 0x010
    POST_PROCESS = 0x020
    BUFFERED = 0x040
    TILEABLE = 0x080
    CENTER_X = 0x100
    CENTER_Y = 0x200
    CENTERED = CENTER_X | CENTER_Y
    VALIDATE = 0x400


class Command(IntEnum):
    VALID = 0
    QUIT = 1
    ERROR = 2
    MENU = 3
    CLOSE = 4
    ZOOM = 5
    RESIZE = 6
    NEXT = 7
    PREV = 8
    HELP = 9
    OK = 10
    CANCEL = 11
    YES = 12
    NO = 13
    DEFAULT = 14
    CUT = 20
    COPY = 21
    PASTE = 22
    UNDO = 23
    CLEAR = 24
    TILE = 25
    CASCADE = 26
    REDO = 27
    NEW = 30
    OPEN = 31
    SAVE = 32
    SAVE_AS = 33
    SAVE_ALL = 34
    CHDIR = 35
    DOS_SHELL = 36
    CLOSE_ALL = 37
    RECEIVED_FOCUS = 50
    RELEASED_FOCUS = 51
    COMMAND_SET_CHANGED = 52
    SCROLL_BAR_CHANGED = 53
    SCROLL_BAR_CLICKED = 54
    SELECT_WINDOW_NUM = 55
    LIST_ITEM_SELECTED = 56
    SCREEN_CHANGED = 57
    TIMER_EXPIRED = 58


class WindowFlag(IntFlag):
    MOVE = 0x01
    GROW = 0x02
    CLOSE = 0x04
    ZOOM = 0x08


class DragMode(IntFlag):
    LIMIT_LO_X = 0x01
    LIMIT_LO_Y = 0x02
    LIMIT_HI_X = 0x04
    LIMIT_HI_Y = 0x08
    LIMIT_ALL = LIMIT_LO_X | LIMIT_LO_Y | LIMIT_HI_X | LIMIT_HI_Y
