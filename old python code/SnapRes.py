import os
import re
import sys
import json
import atexit
import ctypes
import tkinter as tk
import tkinter.font as tkfont
import webbrowser

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageColor


def _set_dpi_awareness():
    if sys.platform != "win32":
        return
    print("SnapRes: setting DPI awareness...", flush=True)
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass
    print("SnapRes: DPI awareness done.", flush=True)


_set_dpi_awareness()

try:
    ctk.deactivate_automatic_dpi_awareness()
except Exception:
    pass


AUTHOR_DISPLAY = "Made by bku"

YOUTUBE_URL = "https://www.youtube.com/@bkuuuuu"
DISCORD_URL = "https://discord.gg/MzX9wJ6Tyf"
GITHUB_URL = "https://github.com/bkuwu"
PAYPAL_EMAIL = "saywhatevl@Gmail.com"

FONT_TITLE = "Nunito Black"
FONT_BODY = "Nunito Light"

FONT_TITLE_FALLBACK = "Segoe UI Semibold" if sys.platform == "win32" else "Helvetica"
FONT_BODY_FALLBACK = "Segoe UI" if sys.platform == "win32" else "Helvetica"

FONT_DIR = "fonts"
FONT_FILES = ["Nunito-Black.ttf", "Nunito-Light.ttf"]

LOGO_MAIN_FILE = "logo_main.png"
LOGO_DARK_FILE = "logo_dark.png"
ICON_FILE = "Logo_Main.ico"

BRAND_ICON_DIR = "icons"
BRAND_ICON_FILES = {
    "youtube": "youtube.png",
    "discord": "discord.png",
    "github": "github.png",
}


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
        btn_idle=GRAY_300,
        btn_hover=WHITE,
        btn_text=GRAY_900,
        btn_hover_text=GRAY_900,
    ),
}

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
    ("1568x1080", 1568, 1080),
]

REVERT_LIST = [
    ("1920x1080", 1920, 1080),
    ("2560x1440", 2560, 1440),
    ("3840x2160", 3840, 2160),
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


_brand_icon_cache = {}


def load_brand_icon(name, color, size=16):
    key = (name, color, size)
    cached = _brand_icon_cache.get(key)
    if cached is not None:
        return cached
    fname = BRAND_ICON_FILES.get(name)
    if not fname:
        return None
    path = resource_path(os.path.join(BRAND_ICON_DIR, fname))
    if not os.path.isfile(path):
        return None
    try:
        raw = Image.open(path).convert("RGBA")
        render_size = size * 4
        base = raw.resize((render_size, render_size), Image.LANCZOS, reducing_gap=3.0)
        r, g, b = ImageColor.getrgb(color)
        solid = Image.new("RGBA", base.size, (r, g, b, 255))
        alpha = base.split()[3].point(lambda a: 255 if a >= 128 else 0)
        alpha = alpha.filter(ImageFilter.GaussianBlur(render_size * 0.006))
        solid.putalpha(alpha)
        solid = solid.resize((size, size), Image.LANCZOS, reducing_gap=3.0)
        img = ctk.CTkImage(light_image=solid, dark_image=solid, size=(size, size))
    except Exception:
        return None
    _brand_icon_cache[key] = img
    return img


PROFILES_FILE = "profiles.json"


def _profiles_file_path():
    base = os.environ.get("APPDATA")
    if not base:
        base = os.path.dirname(os.path.abspath(sys.argv[0]))
    folder = os.path.join(base, "SnapRes")
    try:
        os.makedirs(folder, exist_ok=True)
    except Exception:
        pass
    return os.path.join(folder, PROFILES_FILE)


def load_profiles():
    path = _profiles_file_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []

    cleaned = []
    try:
        for item in data:
            width, height = int(item["width"]), int(item["height"])
            cleaned.append({"label": f"{width}x{height}", "width": width, "height": height})
    except Exception:
        return []
    return cleaned


def save_profiles(profiles):
    path = _profiles_file_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                [{"width": p["width"], "height": p["height"]} for p in profiles],
                f,
            )
    except Exception:
        pass


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
            SMTO_ABORTIFHUNG = 0x0002
            SMTO_NORMAL = 0x0000
            result = ctypes.c_ulong()
            ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST, WM_FONTCHANGE, 0, 0,
                SMTO_ABORTIFHUNG | SMTO_NORMAL, 1000, ctypes.byref(result),
            )
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
    global FONT_TITLE, FONT_BODY
    try:
        available = set(tkfont.families())
    except Exception:
        return
    if FONT_TITLE not in available:
        FONT_TITLE = FONT_TITLE_FALLBACK
    if FONT_BODY not in available:
        FONT_BODY = FONT_BODY_FALLBACK


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


