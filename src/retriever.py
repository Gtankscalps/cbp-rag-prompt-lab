"""Retrieval over the knowledge base.

Two backends:
- tfidf: pure-standard-library TF-IDF cosine search. Always available.
- chroma: ChromaDB vector search when the chromadb package and an
  embedding model are available; otherwise it falls back to TF-IDF and
  says so once, so the lab still runs in a minimal environment.

The knowledge base is a folder of short markdown files, one per topic.
Each file is split into paragraph chunks; a chunk keeps its file's
stem as its doc_id, which is what citations and scoring use.
"""
import math
import re
from collections import Counter
from pathlib import Path

_STOP = set("a an the is are i you he she it we they can do does did how what when where which who whom my your me to of in on for and or if so as at by from with into about".split())


_SYNONYMS = {"cash": "currency", "money": "currency"}


def _tokens(text):
    out = []
    for w in re.findall(r"[a-z0-9$.,]+", text.lower()):
        if w in _STOP or len(w) <= 2:
            continue
        w = w.strip("s")
        out.append(_SYNONYMS.get(w, w))
    return out


def load_chunks(kb_dir: Path):
    chunks = []
    for path in sorted(kb_dir.glob("*.md")):
        doc_id = path.stem
        for para in re.split(r"\n\s*\n", path.read_text(encoding="utf-8")):
            text = " ".join(para.split())
            if len(text) >= 40 and not text.startswith("#"):
                chunks.append({"doc_id": doc_id, "text": text})
    return chunks


class TfidfRetriever:
    def __init__(self, chunks):
        self.chunks = chunks
        self._df = Counter()
        tokenized = []
        for c in chunks:
            toks = _tokens(c["text"])
            tokenized.append(Counter(toks))
            for t in set(toks):
                self._df[t] += 1
        n = max(len(chunks), 1)
        self._idf = {t: math.log((n + 1) / (df + 1)) + 1 for t, df in self._df.items()}
        self._vectors = [self._vectorize(tc) for tc in tokenized]

    def _vectorize(self, counts):
        return {t: c * self._idf.get(t, 1.0) for t, c in counts.items()}

    @staticmethod
    def _cosine(a, b):
        dot = sum(v * b.get(t, 0.0) for t, v in a.items())
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        return dot / (na * nb) if na and nb else 0.0

    def search(self, query, top_k=4):
        qv = self._vectorize(Counter(_tokens(query)))
        scored = [
            (self._cosine(qv, vec), chunk)
            for vec, chunk in zip(self._vectors, self.chunks)
        ]
        scored.sort(key=lambda x: -x[0])
        return [
            {"doc_id": c["doc_id"], "text": c["text"], "score": round(s, 4)}
            for s, c in scored[:top_k]
        ]


class Retriever:
    """Facade: chroma when genuinely available, TF-IDF otherwise."""

    def __init__(self, settings):
        self._chunks = load_chunks(settings.kb_dir)
        self._tfidf = TfidfRetriever(self._chunks)
        self._chroma = None
        self._top_k = settings.top_k
        if settings.retriever == "chroma":
            self._chroma = self._try_chroma(settings)

    def _try_chroma(self, settings):
        try:
            import chromadb

            client = chromadb.PersistentClient(path=str(settings.kb_dir.parent.parent / ".chroma_db"))
            collection = client.get_or_create_collection("cbp_kb")
            if collection.count() == 0:
                collection.add(
                    ids=[f"{c['doc_id']}-{i}" for i, c in enumerate(self._chunks)],
                    documents=[c["text"] for c in self._chunks],
                    metadatas=[{"doc_id": c["doc_id"]} for c in self._chunks],
                )
            return collection
        except Exception as exc:  # chromadb or its embedding model unavailable
            print(f"[retriever] chroma unavailable ({exc.__class__.__name__}); using tfidf")
            return None

    def search(self, query, top_k=None):
        k = top_k or self._top_k
        if self._chroma is not None:
            try:
                res = self._chroma.query(query_texts=[query], n_results=k)
                out = []
                for doc, meta, dist in zip(
                    res["documents"][0], res["metadatas"][0], res["distances"][0]
                ):
                    out.append({
                        "doc_id": meta["doc_id"],
                        "text": " ".join(doc.split()),
                        "score": round(1 - dist, 4),
                    })
                return out
            except Exception:
                pass
        return self._tfidf.search(query, k)
