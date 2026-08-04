from warise.utils import extract_citations, sanitize_citations


def test_extract_citations():
    assert extract_citations("a [1] b [2] [9]") == [1, 2, 9]


def test_sanitize_citations():
    text, removed = sanitize_citations("a [1] b [3]", [1, 2])

    assert "[1]" in text
    assert "[3]" not in text
    assert removed == [3]