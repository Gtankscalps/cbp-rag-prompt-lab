"""Prompt Evaluation Lab: run every prompt version over the test questions and score them.

Examples:
  python run_eval.py                                  # all versions, settings from .env
  python run_eval.py --versions v3_grounded_fewshot,v4_hardened_json
  python run_eval.py --limit 5                        # quick smoke test
"""
import pandas as pd

from src.assistant import Assistant
from src.report import make_report
from src.runner import base_parser, load_jsonl, settings_from_args, versions_from_args, write_meta
from src.scoring import score_question


def main():
    args = base_parser(__doc__).parse_args()
    settings = settings_from_args(args)
    versions = versions_from_args(args)
    items = load_jsonl(settings.eval_dir / "questions.jsonl")[: args.limit]
    settings.results_dir.mkdir(exist_ok=True)

    print(f"Model: {settings.provider}:{settings.model} | retriever: {settings.retriever} | {len(items)} questions")
    rows = []
    for v in versions:
        bot = Assistant(settings, v)
        print(f"\n== {v} ==")
        for item in items:
            r = bot.ask(item["question"])
            s = score_question(r, item)
            rows.append(
                {
                    "version": v,
                    "id": item["id"],
                    "category": item["category"],
                    "answerable": item["answerable"],
                    "question": item["question"],
                    "answer": r["answer"],
                    "citations": ",".join(r["citations"]),
                    "expected_source": item["expected_source"],
                    "refused": r["refused"],
                    "json_valid": r["json_valid"],
                    "latency_s": r["latency_s"],
                    "error": r["error"],
                    **s,
                }
            )
            mark = "PASS" if s["correct"] else "FAIL"
            print(f"  {item['id']} {mark}  {r['answer'][:80]!r}")

    df = pd.DataFrame(rows)
    df.to_csv(settings.results_dir / "eval_results.csv", index=False)

    ans = df[df.answerable]
    unans = df[~df.answerable]
    summary = pd.DataFrame(
        {
            "accuracy": df.groupby("version")["correct"].mean(),
            "answerable_accuracy": ans.groupby("version")["correct"].mean(),
            "citation_accuracy": ans.groupby("version")["cited_right"].mean(),
            "refusal_rate_on_unanswerable": unans.groupby("version")["correct"].mean(),
            "hallucination_rate": unans.groupby("version")["hallucinated"].mean(),
            "json_valid_rate": df.groupby("version")["json_valid"].apply(
                lambda s: s.dropna().astype(float).mean() if s.notna().any() else None
            ),
            "retrieval_hit_rate": ans.groupby("version")["retrieval_hit"].apply(
                lambda s: s.dropna().astype(float).mean() if s.notna().any() else None
            ),
            "avg_latency_s": df.groupby("version")["latency_s"].mean(),
            "errors": df.groupby("version")["error"].apply(lambda s: int(s.notna().sum())),
        }
    ).reindex(versions)
    summary.index.name = "version"
    summary.round(3).to_csv(settings.results_dir / "eval_summary.csv")
    write_meta(settings.results_dir, "eval", settings, versions, len(items))

    print("\n" + summary.round(3).to_string())
    make_report(settings.results_dir)
    print(f"\nSaved results to {settings.results_dir}")


if __name__ == "__main__":
    main()
