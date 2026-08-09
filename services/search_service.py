"""
search_service.py
Handles web search using Tavily API.
Applies a smart context budget instead of blind per-source truncation.
"""

from tavily import TavilyClient
import config


def search_web(query: str, max_results: int = None) -> list[dict]:
    """
    Search the web for a given query.

    Returns:
        List of dicts with keys: 'title', 'url', 'content'
    """
    if max_results is None:
        max_results = config.MAX_SEARCH_RESULTS

    client = TavilyClient(api_key=config.TAVILY_API_KEY)

    try:
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced"  # Deep, clean extraction
        )

        results = []
        for item in response.get("results", []):
            results.append({
                "title": item.get("title", "Untitled"),
                "url": item.get("url", ""),
                "content": item.get("content", "")  # No blind truncation
            })

        return _apply_context_budget(results)

    except Exception as e:
        print(f"[Search Error] {e}")
        return []


def _apply_context_budget(sources: list[dict]) -> list[dict]:
    """
    Smart budget: if total context exceeds MAX_CONTEXT_CHARS,
    trim the tail (least relevant sources) while keeping
    top results fully intact.
    """
    total_chars = 0
    trimmed = []

    for src in sources:
        content_len = len(src["content"])

        if total_chars + content_len > config.MAX_CONTEXT_CHARS:
            remaining = config.MAX_CONTEXT_CHARS - total_chars
            if remaining > 0:
                src["content"] = src["content"][:remaining]
                trimmed.append(src)
            break  # Stop adding further sources

        total_chars += content_len
        trimmed.append(src)

    return trimmed
