"""
SnapRes - Competitive Resolution Switcher
Coded by bku

Fonts:
    Put your font .ttf files in a "fonts" folder next to this script:
        fonts/yourfonttype1.ttf
        fonts/yourfonttype2.ttf
    These are loaded as PRIVATE fonts at runtime
    via ctypes, so end users do NOT need your font installed on their PC.
    If the filenames you have differ, just update FONT_FILES below.

Build:
    pip install customtkinter pillow pyinstaller
    pyinstaller --onefile --noconsole --icon=Logo_Main.ico ^
        --add-data "Logo_Main.ico;." --add-data "logo_main.png;." ^
        --add-data "logo_dark.png;." --add-data "fonts;fonts" ^
        --name SnapRes SnapRes.py
"""

import os
import re
import sys
import atexit
import ctypes
import tkinter as tk
import tkinter.font as tkfont
import webbrowser

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFilter

# ---------------------------------------------------------------------------
# DPI awareness (must happen before ANY Tk/CTk object is created)
# ---------------------------------------------------------------------------
# Without this, Windows silently scales/virtualizes the whole window on
# displays running >100% zoom (or certain resolution/scaling combos), which
# is what causes the window to be mis-sized and clipped. Declaring the
# process as per-monitor DPI aware makes Tkinter see real pixel values.


def _set_dpi_awareness():
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # per-monitor v2
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()  # older Windows fallback
        except Exception:
            pass


_set_dpi_awareness()

# customtkinter has its own automatic DPI-awareness/scaling detection built
# in. Since we already declared DPI awareness ourselves above, we need to
# tell customtkinter not to also do its own — otherwise, on any monitor
# running Windows display scaling other than 100%, the two systems fight:
# CTk widgets (buttons, panels) get scaled/positioned one way, while the
# header (a raw Tkinter Canvas that doesn't go through CTk's scaling at
# all) doesn't, and the two drift out of alignment.
try:
    ctk.deactivate_automatic_dpi_awareness()
except Exception:
    pass

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

AUTHOR_DISPLAY = "Made by bku"
VERSION = "1.0.0"

YOUTUBE_URL = "https://www.youtube.com/@bkuuuuu"
GITHUB_URL = "https://github.com/bkuwu"
PAYPAL_EMAIL = "saywhatevl@Gmail.com"

# Fonts
# These are bundled as .ttf files (see FONT_DIR/FONT_FILES below) and loaded
# as private fonts at runtime, so the user does NOT need them installed.
FONT_TITLE = "Nunito Black"
FONT_BODY = "Nunito Light"

# Fallback fonts used only if the bundled .ttf files are missing/fail to
# load, so the app still looks reasonable instead of falling back to a
# random default Tk font.
FONT_TITLE_FALLBACK = "Segoe UI Semibold" if sys.platform == "win32" else "Helvetica"
FONT_BODY_FALLBACK = "Segoe UI" if sys.platform == "win32" else "Helvetica"

FONT_DIR = "fonts"
FONT_FILES = ["Nunito-Black.ttf", "Nunito-Light.ttf"]

LOGO_MAIN_FILE = "logo_main.png"
LOGO_DARK_FILE = "logo_dark.png"
ICON_FILE = "Logo_Main.ico"

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

GRAY_900 = "#0F0F0F"
GRAY_800 = "#1C1C1C"
GRAY_700 = "#3C3C3C"
GRAY_600 = "#5A5A5A"
GRAY_500 = "#7A7A7A"
GRAY_400 = "#9B9B9B"
GRAY_300 = "#BFBFBF"
GRAY_200 = "#DCDCDC"
GRAY_100 = "#F4F4F4"
WHITE = "#FFFFFF"
BLACK = "#000000"

THEMES = {
    "light": dict(
        bg=GRAY_100,
        panel=WHITE,
        border=GRAY_200,
        border_soft="#EFEFEF",
        text_main=GRAY_900,
        text_dim=GRAY_600,
        text_dimmer=GRAY_400,
        glow_rgba=(15, 15, 15, 24),
        status_ok="#2f6f4f",
        status_bad="#8a2f2f",
        # Idle chip is a light gray; hovering inverts to a dark chip with
        # light text, so the hover is a clear reversal, not a wash-out
        # against the already-light background.
        btn_idle=GRAY_300,
        btn_hover=GRAY_900,
        btn_text=GRAY_900,
        btn_hover_text=WHITE,
    ),
    "dark": dict(
        bg=GRAY_900,
        panel=GRAY_800,
        border=GRAY_700,
        border_soft="#242424",
        text_main=GRAY_100,
        text_dim=GRAY_400,
        text_dimmer=GRAY_600,
        glow_rgba=(255, 255, 255, 30),
        status_ok="#7fe3ac",
        status_bad="#ff8a8a",
        # Idle chip is a light gray on the dark background; hovering
        # brightens it to white, which already reads as a clear highlight.
        btn_idle=GRAY_300,
        btn_hover=WHITE,
        btn_text=GRAY_900,
        btn_hover_text=GRAY_900,
    ),
}

# Fallback defaults (used only if a HoverButton is ever built without
# theme colors passed in explicitly).
BUTTON_IDLE = GRAY_300
BUTTON_HOVER = WHITE
BUTTON_TEXT = GRAY_900

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

user32 = ctypes.windll.user32


def FT(size):
    return (FONT_TITLE, size)


def FB(size):
    return (FONT_BODY, size)


# ---------------------------------------------------------------------------
# Win32 resolution switching
# ---------------------------------------------------------------------------

