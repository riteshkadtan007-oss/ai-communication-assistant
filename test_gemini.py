"""
Quick CLI sanity check for your Gemini API key — no Kivy involved.

Why this exists: if the full app misbehaves, run this first to confirm
your key and the API itself are healthy. Eliminates 90% of "is it me or
is it the app?" confusion.

Run:    python test_gemini.py
"""
import sys

from gemini_client import GeminiClient, GeminiError
import config


def main() -> int:
    print("=" * 50)
    print("Gemini API key check")
    print("=" * 50)

    key = config.load_api_key()
    if not key:
        # Allow passing key on the command line for first-time testing
        if len(sys.argv) > 1:
            key = sys.argv[1].strip()
            print("Using key from command line argument.")
        else:
            print(
                "\nNo saved key found.\n"
                "Either run the app once and save a key in Settings,\n"
                "or pass one here:\n"
                "    python test_gemini.py AIza...your_key_here\n"
            )
            return 1
    else:
        print("Using saved key from ~/.ai_keyboard/config.json")

    client = GeminiClient(api_key=key)
    print(f"Model: {client.model}")
    print(f"Key:   {key[:6]}...{key[-4:]}\n")

    # Ping — call _call_once directly so we see the real error message,
    # not the swallowed boolean from ping().
    print("1) Pinging Gemini...")
    try:
        client._call_once("Reply with exactly the word: ok")
        print("   OK — key works.\n")
    except GeminiError as e:
        print(f"   FAILED: {e}\n")
        print("   Common fixes:")
        print("   - Try a different model: edit DEFAULT_MODEL in gemini_client.py")
        print("     Options: gemini-1.5-flash-latest, gemini-1.5-flash, gemini-2.0-flash")
        print("   - Make sure the Generative Language API is enabled for your Google project")
        print("     (visit aistudio.google.com, regenerate the key if needed)")
        return 1
    except Exception as e:
        print(f"   FAILED (unexpected): {type(e).__name__}: {e}\n")
        return 1

    # One real transform — proves prompts module wires up
    print("2) Running a real transformation (polish)...")
    sample = "hey can u send me the report asap thx"
    try:
        result = client.transform(sample, "polish")
        print(f"   Input:  {sample}")
        print(f"   Output: {result}\n")
    except GeminiError as e:
        print(f"   FAILED: {e}\n")
        return 1

    print("All checks passed. You're good to run: python main.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
