# 02 — RAG-Based Question Answering System

A small Retrieval-Augmented Generation system implementing:

- document loading
- text chunking
- embedding generation
- vector indexing
- top-k retrieval
- context-grounded response generation

The demo uses local sample documents about Java, Operating Systems, and DBMS.

## Run

```bash
pip install -r requirements.txt
copy .env.example .env
python app.py
```

macOS/Linux:

```bash
cp .env.example .env
python app.py
```

The first run downloads the embedding model used by `sentence-transformers`.

## Architecture

```text
Documents
   ↓
Chunking
   ↓
Sentence Embeddings
   ↓
FAISS Index
   ↓
Question Embedding
   ↓
Top-K Retrieval
   ↓
Prompt + Context
   ↓
LLM Answer
```