class DEVMODE(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", ctypes.c_wchar * 32),
        ("dmSpecVersion", ctypes.c_ushort),
        ("dmDriverVersion", ctypes.c_ushort),
        ("dmSize", ctypes.c_ushort),
        ("dmDriverExtra", ctypes.c_ushort),
        ("dmFields", ctypes.c_ulong),
        ("dmPositionX", ctypes.c_long),
        ("dmPositionY", ctypes.c_long),
        ("dmDisplayOrientation", ctypes.c_ulong),
        ("dmDisplayFixedOutput", ctypes.c_ulong),
        ("dmColor", ctypes.c_short),
        ("dmDuplex", ctypes.c_short),
        ("dmYResolution", ctypes.c_short),
        ("dmTTOption", ctypes.c_short),
        ("dmCollate", ctypes.c_short),
        ("dmFormName", ctypes.c_wchar * 32),
        ("dmLogPixels", ctypes.c_ushort),
        ("dmBitsPerPel", ctypes.c_ulong),
        ("dmPelsWidth", ctypes.c_ulong),
        ("dmPelsHeight", ctypes.c_ulong),
        ("dmDisplayFlags", ctypes.c_ulong),
        ("dmDisplayFrequency", ctypes.c_ulong),
    ]


DM_PELSWIDTH = 0x80000
DM_PELSHEIGHT = 0x100000


def set_resolution(width: int, height: int):
    devmode = DEVMODE()
    devmode.dmSize = ctypes.sizeof(DEVMODE)
    devmode.dmPelsWidth = width
    devmode.dmPelsHeight = height
    devmode.dmFields = DM_PELSWIDTH | DM_PELSHEIGHT

    result = user32.ChangeDisplaySettingsW(ctypes.byref(devmode), 0)
    if result == 0:
        return True, f"Now running {width} x {height}"
    return False, (
        "ERROR! Try running as Administrator, or that resolution isn't "
        "registered with your GPU driver yet."
    )


STRETCH_LIST = [
    ("1920x1440", 1920, 1440),
    ("1440x1080", 1440, 1080),
    ("1600x1080", 1600, 1080),
    ("1280x1080", 1280, 1080),
    ("1280x1024", 1280, 1024),
    ("1280x960", 1280, 960),
]

REVERT_LIST = [
    ("1920x1080", 1920, 1080),
    ("2560x1440", 2560, 1440),
]

SETUP_NOTES = [
    (
        "1. Disable your other monitor(s)",
        "If you run multiple monitors, open Device Manager > Monitors and "
        "disable every monitor except your main one. Skip this if you "
        "only have a single display.",
    ),
    (
        "2. Add every resolution as a custom resolution",
        "Windows can only switch to a resolution your GPU driver already "
        "knows about - SnapRes can't invent new ones on the fly. Open "
        "your graphics control panel (NVIDIA Control Panel > Display > "
        "Change Resolution > Customize > Create Custom Resolution, AMD "
        "Software > Display > Custom Resolutions > Create New, or Intel "
        "Graphics Software > Display > Custom Resolutions) and manually "
        "add each stretched resolution you plan to use. Once it's "
        "registered there, SnapRes can switch to it instantly.",
    ),
    (
        "3. Set your GPU scaling to Full Screen",
        "In the same control panel, find the scaling setting and set it "
        "to Full Screen - not Aspect Ratio, not Centered. This makes "
        "sure the stretched resolution fills the whole monitor instead "
        "of leaving black bars or a small centered image.",
    ),
    (
        "4. Set Valorant to windowed fullscreen + Fill",
        "In Valorant's video settings: Display Mode > Windowed "
        "Fullscreen, and Aspect Ratio Method > Fill. Both need to be set "
        "for the stretch to actually apply correctly.",
    ),
    (
        "5. Only switch once you're in a match",
        "Stretched resolutions only work while you're fully loaded into "
        "a game. Using SnapRes at the main menu, agent select, or the "
        "item shop will just glitch out - wait until you're actually "
        "in-game first. You don't need to keep SnapRes open after that "
        "either: once the resolution is applied in-game, you can close "
        "the app.",
    ),
]

ABOUT_SECTIONS = [
    (
        "What It Is",
        "SnapRes is a one-click resolution switcher for stretched res in "
        "Valorant. You pick a resolution, it applies instantly, done.",
    ),
    (
        "Why I Made It",
        "Honestly I just got sick of doing this manually every match. "
        "Alt-tab out, dig through Windows display settings, type in the "
        "same numbers I always use, wait for it to apply, alt-tab back "
        "in - and then undo the whole thing after the match. Multiply "
        "that by every game you play in a session and it's just "
        "annoying for no reason. So I built this to skip all of that.",
    ),
    (
        "Why It's Worth Using",
        "It's genuinely just one click now instead of a whole process. "
        "No ads, no account, no background junk running when you're not "
        "using it - it does the one thing it's supposed to do and gets "
        "out of your way. If stretched res is part of your setup, this "
        "just saves you the hassle every single game.",
    ),
]

CREDITS_TEXT = (
    "SnapRes was built and is maintained by bku.\n\n"
    "If you've got questions, suggestions, or just want to see what else "
    "is in the works, the links below are the best places to catch up."
)

SUPPORT_TEXT = (
    "SnapRes is free and always will be. If it saved you some time and "
    "you feel like tossing a couple bucks my way, my PayPal email is "
    "below - never expected, always appreciated."
)


def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


