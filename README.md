# AI & LLM Practical Projects

Three GitHub-ready Python projects demonstrating common LLM application patterns:

1. **Text-to-SQL Workflow** — retrieval + SQL generation + validation + SQLite execution.
2. **RAG-Based Question Answering** — document indexing + embeddings + similarity retrieval + answer generation.
3. **Prompt Chaining for Summarization** — multi-step extraction + summarization + synthesis + refinement.

## Requirements

- Python 3.10+
- An OpenAI API key

## Quick Start

```bash
git clone <YOUR_REPOSITORY_URL>
cd AI-LLM-Projects

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r 01-text-to-sql/requirements.txt
pip install -r 02-rag-question-answering/requirements.txt
pip install -r 03-prompt-chaining-summarization/requirements.txt
```

Create a `.env` file in each project directory from its `.env.example`:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5-mini
```

Then run each project from its own directory:

```bash
python app.py
```

> Never commit your real `.env` file or API key. The included `.gitignore` prevents accidental commits.

## Project Architecture

### 01 — Text-to-SQL

```text
User Question
     ↓
Schema Retrieval
     ↓
LLM SQL Generation
     ↓
SQL Validation
     ↓
SQLite Execution
     ↓
Natural Language Answer
```

### 02 — RAG Question Answering

```text
Documents
   ↓
Chunking
   ↓
Embeddings
   ↓
Vector Index
   ↓
Top-K Retrieval
   ↓
LLM
   ↓
Grounded Answer
```

### 03 — Prompt Chaining

```text
Long Text
   ↓
Extract Key Points
   ↓
Summarize
   ↓
Synthesize
   ↓
Refine
   ↓
Final Summary
```

## Notes

These projects are intentionally small enough to understand and demonstrate in a college/project GitHub repository. They include sample data and error handling so they can be run without an external database or document service.
