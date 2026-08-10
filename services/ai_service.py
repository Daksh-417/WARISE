"""
ai_service.py
Handles AI synthesis using Groq (Llama 3.3 70B).
Section-wise generation: each API call writes one section within
the output ceiling; the app concatenates them into a long report.
"""

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
    Each call stays under MAX_REPORT_TOKENS; combined length
    scales with the number of sections, not the ceiling.
    """
    context = _build_context(sources)
    client = Groq(api_key=config.GROQ_API_KEY)
    written_so_far = ""

    for title, instruction in REPORT_SECTIONS:
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
                    f"Report written so far:\n{written_so_far}\n\n"
                    f"Now write the '{title}' section "
                    f"(heading is added by the app — do NOT type it).\n"
                    f"Instructions: {instruction}"
                )
            }
        ]

        try:
            stream = client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=messages,
                temperature=0.3,
                max_completion_tokens=config.MAX_REPORT_TOKENS,
                stream=True
            )
        except Exception as e:
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
