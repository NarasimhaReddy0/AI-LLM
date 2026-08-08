import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
BASE_DIR = Path(__file__).parent


def get_client():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Copy .env.example to .env and add your key."
        )
    return OpenAI(api_key=key)


def call_llm(client, prompt):
    response = client.responses.create(model=MODEL, input=prompt)
    return response.output_text.strip()


def extract_key_points(client, text):
    prompt = f"""
Read the document below.

Extract the most important:
- main ideas
- facts
- concepts
- examples
- challenges

Do not write a polished final summary.
Do not add information that is not present.

DOCUMENT:
{text}
""".strip()

    return call_llm(client, prompt)


def summarize_key_points(client, key_points):
    prompt = f"""
Turn the following key points into a concise section summary.
Use simple English.
Keep important facts and remove repetition.
Do not introduce new information.

KEY POINTS:
{key_points}
""".strip()

    return call_llm(client, prompt)


def synthesize(client, summary):
    prompt = f"""
Create one coherent summary from the material below.

Requirements:
- Keep the main ideas.
- Remove repetition.
- Preserve important examples and challenges.
- Use clear paragraphs.
- Do not add outside facts.

MATERIAL:
{summary}
""".strip()

    return call_llm(client, prompt)


def refine(client, summary):
    prompt = f"""
Refine the following summary into a final version.

Requirements:
- Use simple English.
- Be concise.
- Keep the important information.
- Improve flow and readability.
- Do not introduce new facts.
- Return only the final summary.

SUMMARY:
{summary}
""".strip()

    return call_llm(client, prompt)


def main():
    print("=" * 60)
    print("PROMPT CHAINING FOR SUMMARIZATION")
    print("=" * 60)

    sample_path = BASE_DIR / "sample_article.txt"
    text = sample_path.read_text(encoding="utf-8")

    client = get_client()

    print("\nStep 1/4: Extracting key points...")
    key_points = extract_key_points(client, text)

    print("Step 2/4: Creating summary...")
    section_summary = summarize_key_points(client, key_points)

    print("Step 3/4: Synthesizing...")
    synthesized = synthesize(client, section_summary)

    print("Step 4/4: Refining final summary...")
    final_summary = refine(client, synthesized)

    print("\n" + "-" * 60)
    print("FINAL SUMMARY")
    print("-" * 60)
    print(final_summary)

    print("\n" + "-" * 60)
    print("PIPELINE OUTPUTS")
    print("-" * 60)
    print("\n[1] Key Points:\n")
    print(key_points)
    print("\n[2] Section Summary:\n")
    print(section_summary)
    print("\n[3] Synthesized Summary:\n")
    print(synthesized)


if __name__ == "__main__":
    main()
