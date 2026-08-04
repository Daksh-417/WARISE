from warise.chunk import chunk_text


def test_chunk_text():
    text = " ".join(f"w{i}" for i in range(900))
    chunks = chunk_text(text, words=400, overlap=75)

    assert len(chunks) >= 2
    assert len(chunks[0].split()) <= 400