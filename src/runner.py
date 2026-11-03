"""Shared CLI helpers for run_eval.py and run_redteam.py."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from src.config import get_settings
from src.prompts import VERSIONS


def base_parser(doc: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=doc)
    parser.add_argument("--versions", default=None,
                        help="Comma-separated prompt versions (default: all)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Only run the first N items")
    parser.add_argument("--provider", default=None, help="Override LLM_PROVIDER")
    parser.add_argument("--model", default=None, help="Override LLM_MODEL")
    parser.add_argument("--retriever", default=None, help="Override RETRIEVER")
    return parser


def settings_from_args(args):
    settings = get_settings()
    if args.provider:
        settings.provider = args.provider
        settings.model = ""
        settings.__post_init__()
    if args.model:
        settings.model = args.model
    if args.retriever:
        settings.retriever = args.retriever
    return settings


def versions_from_args(args):
    if args.versions:
        picked = [v.strip() for v in args.versions.split(",") if v.strip()]
        unknown = [v for v in picked if v not in VERSIONS]
        if unknown:
            raise SystemExit(f"Unknown prompt versions: {unknown}. Known: {list(VERSIONS)}")
        return picked
    return list(VERSIONS)


def load_jsonl(path: Path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def write_meta(results_dir: Path, kind: str, settings, versions, n_items: int):
    meta = {
        "kind": kind,
        "provider": settings.provider,
        "model": settings.model,
        "retriever": settings.retriever,
        "embedding": settings.embedding,
        "versions": versions,
        "items": n_items,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (Path(results_dir) / f"{kind}_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