# ---------------------------------------------------------------------------
# Private (no-install) font loading
# ---------------------------------------------------------------------------
# Loads the bundled .ttf files as PRIVATE font resources: Windows makes them
# usable by this process only, for as long as it's running. Nothing gets
# written to the system font folder or registry, no admin rights needed, and
# the fonts are automatically released when the app closes.

FR_PRIVATE = 0x10
_loaded_font_paths = []


def load_bundled_fonts():
    if sys.platform != "win32":
        return
    gdi32 = ctypes.windll.gdi32
    for fname in FONT_FILES:
        path = resource_path(os.path.join(FONT_DIR, fname))
        if not os.path.isfile(path):
            continue
        added = gdi32.AddFontResourceExW(ctypes.c_wchar_p(path), FR_PRIVATE, 0)
        if added:
            _loaded_font_paths.append(path)

    if _loaded_font_paths:
        try:
            HWND_BROADCAST = 0xFFFF
            WM_FONTCHANGE = 0x001D
            ctypes.windll.user32.SendMessageW(HWND_BROADCAST, WM_FONTCHANGE, 0, 0)
        except Exception:
            pass


def _unload_bundled_fonts():
    if sys.platform != "win32":
        return
    gdi32 = ctypes.windll.gdi32
    for path in _loaded_font_paths:
        try:
            gdi32.RemoveFontResourceExW(ctypes.c_wchar_p(path), FR_PRIVATE, 0)
        except Exception:
            pass


atexit.register(_unload_bundled_fonts)


def resolve_fonts():
    """Call once a Tk root exists. Falls back to a system font if the
    bundled .ttf files didn't load for some reason (e.g. missing files),
    so the app never crashes or silently renders in the wrong font."""
    global FONT_TITLE, FONT_BODY
    try:
        available = set(tkfont.families())
    except Exception:
        return
    if FONT_TITLE not in available:
        FONT_TITLE = FONT_TITLE_FALLBACK
    if FONT_BODY not in available:
        FONT_BODY = FONT_BODY_FALLBACK


# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------

def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(c))) for c in rgb)


def _lerp_color(c1, c2, t):
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    return _rgb_to_hex((r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t))


def _ease_out(t):
    return 1 - (1 - t) ** 2


# ---------------------------------------------------------------------------
# Theme-toggle icons (drawn, not loaded from files)
# ---------------------------------------------------------------------------
# Both are rendered at 4x then downsampled with LANCZOS for clean anti-
# aliased edges, on a fully transparent canvas so they drop straight onto
# whatever background is behind the button - no chip, no re-theming needed
# later when the background changes.

def _draw_moon_icon(size, rgb):
    """Crescent moon - shown while in light mode, to switch to dark.
    Colored with the current theme's text color so it's always legible
    against the panel/background it's sitting on."""
    scale = 4
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    r = s * 0.34
    cx, cy = s * 0.52, s * 0.50
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*rgb, 255))

    # "Cut" a second, offset circle out of the first using a fully
    # transparent fill - this carves out the crescent shape.
    cut_r = r * 0.86
    cut_cx = cx + r * 0.62
    cut_cy = cy - r * 0.30
    d.ellipse(
        [cut_cx - cut_r, cut_cy - cut_r, cut_cx + cut_r, cut_cy + cut_r],
        fill=(0, 0, 0, 0),
    )

    return img.resize((size, size), Image.LANCZOS)


def _draw_glow_icon(size, rgb=(255, 255, 255)):
    """Soft glowing circle - shown while in dark mode, to switch to
    light. Reuses the same soft glow already used behind the header logo,
    so it reads as part of the app's existing visual language."""
    scale = 4
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = s / 2, s / 2

    for rad, alpha in ((0.50, 35), (0.40, 65), (0.30, 110)):
        r = s * rad
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*rgb, alpha))

    r_core = s * 0.20
    d.ellipse(
        [cx - r_core, cy - r_core, cx + r_core, cy + r_core],
        fill=(*rgb, 255),
    )

    img = img.filter(ImageFilter.GaussianBlur(s * 0.015))
    return img.resize((size, size), Image.LANCZOS)


def _scale_alpha(img, factor):
    """Scale only the alpha channel of an RGBA image by `factor` (0-1),
    leaving every RGB value untouched. Used to fade the hover halo in/out
    without any hue shift or color interpolation along the way."""
    if factor >= 0.999:
        return img
    if factor <= 0.001:
        return Image.new("RGBA", img.size, (0, 0, 0, 0))
    r, g, b, a = img.split()
    a = a.point(lambda v: int(v * factor))
    return Image.merge("RGBA", (r, g, b, a))


def _draw_halo(canvas_size, rgb, max_alpha=100):
    """Soft radial glow used behind the theme-toggle icon on hover - a
    'selected' halo. Built once at full opacity per icon color; faded in
    and out afterward purely via _scale_alpha, so the color never shifts
    mid-animation, only its strength."""
    scale = 3
    s = canvas_size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = s / 2

    steps = 24
    for i in range(steps, 0, -1):
        t = i / steps
        r = (s * 0.46) * t
        alpha = int(max_alpha * (1 - t) ** 1.6)
        if alpha <= 0:
            continue
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*rgb, alpha))

    img = img.filter(ImageFilter.GaussianBlur(s * 0.02))
    return img.resize((canvas_size, canvas_size), Image.LANCZOS)


# ---------------------------------------------------------------------------
# Hover button
# ---------------------------------------------------------------------------

