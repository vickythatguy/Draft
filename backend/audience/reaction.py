"""Reaction engine: persona + stimulus -> structured reaction.

Three modes:
- "mock"  : deterministic heuristic engine. Zero cost, runs offline, varies
            sensibly with the content text. Default when no API key is set.
- "live"  : Anthropic API, claude-haiku-4-5 (cheapest/fastest tier) with
            structured outputs, fanned out over a thread pool.
- "batch" : Message Batches API — 50% of live cost, completes within ~1h.
            Right choice for audiences in the thousands when latency is fine.
"""
import hashlib
import json
import os
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from typing import List, Optional

from .schema import Persona
from .prompts import REACTION_SYSTEM_PROMPT, REACTION_SCHEMA, reaction_user_prompt

# Cheap/fast tier for bulk reactions ($1/$5 per MTok). Override with env var.
DEFAULT_MODEL = os.environ.get("REACTION_MODEL", "claude-haiku-4-5")
MAX_TOKENS = 300
CONCURRENCY = int(os.environ.get("REACTION_CONCURRENCY", "8"))

SENTIMENTS = ["love", "like", "meh", "dislike", "cringe"]
ACTIONS = ["share", "comment", "like", "watch_full", "watch_part", "scroll_past"]


@dataclass
class Reaction:
    persona_id: str
    sentiment: str
    action: str
    quote: str
    why: str

    def to_dict(self):
        return asdict(self)


def api_key_available() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def _platform_hint(content: str, persona: Persona) -> str:
    lowered = content.lower()
    for p in ("tiktok", "instagram", "youtube", "facebook"):
        if p in lowered:
            return p
    return persona.platforms[0] if persona.platforms else "instagram"


# ---------------------------------------------------------------------------
# Mock engine (offline default)
# ---------------------------------------------------------------------------

_QUOTES = {
    "love": [
        "ok this is actually so good, sending to the group chat",
        "not me watching this three times in a row lol",
        "finally content that gets it. more of this please",
        "yooo this is exactly my life, who made this",
    ],
    "like": [
        "ha, decent. the {interest} bit got me",
        "pretty solid ngl, would watch another one",
        "cute. not sharing it but I watched the whole thing",
        "ok that was better than most of the stuff on my feed",
    ],
    "meh": [
        "it's fine I guess? feels like every other {interest} video",
        "watched half, got the idea, kept scrolling",
        "sorry but I've seen this exact format a hundred times",
        "eh. not for me, but somebody's aunt will love it",
    ],
    "dislike": [
        "this is trying way too hard",
        "who is this even for? skip",
        "the algorithm really thought I'd want this huh",
        "nah. felt like an ad the second it started",
    ],
    "cringe": [
        "oh this is painful. instant scroll",
        "brands need to stop doing this, genuinely embarrassing",
        "the fake enthusiasm is giving pyramid scheme",
        "I physically recoiled. who approved this",
    ],
}

_AD_WORDS = re.compile(r"\b(ad|sponsored|brand|promo|sale|discount|buy|launch|product)\b", re.I)


def _mock_reaction(persona: Persona, content: str, content_seed: int) -> Reaction:
    rng = random.Random(f"{persona.id}:{content_seed}")
    lowered = content.lower()

    # Interest affinity: keyword overlap between content and persona interests.
    affinity = 0.0
    matched = None
    for interest in persona.interests:
        for word in re.findall(r"[a-z]{4,}", interest.lower()):
            if word in lowered:
                affinity += 1.2
                matched = interest
                break
    # Local-identity content travels well in Toronto.
    for token in ("toronto", "ttc", "raptors", "leafs", "scarborough", "gta",
                  "drake", "six", "canada", "canadian", "winter", "housing", "rent"):
        if token in lowered:
            affinity += 0.5

    # Ad cynicism and platform mismatch.
    if _AD_WORDS.search(content):
        affinity -= 0.45 * persona.skepticism
    hint = _platform_hint(content, persona)
    if hint not in persona.platforms:
        affinity -= 1.2
    # Heavy scrollers are jaded; polite people round up.
    affinity -= (persona.daily_minutes / 120.0) * 0.4
    affinity += (persona.agreeableness - 3) * 0.35
    if persona.humour_style in ("dry / deadpan", "absurdist / memey") and \
            any(w in lowered for w in ("funny", "joke", "comedy", "skit", "meme")):
        affinity += 0.8
    affinity += rng.gauss(0, 0.9)

    if affinity > 2.2:
        sentiment = "love"
    elif affinity > 1.0:
        sentiment = "like"
    elif affinity > -0.6:
        sentiment = "meh"
    elif affinity > -1.8:
        sentiment = "dislike"
    else:
        sentiment = "cringe"

    share_chance = {"love": 0.30, "like": 0.06, "meh": 0.0, "dislike": 0.0, "cringe": 0.01}
    if rng.random() < share_chance[sentiment] * (persona.sharing_propensity / 3.0):
        action = "share"
    elif sentiment == "love":
        action = rng.choice(["watch_full", "like", "comment"])
    elif sentiment == "like":
        action = rng.choice(["watch_full", "watch_part", "like"])
    elif sentiment == "meh":
        action = rng.choice(["watch_part", "scroll_past", "scroll_past"])
    else:
        action = "scroll_past"

    quote = rng.choice(_QUOTES[sentiment]).format(
        interest=(matched or rng.choice(persona.interests)))
    why = matched and f"matches interest: {matched}" or (
        "smells like an ad" if _AD_WORDS.search(content) and persona.skepticism >= 4
        else "low relevance to them" if sentiment in ("meh", "dislike", "cringe")
        else "tone matched their humour")
    return Reaction(persona.id, sentiment, action, quote, why)


