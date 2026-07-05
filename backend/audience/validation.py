"""Validation hook: compare synthetic reactions against a real human panel.

Workflow:
1. Run the same content past a small real panel (n=50-200 Torontonians via
   Prolific/Dynata, quota-matched on age x neighbourhood area).
2. Record each respondent as a row in a CSV shaped like
   backend/validation/panel_template.csv (sentiment + action, same enums).
3. Call `parity_report(synthetic_result, "panel.csv")` — or POST the CSV to
   /api/validate — to get parity metrics.

Metrics (v0):
- sentiment_mae ... mean absolute error between synthetic and human sentiment
                    shares (0 = perfect, >0.15 = poor).
- share_gap / skip_gap ... absolute difference in predicted vs observed rates.
- direction_hit ... whether synthetic and human agree on net-positive vs
                    net-negative (the cheapest pre-filter claim to validate).
"""
import csv
from collections import Counter
from typing import Dict

from .aggregate import SENTIMENT_ORDER, _SCORE


def load_panel_csv(path: str) -> Dict:
    sentiments, actions = Counter(), Counter()
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            sentiments[row["sentiment"].strip()] += 1
            actions[row["action"].strip()] += 1
    n = sum(sentiments.values())
    if n == 0:
        raise ValueError("panel CSV has no rows")
    return {
        "n": n,
        "sentiment": {s: sentiments.get(s, 0) / n for s in SENTIMENT_ORDER},
        "share": actions.get("share", 0) / n,
        "skip": actions.get("scroll_past", 0) / n,
    }


def parity_report(synthetic: dict, panel_csv_path: str) -> dict:
    human = load_panel_csv(panel_csv_path)
    syn_sent = synthetic["sentiment"]

    mae = sum(abs(syn_sent[s] - human["sentiment"][s])
              for s in SENTIMENT_ORDER) / len(SENTIMENT_ORDER)

    def net(shares):
        return sum(_SCORE[s] * shares[s] for s in SENTIMENT_ORDER)

    return {
        "panel_n": human["n"],
        "synthetic_n": synthetic["meta"]["n"],
        "sentiment_mae": round(mae, 4),
        "share_gap": round(abs(synthetic["rates"]["share"] - human["share"]), 4),
        "skip_gap": round(abs(synthetic["rates"]["skip"] - human["skip"]), 4),
        "direction_hit": (net(syn_sent) >= 0) == (net(human["sentiment"]) >= 0),
        "human_sentiment": {s: round(v, 4) for s, v in human["sentiment"].items()},
    }