class HoverButton(ctk.CTkFrame):
    def __init__(self, master, text, command,
                 width=150, height=48, corner_radius=14,
                 font=None,
                 fg_color=BUTTON_IDLE, hover_color=BUTTON_HOVER,
                 text_color=BUTTON_TEXT, hover_text_color=BUTTON_TEXT,
                 blend_color=None,
                 grow=6, steps=10, interval=12, **kwargs):
        container_w = width + grow * 2 + 10
        container_h = height + grow * 2 + 10
        blend = blend_color if blend_color else "transparent"
        super().__init__(master, width=container_w, height=container_h,
                          corner_radius=0, fg_color=blend, bg_color=blend)
        self.pack_propagate(False)
        self.grid_propagate(False)

        self._base_w, self._base_h = width, height
        self._grow, self._steps, self._interval = grow, steps, interval
        self._blend_color = blend
        self._fg, self._hover_fg = fg_color, hover_color
        self._txt, self._hover_txt = text_color, hover_text_color
        self._cur_w, self._cur_h = width, height
        self._cur_fg, self._cur_txt = fg_color, text_color
        self._hovering = False
        self._anim_job = None

        font = font or FT(13)
        self.btn = ctk.CTkButton(
            self, text=text, command=command, width=width, height=height,
            corner_radius=corner_radius, font=font,
            fg_color=fg_color, hover=False, text_color=text_color,
            border_width=0,
            **kwargs,
        )
        self.btn.place(relx=0.5, rely=0.5, anchor="center")
        self.btn.bind("<Enter>", self._on_enter)
        self.btn.bind("<Leave>", self._on_leave)
        self.btn.bind("<ButtonPress-1>", self._on_press)
        self.btn.bind("<ButtonRelease-1>", self._on_release)

    def set_blend_color(self, color):
        """Update the container's matte background so it keeps blending
        with a background that isn't static (e.g. an animated gradient)."""
        if color == self._blend_color:
            return
        self._blend_color = color
        try:
            self.configure(fg_color=color, bg_color=color)
        except Exception:
            pass

    def _on_enter(self, _e=None):
        self._hovering = True
        self._animate(self._base_w + self._grow, self._base_h + self._grow,
                       self._hover_fg, self._hover_txt)

    def _on_leave(self, _e=None):
        self._hovering = False
        self._animate(self._base_w, self._base_h, self._fg, self._txt)

    def _on_press(self, _e=None):
        w = max(self._base_w - 8, self._cur_w - 8)
        h = max(self._base_h - 8, self._cur_h - 8)
        try:
            self.btn.configure(width=w, height=h)
        except Exception:
            pass

    def _on_release(self, _e=None):
        target_w = self._base_w + self._grow if self._hovering else self._base_w
        target_h = self._base_h + self._grow if self._hovering else self._base_h
        try:
            self.btn.configure(width=target_w, height=target_h)
        except Exception:
            pass
        self._cur_w, self._cur_h = target_w, target_h

    def _animate(self, end_w, end_h, end_fg, end_txt):
        if self._anim_job:
            self.after_cancel(self._anim_job)
            self._anim_job = None
        start_w, start_h = self._cur_w, self._cur_h
        start_fg, start_txt = self._cur_fg, self._cur_txt

        def step(i=0):
            t = _ease_out(i / self._steps)
            w = int(start_w + (end_w - start_w) * t)
            h = int(start_h + (end_h - start_h) * t)
            fg = _lerp_color(start_fg, end_fg, t)
            txt = _lerp_color(start_txt, end_txt, t)
            try:
                self.btn.configure(width=w, height=h, fg_color=fg, text_color=txt)
            except Exception:
                return
            self._cur_w, self._cur_h, self._cur_fg, self._cur_txt = w, h, fg, txt
            if i < self._steps:
                self._anim_job = self.after(self._interval, lambda: step(i + 1))
            else:
                self._anim_job = None

        step()


# ---------------------------------------------------------------------------
# Icon toggle button (chip-free)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Icon toggle button (chip-free, with a real hover "select" effect)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Icon toggle button (chip-free, with a real hover "select" effect)
# ---------------------------------------------------------------------------
# Drawn directly onto the header's own Canvas via create_image/tag_bind -
# the same technique already used for the logo, glow, and the clickable
# credit line just above it. A CTkButton was tried first, but CTkButton
# renders its image through an internal child Label that fully covers the
# button; Tkinter's <Enter>/<Leave> only fire on whatever widget is
# directly under the cursor, so those events landed on that hidden child
# instead of the button we bound - the animation never ran. A single
# canvas item has no children to steal the event, so hover is reliable.

