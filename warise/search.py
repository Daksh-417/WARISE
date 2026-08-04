from . import mock
from .config import TAVILY_API_KEY


def _norm_ddg(items):
    out = []

    for item in items:
        url = item.get("href") or item.get("url") or ""
        if not url:
            continue

        out.append(
            {
                "title": item.get("title", url),
                "url": url,
                "snippet": item.get("body") or item.get("snippet", ""),
            }
        )

    return out


def ddg_search(query, max_results):
    try:
        from duckduckgo_search import DDGS

        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=max_results))
        return _norm_ddg(results)
    except Exception:
        return []


def tavily_search(query, max_results):
    if not TAVILY_API_KEY:
        return []

    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(query=query, max_results=max_results)

        out = []
        for item in response.get("results", []):
            url = item.get("url", "")
            if not url:
                continue

            out.append(
                {
                    "title": item.get("title", url),
                    "url": url,
                    "snippet": item.get("content", "")[:500],
                }
            )

        return out
    except Exception:
        return []


def web_search(query, max_results=5, mock_mode=False):
    if mock_mode:
        return mock.search_results(query), "Mock"

    results = ddg_search(query, max_results)
    if results:
        return results, "DuckDuckGo"

    results = tavily_search(query, max_results)
    if results:
        return results, "Tavily"

    return [], "None"