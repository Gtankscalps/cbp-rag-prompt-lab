"""Settings, read from environment variables (and a local .env if present).

Defaults mirror .env.example. Nothing here requires any particular
provider: LLM_PROVIDER=mock plus RETRIEVER=tfidf runs the whole lab
offline with the standard library only.
"""
import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_DEFAULT_MODELS = {
    "ollama": "llama3.1:8b",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-haiku-5-5",
    "mock": "mock-1",
}


@dataclass
class Settings:
    provider: str = "ollama"
    model: str = ""
    retriever: str = "chroma"
    embedding: str = "default"
    top_k: int = 4
    kb_dir: Path = ROOT / "data" / "knowledge_base"
    eval_dir: Path = ROOT / "data" / "eval"
    results_dir: Path = ROOT / "results"

    def __post_init__(self):
        if not self.model:
            self.model = _DEFAULT_MODELS.get(self.provider, "")


def get_settings() -> Settings:
    try:
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env")
    except ImportError:
        pass
    provider = os.environ.get("LLM_PROVIDER", "ollama").strip().lower()
    return Settings(
        provider=provider,
        model=os.environ.get("LLM_MODEL", "").strip(),
        retriever=os.environ.get("RETRIEVER", "chroma").strip().lower(),
        embedding=os.environ.get("EMBEDDING", "default").strip().lower(),
        top_k=int(os.environ.get("TOP_K", "4")),
    )
