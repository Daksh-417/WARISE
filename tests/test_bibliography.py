from warise.bibliography import format_bibliography


def test_bibliography():
    pages = [
        {
            "title": "Test Title",
            "url": "https://www.example.com/page",
        }
    ]

    apa = format_bibliography(pages, "APA")[0]
    mla = format_bibliography(pages, "MLA")[0]

    assert "example.com" in apa
    assert "Test Title" in mla