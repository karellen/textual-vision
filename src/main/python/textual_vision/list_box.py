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

from textual_vision.list_viewer import ListViewer
from textual_vision.scroll_bar import ScrollBar


class ListBox(ListViewer):
    """Concrete list backed by a Python list of strings.

    Port of TV's TListBox. Stores items in a Python list and
    implements get_text() to retrieve them by index.
    """

    def __init__(self, items: list[str] | None = None,
                 num_cols: int = 1,
                 v_scroll_bar: ScrollBar | None = None,
                 h_scroll_bar: ScrollBar | None = None,
                 **kwargs: Any) -> None:
        super().__init__(num_cols=num_cols, v_scroll_bar=v_scroll_bar,
                         h_scroll_bar=h_scroll_bar, **kwargs)
        self._items: list[str] = list(items) if items else []
        self._range = len(self._items)
        self._update_scrollbars()

    @property
    def items(self) -> list[str]:
        return self._items

    def get_text(self, item: int) -> str:
        if 0 <= item < len(self._items):
            return self._items[item]
        return ""

    def set_list(self, items: list[str]) -> None:
        self._items = list(items)
        self.set_range(len(self._items))
        self.focus_item(0)
