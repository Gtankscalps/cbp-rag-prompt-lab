"""The RAG pipeline: retrieve -> build prompt -> call model -> parse -> guard.

The output guard applies only to the hardened version (v4). It scans
the model's answer for the canary code and for marker words that only
appear when an injection succeeded. A hit replaces the answer with a
safe fallback. This is deliberate defense-in-depth: the prompt asks
for good behavior, the guard enforces a floor under it.
"""
import json
import re
import time

from src.llm import get_llm
from src.prompts import CANARY, VERSIONS
from src.retriever import Retriever

_REFUSAL_PHRASES = (
    "i don't have", "i do not have", "can't help", "cannot help",
    "can't share", "cannot share", "i can't answer", "i don't know",
    "can't pretend", "cannot pretend",
)
_GUARD_MARKERS = ("PWNED", CANARY, "CANARY")
_SAFE_FALLBACK = ("I can't help with that request, but I can answer "
                  "questions about CBP travel and import guidance.")


class Assistant:
    def __init__(self, settings, version: str):
        self.settings = settings
        self.version = VERSIONS[version]
        self.llm = get_llm(settings)
        self.retriever = Retriever(settings) if self.version.uses_retrieval else None

    def ask(self, question: str, injected_context: str | None = None) -> dict:
        t0 = time.perf_counter()
        result = {
            "answer": "", "citations": [], "refused": False,
            "json_valid": None, "latency_s": 0.0, "error": None,
            "raw": "", "reasoning": None, "confidence": None,
            "retrieved_chunks": [],
        }
        try:
            chunks = []
            if self.retriever is not None:
                chunks = self.retriever.search(question, self.settings.top_k)
                if injected_context:
                    chunks = [{"doc_id": "injected_context",
                               "text": " ".join(injected_context.split()),
                               "score": None}] + chunks
            result["retrieved_chunks"] = chunks
            messages = self.version.build(question, chunks)
            raw = self.llm.complete(messages)
            result["raw"] = raw
            if self.version.expects_json:
                self._parse_json(raw, result)
            else:
                self._parse_text(raw, result)
            if self.version.hardened:
                self._guard(result)
        except Exception as exc:  # provider down, bad key, etc.
            result["error"] = f"{exc.__class__.__name__}: {exc}"
        result["latency_s"] = round(time.perf_counter() - t0, 3)
        return result

    # ------------------------------------------------------------ parsing
    def _parse_text(self, raw: str, result: dict) -> None:
        answer = raw.strip()
        citations = re.findall(r"\(Source:\s*([a-z0-9_]+)\)", answer)
        answer = re.sub(r"\s*\(Source:\s*[a-z0-9_]+\)", "", answer).strip()
        result["answer"] = answer
        result["citations"] = citations
        low = answer.lower()
        result["refused"] = any(p in low for p in _REFUSAL_PHRASES)

    def _parse_json(self, raw: str, result: dict) -> None:
        text = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
        try:
            obj = json.loads(text)
            result["json_valid"] = True
            result["answer"] = str(obj.get("answer", "")).strip()
            result["citations"] = [str(c) for c in obj.get("citations", [])]
            result["refused"] = bool(obj.get("refused", False))
            result["reasoning"] = obj.get("reasoning")
            result["confidence"] = obj.get("confidence")
        except (json.JSONDecodeError, AttributeError):
            result["json_valid"] = False
            result["answer"] = raw.strip()
            low = raw.lower()
            result["refused"] = any(p in low for p in _REFUSAL_PHRASES)

    # ------------------------------------------------------------ guard
    def _guard(self, result: dict) -> None:
        haystack = (result["answer"] + " " + (result["raw"] or "")).upper()
        if any(marker.upper() in haystack for marker in _GUARD_MARKERS):
            result["answer"] = _SAFE_FALLBACK
            result["citations"] = []
            result["refused"] = True
