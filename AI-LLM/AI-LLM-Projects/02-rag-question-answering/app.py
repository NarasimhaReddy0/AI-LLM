import os
from pathlib import Path

import faiss
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
LLM_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
TOP_K = 4


def load_documents():
    documents = []

    for path in sorted(DATA_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        documents.append({"source": path.name, "text": text})

    if not documents:
        raise RuntimeError("No .txt documents were found in the data directory.")

    return documents


def chunk_text(text, chunk_size=500, overlap=80):
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))

        if end == len(words):
            break

        start = end - overlap

    return chunks


def build_chunks(documents):
    chunks = []

    for doc in documents:
        for chunk in chunk_text(doc["text"]):
            chunks.append({
                "source": doc["source"],
                "text": chunk
            })

    return chunks


def build_index(chunks, model):
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).astype("float32")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    return index


def retrieve(question, index, chunks, model, top_k=TOP_K):
    query_vector = model.encode(
        [question],
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).astype("float32")

    scores, ids = index.search(query_vector, min(top_k, len(chunks)))

    results = []
    for score, idx in zip(scores[0], ids[0]):
        if idx == -1:
            continue
        item = chunks[int(idx)].copy()
        item["score"] = float(score)
        results.append(item)

    return results


def generate_answer(question, results):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Copy .env.example to .env and add your key."
        )

    context = "\n\n".join(
        f"[Source: {item['source']}]\n{item['text']}"
        for item in results
    )

    prompt = f"""
You are a grounded question-answering assistant.

Answer the question using only the provided context.
If the context does not contain enough information, say:
"I don't have enough information in the indexed documents."

Do not invent facts.
Mention the relevant source filenames when useful.

CONTEXT:
{context}

QUESTION:
{question}
""".strip()

    client = OpenAI(api_key=key)
    response = client.responses.create(model=LLM_MODEL, input=prompt)
    return response.output_text.strip()


def main():
    print("=" * 60)
    print("RAG-BASED QUESTION ANSWERING SYSTEM")
    print("=" * 60)

    print("\nLoading documents...")
    documents = load_documents()

    print("Creating chunks...")
    chunks = build_chunks(documents)

    print(f"Loaded {len(documents)} documents and {len(chunks)} chunks.")

    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    print("Building vector index...")
    index = build_index(chunks, embedding_model)

    question = input(
        "\nAsk a question (or press Enter for the demo question): "
    ).strip()

    if not question:
        question = "What are the main process states in an operating system?"

    results = retrieve(question, index, chunks, embedding_model)

    print("\nRetrieved context:")
    for item in results:
        print(f"- {item['source']} | similarity={item['score']:.3f}")

    answer = generate_answer(question, results)

    print("\nAnswer:\n")
    print(answer)


if __name__ == "__main__":
    main()
