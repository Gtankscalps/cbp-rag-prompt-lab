"""Red Team Lab: attack every prompt version with prompt injection and jailbreak attempts.

Examples:
  python run_redteam.py
  python run_redteam.py --versions v2_basic_rag,v4_hardened_json
"""
import pandas as pd

from src.assistant import Assistant
from src.report import make_report
from src.runner import base_parser, load_jsonl, settings_from_args, versions_from_args, write_meta
from src.scoring import score_attack


def main():
    args = base_parser(__doc__).parse_args()
    settings = settings_from_args(args)
    versions = versions_from_args(args)
    attacks = load_jsonl(settings.eval_dir / "attacks.jsonl")[: args.limit]
    settings.results_dir.mkdir(exist_ok=True)

    print(f"Model: {settings.provider}:{settings.model} | {len(attacks)} attacks")
    rows = []
    for v in versions:
        bot = Assistant(settings, v)
        print(f"\n== {v} ==")
        for atk in attacks:
            r = bot.ask(atk["prompt"], injected_context=atk.get("injected_context"))
            s = score_attack(r, atk)
            rows.append(
                {
                    "version": v,
                    "id": atk["id"],
                    "type": atk["type"],
                    "prompt": atk["prompt"],
                    "answer": r["answer"],
                    "defended": s["defended"],
                    "fail_markers_found": ";".join(s["fail_markers_found"]),
                    "required_missing": ";".join(s["required_missing"]),
                    "error": r["error"],
                }
            )
            mark = "DEFENDED" if s["defended"] else "BROKEN  "
            print(f"  {atk['id']} {mark} {atk['type']:<20} {r['answer'][:70]!r}")

    df = pd.DataFrame(rows)
    df.to_csv(settings.results_dir / "redteam_results.csv", index=False)
    summary = df.pivot_table(index="type", columns="version", values="defended", aggfunc="mean").reindex(
        columns=versions
    )
    summary.loc["OVERALL"] = df.groupby("version")["defended"].mean().reindex(versions)
    summary.round(3).to_csv(settings.results_dir / "redteam_summary.csv")
    write_meta(settings.results_dir, "redteam", settings, versions, len(attacks))

    print("\nDefense rate (1.0 = blocked every attack):")
    print(summary.round(2).to_string())
    make_report(settings.results_dir)
    print(f"\nSaved results to {settings.results_dir}")


if __name__ == "__main__":
    main()
