"""
ai_service.py
Handles AI synthesis using Groq (Llama 3).
Takes search context and generates a structured research report.
"""

from groq import Groq
import config


def synthesize_report(question: str, sources: list[dict]) -> str:
    """
    Generate a complete research report from sources.

    Args:
        question: The user's research question.
        sources: List of source dicts from search_service.

    Returns:
        The full report as a string (non-streaming).
    """
    # Build context string from all sources
    context = _build_context(sources)

    client = Groq(api_key=config.GROQ_API_KEY)

    messages = [
        {
            "role": "system",
            "content": (
                "You are WARISE, a research synthesis engine. "
                "Write a structured report with these sections:\n"
                "## Overview\n"
                "## Key Findings\n"
                "- Bullet points\n"
                "## Analysis\n"
                "## Conclusion\n\n"
                "Cite sources as [Source 1], [Source 2], etc. "
                "Be concise, factual, and well-organized."
            )
        },
        {
            "role": "user",
            "content": f"Research Question: {question}\n\nSources:\n{context}"
        }
    ]

    try:
        response = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=messages,
            temperature=0.3,  # Lower = more factual
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"❌ AI Generation Error: {e}"


def synthesize_report_stream(question: str, sources: list[dict]):
    """
    Generator version: streams the report word-by-word.
    Used with st.write_stream() for live output.
    """
    context = _build_context(sources)

    client = Groq(api_key=config.GROQ_API_KEY)

    messages = [
        {
            "role": "system",
            "content": (
                "You are WARISE, a research synthesis engine. "
                "Write a structured report with these sections:\n"
                "## Overview\n"
                "## Key Findings\n"
                "- Bullet points\n"
                "## Analysis\n"
                "## Conclusion\n\n"
                "Cite sources as [Source 1], [Source 2], etc."
            )
        },
        {
            "role": "user",
            "content": f"Research Question: {question}\n\nSources:\n{context}"
        }
    ]

    stream = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=messages,
        temperature=0.3,
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


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