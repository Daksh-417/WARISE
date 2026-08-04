import re

POSITIVE = {
    "agree",
    "advantage",
    "beneficial",
    "benefit",
    "benefits",
    "confirmed",
    "confirms",
    "correct",
    "effective",
    "good",
    "help",
    "helps",
    "improve",
    "improved",
    "improves",
    "positive",
    "reliable",
    "safe",
    "success",
    "successful",
    "supported",
    "supports",
    "true",
    "valid",
}

NEGATIVE = {
    "bad",
    "contradict",
    "contradicts",
    "danger",
    "dangerous",
    "debunked",
    "disagree",
    "dispute",
    "disputes",
    "doubt",
    "doubtful",
    "fail",
    "failed",
    "failure",
    "fails",
    "false",
    "harm",
    "harmful",
    "incorrect",
    "ineffective",
    "negative",
    "problem",
    "problems",
    "risk",
    "risks",
    "risky",
    "unsupported",
}


def _sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text or "")
    return [part.strip() for part in parts if len(part.strip()) > 20]


def _sentiment(sentence):
    tokens = set(re.findall(r"\w+", sentence.lower()))
    pos = len(tokens & POSITIVE)
    neg = len(tokens & NEGATIVE)

    if pos > neg:
        return "positive", pos - neg

    if neg > pos:
        return "negative", neg - pos

    return "neutral", 0


def _page_stance(page, query_tokens):
    sentences = _sentences(page.get("text", ""))
    if not sentences:
        return "neutral", ""

    relevant = [
        sentence
        for sentence in sentences
        if any(token in sentence.lower() for token in query_tokens)
    ]

    pool = relevant[:20] if relevant else sentences[:10]

    pos = 0
    neg = 0
    best = pool[0]
    best_strength = -1

    for sentence in pool:
        label, strength = _sentiment(sentence)

        if label == "positive":
            pos += 1

        if label == "negative":
            neg += 1

        if strength > best_strength:
            best_strength = strength
            best = sentence

    if pos > neg:
        label = "positive"
    elif neg > pos:
        label = "negative"
    else:
        label = "neutral"

    return label, best


def detect_contradictions(pages, query):
    query_tokens = set(re.findall(r"\w+", query.lower()))
    stances = []

    for source_id, page in enumerate(pages, 1):
        label, quote = _page_stance(page, query_tokens)

        stances.append(
            {
                "source_id": source_id,
                "title": page.get("title", "Untitled"),
                "url": page.get("url", ""),
                "label": label,
                "quote": quote,
            }
        )

    contradictions = []

    for a in stances:
        for b in stances:
            if a["source_id"] >= b["source_id"]:
                continue

            if {a["label"], b["label"]} == {"positive", "negative"}:
                contradictions.append(
                    {
                        "source_a": f"[{a['source_id']}] {a['title'][:70]}",
                        "source_b": f"[{b['source_id']}] {b['title'][:70]}",
                        "reason": "Opposite sentiment detected around query terms.",
                        "quote_a": a["quote"][:250],
                        "quote_b": b["quote"][:250],
                    }
                )

    return contradictions[:5]


def confidence_score(pages, evidence, contradictions):
    base = min(55, len(pages) * 11)
    base += min(35, len(evidence) * 3)
    penalty = len(contradictions) * 15

    return max(5, min(100, base - penalty))