def _draw_moon_icon(size, rgb):
    scale = 4
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    r = s * 0.34
    cx, cy = s * 0.52, s * 0.50
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*rgb, 255))

    cut_r = r * 0.86
    cut_cx = cx + r * 0.62
    cut_cy = cy - r * 0.30
    d.ellipse(
        [cut_cx - cut_r, cut_cy - cut_r, cut_cx + cut_r, cut_cy + cut_r],
        fill=(0, 0, 0, 0),
    )

    return img.resize((size, size), Image.LANCZOS)


def _draw_glow_icon(size, rgb=(255, 255, 255)):
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


def _draw_broom_icon(size, rgb):
    scale = 4
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lw = max(2, int(s * 0.09))

    handle_top = (s * 0.30, s * 0.06)
    handle_bottom = (s * 0.60, s * 0.50)
    d.line([handle_top, handle_bottom], fill=(*rgb, 255), width=lw, joint="curve")

    d.line(
        [(s * 0.42, s * 0.48), (s * 0.80, s * 0.48)],
        fill=(*rgb, 255), width=lw, joint="curve",
    )

    bristle_top_xs = [s * 0.46, s * 0.56, s * 0.66, s * 0.76]
    bristle_base_xs = [s * 0.30, s * 0.52, s * 0.74, s * 0.94]
    bristle_w = max(2, int(lw * 0.7))
    for tx, bx in zip(bristle_top_xs, bristle_base_xs):
        d.line(
            [(tx, s * 0.50), (bx, s * 0.90)],
            fill=(*rgb, 255), width=bristle_w,
        )

    return img.resize((size, size), Image.LANCZOS)


def _scale_alpha(img, factor):
    if factor >= 0.999:
        return img
    if factor <= 0.001:
        return Image.new("RGBA", img.size, (0, 0, 0, 0))
    r, g, b, a = img.split()
    a = a.point(lambda v: int(v * factor))
    return Image.merge("RGBA", (r, g, b, a))


def _draw_halo(canvas_size, rgb, max_alpha=100):
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


class HoverButton(ctk.CTkFrame):
    RING_HOVER_COLOR = WHITE

    def __init__(self, master, text, command,
                 width=150, height=48, corner_radius=14,
                 font=None,
                 fg_color=BUTTON_IDLE, hover_color=BUTTON_HOVER,
                 text_color=BUTTON_TEXT, hover_text_color=BUTTON_TEXT,
                 blend_color=None,
                 border_width=2, ring_color=None, ring_hover_color=None,
                 grow=6, steps=10, interval=12, icon=None, icon_size=16, **kwargs):
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
        self._border_width = border_width
        self._ring = ring_color or _lerp_color(fg_color, BLACK, 0.15)
        self._hover_ring = ring_hover_color or self.RING_HOVER_COLOR
        self._cur_w, self._cur_h = width, height
        self._cur_fg, self._cur_txt = fg_color, text_color
        self._cur_ring = self._ring
        self._hovering = False
        self._anim_job = None

        self._icon_idle_img = load_brand_icon(icon, text_color, icon_size) if icon else None
        self._icon_hover_img = load_brand_icon(icon, hover_text_color, icon_size) if icon else None

        font = font or FT(13)
        btn_kwargs = dict(
            text=text, command=command, width=width, height=height,
            corner_radius=corner_radius, font=font,
            fg_color=fg_color, hover=False, text_color=text_color,
            border_width=border_width, border_color=self._ring,
        )
        if self._icon_idle_img:
            btn_kwargs["image"] = self._icon_idle_img
            btn_kwargs["compound"] = "left"
        btn_kwargs.update(kwargs)
        self.btn = ctk.CTkButton(self, **btn_kwargs)
        self.btn.place(relx=0.5, rely=0.5, anchor="center")
        self.btn.bind("<Enter>", self._on_enter)
        self.btn.bind("<Leave>", self._on_leave)
        self.btn.bind("<ButtonPress-1>", self._on_press)
        self.btn.bind("<ButtonRelease-1>", self._on_release)

    def set_blend_color(self, color):
        if color == self._blend_color:
            return
        self._blend_color = color
        try:
            self.configure(fg_color=color, bg_color=color)
        except Exception:
            pass

    def _on_enter(self, _e=None):
        self._hovering = True
        self._set_ring(self._hover_ring)
        if self._icon_hover_img:
            try:
                self.btn.configure(image=self._icon_hover_img)
            except Exception:
                pass
        self._animate(self._base_w + self._grow, self._base_h + self._grow,
                       self._hover_fg, self._hover_txt)

    def _on_leave(self, _e=None):
        self._hovering = False
        self._set_ring(self._ring)
        if self._icon_idle_img:
            try:
                self.btn.configure(image=self._icon_idle_img)
            except Exception:
                pass
        self._animate(self._base_w, self._base_h, self._fg, self._txt)

    def _set_ring(self, color):
        self._cur_ring = color
        try:
            self.btn.configure(border_color=color)
        except Exception:
            pass

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
            self._cur_w, self._cur_h = w, h
            self._cur_fg, self._cur_txt = fg, txt
            if i < self._steps:
                self._anim_job = self.after(self._interval, lambda: step(i + 1))
            else:
                self._anim_job = None

        step()


