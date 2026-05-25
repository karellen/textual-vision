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

"""Classic Turbo Vision color themes for Textual.

Provides the two iconic IDE palettes from the DOS era:

- **Turbo Pascal** (``turbo-pascal``): Blue desktop, cyan/white dialogs,
  gray menus. The Turbo Pascal 7.0 / Borland Pascal look.
  TV's cpAppColor palette.

- **Turbo C** (``turbo-c``): Dark/black desktop, yellow text,
  cyan accents. The Turbo C / Borland C++ 3.x look.

Both palettes map the 16 CGA/VGA BIOS colors to Textual theme
variables.
"""

from __future__ import annotations

from textual.theme import Theme

# ── CGA/VGA BIOS palette in hex RGB ──────────────────────────────
# Standard 16-color VGA text-mode palette used by Turbo Vision.
CGA_BLACK = "#000000"
CGA_BLUE = "#0000AA"
CGA_GREEN = "#00AA00"
CGA_CYAN = "#00AAAA"
CGA_RED = "#AA0000"
CGA_MAGENTA = "#AA00AA"
CGA_BROWN = "#AA5500"
CGA_LIGHT_GRAY = "#AAAAAA"
CGA_DARK_GRAY = "#555555"
CGA_LIGHT_BLUE = "#5555FF"
CGA_LIGHT_GREEN = "#55FF55"
CGA_LIGHT_CYAN = "#55FFFF"
CGA_LIGHT_RED = "#FF5555"
CGA_LIGHT_MAGENTA = "#FF55FF"
CGA_YELLOW = "#FFFF55"
CGA_WHITE = "#FFFFFF"

# ── Turbo Pascal 7.0 theme ───────────────────────────────────────
# cpAppColor: blue desktop, gray dialogs, cyan highlights.
# Desktop: white-on-blue (BIOS 0x1F = bg 1 fg F)
# Dialogs: black-on-lightgray (BIOS 0x70 = bg 7 fg 0)
# Menus/status: black-on-lightgray (BIOS 0x70)
# Active title: white-on-blue (BIOS 0x1F)
# Scrollbars: green-on-blue (BIOS 0x1A)
# Buttons: black-on-cyan (BIOS 0x30)

THEME_TURBO_PASCAL = Theme(
    name="turbo-pascal",
    primary=CGA_LIGHT_CYAN,
    secondary=CGA_CYAN,
    accent=CGA_GREEN,
    foreground=CGA_WHITE,
    background=CGA_BLUE,
    surface=CGA_LIGHT_GRAY,
    panel=CGA_CYAN,
    warning=CGA_YELLOW,
    error=CGA_LIGHT_RED,
    success=CGA_LIGHT_GREEN,
    dark=True,
    variables={
        "block-cursor-foreground": CGA_BLUE,
        "block-cursor-background": CGA_LIGHT_CYAN,
        "block-cursor-text-style": "bold",
        "input-cursor-foreground": CGA_WHITE,
        "input-cursor-background": CGA_CYAN,
        "input-cursor-text-style": "none",
        "scrollbar": CGA_LIGHT_BLUE,
        "scrollbar-active": CGA_LIGHT_CYAN,
        "scrollbar-background": CGA_BLUE,
        "scrollbar-background-hover": CGA_BLUE,
        "scrollbar-background-active": CGA_BLUE,
        "scrollbar-corner-color": CGA_BLUE,
        "scrollbar-color-hover": CGA_LIGHT_CYAN,
        "link-color": CGA_LIGHT_CYAN,
        "link-background": "transparent",
        "link-color-hover": CGA_WHITE,
        "link-background-hover": CGA_CYAN,
        "footer-foreground": CGA_BLACK,
        "footer-background": CGA_LIGHT_GRAY,
        "footer-key-foreground": CGA_WHITE,
        "footer-key-background": CGA_CYAN,
        "footer-description-foreground": CGA_BLACK,
        "footer-description-background": CGA_LIGHT_GRAY,
        "menu-hotkey": CGA_RED,
    },
)

# ── Turbo C / Borland C++ theme ──────────────────────────────────
# Darker theme: black desktop, yellow/cyan accents.
# Desktop: lightgray-on-black (BIOS 0x07)
# Dialogs: black-on-lightgray (BIOS 0x70)
# Menus: white-on-black or black-on-lightgray
# Highlights: yellow-on-black (BIOS 0x0E)
# Active items: black-on-cyan (BIOS 0x30)
# Editor text: yellow-on-blue (BIOS 0x1E)

THEME_TURBO_C = Theme(
    name="turbo-c",
    primary=CGA_CYAN,
    secondary=CGA_LIGHT_CYAN,
    accent=CGA_YELLOW,
    foreground=CGA_YELLOW,
    background=CGA_BLACK,
    surface=CGA_LIGHT_GRAY,
    panel=CGA_CYAN,
    warning=CGA_YELLOW,
    error=CGA_LIGHT_RED,
    success=CGA_LIGHT_GREEN,
    dark=True,
    variables={
        "block-cursor-foreground": CGA_BLACK,
        "block-cursor-background": CGA_YELLOW,
        "block-cursor-text-style": "bold",
        "input-cursor-foreground": CGA_WHITE,
        "input-cursor-background": CGA_CYAN,
        "input-cursor-text-style": "none",
        "scrollbar": CGA_LIGHT_GRAY,
        "scrollbar-active": CGA_WHITE,
        "scrollbar-background": CGA_DARK_GRAY,
        "scrollbar-background-hover": CGA_DARK_GRAY,
        "scrollbar-background-active": CGA_DARK_GRAY,
        "scrollbar-corner-color": CGA_BLACK,
        "scrollbar-color-hover": CGA_WHITE,
        "link-color": CGA_LIGHT_CYAN,
        "link-background": "transparent",
        "link-color-hover": CGA_WHITE,
        "link-background-hover": CGA_CYAN,
        "footer-foreground": CGA_BLACK,
        "footer-background": CGA_LIGHT_GRAY,
        "footer-key-foreground": CGA_WHITE,
        "footer-key-background": CGA_CYAN,
        "footer-description-foreground": CGA_BLACK,
        "footer-description-background": CGA_LIGHT_GRAY,
        "menu-hotkey": CGA_RED,
    },
)

ALL_THEMES: dict[str, Theme] = {
    THEME_TURBO_PASCAL.name: THEME_TURBO_PASCAL,
    THEME_TURBO_C.name: THEME_TURBO_C,
}


def register_themes(app) -> None:
    """Register all Textual Vision themes with a Textual App."""
    for theme in ALL_THEMES.values():
        app.register_theme(theme)
