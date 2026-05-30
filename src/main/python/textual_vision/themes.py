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

"""Classic color themes for Textual Vision.

Provides themes based on actual extracted palette data:

- **Turbo Pascal** (``turbo-pascal``): TV cpAppColor palette.
  Gray menus, blue desktop, green selection, red hotkeys.

- **Turbo C** (``turbo-c``): TC 2.01 default palette (from TC.EXE).
  Gray menus, yellow-on-blue editor, white-on-black menu hotkeys.

- **Turbo C 1.x** (``turbo-c-1x``): TC 2.01 "Version 1.x" preset.
  Cyan menus, blue-on-cyan chrome, yellow highlights.

- **Turbo C Turquoise** (``turbo-c-turquoise``): TC 2.01 "Turquoise" preset.
  Black editor background, yellow text, magenta selection highlights.

All palettes use the 16 CGA/VGA BIOS text-mode colors.
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

# ── Shared cursor/scrollbar defaults ────────────────────────────
_BLUE_SCROLLBAR_VARS = {
    "scrollbar": CGA_LIGHT_BLUE,
    "scrollbar-active": CGA_LIGHT_CYAN,
    "scrollbar-background": CGA_BLUE,
    "scrollbar-background-hover": CGA_BLUE,
    "scrollbar-background-active": CGA_BLUE,
    "scrollbar-corner-color": CGA_BLUE,
    "scrollbar-color-hover": CGA_LIGHT_CYAN,
}

# ── Dialog element colors from cpAppColor palette ───────────────
# Decoded from tvision cpAppColor[] positions 32-63 (Gray Dialog)
# and 96-127 (Cyan Dialog). Each byte is a BIOS text-mode attribute:
# high nibble = background (0-7), low nibble = foreground (0-F).
#
# These variables give each widget its own foreground/background pair,
# matching the TV palette chain: Widget → Dialog → Application.

_DIALOG_COMMON_VARS = {
    # InputLine: pos 50=0x1F (WHITE/BLUE), pos 51=0x2F (WHITE/GREEN),
    # pos 52=0x1A (LGREEN/BLUE)
    "input-fg": CGA_WHITE,
    "input-bg": CGA_BLUE,
    "input-selected-fg": CGA_WHITE,
    "input-selected-bg": CGA_GREEN,
    "input-arrow": CGA_LIGHT_GREEN,
    # Button: pos 41=0x20 (BLACK/GREEN), pos 42=0x2B (LCYAN/GREEN),
    # pos 43=0x2F (WHITE/GREEN), pos 44=0x78 (DGRAY/LGRAY),
    # pos 45=0x2E (YELLOW/GREEN)
    "button-face-fg": CGA_BLACK,
    "button-face-bg": CGA_GREEN,
    "button-default-fg": CGA_LIGHT_CYAN,
    "button-focused-fg": CGA_WHITE,
    "button-focused-bg": CGA_GREEN,
    "button-disabled-fg": CGA_DARK_GRAY,
    "button-disabled-bg": CGA_LIGHT_GRAY,
    "button-hotkey": CGA_YELLOW,
    # Label: pos 38=0x70 (BLACK/LGRAY), pos 39=0x7F (WHITE/LGRAY),
    # pos 40=0x7E (YELLOW/LGRAY)
    "label-highlight": CGA_WHITE,
    "label-hotkey": CGA_YELLOW,
    # Frame icon: pos 34=0x7A (LGREEN/LGRAY), pos 10=0x1A (LGREEN/BLUE)
    "frame-icon": CGA_LIGHT_GREEN,
    # History/ComboBox: pos 53=0x20 (BLACK/GREEN), pos 54=0x72 (GREEN/LGRAY)
    "combo-arrow-fg": CGA_BLACK,
    "combo-arrow-bg": CGA_GREEN,
    "combo-sides-fg": CGA_GREEN,
    "combo-sides-bg": CGA_LIGHT_GRAY,
}

# Gray Dialog (TP, TC, TC Turquoise — $surface = LGRAY)
_GRAY_DIALOG_VARS = {
    **_DIALOG_COMMON_VARS,
    # Button shadow: pos 46=0x70 (BLACK/LGRAY)
    "button-shadow-fg": CGA_BLACK,
    "button-shadow-bg": CGA_LIGHT_GRAY,
    # Cluster: pos 47=0x30 (BLACK/CYAN), pos 48=0x3F (WHITE/CYAN),
    # pos 49=0x3E (YELLOW/CYAN), pos 62=0x38 (DGRAY/CYAN)
    "cluster-fg": CGA_BLACK,
    "cluster-bg": CGA_CYAN,
    "cluster-focused-fg": CGA_WHITE,
    "cluster-focused-bg": CGA_CYAN,
    "cluster-hotkey": CGA_YELLOW,
    "cluster-disabled-fg": CGA_DARK_GRAY,
    "cluster-disabled-bg": CGA_CYAN,
}

# Cyan Dialog (TC 1.x — $surface = CYAN)
_CYAN_DIALOG_VARS = {
    **_DIALOG_COMMON_VARS,
    # Button shadow: pos 110=0x30 (BLACK/CYAN)
    "button-shadow-fg": CGA_BLACK,
    "button-shadow-bg": CGA_CYAN,
    # Cluster: pos 111=0x70 (BLACK/LGRAY), pos 112=0x7F (WHITE/LGRAY),
    # pos 113=0x7E (YELLOW/LGRAY), pos 126=0x78 (DGRAY/LGRAY)
    "cluster-fg": CGA_BLACK,
    "cluster-bg": CGA_LIGHT_GRAY,
    "cluster-focused-fg": CGA_WHITE,
    "cluster-focused-bg": CGA_LIGHT_GRAY,
    "cluster-hotkey": CGA_YELLOW,
    "cluster-disabled-fg": CGA_DARK_GRAY,
    "cluster-disabled-bg": CGA_LIGHT_GRAY,
}

# ── Turbo Pascal / TV cpAppColor ────────────────────────────────
# Extracted from tvision/include/tvision/app.h cpAppColor[].
# Menu/Status: 0x70=BLACK/LGRAY, 0x74=RED/LGRAY, 0x20=BLACK/GREEN
# Blue Window: 0x17=LGRAY/BLUE, 0x1F=WHITE/BLUE, 0x1A=LGREEN/BLUE
# Gray Dialog: 0x70=BLACK/LGRAY, 0x30=BLACK/CYAN, 0x20=BLACK/GREEN
# TBackground: 0x71=BLUE/LGRAY (░ pattern)

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
        "text": CGA_BLACK,
        "text-muted": CGA_DARK_GRAY,
        "window-content-background": CGA_BLUE,
        "block-cursor-foreground": CGA_BLUE,
        "block-cursor-background": CGA_LIGHT_CYAN,
        "block-cursor-text-style": "bold",
        "input-cursor-foreground": CGA_WHITE,
        "input-cursor-background": CGA_CYAN,
        "input-cursor-text-style": "none",
        **_BLUE_SCROLLBAR_VARS,
        **_GRAY_DIALOG_VARS,
        "link-color": CGA_LIGHT_CYAN,
        "link-background": "transparent",
        "link-color-hover": CGA_WHITE,
        "link-background-hover": CGA_CYAN,
        "footer-foreground": CGA_BLACK,
        "footer-background": CGA_LIGHT_GRAY,
        "footer-key-foreground": CGA_RED,
        "footer-key-background": CGA_LIGHT_GRAY,
        "footer-description-foreground": CGA_BLACK,
        "footer-description-background": CGA_LIGHT_GRAY,
        "menu-hotkey": CGA_RED,
        "menu-hotkey-background": CGA_LIGHT_GRAY,
        "desktop-pattern-color": CGA_LIGHT_CYAN,
    },
)

# ── Turbo C 2.01 Default ───────────────────────────────────────
# Extracted from TC.EXE at offset 0x434DA (70 bytes).
# Same gray chrome as cpAppColor, but:
#   Editor text: 0x1E = YELLOW/BLUE (not WHITE/BLUE)
#   Menu hotkey: 0x0F = WHITE/BLACK (not RED/LGRAY)
#   Status hotkey: 0x74 = RED/LGRAY (same as cpAppColor)
#   Pulldown normal: 0x7F = WHITE/LGRAY (not BLACK/LGRAY)
#   Pop-up selected: 0x0F = WHITE/BLACK

THEME_TURBO_C = Theme(
    name="turbo-c",
    primary=CGA_YELLOW,
    secondary=CGA_LIGHT_GRAY,
    accent=CGA_GREEN,
    foreground=CGA_YELLOW,
    background=CGA_BLUE,
    surface=CGA_LIGHT_GRAY,
    panel=CGA_LIGHT_GRAY,
    warning=CGA_YELLOW,
    error=CGA_LIGHT_RED,
    success=CGA_LIGHT_GREEN,
    dark=True,
    variables={
        "text": CGA_BLACK,
        "text-muted": CGA_DARK_GRAY,
        "window-content-background": CGA_BLUE,
        "block-cursor-foreground": CGA_BLUE,
        "block-cursor-background": CGA_YELLOW,
        "block-cursor-text-style": "bold",
        "input-cursor-foreground": CGA_BLACK,
        "input-cursor-background": CGA_LIGHT_GRAY,
        "input-cursor-text-style": "none",
        **_BLUE_SCROLLBAR_VARS,
        **_GRAY_DIALOG_VARS,
        "link-color": CGA_LIGHT_CYAN,
        "link-background": "transparent",
        "link-color-hover": CGA_WHITE,
        "link-background-hover": CGA_CYAN,
        "footer-foreground": CGA_BLACK,
        "footer-background": CGA_LIGHT_GRAY,
        "footer-key-foreground": CGA_RED,
        "footer-key-background": CGA_LIGHT_GRAY,
        "footer-description-foreground": CGA_BLACK,
        "footer-description-background": CGA_LIGHT_GRAY,
        "menu-hotkey": CGA_WHITE,
        "menu-hotkey-background": CGA_BLACK,
        "desktop-pattern-color": CGA_LIGHT_CYAN,
    },
)

# ── Turbo C 2.01 "Version 1.x" preset ──────────────────────────
# Extracted from TCINST.EXE at offset 0x0734D.
# Cyan-dominant scheme matching TC 1.x look.
#   Menu bar: 0x31 = BLUE/CYAN, hotkey 0x1E = YELLOW/BLUE
#   Status: 0x3E = YELLOW/CYAN, hotkey 0x3F = WHITE/CYAN
#   Editor: 0x17 = LGRAY/BLUE
#   Pulldown: 0x1E = YELLOW/BLUE, selected 0x1F = WHITE/BLUE
#   Pop-up selected: 0x5E = YELLOW/MAGENTA

THEME_TURBO_C_1X = Theme(
    name="turbo-c-1x",
    primary=CGA_YELLOW,
    secondary=CGA_CYAN,
    accent=CGA_MAGENTA,
    foreground=CGA_LIGHT_GRAY,
    background=CGA_BLUE,
    surface=CGA_CYAN,
    panel=CGA_CYAN,
    warning=CGA_YELLOW,
    error=CGA_LIGHT_RED,
    success=CGA_LIGHT_GREEN,
    dark=True,
    variables={
        "text": CGA_BLUE,
        "text-muted": CGA_LIGHT_BLUE,
        "window-content-background": CGA_BLUE,
        "block-cursor-foreground": CGA_BLUE,
        "block-cursor-background": CGA_YELLOW,
        "block-cursor-text-style": "bold",
        "input-cursor-foreground": CGA_BLUE,
        "input-cursor-background": CGA_CYAN,
        "input-cursor-text-style": "none",
        **_BLUE_SCROLLBAR_VARS,
        **_CYAN_DIALOG_VARS,
        "link-color": CGA_LIGHT_CYAN,
        "link-background": "transparent",
        "link-color-hover": CGA_WHITE,
        "link-background-hover": CGA_BLUE,
        "footer-foreground": CGA_YELLOW,
        "footer-background": CGA_CYAN,
        "footer-key-foreground": CGA_WHITE,
        "footer-key-background": CGA_CYAN,
        "footer-description-foreground": CGA_YELLOW,
        "footer-description-background": CGA_CYAN,
        "menu-hotkey": CGA_YELLOW,
        "menu-hotkey-background": CGA_BLUE,
        "desktop-pattern-color": CGA_CYAN,
    },
)

# ── Turbo C 2.01 "Turquoise" preset ────────────────────────────
# Extracted from TCINST.EXE at offset 0x07488.
# Black-background editor, yellow text, magenta selection.
#   Menu bar: 0x7F = WHITE/LGRAY, hotkey 0x5E = YELLOW/MAGENTA
#   Status: 0x1E = YELLOW/BLUE, hotkey 0x1B = LCYAN/BLUE
#   Editor: 0x0E = YELLOW/BLACK
#   Selection: 0x5E = YELLOW/MAGENTA
#   Pop-up: 0x1E = YELLOW/BLUE, selected 0x5E = YELLOW/MAGENTA

THEME_TURBO_C_TURQUOISE = Theme(
    name="turbo-c-turquoise",
    primary=CGA_YELLOW,
    secondary=CGA_CYAN,
    accent=CGA_MAGENTA,
    foreground=CGA_YELLOW,
    background=CGA_BLACK,
    surface=CGA_LIGHT_GRAY,
    panel=CGA_LIGHT_GRAY,
    warning=CGA_YELLOW,
    error=CGA_LIGHT_RED,
    success=CGA_LIGHT_GREEN,
    dark=True,
    variables={
        "text": CGA_WHITE,
        "text-muted": CGA_DARK_GRAY,
        "window-content-background": CGA_BLACK,
        "block-cursor-foreground": CGA_BLACK,
        "block-cursor-background": CGA_YELLOW,
        "block-cursor-text-style": "bold",
        "input-cursor-foreground": CGA_BLACK,
        "input-cursor-background": CGA_LIGHT_GRAY,
        "input-cursor-text-style": "none",
        "scrollbar": CGA_CYAN,
        "scrollbar-active": CGA_YELLOW,
        "scrollbar-background": CGA_BLACK,
        "scrollbar-background-hover": CGA_BLACK,
        "scrollbar-background-active": CGA_BLACK,
        "scrollbar-corner-color": CGA_BLACK,
        "scrollbar-color-hover": CGA_LIGHT_CYAN,
        **_GRAY_DIALOG_VARS,
        "link-color": CGA_LIGHT_CYAN,
        "link-background": "transparent",
        "link-color-hover": CGA_YELLOW,
        "link-background-hover": CGA_MAGENTA,
        "footer-foreground": CGA_YELLOW,
        "footer-background": CGA_BLUE,
        "footer-key-foreground": CGA_LIGHT_CYAN,
        "footer-key-background": CGA_BLUE,
        "footer-description-foreground": CGA_YELLOW,
        "footer-description-background": CGA_BLUE,
        "menu-hotkey": CGA_YELLOW,
        "menu-hotkey-background": CGA_MAGENTA,
        "desktop-pattern-color": CGA_BLACK,
    },
)

ALL_THEMES: dict[str, Theme] = {
    THEME_TURBO_PASCAL.name: THEME_TURBO_PASCAL,
    THEME_TURBO_C.name: THEME_TURBO_C,
    THEME_TURBO_C_1X.name: THEME_TURBO_C_1X,
    THEME_TURBO_C_TURQUOISE.name: THEME_TURBO_C_TURQUOISE,
}


def register_themes(app) -> None:
    """Register all Textual Vision themes with a Textual App."""
    for theme in ALL_THEMES.values():
        app.register_theme(theme)
