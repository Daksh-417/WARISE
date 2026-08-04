def search_results(query):
    return [
        {
            "title": "Mock Edu Overview",
            "url": "https://mock.edu/overview",
            "snippet": f"Mock overview for {query}",
        },
        {
            "title": "Mock Org Risks",
            "url": "https://mock.org/risks",
            "snippet": f"Mock risks for {query}",
        },
        {
            "title": "Mock Net Mixed",
            "url": "https://mock.net/mixed",
            "snippet": f"Mock mixed evidence for {query}",
        },
    ]


def pages(query):
    topic = query or "the topic"

    return [
        {
            "title": "Mock Edu Overview",
            "url": "https://mock.edu/overview",
            "text": (
                f"{topic} is effective and beneficial. Studies support that {topic} "
                "can improve outcomes and help users. The evidence is positive, "
                "reliable, and successful. "
            )
            * 3,
        },
        {
            "title": "Mock Org Risks",
            "url": "https://mock.org/risks",
            "text": (
                f"{topic} is risky and harmful. Critics argue that {topic} can fail, "
                "cause problems, and is dangerous. The evidence is negative and "
                "unsupported. "
            )
            * 3,
        },
        {
            "title": "Mock Net Mixed",
            "url": "https://mock.net/mixed",
            "text": (
                f"{topic} has mixed evidence. Some reports agree and support benefits, "
                "while other reports dispute effectiveness and mention risks. "
            )
            * 3,
        },
    ]


def llm_stream(query, mode, evidence):
    if mode == "Fact Check":
        text = (
            f"Supported. Mock evidence says {query} is supported [1]. "
            "A second mock source agrees [2]."
        )

    elif mode == "Claim Table":
        text = (
            "| Claim | Source | Evidence Quote |\n"
            "|---|---|---|\n"
            "| Mock claim is supported | [1] | Mock evidence quote one. |\n"
            "| Mock source two agrees | [2] | Mock evidence quote two. |"
        )

    elif mode == "Study Mode":
        text = (
            f"1. MCQ: Which source supports {query}? A [1] B [2] C [3]. Answer: A [1].\n"
            "2. MCQ: Which source mentions risk? A [1] B [2] C [3]. Answer: B [2].\n"
            "3. Flashcard: What does source [1] provide? Answer: support [1].\n"
            "4. Flashcard: What does source [2] mention? Answer: risk [2].\n"
            "5. Flashcard: What does source [3] report? Answer: mixed evidence [3]."
        )

    elif mode == "Bullet Points":
        text = (
            f"- Mock point one about {query} [1].\n"
            "- Mock point two adds caution [2].\n"
            "- Mock point three reports mixed evidence [3]."
        )

    else:
        text = (
            f"This mock answer summarizes {query}. "
            "Source one provides support [1]. "
            "Source two adds caution [2]. "
            "Source three reports mixed evidence [3]."
        )

    for token in text.split(" "):
        yield token + " "