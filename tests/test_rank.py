from warise.rank import rank_chunks


def test_rank_chunks():
    chunks = [
        {
            "source_id": 1,
            "title": "climate",
            "url": "u",
            "text": "climate change warming evidence climate",
        },
        {
            "source_id": 2,
            "title": "food",
            "url": "u",
            "text": "pizza pasta recipe food",
        },
    ]

    ranked = rank_chunks(chunks, "climate change", top_k=2)

    assert ranked[0]["source_id"] == 1
    assert ranked[0]["score"] >= ranked[1]["score"]