class IconToggleAnimator:

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
        self._photo = None

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


WIN_W, WIN_H = 704, 900

HEADER_TOP = 36
LOGO_SIZE = 66
HEADER_BLOCK_HEIGHT = 260

SCROLLBAR_IDLE_WIDTH = 4
SCROLLBAR_HOVER_WIDTH = 16


class ResSwitcherApp(ctk.CTk):
    def __init__(self):
        print("SnapRes:   Tk root init...", flush=True)
        super().__init__()
        print("SnapRes:   Tk root created.", flush=True)

        self.mode = "dark"

        print("SnapRes:   resolving fonts...", flush=True)
        resolve_fonts()
        print("SnapRes:   fonts resolved.", flush=True)

        self.title("SnapRes")
        self.minsize(420, 480)
        self.resizable(True, True)

        self._popups = {}
        self._logo_photo = None
        self._glow_photo = None
        self._app_icon_photo = None
        self._clear_icon_photo = None
        self._content_frame = None
        self._version_label = None
        self._version_bar = None

        self.profiles = load_profiles()

        print("SnapRes:   loading icon...", flush=True)
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
        print("SnapRes:   icon done.", flush=True)

        print("SnapRes:   centering window...", flush=True)
        self._center()
        print("SnapRes:   centered, rendering UI...", flush=True)
        self._render()
        print("SnapRes:   UI rendered.", flush=True)

    @property
    def C(self):
        return THEMES[self.mode]


    def _toggle_theme(self):
        self.mode = "dark" if self.mode == "light" else "light"
        ctk.set_appearance_mode(self.mode)

        self._close_clear_popup()

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

        self._build_version_label()
        self._build_content_frame()

    def _build_version_label(self):
        C = self.C
        if self._version_label is None:
            bar = ctk.CTkFrame(self, fg_color="transparent", height=22)
            bar.pack(side="bottom", fill="x")
            bar.pack_propagate(False)
            label = ctk.CTkLabel(
                bar, text=f"v{VERSION}", font=FB(10), text_color=C["text_dimmer"],
            )
            label.pack(side="left", padx=12, pady=(0, 4))
            self._version_bar = bar
            self._version_label = label
        else:
            self._version_label.configure(text=f"v{VERSION}", text_color=C["text_dimmer"])


    def _center(self):
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

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

        logo_file = LOGO_MAIN_FILE if self.mode == "light" else LOGO_DARK_FILE
        try:
            pil_logo = Image.open(resource_path(logo_file)).convert("RGBA")
            pil_logo = pil_logo.resize((LOGO_SIZE, LOGO_SIZE), Image.LANCZOS)
            self._logo_photo = ImageTk.PhotoImage(pil_logo)
            c.create_image(logo_cx, logo_cy, image=self._logo_photo, anchor="center", tags="header")
        except Exception:
            pass

        c.create_text(
            text_x + 1, title_y + 1, text=title_text, anchor="w",
            font=title_font, fill=C["border"], tags="header",
        )
        c.create_text(
            text_x, title_y, text=title_text, anchor="w",
            font=title_font, fill=C["text_main"], tags="header",
        )

        credit_id = c.create_text(
            text_x, credit_y, text=credit_text, anchor="w",
            font=credit_font, fill=C["text_dim"], tags="header",
        )
        c.tag_bind(credit_id, "<Button-1>", lambda e: webbrowser.open(YOUTUBE_URL))
        c.tag_bind(credit_id, "<Enter>", lambda e: c.config(cursor="hand2"))
        c.tag_bind(credit_id, "<Leave>", lambda e: c.config(cursor=""))

        subtitle_y = HEADER_TOP + LOGO_SIZE + 32
        c.create_text(
            WIN_W / 2, subtitle_y, text=subtitle_text, anchor="center",
            font=subtitle_font, fill=C["text_dim"], tags="header",
        )

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
        self._theme_toggle_anim = toggle_anim

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
        self._content_frame = frame

        self._scrollbar = getattr(frame, "_scrollbar", None)
        self._wire_autohide_scrollbar(self._scrollbar)

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
        self._build_custom_status(page)
        self._build_custom_error(page)
        self._build_profiles_panel(page)
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
        self._fill_res_grid(grid, res_list, cols)

        return panel

    def _fill_res_grid(self, grid, res_list, cols, command=None):
        C = self.C
        total = len(res_list)
        full_rows, remainder = divmod(total, cols)

        for i, (label, width, height) in enumerate(res_list):
            r, c = divmod(i, cols)
            if r == full_rows and remainder:
                c += (cols - remainder) // 2
            HoverButton(
                grid, text=label, width=165, height=52,
                corner_radius=14, font=FT(13),
                fg_color=C["btn_idle"], hover_color=C["btn_hover"],
                text_color=C["btn_text"], hover_text_color=C["btn_hover_text"],
                blend_color=C["panel"], grow=6,
                command=lambda w=width, h=height: (command or self.apply_resolution)(w, h),
            ).grid(row=r, column=c, padx=9, pady=9)

    def _build_resolution_grid(self, parent):
        first = self._build_res_panel(
            parent, "TRUE STRETCH RESOLUTIONS", STRETCH_LIST,
            cols=3, top_pad=18,
        )
        self._build_res_panel(
            parent, "REVERT BACK", REVERT_LIST,
            cols=3, top_pad=0,
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

        self._custom_row_panel = panel

        self.custom_entry = ctk.CTkEntry(
            row, placeholder_text="1280x1080", height=48,
            corner_radius=14, fg_color=C["bg"], border_width=1,
            border_color=C["border"], text_color=C["text_main"], font=FB(13),
        )
        self.custom_entry.pack(side="left", fill="x", expand=True)
        self.custom_entry.bind("<Return>", lambda e: self.apply_custom())
        self.custom_entry.bind("<KeyRelease>", self._on_custom_entry_changed)

        HoverButton(
            row, text="Apply", command=self.apply_custom,
            width=92, height=48, corner_radius=14, font=FT(13),
            fg_color=C["btn_idle"], hover_color=C["btn_hover"],
            text_color=C["btn_text"], hover_text_color=C["btn_hover_text"],
            blend_color=C["panel"], grow=4,
        ).pack(side="left", padx=(12, 0))

        self.save_profile_btn = HoverButton(
            row, text="Save Profile", command=self.save_profile,
            width=118, height=48, corner_radius=14, font=FT(13),
            fg_color=C["btn_idle"], hover_color=C["btn_hover"],
            text_color=C["btn_text"], hover_text_color=C["btn_hover_text"],
            blend_color=C["panel"], grow=4,
        )

    def _build_custom_status(self, parent):
        C = self.C
        self._custom_status_after_id = None
        self.custom_status_panel = ctk.CTkFrame(
            parent, fg_color=C["panel"], corner_radius=16,
            border_width=1, border_color=C["border"],
        )

        self.custom_status_var = ctk.StringVar(value="")
        self.custom_status_label = ctk.CTkLabel(
            self.custom_status_panel, textvariable=self.custom_status_var,
            font=FB(13), text_color=C["status_ok"],
            wraplength=WIN_W - 122, justify="center",
        )
        self.custom_status_label.pack(padx=16, pady=12)

    def _show_custom_status(self, msg, ok=True):
        C = self.C
        color = C["status_ok"] if ok else C["status_bad"]
        try:
            self.custom_status_label.configure(text_color=color)
            self.custom_status_panel.configure(border_color=color)
        except Exception:
            return
        self.custom_status_var.set(msg)

        if not self.custom_status_panel.winfo_ismapped():
            self.custom_status_panel.pack(
                before=self._custom_row_panel, padx=26, pady=(0, 18), fill="x",
            )

        if self._custom_status_after_id is not None:
            try:
                self.after_cancel(self._custom_status_after_id)
            except Exception:
                pass
        self._custom_status_after_id = self.after(10000, self._hide_custom_status)

    def _hide_custom_status(self):
        self._custom_status_after_id = None
        try:
            self.custom_status_panel.pack_forget()
        except Exception:
            pass
        self.custom_status_var.set("")

    def _on_custom_entry_changed(self, _e=None):
        text = self.custom_entry.get().strip()
        if text:
            if not self.save_profile_btn.winfo_ismapped():
                self.save_profile_btn.pack(side="left", padx=(12, 0))
        else:
            if self.save_profile_btn.winfo_ismapped():
                self.save_profile_btn.pack_forget()
            self._hide_custom_error()

    def _build_custom_error(self, parent):
        C = self.C
        self._custom_error_after_id = None
        self.custom_error_panel = ctk.CTkFrame(
            parent, fg_color=C["panel"], corner_radius=16,
            border_width=1, border_color=C["status_bad"],
        )

        self.custom_error_var = ctk.StringVar(value="")
        self.custom_error_label = ctk.CTkLabel(
            self.custom_error_panel, textvariable=self.custom_error_var, font=FB(13),
            text_color=C["status_bad"], wraplength=WIN_W - 122, justify="center",
        )
        self.custom_error_label.pack(padx=16, pady=12)

    def _show_custom_error(self, msg):
        C = self.C
        try:
            self.custom_error_label.configure(text_color=C["status_bad"])
            self.custom_error_panel.configure(border_color=C["status_bad"])
        except Exception:
            return
        self.custom_error_var.set(msg)

        if not self.custom_error_panel.winfo_ismapped():
            self.custom_error_panel.pack(
                before=self._profiles_panel, padx=26, pady=(0, 18), fill="x",
            )

        if self._custom_error_after_id is not None:
            try:
                self.after_cancel(self._custom_error_after_id)
            except Exception:
                pass
        self._custom_error_after_id = self.after(8000, self._hide_custom_error)

    def _hide_custom_error(self):
        self._custom_error_after_id = None
        try:
            self.custom_error_panel.pack_forget()
        except Exception:
            pass
        self.custom_error_var.set("")

    def _build_profiles_panel(self, parent):
        C = self.C
        panel = ctk.CTkFrame(
            parent, fg_color=C["panel"], corner_radius=22,
            border_width=1, border_color=C["border"],
        )
        self._profiles_panel = panel

        header_row = ctk.CTkFrame(panel, fg_color="transparent")
        header_row.pack(fill="x", padx=22, pady=(20, 12))

        ctk.CTkLabel(
            header_row, text="SAVED PROFILES", font=FT(11), text_color=C["text_dim"],
        ).pack(side="left")

        self._profiles_header_right = ctk.CTkFrame(header_row, fg_color="transparent")
        self._profiles_header_right.pack(side="right")

        self._profiles_grid = ctk.CTkFrame(panel, fg_color="transparent")
        self._profiles_grid.pack(padx=10, pady=(0, 20))

        self._clear_popup = None
        self._clear_popup_parts = []
        self._clear_popup_scroll_job = None
        self._clear_popup_scroll_at_open = None
        self._profile_select_mode = False
        self._selected_profile_keys = set()

        self._render_profiles_header_right()
        self._render_profile_buttons()
        if self.profiles:
            panel.pack(padx=26, pady=(0, 18), fill="x")


    def _render_profiles_header_right(self):
        C = self.C
        for child in self._profiles_header_right.winfo_children():
            child.destroy()

        if self._profile_select_mode:
            self._select_count_var = ctk.StringVar(value=self._select_count_text())
            ctk.CTkLabel(
                self._profiles_header_right, textvariable=self._select_count_var,
                font=FB(11), text_color=C["text_dimmer"],
            ).pack(side="left", padx=(0, 12))

            cancel_label = ctk.CTkLabel(
                self._profiles_header_right, text="Cancel", font=FB(11),
                text_color=C["text_dimmer"], cursor="hand2",
            )
            cancel_label.pack(side="left", padx=(0, 14))
            cancel_label.bind("<Button-1>", lambda e: self._exit_select_mode())
            cancel_label.bind(
                "<Enter>", lambda e: cancel_label.configure(text_color=C["text_dim"])
            )
            cancel_label.bind(
                "<Leave>", lambda e: cancel_label.configure(text_color=C["text_dimmer"])
            )

            HoverButton(
                self._profiles_header_right, text="\u2713 Done",
                command=self._confirm_delete_selected,
                width=84, height=30, corner_radius=9, font=FT(11),
                fg_color=C["btn_idle"], hover_color=C["btn_hover"],
                text_color=C["btn_text"], hover_text_color=C["btn_hover_text"],
                blend_color=C["panel"], grow=3,
            ).pack(side="left")
        else:
            clear_row = ctk.CTkFrame(
                self._profiles_header_right, fg_color="transparent", cursor="hand2",
            )
            clear_row.pack(side="right")
            self._clear_row = clear_row

            icon_size = 15
            icon_img = _draw_broom_icon(icon_size, _hex_to_rgb(C["text_dimmer"]))
            self._clear_icon_photo = ImageTk.PhotoImage(icon_img)
            icon_label = ctk.CTkLabel(clear_row, image=self._clear_icon_photo, text="")
            icon_label.pack(side="left", padx=(0, 5))
            clear_label = ctk.CTkLabel(
                clear_row, text="Clear", font=FB(11), text_color=C["text_dimmer"],
            )
            clear_label.pack(side="left")

            def _clear_enter(_e=None):
                clear_label.configure(text_color=C["text_dim"])

            def _clear_leave(_e=None):
                clear_label.configure(text_color=C["text_dimmer"])

            for w in (clear_row, icon_label, clear_label):
                w.bind("<Enter>", _clear_enter)
                w.bind("<Leave>", _clear_leave)
                w.bind("<Button-1>", lambda e: self._toggle_clear_popup())

    def _select_count_text(self):
        n = len(self._selected_profile_keys)
        return f"{n} selected" if n else "Tap profiles to select"


    def _toggle_clear_popup(self):
        if self._clear_popup is not None and self._clear_popup.winfo_exists():
            self._close_clear_popup()
            return
        self._open_clear_popup()

    _CLEAR_CARD_W = 204

    def _clear_popup_xy(self, card_h=None):
        card_w = self._CLEAR_CARD_W
        self.update_idletasks()
        anchor = getattr(self, "_clear_row", None) or self._profiles_header_right
        anchor_left = anchor.winfo_rootx() - self.winfo_rootx()
        anchor_top = anchor.winfo_rooty() - self.winfo_rooty()
        anchor_right = anchor_left + anchor.winfo_width()
        anchor_bottom = anchor_top + anchor.winfo_height()
        win_h = self.winfo_height()

        x0 = max(0, min(anchor_right - card_w, max(0, self.winfo_width() - card_w)))

        y0 = anchor_bottom + 8
        if card_h is not None:
            if y0 + card_h > win_h:
                y0_above = anchor_top - card_h - 8
                if y0_above >= 0:
                    y0 = y0_above
                else:
                    y0 = max(0, win_h - card_h)
        return x0, y0

    def _open_clear_popup(self):
        if not self.profiles:
            return
        C = self.C
        card_w = self._CLEAR_CARD_W

        card = ctk.CTkFrame(
            self, width=card_w, corner_radius=14,
            fg_color=C["panel"], bg_color=C["panel"],
            border_width=1, border_color=C["border"],
        )

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(side="top", fill="x", padx=14, pady=(8, 0))
        ctk.CTkLabel(
            top_row, text="Clear profiles", font=FT(11), text_color=C["text_dim"],
        ).pack(side="left")
        close_label = ctk.CTkLabel(
            top_row, text="\u2715", font=FB(12), text_color=C["text_dimmer"],
            cursor="hand2",
        )
        close_label.pack(side="right")
        close_label.bind("<Button-1>", lambda e: self._close_clear_popup())

        btn1 = HoverButton(
            card, text="Select to Delete", command=self._enter_select_mode,
            width=176, height=38, corner_radius=10, font=FB(12),
            fg_color=C["btn_idle"], hover_color=C["btn_hover"],
            text_color=C["btn_text"], hover_text_color=C["btn_hover_text"],
            blend_color=C["panel"], grow=3,
        )
        btn1.pack(side="top", pady=(6, 4))
        btn2 = HoverButton(
            card, text="Clear All", command=self._confirm_clear_all,
            width=176, height=38, corner_radius=10, font=FB(12),
            fg_color=C["btn_idle"], hover_color=C["status_bad"],
            text_color=C["btn_text"], hover_text_color=WHITE,
            blend_color=C["panel"], grow=3,
        )
        btn2.pack(side="top", pady=(4, 8))

        self.update_idletasks()
        card_h = card.winfo_reqheight()
        card.configure(height=card_h)
        card.pack_propagate(False)
        x0, y0 = self._clear_popup_xy(card_h)
        card.place(x=x0, y=y0)
        card.lift()
        self._clear_popup = card
        self._clear_popup_parts = [card]

        try:
            self._clear_popup_scroll_at_open = self._content_frame._parent_canvas.yview()
        except Exception:
            self._clear_popup_scroll_at_open = None
        self._watch_clear_popup_scroll()

    def _watch_clear_popup_scroll(self):
        if self._clear_popup is None or not self._clear_popup.winfo_exists():
            self._clear_popup_scroll_job = None
            return
        if self._clear_popup_scroll_at_open is not None:
            try:
                current = self._content_frame._parent_canvas.yview()
            except Exception:
                current = None
            if current is not None and current != self._clear_popup_scroll_at_open:
                self._close_clear_popup()
                return
        self._clear_popup_scroll_job = self.after(150, self._watch_clear_popup_scroll)

    def _close_clear_popup(self):
        if self._clear_popup_scroll_job is not None:
            try:
                self.after_cancel(self._clear_popup_scroll_job)
            except Exception:
                pass
            self._clear_popup_scroll_job = None
        for w in getattr(self, "_clear_popup_parts", None) or []:
            try:
                w.destroy()
            except Exception:
                pass
        self._clear_popup_parts = []
        self._clear_popup = None

    def _confirm_clear_all(self):
        self._close_clear_popup()
        self.clear_profiles()


    def _enter_select_mode(self):
        self._close_clear_popup()
        self._profile_select_mode = True
        self._selected_profile_keys = set()
        self._render_profiles_header_right()
        self._render_profile_buttons()

    def _exit_select_mode(self):
        self._profile_select_mode = False
        self._selected_profile_keys = set()
        self._render_profiles_header_right()
        self._render_profile_buttons()

    def _toggle_profile_selected(self, key):
        if key in self._selected_profile_keys:
            self._selected_profile_keys.discard(key)
        else:
            self._selected_profile_keys.add(key)
        self._render_profile_buttons()
        if hasattr(self, "_select_count_var"):
            self._select_count_var.set(self._select_count_text())

    def _confirm_delete_selected(self):
        if self._selected_profile_keys:
            self.profiles = [
                p for p in self.profiles
                if (p["width"], p["height"]) not in self._selected_profile_keys
            ]
            save_profiles(self.profiles)
        self._profile_select_mode = False
        self._selected_profile_keys = set()
        self._render_profiles_header_right()
        self._refresh_profiles_panel()


    def _render_profile_buttons(self):
        for child in self._profiles_grid.winfo_children():
            child.destroy()

        C = self.C
        cols = 3
        total = len(self.profiles)
        full_rows, remainder = divmod(total, cols)

        for i, prof in enumerate(self.profiles):
            r, c = divmod(i, cols)
            if r == full_rows and remainder:
                c += (cols - remainder) // 2

            key = (prof["width"], prof["height"])
            if self._profile_select_mode:
                selected = key in self._selected_profile_keys
                btn = HoverButton(
                    self._profiles_grid, text=prof["label"], width=165, height=52,
                    corner_radius=14, font=FT(13),
                    fg_color=C["status_bad"] if selected else C["btn_idle"],
                    hover_color=C["status_bad"] if selected else C["btn_hover"],
                    text_color=WHITE if selected else C["btn_text"],
                    hover_text_color=WHITE if selected else C["btn_hover_text"],
                    blend_color=C["panel"], grow=4,
                    command=lambda k=key: self._toggle_profile_selected(k),
                )
            else:
                btn = HoverButton(
                    self._profiles_grid, text=prof["label"], width=165, height=52,
                    corner_radius=14, font=FT(13),
                    fg_color=C["btn_idle"], hover_color=C["btn_hover"],
                    text_color=C["btn_text"], hover_text_color=C["btn_hover_text"],
                    blend_color=C["panel"], grow=6,
                    command=lambda w=prof["width"], h=prof["height"]:
                        self.apply_profile(w, h),
                )
            btn.grid(row=r, column=c, padx=9, pady=9)

    def _refresh_profiles_panel(self):
        self._render_profile_buttons()
        if self.profiles:
            if not self._profiles_panel.winfo_ismapped():
                self._profiles_panel.pack(
                    before=self._footer_separator, padx=26, pady=(0, 18), fill="x",
                )
        else:
            if self._profiles_panel.winfo_ismapped():
                self._profiles_panel.pack_forget()

    def _build_status(self, parent):
        C = self.C
        self._status_after_id = None
        self.status_panel = ctk.CTkFrame(
            parent, fg_color=C["panel"], corner_radius=16,
            border_width=1, border_color=C["border"],
        )

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
        self._footer_separator = separator

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


    def apply_resolution(self, width, height):
        ok, msg = set_resolution(width, height)
        self._show_status(msg, ok)

    def apply_profile(self, width, height):
        ok, msg = set_resolution(width, height)
        self._show_custom_status(msg, ok)

    def apply_custom(self):
        text = self.custom_entry.get().strip()

        match = re.match(r"^(\d{2,5})\s*[x, ]\s*(\d{2,5})$", text)
        if not match:
            self._show_custom_status(
                "ERROR! Enter a full resolution like 1280x1080.", ok=False,
            )
            return

        width, height = int(match.group(1)), int(match.group(2))

        if width < 100 or height < 100:
            self._show_custom_status(
                "ERROR! That resolution is too small to be valid.", ok=False,
            )
            return

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        if width > screen_w or height > screen_h:
            self._show_custom_status(
                f"ERROR! That's larger than your monitor's native "
                f"resolution ({screen_w}x{screen_h}).", ok=False,
            )
            return

        ok, msg = set_resolution(width, height)
        self._show_custom_status(msg, ok)

    def save_profile(self):
        text = self.custom_entry.get().strip()
        match = re.match(r"^(\d{2,5})\s*[x, ]\s*(\d{2,5})$", text)
        if not match:
            self._show_custom_error("Type a full resolution, like 1920x1080.")
            return

        width, height = int(match.group(1)), int(match.group(2))

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        if width > screen_w or height > screen_h:
            self._show_custom_error(
                f"That's larger than your monitor's native resolution "
                f"({screen_w}x{screen_h})."
            )
            return

        if any(p["width"] == width and p["height"] == height for p in self.profiles):
            self._show_custom_error("That resolution is already saved as a profile.")
            return

        self.profiles.append({
            "label": f"{width}x{height}", "width": width, "height": height,
        })
        save_profiles(self.profiles)
        self._hide_custom_error()
        self._refresh_profiles_panel()

    def clear_profiles(self):
        if not self.profiles:
            return
        self.profiles = []
        save_profiles(self.profiles)
        self._refresh_profiles_panel()


    def _open_singleton(self, key, build_fn):
        existing = self._popups.get(key)
        if existing is not None and existing.winfo_exists():
            existing.lift()
            existing.focus_force()
            return
        win = build_fn()
        self._popups[key] = win

    def _wire_autohide_scrollbar(self, scrollbar):
        if scrollbar is None:
            return
        state = {"w": SCROLLBAR_IDLE_WIDTH, "job": None, "held": False, "hover": False}
        try:
            scrollbar.configure(
                width=SCROLLBAR_IDLE_WIDTH,
                corner_radius=max(1, SCROLLBAR_IDLE_WIDTH // 2),
            )
        except Exception:
            pass

        def animate(target_w):
            if state["job"]:
                try:
                    scrollbar.after_cancel(state["job"])
                except Exception:
                    pass
                state["job"] = None
            start_w = state["w"]
            steps, interval = 8, 12

            def step(i=0):
                t = _ease_out(i / steps)
                w = max(1, int(start_w + (target_w - start_w) * t))
                try:
                    scrollbar.configure(width=w, corner_radius=max(1, w // 2))
                except Exception:
                    return
                state["w"] = w
                if i < steps:
                    state["job"] = scrollbar.after(interval, lambda: step(i + 1))
                else:
                    state["job"] = None

            step()

        def on_enter(_e=None):
            state["hover"] = True
            animate(SCROLLBAR_HOVER_WIDTH)

        def on_leave(_e=None):
            state["hover"] = False
            if state["held"]:
                return
            animate(SCROLLBAR_IDLE_WIDTH)

        def on_press(_e=None):
            state["held"] = True

        def on_release(_e=None):
            if not state["held"]:
                return
            state["held"] = False
            animate(SCROLLBAR_HOVER_WIDTH if state["hover"] else SCROLLBAR_IDLE_WIDTH)

        scrollbar.bind("<Enter>", on_enter)
        scrollbar.bind("<Leave>", on_leave)
        scrollbar.bind("<ButtonPress-1>", on_press, add="+")
        scrollbar.bind("<ButtonRelease-1>", on_release, add="+")

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
            self._wire_autohide_scrollbar(getattr(scroll, "_scrollbar", None))

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
                width=124, height=40, corner_radius=12, font=FT(12),
                fg_color=C["btn_idle"], hover_color=C["btn_hover"],
                text_color=C["btn_text"], hover_text_color=C["btn_hover_text"],
                blend_color=C["bg"], grow=4, icon="youtube", icon_size=18,
            ).pack(side="left", padx=(0, 10))
            HoverButton(
                links_row, text="Discord", command=lambda: webbrowser.open(DISCORD_URL),
                width=124, height=40, corner_radius=12, font=FT(12),
                fg_color=C["btn_idle"], hover_color=C["btn_hover"],
                text_color=C["btn_text"], hover_text_color=C["btn_hover_text"],
                blend_color=C["bg"], grow=4, icon="discord", icon_size=18,
            ).pack(side="left", padx=(0, 10))
            HoverButton(
                links_row, text="GitHub", command=lambda: webbrowser.open(GITHUB_URL),
                width=124, height=40, corner_radius=12, font=FT(12),
                fg_color=C["btn_idle"], hover_color=C["btn_hover"],
                text_color=C["btn_text"], hover_text_color=C["btn_hover_text"],
                blend_color=C["bg"], grow=4, icon="github", icon_size=18,
                border_width=0,
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


def _acquire_single_instance_lock():
    ERROR_ALREADY_EXISTS = 183
    kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW(None, False, "Global\\SnapRes_bku_single_instance")
    if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        return False
    return True


def _log_startup_error(exc):
    import traceback
    log_path = os.path.join(os.environ.get("TEMP", "."), "SnapRes_error.log")
    try:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
    except Exception:
        pass
    try:
        messagebox.showerror(
            "SnapRes failed to start",
            f"{type(exc).__name__}: {exc}\n\nDetails saved to:\n{log_path}",
        )
    except Exception:
        pass


VERSION = "1.0.6"

if __name__ == "__main__":
    if sys.platform != "win32":
        messagebox.showerror("Unsupported", "This tool only works on Windows.")
        sys.exit(1)

    if not _acquire_single_instance_lock():
        print("SnapRes: another instance already holds the lock, exiting.", flush=True)
        sys.exit(0)

    print("SnapRes: starting up...", flush=True)
    try:
        print("SnapRes: loading fonts...", flush=True)
        load_bundled_fonts()
        print("SnapRes: fonts loaded, creating window...", flush=True)
        app = ResSwitcherApp()
        print("SnapRes: window created, bringing to foreground...", flush=True)

        app.update_idletasks()
        app.deiconify()
        app.lift()
        app.attributes("-topmost", True)
        app.after(250, lambda: app.attributes("-topmost", False))
        app.focus_force()

        print("SnapRes: entering mainloop.", flush=True)
        app.mainloop()
        print("SnapRes: mainloop exited normally.", flush=True)
    except Exception as e:
        print(f"SnapRes: startup FAILED - {type(e).__name__}: {e}", flush=True)
        _log_startup_error(e)
        sys.exit(1)
