"""Charts and a written report from whatever result CSVs exist.

Generates PNG charts (used by the Streamlit dashboard) and SVG charts
(used by the GitHub README, since SVG is text and renders anywhere),
plus results/REPORT.md. Safe to call when only one of the two labs
has been run.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

_COLORS = {"accuracy": "#1F3A5F", "citation_accuracy": "#4E79A7", "hallucination_rate": "#C0392B"}


def _save(fig, path_base: Path):
    fig.savefig(path_base.with_suffix(".png"), dpi=140, bbox_inches="tight")
    fig.savefig(path_base.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


def make_report(results_dir: Path) -> None:
    results_dir = Path(results_dir)
    lines = ["# Lab report", ""]
    eval_path = results_dir / "eval_summary.csv"
    red_path = results_dir / "redteam_summary.csv"

    if eval_path.exists():
        summ = pd.read_csv(eval_path, index_col="version")
        cols = [c for c in ("accuracy", "citation_accuracy", "hallucination_rate") if c in summ]
        ax = summ[cols].plot(kind="bar", color=[_COLORS[c] for c in cols],
                             figsize=(8, 4), ylim=(0, 1))
        ax.set_title("Prompt evaluation: accuracy, citations, hallucinations")
        ax.set_ylabel("rate")
        ax.legend(loc="lower left", fontsize=8)
        _save(ax.get_figure(), results_dir / "eval_chart")
        best = summ["accuracy"].idxmax()
        lines += [
            "## Prompt evaluation",
            "",
            summ.round(3).to_markdown(),
            "",
            f"Best version by accuracy: **{best}** ({summ.loc[best, 'accuracy']:.0%}). "
            f"Hallucination rate went from {summ['hallucination_rate'].iloc[0]:.0%} "
            f"in {summ.index[0]} to {summ.loc[best, 'hallucination_rate']:.0%} in {best}.",
            "",
        ]

    if red_path.exists():
        red = pd.read_csv(red_path, index_col=0)
        if "OVERALL" in red.index:
            overall = red.loc["OVERALL"]
            ax = overall.plot(kind="bar", color="#1F3A5F", figsize=(8, 4), ylim=(0, 1))
            ax.set_title("Red team: defense rate by prompt version (1.0 = all attacks blocked)")
            ax.set_ylabel("defense rate")
            _save(ax.get_figure(), results_dir / "redteam_chart")
            lines += [
                "## Red team",
                "",
                red.round(3).to_markdown(),
                "",
                f"Overall defense rate: " + ", ".join(
                    f"{v} {overall[v]:.0%}" for v in overall.index) + ".",
                "",
            ]

    (results_dir / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
