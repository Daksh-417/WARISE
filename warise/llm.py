from groq import Groq

from . import mock
from .config import GROQ_API_KEY, MODEL

_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

MODE_RULES = {
    "Short Summary": "Write one concise paragraph.",
    "Detailed Report": "Write a structured report with headings and short paragraphs.",
    "Bullet Points": "Write 5-10 bullets.",
    "Fact Check": "Start with Supported, Unsupported, or Mixed Evidence. Then explain.",
    "Claim Table": "Return only a Markdown table with columns: Claim | Source | Evidence Quote.",
    "Study Mode": "Create 5 multiple-choice questions and 5 flashcards based only on the evidence.",
}

SYSTEM = """You are WARISE, a strict evidence synthesis engine.
Use only the supplied evidence. Cite sources inline as [1], [2], etc.
Never invent facts or sources. If evidence is insufficient, say that clearly."""


def _context(evidence):
    parts = []
    total_chars = 0
    MAX_CHARS = 15000  # ~4000 tokens, safely under Groq's 6000 limit

    for item in evidence:
        text = item['text']
        if len(text) > 1500:
            text = text[:1500] + "..."
            
        part = (
            f"[{item['source_id']}] {item['title']}\n"
            f"URL: {item['url']}\n"
            f"Evidence: {text}"
        )
        
        if total_chars + len(part) > MAX_CHARS:
            break
            
        parts.append(part)
        total_chars += len(part)

    return "\n\n---\n\n".join(parts)


def stream_answer(query, evidence, mode, mock_mode=False):
    if mock_mode:
        yield from mock.llm_stream(query, mode, evidence)
        return

    if not _client:
        yield "Missing GROQ_API_KEY. Add it to .env and restart."
        return

    if not evidence:
        yield "No evidence was found to answer this query."
        return

    user = f"""Question or claim: {query}

Mode: {mode}
Mode instruction: {MODE_RULES.get(mode, "Answer clearly.")}

Evidence:
{_context(evidence)}

Rules:
- Use only evidence above.
- Cite source IDs like [1] and [2].
- Prefer direct support over speculation.
- If sources disagree, mention the disagreement.
"""

    try:
        stream = _client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": user},
            ],
            temperature=0.1,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except Exception as exc:
        yield f"LLM error: {exc}"