class IconToggleAnimator:
    """Owns the hover animation state for a canvas-drawn toggle icon:
    zooms the icon up and fades in a soft halo behind it. Both effects
    are pure resize / alpha-channel scaling - never color blending - so
    nothing shifts hue or flickers mid-animation."""

    def __init__(self, canvas, item_id, icon_builder, icon_rgb,
                 size=44, hover_grow=12, halo_alpha=110,
                 steps=10, interval=12):
        self.canvas = canvas
        self.item_id = item_id
        self._base_icon = size
        self._hover_icon = size + hover_grow
        self._canvas_size = int(self._hover_icon * 1.9)
        self._steps, self._interval = steps, interval
        self._t = 0.0
        self._anim_job = None
        self._photo = None  # keep a reference alive - Tk drops GC'd images

        # Both rendered once at the larger (hover) resolution - every
        # animation frame just resizes/alpha-scales these masters rather
        # than redrawing, so frames stay cheap and consistent.
        self._icon_master = icon_builder(self._hover_icon, icon_rgb)
        self._halo_master = _draw_halo(self._canvas_size, icon_rgb, max_alpha=halo_alpha)

        self.render(0.0)

    @property
    def canvas_size(self):
        return self._canvas_size

    def on_enter(self, _e=None):
        self._animate(1.0)

    def on_leave(self, _e=None):
        self._animate(0.0)

    def _animate(self, target_t):
        if self._anim_job:
            self.canvas.after_cancel(self._anim_job)
            self._anim_job = None
        start_t = self._t

        def step(i=0):
            eased = _ease_out(i / self._steps)
            self.render(start_t + (target_t - start_t) * eased)
            if i < self._steps:
                self._anim_job = self.canvas.after(self._interval, lambda: step(i + 1))
            else:
                self._anim_job = None

        step()

    def render(self, t):
        t = max(0.0, min(1.0, t))
        self._t = t

        icon_size = max(1, int(self._base_icon + (self._hover_icon - self._base_icon) * t))
        icon_frame = self._icon_master.resize((icon_size, icon_size), Image.LANCZOS)
        halo_frame = _scale_alpha(self._halo_master, t)

        composite = Image.new("RGBA", (self._canvas_size, self._canvas_size), (0, 0, 0, 0))
        composite.alpha_composite(halo_frame, (0, 0))
        off = (self._canvas_size - icon_size) // 2
        composite.alpha_composite(icon_frame, (off, off))

        self._photo = ImageTk.PhotoImage(composite)
        try:
            self.canvas.itemconfig(self.item_id, image=self._photo)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------

WIN_W, WIN_H = 704, 900

HEADER_TOP = 36
LOGO_SIZE = 66
HEADER_BLOCK_HEIGHT = 260


class ResSwitcherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.mode = "dark"

        # Now that a Tk root exists, confirm the bundled fonts actually
        # loaded; fall back cleanly if not.
        resolve_fonts()

        self.title("SnapRes")
        self.minsize(420, 480)
        self.resizable(True, True)

        self._popups = {}
        self._logo_photo = None
        self._glow_photo = None
        self._app_icon_photo = None
        self._content_frame = None

        # App icon
        try:
            self.iconbitmap(resource_path(ICON_FILE))
        except Exception:
            pass
        try:
            icon_img = Image.open(resource_path(LOGO_MAIN_FILE)).convert("RGBA")
            self._app_icon_photo = ImageTk.PhotoImage(icon_img)
            self.iconphoto(True, self._app_icon_photo)
        except Exception:
            pass

        self._center()
        self._render()

    @property
    def C(self):
        return THEMES[self.mode]

    # -- theme --------------------------------------------------------------

    def _toggle_theme(self):
        self.mode = "dark" if self.mode == "light" else "light"
        ctk.set_appearance_mode(self.mode)

        # Close open popups
        for win in list(self._popups.values()):
            try:
                if win.winfo_exists():
                    win.destroy()
            except Exception:
                pass
        self._popups = {}

        self._render()

    def _render(self):
        C = self.C
        self.configure(fg_color=C["bg"])

        if self._content_frame is not None:
            try:
                self._content_frame.destroy()
            except Exception:
                pass
            self._content_frame = None

        self._build_content_frame()

    # -- layout -----------------------------------------------------------

    def _center(self):
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        # Leave room for the taskbar / window chrome so the window never
        # opens taller/wider than what's actually usable on screen. The
        # content lives inside a CTkScrollableFrame, so shrinking the
        # window just makes it scroll instead of clipping.
        margin_w, margin_h = 40, 90

        win_w = min(WIN_W, max(360, screen_w - margin_w))
        win_h = min(WIN_H, max(420, screen_h - margin_h))

        x = max(0, (screen_w - win_w) // 2)
        y = max(0, (screen_h - win_h) // 2)
        self.geometry(f"{win_w}x{win_h}+{x}+{y}")

    def _center_toplevel(self, win, w, h):
        self.update_idletasks()
        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

    def _build_header(self, parent):
        C = self.C
        c = tk.Canvas(
            parent, width=WIN_W - 4, height=HEADER_BLOCK_HEIGHT,
            highlightthickness=0, bd=0, bg=C["bg"],
        )
        c.pack(fill="x")
        self._header_canvas = c

        # Negative size = pixels, not points. Points auto-scale with Windows
        # display zoom (that's what was causing the text to balloon and
        # collide at 125%/150%/172% zoom); pixels stay a fixed, predictable
        # size no matter the zoom level, matching the rest of the UI.
        title_font = tkfont.Font(family=FONT_TITLE, size=-38)
        credit_font = tkfont.Font(family=FONT_TITLE, size=-16)
        subtitle_font = tkfont.Font(family=FONT_BODY, size=-13)
        setup_label_font = tkfont.Font(family=FONT_TITLE, size=-11)

        title_text = "SnapRes"
        credit_text = AUTHOR_DISPLAY
        subtitle_text = "Instant Resolution Switching For Stretched Res"

        title_w = title_font.measure(title_text)
        credit_w = credit_font.measure(credit_text)
        text_block_w = max(title_w, credit_w)
        gap = 18
        group_w = LOGO_SIZE + gap + text_block_w
        group_x0 = (WIN_W - group_w) / 2

        logo_cx = group_x0 + LOGO_SIZE / 2
        logo_cy = HEADER_TOP + LOGO_SIZE / 2
        text_x = group_x0 + LOGO_SIZE + gap
        title_y = HEADER_TOP + LOGO_SIZE * 0.30
        credit_y = title_y + 50

        # Glow
        glow_w, glow_h = int(group_w + 130), 150
        glow_img = Image.new("RGBA", (glow_w, glow_h), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow_img)
        gd.ellipse(
            [glow_w * 0.08, glow_h * 0.10, glow_w * 0.92, glow_h * 0.90],
            fill=C["glow_rgba"],
        )
        glow_img = glow_img.filter(ImageFilter.GaussianBlur(28))
        self._glow_photo = ImageTk.PhotoImage(glow_img)
        c.create_image(
            WIN_W / 2, logo_cy + 6, image=self._glow_photo, anchor="center", tags="header",
        )

        # Logo
        logo_file = LOGO_MAIN_FILE if self.mode == "light" else LOGO_DARK_FILE
        try:
            pil_logo = Image.open(resource_path(logo_file)).convert("RGBA")
            pil_logo = pil_logo.resize((LOGO_SIZE, LOGO_SIZE), Image.LANCZOS)
            self._logo_photo = ImageTk.PhotoImage(pil_logo)
            c.create_image(logo_cx, logo_cy, image=self._logo_photo, anchor="center", tags="header")
        except Exception:
            pass

        # Title
        c.create_text(
            text_x + 1, title_y + 1, text=title_text, anchor="w",
            font=title_font, fill=C["border"], tags="header",
        )
        c.create_text(
            text_x, title_y, text=title_text, anchor="w",
            font=title_font, fill=C["text_main"], tags="header",
        )

        # Credit line
        credit_id = c.create_text(
            text_x, credit_y, text=credit_text, anchor="w",
            font=credit_font, fill=C["text_dim"], tags="header",
        )
        c.tag_bind(credit_id, "<Button-1>", lambda e: webbrowser.open(YOUTUBE_URL))
        c.tag_bind(credit_id, "<Enter>", lambda e: c.config(cursor="hand2"))
        c.tag_bind(credit_id, "<Leave>", lambda e: c.config(cursor=""))

        # Subtitle
        subtitle_y = HEADER_TOP + LOGO_SIZE + 32
        c.create_text(
            WIN_W / 2, subtitle_y, text=subtitle_text, anchor="center",
            font=subtitle_font, fill=C["text_dim"], tags="header",
        )

        # Setup button
        setup_label_y = subtitle_y + 42
        c.create_text(
            WIN_W / 2, setup_label_y, text="BEFORE YOU SWITCH",
            anchor="center", font=setup_label_font, fill=C["text_dimmer"], tags="header",
        )

        setup_btn = HoverButton(
            c, text="Setup", command=self.show_setup,
            width=128, height=38, corner_radius=11, font=FT(12),
            fg_color=C["btn_idle"], hover_color=C["btn_hover"],
            text_color=C["btn_text"], hover_text_color=C["btn_hover_text"],
            blend_color=C["bg"], grow=5,
        )
        c.create_window(WIN_W / 2, setup_label_y + 46, window=setup_btn, anchor="center", tags="header")

        # Theme toggle - a moon while in light mode (switches to dark), a
        # glowing circle while in dark mode (switches to light). Drawn
        # straight on this canvas (like the logo/glow above), so hover
        # zoom + halo glow reliably fires instead of getting swallowed by
        # a child widget.
        icon_size = 40
        if self.mode == "light":
            icon_builder = _draw_moon_icon
            icon_rgb = _hex_to_rgb(C["text_main"])
        else:
            icon_builder = _draw_glow_icon
            icon_rgb = (255, 255, 255)

        toggle_item = c.create_image(20, 20, anchor="nw", tags="header")
        toggle_anim = IconToggleAnimator(
            c, toggle_item, icon_builder, icon_rgb,
            size=icon_size, hover_grow=12, halo_alpha=110,
        )
        self._theme_toggle_anim = toggle_anim  # keep alive - holds the PhotoImage refs

        def _toggle_enter(_e):
            c.config(cursor="hand2")
            toggle_anim.on_enter()

        def _toggle_leave(_e):
            c.config(cursor="")
            toggle_anim.on_leave()

        c.tag_bind(toggle_item, "<Enter>", _toggle_enter)
        c.tag_bind(toggle_item, "<Leave>", _toggle_leave)
        c.tag_bind(toggle_item, "<Button-1>", lambda e: self._toggle_theme())

    def _build_content_frame(self):
        C = self.C
        frame = ctk.CTkScrollableFrame(
            self,
            fg_color=C["bg"],
            scrollbar_fg_color=C["border"],
            scrollbar_button_color=C["text_dim"],
            scrollbar_button_hover_color=C["text_main"],
        )
        frame.pack(fill="both", expand=True)
        try:
            frame._scrollbar.configure(width=18, corner_radius=8)
        except Exception:
            pass
        self._content_frame = frame

        # Everything below is built inside a fixed-design-width "page"
        # column, which sits in the middle of a 3-column grid with equal
        # weight spacer columns on either side. That keeps the whole UI
        # locked to its intended width and perfectly centered no matter
        # how wide the window gets (maximized, ultrawide, etc.) instead of
        # panels stretching edge-to-edge while their content stays drawn
        # at the old, narrower center point.
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)
        frame.grid_columnconfigure(2, weight=1)

        page = ctk.CTkFrame(frame, fg_color="transparent")
        page.grid(row=0, column=1, sticky="n")
        self._page = page

        self._build_header(page)
        self._first_panel = self._build_resolution_grid(page)
        self._build_status(page)
        self._build_custom_row(page)
        self._build_footer(page)

    def _build_res_panel(self, parent, title, res_list, cols=3, top_pad=0):
        C = self.C
        panel = ctk.CTkFrame(
            parent, fg_color=C["panel"], corner_radius=22,
            border_width=1, border_color=C["border"],
        )
        panel.pack(padx=26, pady=(top_pad, 18), fill="x")

        ctk.CTkLabel(
            panel, text=title, font=FT(11), text_color=C["text_dim"],
        ).pack(anchor="w", padx=22, pady=(20, 12))

        grid = ctk.CTkFrame(panel, fg_color="transparent")
        grid.pack(padx=10, pady=(0, 20))

        for i, (label, width, height) in enumerate(res_list):
            r, c = divmod(i, cols)
            HoverButton(
                grid, text=label, width=165, height=52,
                corner_radius=14, font=FT(13),
                fg_color=C["btn_idle"], hover_color=C["btn_hover"],
                text_color=C["btn_text"], hover_text_color=C["btn_hover_text"],
                blend_color=C["panel"], grow=6,
                command=lambda w=width, h=height: self.apply_resolution(w, h),
            ).grid(row=r, column=c, padx=9, pady=9)

        return panel

    def _build_resolution_grid(self, parent):
        first = self._build_res_panel(
            parent, "TRUE STRETCH RESOLUTIONS", STRETCH_LIST,
            cols=3, top_pad=18,
        )
        self._build_res_panel(
            parent, "REVERT BACK", REVERT_LIST,
            cols=2, top_pad=0,
        )
        return first

    def _build_custom_row(self, parent):
        C = self.C
        panel = ctk.CTkFrame(
            parent, fg_color=C["panel"], corner_radius=22,
            border_width=1, border_color=C["border"],
        )
        panel.pack(padx=26, pady=(0, 18), fill="x")

        ctk.CTkLabel(
            panel, text="CUSTOM RESOLUTION", font=FT(11), text_color=C["text_dim"],
        ).pack(anchor="w", padx=22, pady=(20, 12))

        row = ctk.CTkFrame(panel, fg_color="transparent")
        row.pack(padx=22, pady=(0, 20), fill="x")

        self.custom_entry = ctk.CTkEntry(
            row, placeholder_text="1280x1080", height=48,
            corner_radius=14, fg_color=C["bg"], border_width=1,
            border_color=C["border"], text_color=C["text_main"], font=FB(13),
        )
        self.custom_entry.pack(side="left", fill="x", expand=True)
        self.custom_entry.bind("<Return>", lambda e: self.apply_custom())

        HoverButton(
            row, text="Apply", command=self.apply_custom,
            width=92, height=48, corner_radius=14, font=FT(13),
            fg_color=C["btn_idle"], hover_color=C["btn_hover"],
            text_color=C["btn_text"], hover_text_color=C["btn_hover_text"],
            blend_color=C["panel"], grow=4,
        ).pack(side="left", padx=(12, 0))

    def _build_status(self, parent):
        C = self.C
        self._status_after_id = None
        self.status_panel = ctk.CTkFrame(
            parent, fg_color=C["panel"], corner_radius=16,
            border_width=1, border_color=C["border"],
        )
        # Not packed yet — it only appears when there's something to show.

        self.status_var = ctk.StringVar(value="")
        self.status_label = ctk.CTkLabel(
            self.status_panel, textvariable=self.status_var, font=FB(13),
            text_color=C["status_ok"], wraplength=WIN_W - 122, justify="center",
        )
        self.status_label.pack(padx=16, pady=12)

    def _show_status(self, msg, ok=True):
        C = self.C
        color = C["status_ok"] if ok else C["status_bad"]
        try:
            self.status_label.configure(text_color=color)
            self.status_panel.configure(border_color=color)
        except Exception:
            return
        self.status_var.set(msg)

        if not self.status_panel.winfo_ismapped():
            self.status_panel.pack(
                before=self._first_panel, padx=26, pady=(10, 6), fill="x",
            )

        if self._status_after_id is not None:
            try:
                self.after_cancel(self._status_after_id)
            except Exception:
                pass
        self._status_after_id = self.after(10000, self._hide_status)

    def _hide_status(self):
        self._status_after_id = None
        try:
            self.status_panel.pack_forget()
        except Exception:
            pass
        self.status_var.set("")

    def _build_footer(self, parent):
        C = self.C
        separator = ctk.CTkFrame(parent, height=2, corner_radius=0, fg_color=C["border"])
        separator.pack(fill="x", padx=26, pady=(8, 0))

        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.pack(pady=26)

        for label, cmd in [
            ("Credits", self.show_credits),
            ("About", self.show_about),
        ]:
            HoverButton(
                footer, text=label, command=cmd,
                width=108, height=38, corner_radius=11, font=FT(12),
                fg_color=C["btn_idle"], hover_color=C["btn_hover"],
                text_color=C["btn_text"], hover_text_color=C["btn_hover_text"],
                blend_color=C["bg"], grow=5,
            ).pack(side="left", padx=6)

    # -- actions --------------------------------------------------------

    def apply_resolution(self, width, height):
        ok, msg = set_resolution(width, height)
        self._show_status(msg, ok)

    def apply_custom(self):
        text = self.custom_entry.get().strip()
        match = re.match(r"^(\d{2,5})\s*[x, ]\s*(\d{2,5})$", text)
        if not match:
            self._show_status("ERROR! Format like 1280x1080", ok=False)
            return
        self.apply_resolution(int(match.group(1)), int(match.group(2)))

    # -- popups -----------------------------------------------------------

    def _open_singleton(self, key, build_fn):
        existing = self._popups.get(key)
        if existing is not None and existing.winfo_exists():
            existing.lift()
            existing.focus_force()
            return
        win = build_fn()
        self._popups[key] = win

    def _themed_popup(self, title, w, h):
        C = self.C
        win = ctk.CTkToplevel(self)
        win.title(title)
        win.resizable(False, False)
        win.configure(fg_color=C["bg"])
        win.transient(self)
        self._center_toplevel(win, w, h)
        return win

    def show_setup(self):
        C = self.C

        def build():
            w = 520
            win = self._themed_popup("Setup", w, 700)
            wrap_len = w - 90

            ctk.CTkLabel(
                win, text="Before You Switch", font=FT(21),
                text_color=C["text_main"],
            ).pack(pady=(24, 6), padx=24, anchor="w")
            ctk.CTkLabel(
                win, text="A few things need to be set up for stretched res "
                          "to actually work in-game.",
                font=FB(12), text_color=C["text_dim"], wraplength=wrap_len, justify="left",
            ).pack(padx=24, anchor="w", pady=(0, 14))

            scroll = ctk.CTkScrollableFrame(
                win, fg_color="transparent",
                scrollbar_fg_color=C["border"],
                scrollbar_button_color=C["text_dim"],
                scrollbar_button_hover_color=C["text_main"],
            )
            scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            try:
                scroll._scrollbar.configure(width=18, corner_radius=8)
            except Exception:
                pass

            for i, (q, a) in enumerate(SETUP_NOTES):
                card = ctk.CTkFrame(
                    scroll, fg_color=C["panel"], corner_radius=16,
                    border_width=1, border_color=C["border"],
                )
                card.pack(fill="x", pady=(0 if i == 0 else 12, 0))
                ctk.CTkLabel(
                    card, text=q, font=FT(13), text_color=C["text_main"],
                    wraplength=wrap_len - 34, justify="left",
                ).pack(anchor="w", padx=18, pady=(16, 6), fill="x")
                ctk.CTkLabel(
                    card, text=a, font=FB(12), text_color=C["text_dim"],
                    wraplength=wrap_len - 34, justify="left",
                ).pack(anchor="w", padx=18, pady=(0, 16), fill="x")
            return win

        self._open_singleton("setup", build)

    def show_about(self):
        C = self.C

        def build():
            w = 500
            win = self._themed_popup("About", w, 580)
            wrap_len = w - 88

            ctk.CTkLabel(
                win, text="About SnapRes", font=FT(20), text_color=C["text_main"],
            ).pack(pady=(26, 14), padx=24, anchor="w")

            for i, (heading, body) in enumerate(ABOUT_SECTIONS):
                ctk.CTkLabel(
                    win, text=heading, font=FT(14), text_color=C["text_main"],
                ).pack(padx=24, pady=(14 if i else 0, 6), anchor="w")
                ctk.CTkLabel(
                    win, text=body, font=FB(12), text_color=C["text_dim"],
                    wraplength=wrap_len, justify="left",
                ).pack(padx=24, anchor="w")

            ctk.CTkFrame(win, height=20, fg_color="transparent").pack()
            return win

        self._open_singleton("about", build)

    def show_credits(self):
        C = self.C

        def build():
            w = 480
            win = self._themed_popup("Credits", w, 520)
            wrap_len = w - 70

            ctk.CTkLabel(
                win, text="Credits", font=FT(20), text_color=C["text_main"],
            ).pack(pady=(26, 14), padx=24, anchor="w")

            ctk.CTkLabel(
                win, text=CREDITS_TEXT, font=FB(12), text_color=C["text_dim"],
                wraplength=wrap_len, justify="left",
            ).pack(padx=24, anchor="w")

            links_row = ctk.CTkFrame(win, fg_color="transparent")
            links_row.pack(pady=(18, 6), padx=24, anchor="w")
            HoverButton(
                links_row, text="YouTube", command=lambda: webbrowser.open(YOUTUBE_URL),
                width=110, height=40, corner_radius=12, font=FT(12),
                fg_color=C["btn_idle"], hover_color=C["btn_hover"],
                text_color=C["btn_text"], hover_text_color=C["btn_hover_text"],
                blend_color=C["bg"], grow=4,
            ).pack(side="left", padx=(0, 10))
            HoverButton(
                links_row, text="GitHub", command=lambda: webbrowser.open(GITHUB_URL),
                width=110, height=40, corner_radius=12, font=FT(12),
                fg_color=C["btn_idle"], hover_color=C["btn_hover"],
                text_color=C["btn_text"], hover_text_color=C["btn_hover_text"],
                blend_color=C["bg"], grow=4,
            ).pack(side="left")

            support = ctk.CTkFrame(
                win, fg_color=C["panel"], corner_radius=16,
                border_width=1, border_color=C["border"],
            )
            support.pack(fill="x", padx=24, pady=(22, 24))

            ctk.CTkLabel(
                support, text=SUPPORT_TEXT, font=FB(12), text_color=C["text_dim"],
                wraplength=wrap_len - 36, justify="left",
            ).pack(anchor="w", padx=18, pady=(16, 10))

            email_label = ctk.CTkLabel(
                support, text=PAYPAL_EMAIL, font=FT(14),
                text_color=C["text_main"], cursor="hand2",
            )
            email_label.pack(anchor="w", padx=18, pady=(0, 16))
            email_label.bind(
                "<Button-1>", lambda e: webbrowser.open(f"mailto:{PAYPAL_EMAIL}")
            )
            return win

        self._open_singleton("credits", build)


if __name__ == "__main__":
    if sys.platform != "win32":
        messagebox.showerror("Unsupported", "This tool only works on Windows.")
        sys.exit(1)
    load_bundled_fonts()
    app = ResSwitcherApp()
    app.mainloop()
