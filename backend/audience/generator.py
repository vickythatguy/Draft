"""Sample a synthetic Toronto audience matching real 2021-census marginals.

Sampling strategy (v0): weighted draws from census marginals with the
conditional structure that matters most for content reactions —
income | neighbourhood, home language | background, platforms | age.
Deterministic under a seed so runs are reproducible.
"""
import random
from typing import List

from data import toronto_2021 as T
from .schema import Persona

_AGE_RANGE = {
    "18-24": (18, 24), "25-34": (25, 34), "35-44": (35, 44),
    "45-54": (45, 54), "55-64": (55, 64), "65+": (65, 84),
}


def _pick(rng: random.Random, dist: dict) -> str:
    return rng.choices(list(dist.keys()), weights=list(dist.values()))[0]


def _income_for(rng: random.Random, neighbourhood: str) -> str:
    tilt = T.INCOME_TILT[neighbourhood]
    weights = [c * t for c, t in zip(T.INCOME_CITY, tilt)]
    return rng.choices(T.INCOME_BRACKETS, weights=weights)[0]


def _language_for(rng: random.Random, background: str) -> str:
    options = T.HOME_LANGUAGE_BY_BACKGROUND.get(background, T.DEFAULT_HOME_LANGUAGE)
    langs, weights = zip(*options)
    return rng.choices(langs, weights=weights)[0]


def _generation_for(rng: random.Random, background: str) -> str:
    gen = _pick(rng, T.IMMIGRANT_GENERATION)
    # Long-settled European-descent Torontonians skew to deeper generations.
    if background == "White (European descent)" and "recent" in gen and rng.random() < 0.6:
        gen = "third generation or deeper"
    return gen


def make_persona(rng: random.Random, idx: int) -> Persona:
    age_band = _pick(rng, T.AGE_BANDS)
    lo, hi = _AGE_RANGE[age_band]
    neighbourhood = _pick(rng, T.NEIGHBOURHOODS)
    background = _pick(rng, T.BACKGROUNDS)

    platforms = [p for p, prob in T.PLATFORM_BY_AGE[age_band].items()
                 if rng.random() < prob]

    occupation = _pick(rng, T.OCCUPATIONS)
    if age_band == "65+" and rng.random() < 0.7:
        occupation = "retired"
    elif age_band == "18-24" and rng.random() < 0.4:
        occupation = "student"

    interests = rng.sample(T.INTERESTS, k=rng.randint(2, 4))
    if "diaspora culture & home-country news" in interests and \
            background == "White (European descent)":
        interests.remove("diaspora culture & home-country news")
        interests.append("cottage life & outdoors")

    return Persona(
        id=f"p{idx:05d}",
        age_band=age_band,
        age=rng.randint(lo, hi),
        gender=_pick(rng, T.GENDER),
        neighbourhood=neighbourhood,
        income_bracket=_income_for(rng, neighbourhood),
        education=_pick(rng, T.EDUCATION),
        background=background,
        immigrant_generation=_generation_for(rng, background),
        home_language=_language_for(rng, background),
        occupation=occupation,
        platforms=platforms,
        daily_minutes=max(5, int(rng.gauss(75 if age_band in ("18-24", "25-34") else 45, 25))),
        interests=interests,
        values=rng.sample(T.VALUES, k=2),
        humour_style=_pick(rng, T.HUMOUR_STYLES),
        agreeableness=rng.randint(1, 5),
        skepticism=rng.choices([1, 2, 3, 4, 5], weights=[1, 2, 3, 3, 2])[0],
        sharing_propensity=rng.choices([1, 2, 3, 4, 5], weights=[3, 3, 2, 1.5, 0.5])[0],
    )


def generate_audience(n: int, seed: int = 42) -> List[Persona]:
    rng = random.Random(seed)
    return [make_persona(rng, i) for i in range(n)]
