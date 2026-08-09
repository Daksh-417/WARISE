"""
search_service.py
Handles web search using Tavily API.
Returns structured results: title, URL, and clean content.
"""

from tavily import TavilyClient
import config


def search_web(query: str, max_results: int = None) -> list[dict]:
    """
    Search the web for a given query.

    Args:
        query: The research question or topic.
        max_results: Number of results to return (default from config).

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
            search_depth="advanced"  # "basic" is faster; "advanced" is deeper
        )

        # Format results into a clean structure
        results = []
        for item in response.get("results", []):
            results.append({
                "title": item.get("title", "Untitled"),
                "url": item.get("url", ""),
                "content": item.get("content", "")
            })

        return results

    except Exception as e:
        print(f"[Search Error] {e}")
        return []