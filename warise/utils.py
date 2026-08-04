import re
from urllib.parse import urlparse

HIGH_CREDIBILITY = (".edu", ".gov")
LOW_OR_COMMUNITY = ("blogspot", "wordpress", "medium", "reddit", "quora")


def domain(url):
    netloc = urlparse(url).netloc.lower()
    return netloc.removeprefix("www.") if netloc else ""


def source_quality(url):
    d = domain(url)

    if d.endswith(HIGH_CREDIBILITY):
        return "High credibility"

    if any(marker in d for marker in LOW_OR_COMMUNITY):
        return "Low/community"

    return "Standard"


def truncate(text, limit=300):
    text = " ".join(str(text).split())
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "..."


def extract_citations(text):
    return sorted({int(n) for n in re.findall(r"\[(\d+)\]", text or "")})


def sanitize_citations(text, valid_ids):
    valid = set(valid_ids)
    removed = []

    def replace(match):
        n = int(match.group(1))
        if n in valid:
            return match.group(0)
        removed.append(n)
        return ""

    sanitized = re.sub(r"\[(\d+)\]", replace, text or "")
    sanitized = re.sub(r"[ \t]{2,}", " ", sanitized)
    sanitized = re.sub(r"\n{3,}", "\n\n", sanitized)
    return sanitized.strip(), sorted(set(removed))