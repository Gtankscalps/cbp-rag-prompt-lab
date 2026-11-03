# Setup

```bash
git clone https://github.com/Gtankscalps/cbp-rag-prompt-lab.git
cd cbp-rag-prompt-lab
python -m venv .venv
# Windows: .venv\Scripts\activate     Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
```

## Pick a model in .env

- **Offline demo / tests:** `LLM_PROVIDER=mock` and `RETRIEVER=tfidf`.
  No API key, no downloads. The mock is a deterministic test double —
  use it to verify the pipeline, never to quote model quality.
- **Free and local:** install [Ollama](https://ollama.com),
  `ollama pull llama3.1:8b`, set `LLM_PROVIDER=ollama`.
- **OpenAI:** `LLM_PROVIDER=openai` plus `OPENAI_API_KEY`.
- **Anthropic:** `LLM_PROVIDER=anthropic` plus `ANTHROPIC_API_KEY`.

Retrieval: `RETRIEVER=chroma` uses ChromaDB with local MiniLM
embeddings (first run downloads the embedding model). If Chroma or
the model is unavailable, the retriever falls back to TF-IDF and
prints a note. `RETRIEVER=tfidf` selects the keyword baseline
directly.

## Run

```bash
pytest -q                 # offline tests, no model needed
python run_eval.py        # prompt evaluation lab  -> results/
python run_redteam.py     # red team lab           -> results/
streamlit run app.py      # dashboard at http://localhost:8501
```

Never commit your `.env` — it is git-ignored on purpose.
