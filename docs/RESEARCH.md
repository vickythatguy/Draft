# Research Summary — Toronto Demographics & Cultural Personality

This document records the live research that grounds the v0 persona generator,
and how each finding maps into persona attributes. All census figures are from
the **2021 Census of Population (Statistics Canada)** for the **City of
Toronto** (census subdivision) unless noted; platform figures are 2025
Canada-level surveys.

## 1. Demographics (what the generator samples from)

### Population & age
- City of Toronto population: **2,794,356** (2021) — Canada's largest city.
- Age structure (CMA): **15.6%** aged 0–14, **68.3%** aged 15–64, **16.2%** 65+;
  average age ≈ **41.5**. The generator models the **adult (18+) audience**,
  re-normalized from these bands.
- Sources: [StatCan Census Profile — Toronto](https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/page.cfm?Lang=E&SearchText=toronto&GENDERlist=1%2C2%2C3&STATISTIClist=1&DGUIDlist=2021A00053520005&HEADERlist=0),
  [StatCan Focus on Geography — Toronto CMA](https://www12.statcan.gc.ca/census-recensement/2021/as-sa/fogs-spg/page.cfm?lang=e&topic=2&dguid=2021S0503535),
  [City of Toronto census backgrounder (age/sex/dwelling)](https://www.toronto.ca/wp-content/uploads/2022/04/9654-City-Planning-2021-Census-Backgrounder-Age-Sex-Gender-DwellingType.pdf).

### Income
- Median household income: **$84,000** ($74,000 after tax); 1,160,890
  households; 33.2% one-person households.
- Income is **strongly spatially polarized**: Toronto is often called the
  inequality capital of Canada — Bridle Path-area medians run ~6× Jane–Finch;
  parts of Scarborough sit under $35k while central-north pockets exceed $200k.
  The generator therefore samples income **conditionally on neighbourhood**.
- Sources: [Point2Homes summary of StatCan profile](https://www.point2homes.com/CA/Demographics/ON/Toronto-Demographics.html),
  [City of Toronto backgrounder (families/income)](https://www.toronto.ca/wp-content/uploads/2022/07/9877-City-Planning-2021-Census-Backgrounder-Families-Hhlds-Marital-Status-Income.pdf),
  [U of T School of Cities — neighbourhood income](https://schoolofcities.github.io/neighbourhood-income-toronto-2020/),
  [DataLabTO income map](https://www.datalabto.ca/incomes/).

### Ethnicity & immigration
- **55.7%** of Toronto residents are racialized (visible minorities), up from
  51.5% in 2016. Largest groups: **South Asian 14.0%**, **Chinese 10.7%**,
  **Black 9.6%**, plus large Filipino, Latin American, West Asian, Arab,
  Korean and Southeast Asian communities.
- **46.6%** of residents are immigrants (1,286,140 people); recent immigrants
  (2011–2021) are **12.4%** of the population.
- Sources: [City of Toronto 2021 backgrounder — immigration/ethnoracial](https://www.toronto.ca/wp-content/uploads/2023/03/8ff2-2021-Census-Backgrounder-Immigration-Ethnoracial-Mobility-Migration-Religion-FINAL1.1-corrected.pdf),
  [StatCan Focus on Geography — Toronto](https://www12.statcan.gc.ca/census-recensement/2021/as-sa/fogs-spg/page.cfm?lang=E&topic=10&dguid=2021A00053520005),
  [Wikipedia — Demographics of Toronto](https://en.wikipedia.org/wiki/Demographics_of_Toronto).

### Language
- Only **50.2%** of residents report English as their sole mother tongue;
  **42.5%** have a non-official mother tongue. **25.9%** regularly speak a
  non-official language at home — top home languages: **Mandarin (86,150),
  Cantonese (74,845), Tagalog (51,355), Spanish (46,355), Tamil (40,825)**,
  plus Portuguese and Italian.
- Sources: [City of Toronto 2021 language backgrounder](https://www.toronto.ca/wp-content/uploads/2022/08/868f-2021-Census-Backgrounder-Language-FINAL.pdf),
  [CBC — Mandarin now Toronto's 2nd language](https://www.cbc.ca/news/canada/toronto/mandarin-now-toronto-s-2nd-most-common-first-language-reflecting-years-of-demographic-change-1.6554155).

### Neighbourhood distribution
- The generator uses the six former municipalities as coarse "neighbourhood
  areas" (Old Toronto/Downtown, North York, Scarborough, Etobicoke, East York,
  York), with population weights approximated from City of Toronto planning
  data, and income distributions shifted per area to reproduce the documented
  polarization (Scarborough/York lower median, central Old Toronto bimodal,
  North York mixed with wealthy pockets).
- Source: [City of Toronto — Neighbourhoods & Communities](https://www.toronto.ca/city-government/data-research-maps/neighbourhoods-communities/),
  [Three Cities in Toronto (income polarization)](http://3cities.neighbourhoodchange.ca/wp-content/themes/3-Cities/pdfs/three-cities-in-toronto.pdf).

### Platform usage (Canada, 2025)
- TikTok usage by age: 18–24 **65%**, 25–34 **59%**, 35–44 **46%**, 45–54
  **30%**, 55+ **13%**. Instagram: 25–34 **54%**, 18–24 **52%**, 35–44 **40%**,
  45–54 **39%**, 55+ **21%**. YouTube is the most-used platform after Facebook
  (~53% weekly). Women skew slightly higher on both TikTok and Instagram.
- Sources: [DataReportal Digital 2025: Canada](https://datareportal.com/reports/digital-2025-canada),
  [Environics 2025 social media trends](https://environics.ca/insights/articles/2025-social-media-trends-in-canada/),
  [Made in CA — TikTok statistics](https://madeinca.ca/tiktok-statistics-canada/).

## 2. Cultural personality (what shapes reaction style)

Findings, each mapped to a generator/prompt mechanism:

| Finding | Source | How it's encoded |
|---|---|---|
| Canadian humour is self-deprecating, satirical, wordplay-heavy; laughs at national traits (politeness, weather, "sorry") | [Grokipedia — Canadian humour](https://grokipedia.com/page/Canadian_humour), [Go2Canada guide](https://www.go2canadaeducation.ca/faq/understanding-canadian-humour-a-guide-for-international-students) | `humour_style` persona field (dry/self-deprecating/absurdist/earnest/none); reaction prompt tells agents their humour style |
| Politeness is real but thinning under stress; bluntness online is common, especially among younger users | [Narrative Research](https://narrativeresearch.ca/rising-stress-levels-are-threatening-canadas-reputation-for-politeness/) | `agreeableness` field + system prompt explicitly **licensing negativity and scrolling past** so polite bias doesn't flatten reactions |
| Light-hearted US-comparison jokes land well; smugness about healthcare/politics is a shareable trope | [Washington Post](https://www.washingtonpost.com/news/worldviews/wp/2013/01/05/are-canadians-so-funny-because-theyre-making-fun-of-america/) | Interest tags + mock-engine share bonus for local-identity content |
| Toronto-specific identity: TTC complaints, housing costs, weather, Raptors/Leafs, neighbourhood pride, multicultural food culture | city-data synthesis above | `interests` vocabulary and quote banks use these touchstones |
| Half the city grew up in another language/culture; recent immigrants engage differently with Canadian-insider references | census language/immigration data above | `immigrant_generation` + `home_language` alter voice and reference familiarity in prompts |

## 3. Where real data plugs in (marked in code)

- `backend/data/toronto_2021.py` — every distribution is a constant with a
  `# SOURCE:` comment. Replace approximations with exact StatCan table pulls
  (98-316-X2021001 profile tables) or, better, PUMF microdata for joint
  distributions.
- Platform-by-age table — swap for licensed survey data (Environics, Vividata).
- Neighbourhood weights — replace 6 coarse areas with the City of Toronto's
  158 official neighbourhoods (open data portal has census profiles per
  neighbourhood).

## 4. Known simplifications

- Marginals are sampled mostly independently (income conditioned on
  neighbourhood, language conditioned on ethnicity, platforms conditioned on
  age). Real joint correlations (education × income × ethnicity) need PUMF
  microdata.
- Percentages were rounded and small categories merged; each constant carries
  its source so it can be audited.
- Privacy: personas are **types**, sampled from public aggregate
  distributions. No individual-level data is used anywhere (PIPEDA-friendly).
