"""FastAPI backend for the synthetic-audience dashboard.

Run:  uvicorn server:app --reload --port 8000   (from backend/)
Works fully offline in mock mode; set ANTHROPIC_API_KEY to go live.
"""
import shutil
import tempfile
from collections import Counter

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from audience import (generate_audience, run_reactions, aggregate,
                      api_key_available, parity_report, DEFAULT_MODEL)

app = FastAPI(title="Synthetic Audience — Toronto v0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_LAST_RESULT: dict = {}


class RunRequest(BaseModel):
    content: str = Field(..., min_length=10,
                         description="Text description of the Reel/TikTok/Short/ad")
    audience_size: int = Field(500, ge=10, le=5000)
    seed: int = 42
    mode: str = Field("auto", pattern="^(auto|mock|live|batch)$")
    model: str = DEFAULT_MODEL


@app.get("/api/health")
def health():
    return {"ok": True, "live_available": api_key_available(),
            "default_model": DEFAULT_MODEL}


@app.get("/api/population")
def population(n: int = 1000, seed: int = 42):
    """Preview the sampled population so users can sanity-check representativeness."""
    personas = generate_audience(n, seed)
    def dist(attr):
        c = Counter(getattr(p, attr) for p in personas)
        return {k: round(v / n, 4) for k, v in sorted(c.items(), key=lambda x: -x[1])}
    return {
        "n": n,
        "age": dist("age_band"),
        "neighbourhood": dist("neighbourhood"),
        "income": dist("income_bracket"),
        "background": dist("background"),
        "immigrant_generation": dist("immigrant_generation"),
        "sample_personas": [p.to_dict() for p in personas[:5]],
    }


@app.post("/api/run")
def run(req: RunRequest):
    global _LAST_RESULT
    mode = req.mode
    if mode == "auto":
        mode = "live" if api_key_available() else "mock"
    if mode in ("live", "batch") and not api_key_available():
        raise HTTPException(400, "ANTHROPIC_API_KEY is not set; use mode=mock")

    personas = generate_audience(req.audience_size, req.seed)
    reactions = run_reactions(personas, req.content, mode=mode, model=req.model)
    _LAST_RESULT = aggregate(personas, reactions, req.content, mode, req.model)
    return _LAST_RESULT


@app.post("/api/validate")
async def validate(panel: UploadFile):
    """Upload a real-human panel CSV (see backend/validation/panel_template.csv)
    to score parity against the most recent synthetic run."""
    if not _LAST_RESULT:
        raise HTTPException(400, "run a synthetic audience first")
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False) as tmp:
        shutil.copyfileobj(panel.file, tmp)
        path = tmp.name
    try:
        return parity_report(_LAST_RESULT, path)
    except (ValueError, KeyError) as e:
        raise HTTPException(422, f"bad panel CSV: {e}")
