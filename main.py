"""
AI Keyboard Assistant — Mac MVP

Run:    python main.py
Setup:  pip install -r requirements.txt

This is the desktop test build. Same code will package for Android
later via Buildozer (no SDK dependencies that would block that).
"""
from __future__ import annotations

import threading
from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

import config
from gemini_client import GeminiClient, GeminiError


# ─────────────────────────────────────────────────────────────────────────
# Theme
# ─────────────────────────────────────────────────────────────────────────
BG_DARK    = "#0F0F1A"
BG_CARD    = "#1A1A2E"
BG_CARD2   = "#16213E"
ACCENT     = "#7C3AED"
ACCENT2    = "#A78BFA"
SUCCESS    = "#10B981"
DANGER     = "#EF4444"
WARNING    = "#F59E0B"
TEXT_WHITE = "#F1F5F9"
TEXT_GRAY  = "#94A3B8"


def clr(hex_color: str):
    return get_color_from_hex(hex_color)


# ─────────────────────────────────────────────────────────────────────────
# Catalogs
# ─────────────────────────────────────────────────────────────────────────
TONE_OPTIONS = [
    ("Polish It",          "polish"),
    ("Professional",       "professional"),
    ("Make It Funny",      "funny"),
    ("Friendly",           "friendly"),
    ("CEO / Corporate",    "ceo"),
    ("Gen Z Vibes",        "genz"),
    ("Instagram Caption",  "caption"),
    ("LinkedIn Post",      "linkedin"),
    ("Email Format",       "email"),
    ("Summarize",          "summarize"),
    ("Translate",          "translate"),
    ("Add Hashtags",       "hashtags"),
    ("Angry > Polite",     "angry_to_polite"),
    ("Make It Viral",      "viral"),
]

LANGUAGES = [
    "Hindi", "Kannada", "Tamil", "Telugu", "Marathi", "Bengali",
    "Gujarati", "Punjabi", "Malayalam", "Urdu",
    "English", "French", "Spanish", "German", "Japanese", "Arabic",
]


# ─────────────────────────────────────────────────────────────────────────
# Helper: solid background hook (Kivy doesn't have CSS-style bg colors)
# ─────────────────────────────────────────────────────────────────────────
def add_solid_bg(widget, hex_color: str):
    from kivy.graphics import Color, Rectangle
    with widget.canvas.before:
        Color(*clr(hex_color))
        rect = Rectangle(pos=widget.pos, size=widget.size)

    def _update(_inst, _val):
        rect.pos = widget.pos
        rect.size = widget.size

    widget.bind(pos=_update, size=_update)


