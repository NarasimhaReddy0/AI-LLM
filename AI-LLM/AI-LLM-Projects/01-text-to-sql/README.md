# 01 — Text-to-SQL Workflow

An end-to-end LLM workflow that converts a natural-language question into SQL.

## Features

- SQLite sample database
- Schema retrieval based on keyword matching
- LLM SQL generation
- Read-only SQL validation
- SQL execution
- Natural-language result explanation

## Example

Question:

> Which customers spent more than 10000 in 2025?

The application retrieves the relevant schema, asks the LLM to generate SQL, validates it, executes it, and explains the result.

## Run

```bash
pip install -r requirements.txt
copy .env.example .env
python app.py
```

On macOS/Linux use:

```bash
cp .env.example .env
python app.py
```

## Architecture

```text
Question
   ↓
Schema Retrieval
   ↓
Prompt Construction
   ↓
LLM SQL Generation
   ↓
SQL Validation
   ↓
SQLite
   ↓
Result Explanation
```
