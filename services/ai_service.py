"""
ai_service.py
Handles AI synthesis using Groq (Llama 3.3 70B).
Section-wise generation: each API call writes one section within
the output ceiling; the app concatenates them into a long report.

FREE-TIER SAFE:
- Sends a compact progress note instead of the full report.
- Retries automatically if Groq's tokens-per-minute quota is hit.
"""

import time
from groq import Groq
import config

# (title, writing instruction) for each report section
REPORT_SECTIONS = [
    ("Overview", "Introduce the topic and give a clear high-level summary."),
    ("Key Findings", "List the most important facts as bullet points with citations."),
    ("Detailed Analysis", "Compare sources, discuss trends, contradictions, and implications."),
    ("Conclusion", "Summarize insights and suggest future research directions."),
]


def synthesize_report_long(question: str, sources: list[dict]):
    """
    Generator: streams a long, section-wise report.
    Each request stays small enough for the 12K TPM tier.
    """
    context = _build_context(sources)
    client = Groq(api_key=config.GROQ_API_KEY)
    written_so_far = ""
    completed = []

    for title, instruction in REPORT_SECTIONS:
        # Compact progress note (keeps requests small — NOT the full report)
        progress = "Sections completed: " + (", ".join(completed) if completed else "none")
        if written_so_far:
            progress += f"\nLast lines written (for flow): ...{written_so_far[-400:]}"

        messages = [
            {
                "role": "system",
                "content": (
                    "You are WARISE, a research synthesis engine. "
                    "Write ONLY the section you are asked for. "
                    "Do NOT include the section heading or title in your answer — "
                    "the app adds it automatically. Start directly with the content. "
                    "Cite sources as [Source 1], [Source 2], etc. "
                    "Do not repeat content already written."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Research Question: {question}\n\n"
                    f"Sources:\n{context}\n\n"
                    f"{progress}\n\n"
                    f"Now write the '{title}' section "
                    f"(heading is added by the app — do NOT type it).\n"
                    f"Instructions: {instruction}"
                )
            }
        ]

        # Create the stream, with ONE automatic retry on rate-limit errors
        stream = None
        for attempt in range(2):
            try:
                stream = client.chat.completions.create(
                    model=config.LLM_MODEL,
                    messages=messages,
                    temperature=0.3,
                    max_completion_tokens=config.MAX_REPORT_TOKENS,
                    stream=True
                )
                break
            except Exception as e:
                if attempt == 0 and "rate_limit" in str(e):
                    yield ("\n\n⏳ *API minute-quota reached — "
                           "waiting 60 seconds before continuing...*\n\n")
                    time.sleep(60)
                else:
                    yield f"\n\n❌ AI Generation Error: {e}"
                    return

        # Stream section header first (app-controlled, so no duplication)
        header = f"\n\n## {title}\n\n"
        written_so_far += header
        yield header

        # Stream section content token by token
        for chunk in stream:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                written_so_far += text
                yield text

        completed.append(title)


def _build_context(sources: list[dict]) -> str:
    """Helper: combines all source texts into one context string."""
    parts = []
    for i, src in enumerate(sources, 1):
        parts.append(
            f"[Source {i}] Title: {src['title']}\n"
            f"URL: {src['url']}\n"
            f"Content: {src['content']}"
        )
    return "\n\n---\n\n".join(parts)