# ─────────────────────────────────────────────────────────────────────────
# Home screen
# ─────────────────────────────────────────────────────────────────────────
class HomeScreen(Screen):
    def __init__(self, gemini: GeminiClient, **kwargs):
        super().__init__(**kwargs)
        self.gemini = gemini
        self.result_text = ""
        self._in_flight = False
        self._build_ui()

    # ----- build -----
    def _build_ui(self):
        root = BoxLayout(
            orientation="vertical",
            padding=[dp(16), dp(20), dp(16), dp(16)],
            spacing=dp(12),
        )
        add_solid_bg(root, BG_DARK)

        root.add_widget(self._build_header())
        root.add_widget(self._build_input_section())
        root.add_widget(self._build_tone_grid())
        root.add_widget(self._build_language_row())
        root.add_widget(self._build_status_label())
        root.add_widget(self._build_result_section())
        root.add_widget(self._build_action_row())

        self.add_widget(root)

    def _build_header(self):
        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(48),
            spacing=dp(8),
        )

        title = Label(
            text="[b][color=7C3AED]AI[/color] Keyboard[/b]",
            markup=True, font_size=dp(22),
            color=clr(TEXT_WHITE),
            halign="left", valign="middle",
        )
        title.bind(size=title.setter("text_size"))

        self.health_dot = Label(
            text="●", font_size=dp(18),
            color=clr(TEXT_GRAY),
            size_hint_x=None, width=dp(28),
            halign="right", valign="middle",
        )
        self.health_dot.bind(size=self.health_dot.setter("text_size"))

        settings_btn = Button(
            text="Settings", font_size=dp(13),
            size_hint=(None, None), size=(dp(80), dp(36)),
            background_normal="", background_down="",
            background_color=clr(BG_CARD2),
            color=clr(ACCENT2),
        )
        settings_btn.bind(on_press=lambda *_: self.manager.switch_to_settings())

        header.add_widget(title)
        header.add_widget(self.health_dot)
        header.add_widget(settings_btn)
        return header

    def _build_input_section(self):
        wrapper = BoxLayout(
            orientation="vertical",
            spacing=dp(4),
            size_hint_y=None, height=dp(150),
        )

        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(20))
        label = Label(
            text="Your text", font_size=dp(13),
            color=clr(TEXT_GRAY),
            halign="left", valign="middle",
        )
        label.bind(size=label.setter("text_size"))
        self.char_count = Label(
            text="0 chars", font_size=dp(11),
            color=clr(TEXT_GRAY),
            halign="right", valign="middle",
            size_hint_x=None, width=dp(70),
        )
        self.char_count.bind(size=self.char_count.setter("text_size"))
        row.add_widget(label)
        row.add_widget(self.char_count)
        wrapper.add_widget(row)

        self.text_input = TextInput(
            hint_text="Type or paste your message, caption, or email...",
            hint_text_color=clr(TEXT_GRAY),
            foreground_color=clr(TEXT_WHITE),
            background_color=clr(BG_CARD),
            cursor_color=clr(ACCENT2),
            font_size=dp(15),
            padding=[dp(14), dp(12), dp(14), dp(12)],
            multiline=True,
        )
        self.text_input.bind(text=self._on_text_change)
        wrapper.add_widget(self.text_input)
        return wrapper

    def _build_tone_grid(self):
        wrapper = BoxLayout(
            orientation="vertical",
            spacing=dp(4),
            size_hint_y=None, height=dp(220),
        )

        label = Label(
            text="Choose action", font_size=dp(13),
            color=clr(TEXT_GRAY),
            size_hint_y=None, height=dp(20),
            halign="left", valign="middle",
        )
        label.bind(size=label.setter("text_size"))
        wrapper.add_widget(label)

        scroll = ScrollView()
        grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        for tone_label, tone_key in TONE_OPTIONS:
            btn = Button(
                text=tone_label, font_size=dp(13),
                size_hint_y=None, height=dp(42),
                background_normal="", background_down="",
                background_color=clr(BG_CARD2),
                color=clr(ACCENT2),
            )
            btn.bind(on_press=partial(self._on_tone, tone_key))
            grid.add_widget(btn)

        scroll.add_widget(grid)
        wrapper.add_widget(scroll)
        return wrapper

    def _build_language_row(self):
        self.lang_spinner = Spinner(
            text="Select Language",
            values=LANGUAGES,
            size_hint_y=None, height=dp(40),
            background_normal="", background_down="",
            background_color=clr(ACCENT),
            color=clr(TEXT_WHITE),
            font_size=dp(13),
            opacity=0,
            disabled=True,
        )
        return self.lang_spinner

    def _build_status_label(self):
        self.status_label = Label(
            text="Ready.", font_size=dp(12),
            color=clr(ACCENT2),
            size_hint_y=None, height=dp(22),
            halign="center", valign="middle",
        )
        self.status_label.bind(size=self.status_label.setter("text_size"))
        return self.status_label

    def _build_result_section(self):
        self.result_box = TextInput(
            hint_text="AI result will appear here...",
            hint_text_color=clr(TEXT_GRAY),
            foreground_color=clr(TEXT_WHITE),
            background_color=clr(BG_CARD),
            font_size=dp(14),
            padding=[dp(14), dp(12), dp(14), dp(12)],
            size_hint_y=None, height=dp(120),
            multiline=True, readonly=True,
        )
        return self.result_box

    def _build_action_row(self):
        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(46),
            spacing=dp(10),
        )
        copy_btn = Button(
            text="Copy", font_size=dp(14),
            background_normal="", background_color=clr(SUCCESS),
            color=clr(TEXT_WHITE),
        )
        copy_btn.bind(on_press=self._on_copy)

        clear_btn = Button(
            text="Clear", font_size=dp(14),
            background_normal="", background_color=clr(BG_CARD2),
            color=clr(TEXT_GRAY),
        )
        clear_btn.bind(on_press=self._on_clear)

        row.add_widget(copy_btn)
        row.add_widget(clear_btn)
        return row

    # ----- lifecycle -----
    def on_pre_enter(self, *_):
        # Re-check health every time we land on this screen
        # (e.g., after the user saved a new key in Settings).
        self._refresh_health_indicator()

    # ----- handlers -----
    def _refresh_health_indicator(self):
        if not self.gemini.is_configured():
            self.health_dot.color = clr(WARNING)
            if not self.status_label.text.startswith(("Done", "Copied")):
                self.status_label.text = "No API key set — open Settings to add yours."
        else:
            self.health_dot.color = clr(SUCCESS)
            if self.status_label.text.startswith("No API key"):
                self.status_label.text = "Ready."

    def _on_text_change(self, _instance, value):
        self.char_count.text = f"{len(value)} chars"

    def _on_tone(self, tone_key, _btn):
        if self._in_flight:
            return  # ignore taps while a request is running

        text = self.text_input.text.strip()
        if not text:
            self.status_label.text = "Enter some text first."
            return

        if not self.gemini.is_configured():
            self.status_label.text = "Add your Gemini API key in Settings first."
            return

        lang = None
        if tone_key == "translate":
            # Reveal the language picker
            self.lang_spinner.opacity = 1
            self.lang_spinner.disabled = False
            if self.lang_spinner.text == "Select Language":
                self.status_label.text = "Pick a language above, then tap Translate again."
                return
            lang = self.lang_spinner.text

        self._set_busy(True)
        self.status_label.text = "AI is thinking..."
        self.result_box.text = ""

        def worker():
            try:
                result = self.gemini.transform(text, tone_key, lang)
                Clock.schedule_once(lambda _dt: self._on_result(result))
            except GeminiError as e:
                msg = str(e)
                Clock.schedule_once(lambda _dt: self._on_error(msg))
            except Exception as e:
                msg = f"Unexpected error: {e}"
                Clock.schedule_once(lambda _dt: self._on_error(msg))

        threading.Thread(target=worker, daemon=True).start()

    def _on_result(self, result: str):
        self.result_text = result
        self.result_box.text = result
        self.status_label.text = "Done. Tap Copy to use it."
        self._set_busy(False)

    def _on_error(self, message: str):
        # Short summary in the status bar (one line, often truncated)…
        short = message.split(".")[0][:80]
        self.status_label.text = f"Error: {short}"
        # …full message in the result box so the user can actually read it.
        self.result_box.text = f"[Error]\n\n{message}"
        self.result_text = ""  # don't let Copy paste an error
        self._set_busy(False)

    def _set_busy(self, busy: bool):
        self._in_flight = busy

    def _on_copy(self, *_):
        if not self.result_text:
            self.status_label.text = "Nothing to copy yet."
            return
        from kivy.core.clipboard import Clipboard
        Clipboard.copy(self.result_text)
        self.status_label.text = "Copied to clipboard."

    def _on_clear(self, *_):
        self.text_input.text = ""
        self.result_box.text = ""
        self.result_text = ""
        self.lang_spinner.text = "Select Language"
        self.lang_spinner.opacity = 0
        self.lang_spinner.disabled = True
        self.status_label.text = "Ready."


