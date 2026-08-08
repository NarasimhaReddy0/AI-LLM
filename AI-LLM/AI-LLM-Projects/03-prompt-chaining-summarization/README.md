# 03 — Prompt Chaining for Summarization

A multi-step LLM pipeline for summarizing longer text.

## Chain

```text
Input Document
     ↓
1. Extract Key Points
     ↓
2. Create Section Summary
     ↓
3. Synthesize Summary
     ↓
4. Refine Final Summary
```

Each stage has a focused prompt. The output of one stage becomes the input to the next.

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
