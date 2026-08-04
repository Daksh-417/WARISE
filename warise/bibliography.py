from datetime import datetime

from .utils import domain


def _title(page):
    return (page.get("title") or "Untitled").strip()


def apa(page):
    title = _title(page)
    site = domain(page.get("url", "")) or "Unknown site"
    url = page.get("url", "")
    accessed = datetime.now().strftime("%B %d, %Y")

    return f"{title}. (n.d.). {site}. Retrieved {accessed}, from {url}"


def mla(page):
    title = _title(page)
    site = domain(page.get("url", "")) or "Unknown site"
    url = page.get("url", "")
    accessed = datetime.now().strftime("%d %b %Y")

    return f'"{title}." {site}, n.d., {url}. Accessed {accessed}.'


def format_bibliography(pages, style="APA"):
    formatter = apa if style.upper() == "APA" else mla
    return [formatter(page) for page in pages]