# ─────────────────────────────────────────────────────────────────────────
# Settings screen
# ─────────────────────────────────────────────────────────────────────────
class SettingsScreen(Screen):
    def __init__(self, gemini: GeminiClient, **kwargs):
        super().__init__(**kwargs)
        self.gemini = gemini
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(
            orientation="vertical",
            padding=dp(20), spacing=dp(12),
        )
        add_solid_bg(root, BG_DARK)

        # Back
        back_btn = Button(
            text="< Back",
            size_hint_y=None, height=dp(44),
            background_normal="", background_color=clr(BG_CARD2),
            color=clr(ACCENT2), font_size=dp(15),
        )
        back_btn.bind(on_press=lambda *_: self.manager.switch_to_home())
        root.add_widget(back_btn)

        # Title
        title = Label(
            text="[b][color=F1F5F9]Settings[/color][/b]",
            markup=True, font_size=dp(22),
            size_hint_y=None, height=dp(34),
            halign="left", valign="middle",
        )
        title.bind(size=title.setter("text_size"))
        root.add_widget(title)

        # API key label
        api_label = Label(
            text="Google Gemini API key",
            font_size=dp(13), color=clr(TEXT_GRAY),
            size_hint_y=None, height=dp(20),
            halign="left", valign="middle",
        )
        api_label.bind(size=api_label.setter("text_size"))
        root.add_widget(api_label)

        # API key row (input + show/hide)
        key_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(6),
            size_hint_y=None, height=dp(48),
        )
        self.api_input = TextInput(
            hint_text="Paste your Gemini API key (starts with AIza...)",
            hint_text_color=clr(TEXT_GRAY),
            foreground_color=clr(TEXT_WHITE),
            background_color=clr(BG_CARD),
            font_size=dp(13),
            padding=[dp(10), dp(14), dp(10), dp(14)],
            password=True, multiline=False,
        )
        self.api_input.text = config.load_api_key()

        self.show_btn = Button(
            text="Show", font_size=dp(12),
            size_hint=(None, None), size=(dp(64), dp(48)),
            background_normal="", background_color=clr(BG_CARD2),
            color=clr(TEXT_GRAY),
        )
        self.show_btn.bind(on_press=self._toggle_show)
        key_row.add_widget(self.api_input)
        key_row.add_widget(self.show_btn)
        root.add_widget(key_row)

        # Save + Test buttons
        btn_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None, height=dp(48),
        )
        save_btn = Button(
            text="Save", font_size=dp(15),
            background_normal="", background_color=clr(ACCENT),
            color=clr(TEXT_WHITE),
        )
        save_btn.bind(on_press=self._on_save)
        test_btn = Button(
            text="Test key", font_size=dp(15),
            background_normal="", background_color=clr(BG_CARD2),
            color=clr(ACCENT2),
        )
        test_btn.bind(on_press=self._on_test)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(test_btn)
        root.add_widget(btn_row)

        # Status message
        self.msg_label = Label(
            text="", font_size=dp(13),
            color=clr(SUCCESS),
            size_hint_y=None, height=dp(24),
            halign="left", valign="middle",
        )
        self.msg_label.bind(size=self.msg_label.setter("text_size"))
        root.add_widget(self.msg_label)

        # Instructions
        instr = (
            "[color=94A3B8][b]How to get a free Gemini API key:[/b]\n\n"
            "1. Go to [color=A78BFA]aistudio.google.com[/color]\n"
            "2. Sign in with any Google account\n"
            "3. Click 'Get API Key' -> 'Create API key'\n"
            "4. Copy the key (starts with 'AIza...')\n"
            "5. Paste it above, tap Save, then Test key\n\n"
            "Free tier: 15 requests/min, 1500/day. Plenty for personal use.[/color]"
        )
        instr_label = Label(
            text=instr, markup=True,
            font_size=dp(13), color=clr(TEXT_GRAY),
            halign="left", valign="top",
        )
        instr_label.bind(size=instr_label.setter("text_size"))
        root.add_widget(instr_label)

        root.add_widget(Widget())  # spacer
        self.add_widget(root)

    # ----- handlers -----
    def _toggle_show(self, *_):
        self.api_input.password = not self.api_input.password
        self.show_btn.text = "Show" if self.api_input.password else "Hide"

    def _set_msg(self, text: str, kind: str = "ok"):
        self.msg_label.text = text
        if kind == "ok":
            self.msg_label.color = clr(SUCCESS)
        elif kind == "warn":
            self.msg_label.color = clr(WARNING)
        elif kind == "err":
            self.msg_label.color = clr(DANGER)
        else:
            self.msg_label.color = clr(ACCENT2)

    def _on_save(self, *_):
        key = self.api_input.text.strip()
        if not key:
            self._set_msg("Key cannot be empty.", "warn")
            return
        if not key.startswith("AIza"):
            self._set_msg(
                "That doesn't look like a Gemini key (should start with 'AIza').",
                "warn",
            )
            return
        config.save_api_key(key)
        self.gemini.api_key = key  # apply immediately to shared client
        self._set_msg("Saved. Tap 'Test key' to verify it works.", "ok")

    def _on_test(self, *_):
        key = self.api_input.text.strip()
        if not key:
            self._set_msg("Save a key first.", "warn")
            return

        self._set_msg("Testing...", "info")

        # Ping with whatever's currently in the box (works even pre-save)
        gem = GeminiClient(api_key=key, model=self.gemini.model)

        def worker():
            ok = gem.ping()

            def show(_dt):
                if ok:
                    self._set_msg("Key works! You're ready to go.", "ok")
                else:
                    self._set_msg(
                        "Key didn't work. Check it at aistudio.google.com.",
                        "err",
                    )

            Clock.schedule_once(show)

        threading.Thread(target=worker, daemon=True).start()


# ─────────────────────────────────────────────────────────────────────────
# Screen manager
# ─────────────────────────────────────────────────────────────────────────
class AIKeyboardManager(ScreenManager):
    def switch_to_settings(self):
        self.transition = SlideTransition(direction="left")
        self.current = "settings"

    def switch_to_home(self):
        self.transition = SlideTransition(direction="right")
        self.current = "home"


# ─────────────────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────────────────
class AIKeyboardApp(App):
    title = "AI Keyboard"

    def build(self):
        Window.clearcolor = clr(BG_DARK)
        # Phone-ish aspect on Mac, so the layout previews what it'll feel
        # like on Android later.
        Window.size = (420, 760)

        # Single shared client — both screens see/update the same key.
        self.gemini = GeminiClient(
            api_key=config.load_api_key(),
            model=config.load_model(),
        )

        sm = AIKeyboardManager()
        sm.add_widget(HomeScreen(self.gemini, name="home"))
        sm.add_widget(SettingsScreen(self.gemini, name="settings"))
        return sm


if __name__ == "__main__":
    AIKeyboardApp().run()
