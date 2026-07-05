"""CLI demo — runs fully offline (mock mode) or live with ANTHROPIC_API_KEY.

    python run_demo.py "30-second TikTok: a raccoon steals a slice at a
        downtown pizza joint while the owner deadpans about Toronto rent" \
        --n 500 --mode auto
"""
import argparse
import json

from audience import generate_audience, run_reactions, aggregate, DEFAULT_MODEL

DEMO_CONTENT = ("30-second TikTok skit: a raccoon 'inspects' a new condo while a "
                "deadpan realtor lists its features; punchline about Toronto rent "
                "prices. Light branding for a rental-listings app in the last 3s.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("content", nargs="?", default=DEMO_CONTENT)
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--mode", default="auto", choices=["auto", "mock", "live", "batch"])
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--json", action="store_true", help="dump full JSON result")
    args = ap.parse_args()

    personas = generate_audience(args.n, args.seed)
    reactions = run_reactions(personas, args.content, mode=args.mode, model=args.model)
    result = aggregate(personas, reactions, args.content, args.mode, args.model)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(f"\n=== Synthetic Toronto audience, n={result['meta']['n']} "
          f"(mode={result['meta']['mode']}) ===")
    print(f"content: {args.content[:100]}...\n")
    print("sentiment:", {k: f"{v:.0%}" for k, v in result["sentiment"].items()})
    print("rates:    ", {k: f"{v:.1%}" for k, v in result["rates"].items()})
    print(f"avg score: {result['avg_score']:+.2f}  (-2 all cringe .. +2 all love)\n")
    print("--- by age ---")
    for row in result["segments"]["age"]:
        pos = row["sentiment"]["love"] + row["sentiment"]["like"]
        print(f"  {row['segment']:>6}  n={row['n']:<4} positive={pos:.0%} "
              f"share={row['share_rate']:.1%} skip={row['skip_rate']:.1%}")
    print("\n--- sample verbatims ---")
    for q in result["quotes"][:8]:
        p = q["persona"]
        print(f"  [{q['sentiment']:>7}] \"{q['quote']}\" "
              f"— {p['age']}, {p['neighbourhood']}")


if __name__ == "__main__":
    main()
