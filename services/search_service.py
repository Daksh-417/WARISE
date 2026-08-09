"""
search_service.py
Handles web search using Tavily API.
Returns structured results: title, URL, and clean content.
"""

from tavily import TavilyClient
import config

def search_web(query: str, max_results: int = None) -> list[dict]:
    """Searches Tavily with advanced depth. Returns clean content."""
    if max_results is None:
        max_results = config.MAX_SEARCH_RESULTS

    client = TavilyClient(api_key=config.TAVILY_API_KEY)

    try:
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced"  # Deep extraction
        )

        results = []
        for item in response.get("results", []):
            results.append({
                "title": item.get("title", "Untitled"),
                "url": item.get("url", ""),
                "content": item.get("content", "")  # NO truncation here
            })

        # Smart budget: trim total context if it exceeds the limit
        results = _apply_context_budget(results)
        return results

    except Exception as e:
        print(f"[Search Error] {e}")
        return []


def _apply_context_budget(sources: list[dict]) -> list[dict]:
    """
    Instead of cutting each source blindly,
    we trim from the END if total context exceeds budget.
    This preserves the most relevant sources (top results).
    """
    total_chars = 0
    trimmed = []

    for src in sources:
        total_chars += len(src["content"])
        if total_chars > config.MAX_CONTEXT_CHARS:
            # Trim this source to fit remaining budget
            remaining = config.MAX_CONTEXT_CHARS - (total_chars - len(src["content"]))
            src["content"] = src["content"][:remaining]
            trimmed.append(src)
            break  # Stop adding more sources
        trimmed.append(src)

    return trimmed
