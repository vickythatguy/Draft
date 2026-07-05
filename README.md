# Synthetic Audience — Toronto v0

Test a Reel / TikTok / YouTube Short / ad against **thousands of AI agents
grounded in the real demographics and cultural personality of Toronto** —
before you publish. The product is a **pre-filter**: it screens many content
ideas down to the best few cheaply, ahead of real A/B testing. It is not a
replacement for testing with real humans.

**Differentiator:** regional grounding. Agents are sampled to match the 2021
Census of Population for the City of Toronto (age, income by neighbourhood,
racialized-group mix, immigration generation, home language) and carry
research-derived Canadian cultural personality (self-deprecating humour,
politeness-with-limits, local touchstones). See `docs/RESEARCH.md` for the
sources and how each finding maps to a persona attribute.

## Layout

```
docs/RESEARCH.md            research summary + sources + data-mapping table
backend/
  data/toronto_2021.py      census-grounded distributions (every constant sourced)
  audience/schema.py        persona schema (each field justified)
  audience/generator.py     representative population sampler (seeded)
  audience/prompts.py       reaction system prompt (licenses negativity/boredom)
  audience/reaction.py      mock | live (Claude Haiku) | batch engines
  audience/aggregate.py     sentiment/segment/share-skip rollups + verbatims
  audience/validation.py    human-panel parity hook
  server.py                 FastAPI API
  run_demo.py               CLI demo (works offline)
  validation/panel_template.csv
frontend/                   React + Tailwind + Recharts dashboard
```

## Run it offline (no API key, $0)

Backend (Python 3.10+):

```bash
cd backend
pip install -r requirements.txt
python run_demo.py                      # CLI smoke test, mock engine
uvicorn server:app --reload --port 8000
```

Dashboard:

```bash
cd frontend
npm install
npm run dev                             # http://localhost:5173 (proxies /api → :8000)
```

Type a content description, pick an audience size, hit **Run audience**. With
no API key the deterministic **mock engine** runs: it scores interest overlap,
ad-cynicism, platform-age fit and politeness, so results vary sensibly with
the input — good for developing the UI and the aggregation pipeline.

## Go live (real LLM reactions)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
uvicorn server:app --port 8000
```

- Default model: **`claude-haiku-4-5`** (cheapest/fastest tier, ~$1/$5 per
  MTok). Each reaction is one small structured-output call (~500 in / ~120 out
  tokens ⇒ roughly **$1 per 1,000 agents**; override with `REACTION_MODEL`).
- `mode=live` fans requests over a thread pool (`REACTION_CONCURRENCY`, default 8).
- `mode=batch` uses the **Message Batches API** — 50% of live cost, completes
  asynchronously (usually <1h). Right choice for audiences in the thousands;
  use it via `python run_demo.py --mode batch` or the API.
- Failed/refused calls degrade to the mock engine so one bad call never sinks
  a 1,000-agent run.

### API

- `GET  /api/health` — is a key configured?
- `GET  /api/population?n=1000` — audit the sampled population vs census marginals
- `POST /api/run` — `{content, audience_size, seed, mode}` → full result JSON
- `POST /api/validate` — upload a human-panel CSV, get parity metrics vs the last run

## Validation hook (do this before trusting it)

1. Pick 3–5 pieces of content and run them through the synthetic audience.
2. Run the same content past a small real panel of Torontonians (n=50–200,
   quota-matched on age × area; Prolific/Dynata). Record each respondent using
   the enums in `backend/validation/panel_template.csv`.
3. `POST /api/validate` with the CSV. You get `sentiment_mae`, `share_gap`,
   `skip_gap`, and `direction_hit` (does synthetic agree with humans on
   net-positive vs net-negative — the minimum claim a pre-filter must clear).
4. Track these across contents. If `direction_hit` isn't ~80%+, tune the
   reaction prompt / persona fields before selling any predictive claim.

## Exact next steps

1. **Validate**: run the human-panel loop above on real client content; tune
   the system prompt against measured agreeableness bias (compare synthetic
   negative share vs human negative share).
2. **Tighten the data**: replace APPROX constants in
   `backend/data/toronto_2021.py` with exact StatCan table pulls; move from 6
   coarse areas to the City of Toronto's 158 official neighbourhoods; use PUMF
   microdata for joint distributions (education × income × ethnicity).
3. **Cost/scale**: default big runs to the Batches API; add prompt caching if
   the system prompt grows past the cacheable minimum; persist runs in SQLite.
4. **Product**: compare-two-contents view (the actual pre-filter workflow),
   exportable PDF report, per-segment drill-down into raw verbatims.
5. **Expand regions**: the data module is the only Toronto-specific file —
   add `vancouver_2021.py`, `montreal_2021.py` behind a region picker.

## Honest limitations (v0)

- **Unvalidated**: no human-panel comparison has been run yet; treat every
  number as a hypothesis until the parity loop says otherwise.
- **LLM bias**: even with the negativity-licensing prompt, LLM agents skew
  agreeable and articulate; verbatims read cleaner than real comments.
- **Marginals ≠ joints**: distributions are census-true individually but
  correlations between fields are hand-modelled (income|neighbourhood,
  language|background, platform|age only).
- **Content is text-only**: agents react to a *description* of the creative,
  not the actual video — pacing, faces, music and edit quality are invisible.
- **Mock engine is a toy**: useful for UI development and plumbing, not for
  decisions.
- **Privacy**: personas are types sampled from public aggregates (PIPEDA-
  friendly); keep it that way — never seed personas from individual user data.

**What to validate first:** direction agreement (net-positive vs net-negative)
between synthetic and human panels on ~10 contents. Everything else is noise
until that holds.
