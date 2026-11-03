# Interview guide — how to talk about this project

**The 30-second version:** "I built a CBP policy assistant four times.
Each version changed one thing — retrieval, grounding rules, few-shot
refusals, then a JSON contract plus an output guard — and I measured
every change on 64 scored questions and 25 injection attacks instead
of judging by feel. When I expanded the test set, the scores dropped —
that is the harness doing its job, and the new failures are the most
interesting part."

## Questions it answers, and where the proof is

- **"How do you improve a prompt?"** The changelog (`docs/PROMPT_CHANGELOG.md`):
  every version exists because a measured failure demanded it.
- **"How do you stop hallucinations?"** Grounding rules plus a refusal
  example; the eval counts an invented answer to an unanswerable
  question as a hallucination. On the original 6 unanswerable
  questions v3/v4 refused all 6; expanding to 12 exposed 3 misses —
  all plausible operational questions (a live wait time, a staffing
  count, a specific tariff rate). Say this plainly if asked: the fix
  on the roadmap is a retrieval-confidence threshold, not more wording.
- **"What is RAG, concretely?"** `src/retriever.py`: chunking, TF-IDF
  baseline vs ChromaDB embeddings, and retrieval hit rate scored
  separately so retrieval failures are not confused with prompt failures.
- **"How do you handle prompt injection?"** `run_redteam.py` and
  `results/REPORT.md`: delimiters and data labeling stop most attacks;
  the v4 output guard catches what wording cannot. Defense in depth,
  enforced by code.
- **"Why structured outputs?"** v4's JSON schema makes every answer
  validatable — citations present, refusal explicit, confidence stated —
  before a human or downstream system consumes it.

## Honesty lines (say these before they ask)

- "The knowledge base is hand-summarized public guidance for a demo —
  production would ingest cbp.gov directly with a refresh job."
- "Offline runs use a mock model so the pipeline is testable without
  keys; the eval design is the deliverable, and the same harness runs
  unchanged against Llama, GPT, or Claude."
- "Keyword scoring is strict and simple; an LLM judge is the next
  step, and I would validate it against human labels before trusting it."