# ---------------------------------------------------------------------------
# Live engine (Anthropic API)
# ---------------------------------------------------------------------------

def _live_one(client, persona: Persona, content: str, model: str) -> Reaction:
    from anthropic import APIStatusError
    prompt = reaction_user_prompt(persona.voice_card(), content,
                                  _platform_hint(content, persona))
    try:
        response = client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            system=REACTION_SYSTEM_PROMPT,
            output_config={"format": {"type": "json_schema", "schema": REACTION_SCHEMA}},
            messages=[{"role": "user", "content": prompt}],
        )
        if response.stop_reason == "refusal" or not response.content:
            return Reaction(persona.id, "meh", "scroll_past",
                            "(no reaction returned)", "model declined")
        text = next(b.text for b in response.content if b.type == "text")
        data = json.loads(text)
        return Reaction(persona.id, data["sentiment"], data["action"],
                        data["quote"], data["why"])
    except (APIStatusError, StopIteration, json.JSONDecodeError, KeyError) as e:
        # One bad call shouldn't sink a 1000-agent run; degrade to mock.
        return _mock_reaction(persona, content, _content_seed(content))


def _run_live(personas: List[Persona], content: str, model: str) -> List[Reaction]:
    import anthropic
    client = anthropic.Anthropic()
    results: List[Optional[Reaction]] = [None] * len(personas)
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        futures = {pool.submit(_live_one, client, p, content, model): i
                   for i, p in enumerate(personas)}
        for fut in as_completed(futures):
            results[futures[fut]] = fut.result()
    return results  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Batch engine (50% cost, async — best for thousands of agents)
# ---------------------------------------------------------------------------

def _run_batch(personas: List[Persona], content: str, model: str,
               poll_seconds: int = 30) -> List[Reaction]:
    import anthropic
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    client = anthropic.Anthropic()
    requests = [
        Request(
            custom_id=p.id,
            params=MessageCreateParamsNonStreaming(
                model=model,
                max_tokens=MAX_TOKENS,
                system=REACTION_SYSTEM_PROMPT,
                output_config={"format": {"type": "json_schema", "schema": REACTION_SCHEMA}},
                messages=[{"role": "user", "content": reaction_user_prompt(
                    p.voice_card(), content, _platform_hint(content, p))}],
            ),
        )
        for p in personas
    ]
    batch = client.messages.batches.create(requests=requests)
    while True:
        batch = client.messages.batches.retrieve(batch.id)
        if batch.processing_status == "ended":
            break
        time.sleep(poll_seconds)

    by_id = {p.id: p for p in personas}
    reactions = []
    for result in client.messages.batches.results(batch.id):
        persona = by_id[result.custom_id]
        if result.result.type == "succeeded":
            msg = result.result.message
            try:
                text = next(b.text for b in msg.content if b.type == "text")
                data = json.loads(text)
                reactions.append(Reaction(persona.id, data["sentiment"],
                                          data["action"], data["quote"], data["why"]))
                continue
            except (StopIteration, json.JSONDecodeError, KeyError):
                pass
        reactions.append(_mock_reaction(persona, content, _content_seed(content)))
    return reactions


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _content_seed(content: str) -> int:
    return int(hashlib.sha256(content.encode()).hexdigest()[:8], 16)


def run_reactions(personas: List[Persona], content: str,
                  mode: str = "auto", model: str = DEFAULT_MODEL) -> List[Reaction]:
    """mode: auto | mock | live | batch."""
    if mode == "auto":
        mode = "live" if api_key_available() else "mock"
    if mode == "mock":
        seed = _content_seed(content)
        return [_mock_reaction(p, content, seed) for p in personas]
    if mode == "live":
        return _run_live(personas, content, model)
    if mode == "batch":
        return _run_batch(personas, content, model)
    raise ValueError(f"unknown mode: {mode}")
