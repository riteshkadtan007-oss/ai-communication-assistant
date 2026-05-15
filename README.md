# AI Keyboard Assistant — Mac Test Build

A Kivy desktop MVP for the AI text-rewriting bubble. Built so the same code can later be packaged into an Android APK with minimal changes.

## What's in this folder

| File | What it does |
|---|---|
| `main.py` | The Kivy app — Home + Settings screens |
| `gemini_client.py` | Talks to Google's Gemini REST API (no SDK, lightweight) |
| `prompts.py` | All tone prompts. **This is where you tune output quality.** |
| `config.py` | Saves your API key to `~/.ai_keyboard/config.json` |
| `test_gemini.py` | CLI script to verify your key works before running the app |
| `requirements.txt` | Python deps |

## Setup (one time)

### 1. Get a free Gemini API key

1. Open https://aistudio.google.com
2. Sign in with any Google account
3. Click **Get API Key** → **Create API key**
4. Copy the key (starts with `AIza...`)

Free tier: 15 requests/minute, 1500/day. More than enough for testing.

### 2. Install Python deps

Open Terminal, `cd` into this folder, then:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If `pip install kivy` fails on Mac with SDL errors:

```bash
brew install sdl2 sdl2_image sdl2_ttf sdl2_mixer
pip install --upgrade pip
pip install kivy
```

## Test the API key (before running the full app)

This is the fastest way to confirm your key works. Run it once first:

```bash
python test_gemini.py AIza...your_key_here
```

You should see:

```
1) Pinging Gemini...
   OK — key works.

2) Running a real transformation (polish)...
   Input:  hey can u send me the report asap thx
   Output: Hey, could you send me the report as soon as possible? Thanks.

All checks passed.
```

If you get an error, the message will tell you what's wrong (bad key, no internet, model unavailable, etc.). Fix that before moving on.

## Run the app

```bash
python main.py
```

A 420×760 window opens (sized like a phone so the layout previews Android).

**First run:**
1. Click **Settings**
2. Paste your API key, tap **Save**, then tap **Test key**
3. Wait for "Key works!"
4. Click **Back**

The dot at the top of Home turns green when the key is set. You're ready.

## How to use

1. Paste any text into the input box.
2. Tap a tone button (Polish, Funny, LinkedIn Post, etc.).
3. For Translate, a language dropdown appears — pick a language, then tap Translate again.
4. When the result appears, tap **Copy**.

## Tuning output quality

The single biggest lever is `prompts.py`. Each tone has a dedicated prompt template. If "Make It Funny" feels too dry or "LinkedIn Post" is too generic, edit that tone's prompt and re-run. No other files need to change.

The `OUTPUT_RULES` block at the top is appended to every prompt — that's what stops Gemini from saying things like "Here's the rewritten version:" before the actual result.

## Switching models

Currently using `gemini-2.0-flash` (fast, free). To try a different one, edit `DEFAULT_MODEL` in `gemini_client.py`. Options that work on the free tier:

- `gemini-2.0-flash` — current default, fast, good quality
- `gemini-1.5-flash-latest` — older but very stable
- `gemini-1.5-flash-8b` — fastest, lower quality
- `gemini-1.5-pro-latest` — best quality, slower, stricter rate limit

## Troubleshooting

**"No module named kivy"** — make sure your venv is activated (`source .venv/bin/activate`) and you ran `pip install -r requirements.txt`.

**Window opens but is blank** — try resizing. Some Kivy versions on Mac need an initial resize to lay out.

**"Invalid API key"** — re-copy the key from aistudio.google.com. Make sure there's no leading/trailing whitespace.

**"Rate limit hit"** — wait 60 seconds. Free tier is 15 RPM.

**"Response was blocked by Gemini's safety filter"** — rewrite the input to be less explicit. Gemini has fairly aggressive safety filters by default.

**Emojis show as boxes in buttons** — known Kivy limitation on Mac (it doesn't render Apple Color Emoji). The text labels still work; this is purely cosmetic.

## What's next (when the Mac build feels good)

When you're happy with this version, the next step is the Android build:

1. **buildozer.spec** — Android build config. Will pin the Python version, list permissions (just INTERNET), set the package name.
2. **Test in Google Colab** — easiest place to run Buildozer (Mac's environment is painful for Android builds). I'll set up a Colab notebook when you're ready.
3. **Sideload the APK** — install on your phone via USB / Android File Transfer to test before considering Play Store.

Play Store policies for "floating bubble" / overlay apps got stricter in 2024-25 — the `SYSTEM_ALERT_WINDOW` permission needs justification. Worth designing the Android version to work both as a regular app AND optionally as a bubble, so you have a fallback if review pushes back.
