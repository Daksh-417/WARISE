import concurrent.futures
import html as html_lib
import re

import trafilatura

from . import mock


def scrape_one(url):
    try:
        html = trafilatura.fetch_url(url)
        if not html:
            return None

        if isinstance(html, bytes):
            html = html.decode("utf-8", "ignore")

        text = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            favor_recall=True,
        )

        if not text or len(text.split()) < 40:
            return None

        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
        title = title_match.group(1).strip() if title_match else url
        title = html_lib.unescape(title)
        title = re.sub(r"\s+", " ", title)

        return {
            "url": url,
            "title": title or url,
            "text": re.sub(r"\s+", " ", text).strip(),
        }
    except Exception:
        return None


def scrape_urls(urls, max_pages=5, mock_mode=False, query=""):
    if mock_mode:
        return mock.pages(query)[:max_pages]

    urls = list(dict.fromkeys(urls))[:max_pages]

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        pages = list(executor.map(scrape_one, urls))

    return [page for page in pages if page]