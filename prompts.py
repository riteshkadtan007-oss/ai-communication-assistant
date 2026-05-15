"""
Tone-specific prompts for the AI keyboard.

These prompts are the single biggest lever on output quality.
Each one is engineered so Gemini returns clean text that's ready to
paste — no "Here's the rewritten version:" preamble, no quote marks
around the result.

To tune a tone: edit the template below. No other files need to change.
"""
from __future__ import annotations  # enables `str | None` syntax on Py 3.7+

# Appended to every prompt. Locks down the output format.
OUTPUT_RULES = (
    "\n\nStrict output rules:\n"
    "- Output ONLY the rewritten text. No preamble, no explanation, no quotation marks around it.\n"
    "- Do not add 'Here is...' or 'Sure!' or any meta-commentary.\n"
    "- Match the original language unless the action explicitly says to translate.\n"
    "- Keep roughly the same length as the input unless the action implies a different length "
    "(summarize = shorter; hashtags / caption = adds extra)."
)

TONE_PROMPTS = {
    "polish": (
        "You are an expert editor. Polish this text: fix grammar, spelling, "
        "and awkward phrasing while preserving the original voice and register. "
        "Do NOT make it more formal — keep the same tone the writer used.\n\n"
        "Text:\n{text}"
    ),

    "professional": (
        "Rewrite the following text in a clear, professional tone suitable for "
        "workplace communication. Be concise, respectful, and avoid jargon or "
        "buzzwords. Sound competent, not stiff.\n\n"
        "Text:\n{text}"
    ),

    "funny": (
        "Rewrite the following text to be genuinely funny — witty, with clever "
        "wordplay, an unexpected twist, or a self-aware joke. Avoid corny dad "
        "jokes, generic emoji spam, and cliches like 'just kidding!'. Keep the "
        "core message recognizable.\n\n"
        "Text:\n{text}"
    ),

    "friendly": (
        "Rewrite the following text in a warm, friendly, conversational tone — "
        "like a kind friend texting back. Avoid being overly cheery or "
        "sycophantic. No 'Hope you're doing well!' filler.\n\n"
        "Text:\n{text}"
    ),

    "ceo": (
        "Rewrite the following text in the voice of a confident, executive-level "
        "communicator: direct, decisive, action-oriented. Short sentences. No "
        "fluff. Think of how a sharp CEO writes a Slack message — clear point, "
        "clear ask, no padding.\n\n"
        "Text:\n{text}"
    ),

    "genz": (
        "Rewrite the following text in current Gen Z internet style: mostly "
        "lowercase, natural slang, max 1-2 emojis total, and use terms like "
        "'fr', 'lowkey', 'no cap', 'it's giving...' ONLY where they fit "
        "naturally. Do not overdo it. Avoid forced or cringey phrasing.\n\n"
        "Text:\n{text}"
    ),

    "caption": (
        "Turn the following into a punchy Instagram caption. Structure:\n"
        "- 1-3 short lines with a strong, scroll-stopping opener\n"
        "- Optional 1-line call to action or question\n"
        "- Blank line, then 4-6 highly relevant hashtags (mix of popular and niche)\n\n"
        "Content:\n{text}"
    ),

    "linkedin": (
        "Turn the following into a thoughtful LinkedIn post:\n"
        "- Strong first-line hook (no 'I'm thrilled to announce' or 'Excited to share')\n"
        "- 2-4 short paragraphs with a real insight, lesson, or POV\n"
        "- End with a reflective question that invites comments\n"
        "- Then a blank line and 3-5 relevant hashtags\n"
        "Professional but human. No corporate cliches.\n\n"
        "Content:\n{text}"
    ),

    "email": (
        "Format the following as a professional email. Structure:\n"
        "Subject: <a short, clear subject line>\n"
        "<blank line>\n"
        "<greeting>,\n"
        "<blank line>\n"
        "<body in 1-3 short paragraphs>\n"
        "<blank line>\n"
        "<sign-off>,\n"
        "<Name>\n\n"
        "Keep it concise and respectful.\n\n"
        "Content:\n{text}"
    ),

    "summarize": (
        "Summarize the following text in 2-3 sentences. Capture the main point "
        "and drop the filler. Match the original register (formal stays formal, "
        "casual stays casual).\n\n"
        "Text:\n{text}"
    ),

    "translate": (
        "Translate the following text to {lang}. Preserve the tone, intent, and "
        "register of the original. If the text contains slang or idioms, use the "
        "natural equivalent in {lang} — not a literal word-for-word translation.\n\n"
        "Text:\n{text}"
    ),

    "hashtags": (
        "Repeat the following text exactly as written, then on a new line below "
        "it add 5-8 highly relevant, specific hashtags. Mix popular tags with "
        "more niche ones for better reach. No spaces inside tags.\n\n"
        "Text:\n{text}"
    ),

    "angry_to_polite": (
        "Rewrite the following message so it is calm, respectful, and "
        "constructive. Preserve the underlying concern or request — do NOT "
        "soften it into nothing or apologize for the writer. The goal is a "
        "message that gets a productive response instead of escalating.\n\n"
        "Text:\n{text}"
    ),

    "viral": (
        "Rewrite the following as a high-engagement social media post:\n"
        "- Scroll-stopping first line\n"
        "- Conversational rhythm with short lines\n"
        "- Ends with something that invites comments, shares, or replies\n"
        "Do NOT add 'MUST READ', '🔥', or other spammy phrasing.\n\n"
        "Content:\n{text}"
    ),
}


def build_prompt(tone: str, text: str, lang: str | None = None) -> str:
    """
    Build the full prompt for a given tone and input.

    Falls back to "polish" if an unknown tone is passed.
    """
    template = TONE_PROMPTS.get(tone, TONE_PROMPTS["polish"])

    if tone == "translate":
        prompt = template.format(text=text, lang=lang or "English")
    else:
        prompt = template.format(text=text)

    return prompt + OUTPUT_RULES
