"""Persona schema.

Every field earns its place by plausibly changing how someone reacts to a
piece of social content:

- age_band ......... platform fluency, reference points, tolerance for trends
- gender ........... targeting/relatability of many content categories
- neighbourhood .... local references land differently (TTC vs 401 commutes),
                     proxies income/context
- income_bracket ... price sensitivity, luxury vs value framing, ad cynicism
- education ........ media literacy, response to statistical/health claims
- background ....... cultural in-jokes, representation, diaspora relevance
- immigrant_generation . familiarity with Canadian-insider references,
                     interest in home-country/diaspora content
- home_language .... voice, code-switching, reaction to English-only wordplay
- occupation ....... daypart/attention budget, topical relevance (e.g. gig
                     workers vs office workers see gig-economy ads differently)
- platforms ........ whether they'd even be served this format
- daily_minutes .... scroll speed; heavy users are more jaded, skip faster
- interests ........ the single biggest driver of watch vs scroll-past
- values ........... what makes content share-worthy vs cringe for them
- humour_style ..... whether a joke lands (dry Toronto irony vs earnest)
- agreeableness .... politeness bias control: low scorers say it's bad
- skepticism ....... ad/claim cynicism; high scorers smell "sponsored" a mile
- sharing_propensity . baseline probability of ever sharing anything
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict


@dataclass
class Persona:
    id: str
    age_band: str
    age: int
    gender: str
    neighbourhood: str
    income_bracket: str
    education: str
    background: str
    immigrant_generation: str
    home_language: str
    occupation: str
    platforms: List[str]
    daily_minutes: int
    interests: List[str]
    values: List[str]
    humour_style: str
    agreeableness: int      # 1 (blunt) .. 5 (very polite)
    skepticism: int         # 1 (trusting) .. 5 (deeply cynical about ads)
    sharing_propensity: int # 1 (never shares) .. 5 (shares constantly)

    def to_dict(self) -> Dict:
        return asdict(self)

    def voice_card(self) -> str:
        """Compact description used inside the reaction prompt."""
        return (
            f"{self.age}-year-old {self.gender} from {self.neighbourhood}, Toronto. "
            f"Background: {self.background}; {self.immigrant_generation}; speaks "
            f"{self.home_language} at home. Works as {self.occupation}; household "
            f"income {self.income_bracket}; education: {self.education}. "
            f"Scrolls {', '.join(self.platforms) or 'almost nothing'} about "
            f"{self.daily_minutes} min/day. Into: {', '.join(self.interests)}. "
            f"Values: {', '.join(self.values)}. Humour: {self.humour_style}. "
            f"Politeness {self.agreeableness}/5, ad-skepticism {self.skepticism}/5, "
            f"likelihood to ever share things {self.sharing_propensity}/5."
        )
