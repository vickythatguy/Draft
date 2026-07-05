"""Roll individual reactions up into dashboard-ready aggregates."""
from collections import Counter, defaultdict
from typing import Dict, List

from .schema import Persona
from .reaction import Reaction, SENTIMENTS

# Order matters for the diverging sentiment scale (positive -> negative).
SENTIMENT_ORDER = ["love", "like", "meh", "dislike", "cringe"]
_SCORE = {"love": 2, "like": 1, "meh": 0, "dislike": -1, "cringe": -2}

SEGMENT_FIELDS = {
    "age": "age_band",
    "income": "income_bracket",
    "neighbourhood": "neighbourhood",
}

_AGE_ORDER = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
_INCOME_ORDER = ["<$40k", "$40-80k", "$80-125k", "$125-200k", "$200k+"]


def _sentiment_shares(reactions: List[Reaction]) -> Dict[str, float]:
    counts = Counter(r.sentiment for r in reactions)
    n = max(len(reactions), 1)
    return {s: round(counts.get(s, 0) / n, 4) for s in SENTIMENT_ORDER}


def _rates(reactions: List[Reaction]) -> Dict[str, float]:
    n = max(len(reactions), 1)
    actions = Counter(r.action for r in reactions)
    return {
        "share": round(actions.get("share", 0) / n, 4),
        "skip": round(actions.get("scroll_past", 0) / n, 4),
        "watch_full": round((actions.get("watch_full", 0) + actions.get("share", 0)
                             + actions.get("comment", 0)) / n, 4),
        "engage": round((actions.get("like", 0) + actions.get("comment", 0)
                         + actions.get("share", 0)) / n, 4),
    }


def _segment_order(name: str, keys: List[str]) -> List[str]:
    if name == "age":
        return [k for k in _AGE_ORDER if k in keys]
    if name == "income":
        return [k for k in _INCOME_ORDER if k in keys]
    return sorted(keys)


def _pick_quotes(personas: Dict[str, Persona], reactions: List[Reaction],
                 per_sentiment: int = 3) -> List[dict]:
    """Representative verbatims: spread across sentiments, dedup by text."""
    buckets: Dict[str, List[Reaction]] = defaultdict(list)
    for r in reactions:
        buckets[r.sentiment].append(r)
    out, seen = [], set()
    for s in SENTIMENT_ORDER:
        for r in buckets.get(s, [])[: per_sentiment * 3]:
            if r.quote in seen:
                continue
            seen.add(r.quote)
            p = personas[r.persona_id]
            out.append({
                "quote": r.quote,
                "why": r.why,
                "sentiment": r.sentiment,
                "action": r.action,
                "persona": {
                    "age": p.age, "gender": p.gender,
                    "neighbourhood": p.neighbourhood,
                    "occupation": p.occupation,
                    "background": p.background,
                },
            })
            if sum(1 for q in out if q["sentiment"] == s) >= per_sentiment:
                break
    return out


def aggregate(personas: List[Persona], reactions: List[Reaction],
              content: str, mode: str, model: str) -> dict:
    by_id = {p.id: p for p in personas}
    n = len(reactions)

    segments = {}
    for name, attr in SEGMENT_FIELDS.items():
        groups: Dict[str, List[Reaction]] = defaultdict(list)
        for r in reactions:
            groups[getattr(by_id[r.persona_id], attr)].append(r)
        segments[name] = [
            {
                "segment": key,
                "n": len(groups[key]),
                "sentiment": _sentiment_shares(groups[key]),
                **{f"{k}_rate": v for k, v in _rates(groups[key]).items()},
            }
            for key in _segment_order(name, list(groups.keys()))
        ]

    avg_score = round(sum(_SCORE[r.sentiment] for r in reactions) / max(n, 1), 3)

    return {
        "meta": {"n": n, "mode": mode, "model": model, "content": content},
        "sentiment": _sentiment_shares(reactions),
        "avg_score": avg_score,  # -2 (all cringe) .. +2 (all love)
        "rates": _rates(reactions),
        "segments": segments,
        "quotes": _pick_quotes(by_id, reactions),
    }
