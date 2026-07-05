"""Demographic distributions for Toronto, grounded in the 2021 Census.

Every constant carries a SOURCE comment. Values marked APPROX are rounded or
re-normalized from published aggregates (e.g. adult-only re-normalization);
replace them with exact StatCan table pulls or PUMF microdata for production.
All distributions describe TYPES of people from public aggregate data — no
individual-level data (PIPEDA-friendly by construction).
"""

# SOURCE: StatCan 2021 Census Profile, Toronto CSD. Population 2,794,356.
CITY_POPULATION = 2_794_356

# Adult (18+) age distribution, APPROX re-normalized from the 2021 age pyramid
# (CMA: 15.6% 0-14, 68.3% 15-64, 16.2% 65+; city skews to 25-39).
# SOURCE: City of Toronto 2021 Census Backgrounder — Age, Sex at Birth.
AGE_BANDS = {
    "18-24": 0.11,
    "25-34": 0.22,
    "35-44": 0.18,
    "45-54": 0.15,
    "55-64": 0.14,
    "65+":   0.20,
}

# SOURCE: 2021 census — women slightly over half of adult population.
GENDER = {"woman": 0.52, "man": 0.47, "nonbinary": 0.01}

# Former-municipality "neighbourhood areas" with APPROX population weights.
# SOURCE: City of Toronto planning district populations (see docs/RESEARCH.md).
NEIGHBOURHOODS = {
    "Downtown / Old Toronto": 0.28,
    "North York":             0.24,
    "Scarborough":            0.23,
    "Etobicoke":              0.13,
    "East York":              0.07,
    "York":                   0.05,
}

# Household income brackets. City-wide APPROX from median $84,000 and the
# published bracket curve; per-neighbourhood shift reproduces the documented
# polarization (Scarborough/York low, Old Toronto bimodal, North York mixed).
# SOURCE: StatCan 2021 profile; U of T School of Cities; Three Cities report.
INCOME_BRACKETS = ["<$40k", "$40-80k", "$80-125k", "$125-200k", "$200k+"]
INCOME_CITY = [0.22, 0.25, 0.21, 0.18, 0.14]
# Multiplicative tilt per area applied to INCOME_CITY, then re-normalized.
INCOME_TILT = {
    "Downtown / Old Toronto": [0.9, 0.8, 0.9, 1.2, 1.6],
    "North York":             [1.0, 1.0, 1.0, 1.0, 1.1],
    "Scarborough":            [1.4, 1.3, 1.0, 0.7, 0.4],
    "Etobicoke":              [1.0, 1.0, 1.0, 1.0, 1.0],
    "East York":              [1.0, 1.1, 1.1, 0.9, 0.7],
    "York":                   [1.4, 1.3, 1.0, 0.7, 0.3],
}

# Racialized-group / background mix, city of Toronto 2021 (55.7% racialized).
# SOURCE: City of Toronto 2021 Census Backgrounder — Immigration & Ethnoracial.
BACKGROUNDS = {
    "White (European descent)": 0.443,
    "South Asian":              0.140,
    "Chinese":                  0.107,
    "Black":                    0.096,
    "Filipino":                 0.055,
    "Latin American":           0.034,
    "West Asian / Arab":        0.040,
    "Southeast Asian":          0.015,
    "Korean":                   0.015,
    "Japanese":                 0.005,
    "Multiple / other":         0.050,
}

# Immigrant generation. SOURCE: 46.6% immigrants; recent (2011-21) 12.4%.
# Split of non-immigrants into 2nd vs 3rd+ generation is APPROX from CMA data.
IMMIGRANT_GENERATION = {
    "recent immigrant (<10y)":     0.124,
    "established immigrant":       0.342,
    "second generation":           0.280,
    "third generation or deeper":  0.254,
}

# Non-official home language shares *within* each background (APPROX from the
# 25.9% city-wide rate and top home languages: Mandarin, Cantonese, Tagalog,
# Spanish, Tamil, Portuguese, Italian).
# SOURCE: City of Toronto 2021 language backgrounder; CBC (Mandarin #2).
HOME_LANGUAGE_BY_BACKGROUND = {
    "Chinese":            [("Mandarin", 0.40), ("Cantonese", 0.35), ("English", 0.25)],
    "South Asian":        [("Tamil", 0.12), ("Urdu/Hindi/Punjabi", 0.33), ("English", 0.55)],
    "Filipino":           [("Tagalog", 0.45), ("English", 0.55)],
    "Latin American":     [("Spanish", 0.55), ("English", 0.45)],
    "West Asian / Arab":  [("Arabic/Farsi", 0.45), ("English", 0.55)],
    "Korean":             [("Korean", 0.55), ("English", 0.45)],
    "White (European descent)": [("Portuguese", 0.05), ("Italian", 0.05), ("English", 0.90)],
}
DEFAULT_HOME_LANGUAGE = [("English", 1.0)]

# Education, adults 25-64. APPROX from ~44.5% bachelor+ in Toronto CMA.
# SOURCE: StatCan 2021 education release.
EDUCATION = {
    "high school or less":   0.30,
    "college / trades":      0.25,
    "bachelor's degree":     0.28,
    "graduate degree":       0.17,
}

# Platform usage probability by age band (Canada 2025 surveys).
# SOURCE: DataReportal Digital 2025 Canada; Environics 2025; Made in CA.
PLATFORM_BY_AGE = {
    #            TikTok  Instagram  YouTube(shorts)  Facebook(reels)
    "18-24": {"tiktok": 0.65, "instagram": 0.52, "youtube": 0.80, "facebook": 0.35},
    "25-34": {"tiktok": 0.59, "instagram": 0.54, "youtube": 0.78, "facebook": 0.55},
    "35-44": {"tiktok": 0.46, "instagram": 0.40, "youtube": 0.70, "facebook": 0.65},
    "45-54": {"tiktok": 0.30, "instagram": 0.39, "youtube": 0.60, "facebook": 0.70},
    "55-64": {"tiktok": 0.13, "instagram": 0.21, "youtube": 0.50, "facebook": 0.72},
    "65+":   {"tiktok": 0.13, "instagram": 0.21, "youtube": 0.45, "facebook": 0.70},
}

# Occupation mix, APPROX from Toronto labour-force composition.
OCCUPATIONS = {
    "office / professional": 0.30,
    "tech / creative":       0.12,
    "healthcare / education":0.14,
    "retail / service":      0.16,
    "trades / transport":    0.12,
    "student":               0.07,
    "retired":               0.14,
    "gig / self-employed":   0.05,
}

# Cultural-personality vocabularies (research-derived, see docs/RESEARCH.md §2).
HUMOUR_STYLES = {
    "dry / deadpan":       0.25,
    "self-deprecating":    0.25,
    "absurdist / memey":   0.18,
    "earnest / wholesome": 0.20,
    "not much for jokes":  0.12,
}

INTERESTS = [
    "food & restaurants", "raptors / leafs / sports", "housing & real estate",
    "TTC & commuting", "local news", "fashion & sneakers", "fitness",
    "parenting", "personal finance", "music & concerts", "gaming",
    "travel", "immigration stories", "small business", "comedy & memes",
    "beauty & skincare", "tech & gadgets", "cottage life & outdoors",
    "cooking at home", "diaspora culture & home-country news",
]

VALUES = [
    "multiculturalism", "fairness / don't oversell", "supporting local",
    "practicality / value for money", "community & family",
    "environment", "work-life balance", "getting ahead / hustle",
]
