def chunk_text(text, words=400, overlap=75):
    tokens = text.split()
    if not tokens:
        return []

    step = max(1, words - overlap)
    chunks = []

    for i in range(0, len(tokens), step):
        part = tokens[i : i + words]
        if part:
            chunks.append(" ".join(part))

        if i + words >= len(tokens):
            break

    return chunks

def make_chunks(pages, words=250, overlap=50):
    chunks = []

    for source_id, page in enumerate(pages, 1):
        for text in chunk_text(page.get("text", ""), words, overlap):
            chunks.append(
                {
                    "source_id": source_id,
                    "title": page.get("title", ""),
                    "url": page.get("url", ""),
                    "text": text,
                }
            )

    return chunks
