"""
List the Gemini models your API key can actually use.

Run:    python list_models.py AIza...your_key

This calls Google's ListModels endpoint and filters for models that
support `generateContent` (the method our app uses). Pick one of the
printed model names and set it as DEFAULT_MODEL in gemini_client.py.
"""
import json
import sys
import requests


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python list_models.py AIza...your_key")
        return 1

    key = sys.argv[1].strip()
    url = "https://generativelanguage.googleapis.com/v1beta/models"

    print(f"Asking Google what models key {key[:6]}...{key[-4:]} can use...\n")
    resp = requests.get(url, params={"key": key}, timeout=15)

    if resp.status_code != 200:
        print(f"HTTP {resp.status_code}")
        print(json.dumps(resp.json(), indent=2))
        return 1

    data = resp.json()
    models = data.get("models", [])
    if not models:
        print("No models returned. Response:")
        print(json.dumps(data, indent=2))
        return 1

    usable = []
    for m in models:
        name = m.get("name", "").replace("models/", "")
        methods = m.get("supportedGenerationMethods", [])
        if "generateContent" in methods:
            usable.append(name)

    if not usable:
        print("Found models, but NONE support generateContent. Full list:")
        for m in models:
            print(f"  {m.get('name')}  -- methods: {m.get('supportedGenerationMethods')}")
        return 1

    print(f"Models you can use ({len(usable)} found):\n")
    for name in usable:
        marker = "  <- recommended" if "flash" in name and "lite" not in name else ""
        print(f"  {name}{marker}")

    print("\nNext step:")
    print("  Open gemini_client.py and change DEFAULT_MODEL to one of the names above.")
    print("  For text rewriting, any 'flash' model is a good balance of speed + quality.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
