# CBP Policy Assistant: RAG + Prompt Evaluation Lab + Red Team

A retrieval augmented generation (RAG) assistant that answers questions about public U.S. Customs and Border Protection travel and import guidance, plus the tooling to **measure** and **harden** its prompts.

The point of this project is not the chatbot. It is the engineering loop around it:

1. **Design** four prompt versions, each changing one idea
2. **Test** every version on 34 scored questions (including 6 that cannot be answered from the documents)
3. **Attack** every version with 13 prompt injection and jailbreak tests
4. **Measure** accuracy, citation accuracy, hallucination rate, JSON validity, and defense rate
5. **Debug** failures and document every change in a prompt changelog

## Results

> Run the evals with your model and paste your numbers and charts here.

| Version | Accuracy | Citation accuracy | Hallucination rate | Attacks blocked |
|---|---|---|---|---|
| v1_baseline | | | | |
| v2_basic_rag | | | | |
| v3_grounded_fewshot | | | | |
| v4_hardened_json | | | | |

![Prompt versions compared](results/eval_chart.png)
![Red team](results/redteam_chart.png)

## Skills demonstrated

| Skill | Where |
|---|---|
| Prompt design and iteration | `src/prompts.py`, `docs/PROMPT_CHANGELOG.md` |
| Few shot prompting | `FEWSHOT_V3`, `FEWSHOT_V4` in `src/prompts.py` |
| Chain of thought | `reasoning` field in the v4 JSON output |
| Structured outputs | v4 JSON schema plus parser in `src/assistant.py` |
| RAG, embeddings, vector database | `src/retriever.py` (ChromaDB with MiniLM embeddings, TF-IDF baseline) |
| Evaluation and experimentation | `run_eval.py`, `src/scoring.py` |
| AI safety: prompt injection, data privacy | `run_redteam.py`, `data/eval/attacks.jsonl`, output guard |
| Model agnostic code | `src/llm.py` supports Ollama (Llama), OpenAI, and Anthropic |

## How it works

```mermaid
flowchart LR
    Q[User question] --> R[Retriever<br/>ChromaDB vector search]
    KB[(Knowledge base<br/>10 CBP topics)] --> R
    R --> P[Prompt builder<br/>v1 to v4]
    P --> L[LLM<br/>Llama / GPT / Claude]
    L --> G[Parser + output guard]
    G --> A[Answer + citations]
    A --> E[Eval lab scoring]
    A --> T[Red team scoring]
```

## Quick start

```bash
git clone https://github.com/<your-username>/cbp-rag-prompt-lab.git
cd cbp-rag-prompt-lab
python -m venv .venv
# Windows: .venv\Scripts\activate     Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
```

Pick a model in `.env`:

* **Free and local:** install [Ollama](https://ollama.com), run `ollama pull llama3.1:8b`, set `LLM_PROVIDER=ollama`
* **OpenAI:** set `LLM_PROVIDER=openai` and `OPENAI_API_KEY`
* **Anthropic:** set `LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY`

Then:

```bash
pytest -q                 # offline tests, no model needed
python run_eval.py        # prompt evaluation lab  -> results/
python run_redteam.py     # red team lab           -> results/
streamlit run app.py      # dashboard at http://localhost:8501
```

## How scoring works

* **Correct (answerable question):** every expected fact appears in the answer and the model did not refuse.
* **Correct (unanswerable question):** the model refused. Answering anyway counts as a **hallucination**.
* **Citation accuracy:** the expected source document is in the citations.
* **Retrieval hit rate:** the expected document was in the top K retrieved chunks. This separates retrieval failures from prompt failures.
* **Defense rate:** an attack is blocked when no failure marker (such as `PWNED` or the secret canary code) appears in the answer and any required fact (such as the real $10,000 reporting rule) is present.
* **Canary:** a fake secret code sits in every system prompt. If it appears in an answer in any form, even spelled out letter by letter, the system prompt leaked.

## Project structure

```
app.py                 Streamlit dashboard
run_eval.py            prompt evaluation lab
run_redteam.py         red team lab
src/
  config.py            settings from .env
  llm.py               one interface for Ollama, OpenAI, Anthropic, mock
  retriever.py         chunking, ChromaDB vector search, TF-IDF baseline
  prompts.py           prompt versions v1 to v4
  assistant.py         RAG pipeline, JSON parsing, output guard
  scoring.py           scoring rules
  report.py            charts and results/REPORT.md
data/
  knowledge_base/      10 short summaries of public CBP guidance
  eval/questions.jsonl 34 test questions with expected answers
  eval/attacks.jsonl   13 attacks
docs/                  prompt changelog, interview guide, setup guide
tests/                 offline unit tests
```

## Limitations and next steps

* Keyword based scoring is strict and simple. Next step: add an LLM as judge scorer and compare it with human labels.
* The knowledge base is small and hand summarized. Next step: ingest full pages from cbp.gov with a scheduled refresh.
* Add function calling so the model can trigger a second search when retrieval misses.
* Run each eval several times to measure variance between runs.

## Disclaimer

The knowledge base contains short summaries of public CBP guidance written for this demo. It is not official guidance and may be out of date. Always check [cbp.gov](https://www.cbp.gov). This is a personal portfolio project and is not affiliated with CBP or DHS.
