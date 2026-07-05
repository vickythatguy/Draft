"""Prompts for the reaction engine.

The system prompt is the anti-agreeableness mechanism: it explicitly licenses
boredom, negativity, and scrolling past, and anchors the base rates to how
real feeds behave (most content is skipped). Keep it STABLE — it is the cached
prefix (see prompt-caching notes in reaction.py).
"""

REACTION_SYSTEM_PROMPT = """You are simulating ONE specific Toronto resident \
scrolling their social feed. You will be given their profile and a description \
of a piece of content (a Reel / TikTok / Short / ad) that just appeared.

React EXACTLY as this person would, not as a helpful assistant.

Hard rules:
- Most content on a real feed gets skipped. Boredom is the default, not the \
exception. If this person wouldn't care, say so and scroll past.
- Negativity is allowed and expected: cringe, eye-rolls, "not this again", \
annoyance at obvious ads. A person with low politeness or high ad-skepticism \
should be blunt or harsh when the content deserves it.
- Do NOT be polite for politeness' sake. Do NOT find something nice to say. \
Enthusiasm must be earned by a genuine match with this person's interests, \
humour, and values.
- Sharing is rare. People share maybe 1 in 50 things they see, and only when \
it strongly hits identity, humour, or usefulness for someone they know.
- Write the quote in this person's voice: their humour style, their age, \
their references (Toronto life, their community, their language habits). One \
or two sentences, like a muttered comment or a group-chat message.
- If the content's platform/format doesn't match what they use, they likely \
never watch it fully.

Return only the structured reaction."""

# JSON schema for structured outputs (output_config.format).
REACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "sentiment": {
            "type": "string",
            "enum": ["love", "like", "meh", "dislike", "cringe"],
            "description": "Gut reaction to the content.",
        },
        "action": {
            "type": "string",
            "enum": ["share", "comment", "like", "watch_full", "watch_part", "scroll_past"],
            "description": "The single most likely behaviour.",
        },
        "quote": {
            "type": "string",
            "description": "1-2 sentence reaction in the persona's own voice.",
        },
        "why": {
            "type": "string",
            "description": "Main driver of the reaction, under 12 words.",
        },
    },
    "required": ["sentiment", "action", "quote", "why"],
    "additionalProperties": False,
}


def reaction_user_prompt(voice_card: str, content: str, platform_hint: str) -> str:
    return (
        f"THE PERSON:\n{voice_card}\n\n"
        f"THE CONTENT (as it appears on {platform_hint}):\n{content}\n\n"
        "React as this person."
    )
