import datetime
import time

import streamlit as st

from warise import (
    bibliography,
    chunk,
    config,
    db,
    export,
    insights,
    llm,
    rank,
    scrape,
    search,
    utils,
)

st.set_page_config(
    page_title="WARISE",
    page_icon="🔎",
    layout="wide",
)

st.title("WARISE")
st.caption(
    "Full evidence pipeline: DuckDuckGo primary, Tavily fallback, BM25 ranking, "
    "citations, evidence panel, contradictions, PDF export, SQLite history."
)

db.init_db()


@st.cache_data(ttl=config.CACHE_TTL, show_spinner=False)
def cached_search(query, max_sources, mock_mode):
    return search.web_search(query, max_results=max_sources, mock_mode=mock_mode)


@st.cache_data(ttl=config.CACHE_TTL, show_spinner=False)
def cached_scrape(urls, max_sources, mock_mode, query):
    return scrape.scrape_urls(
        list(urls),
        max_pages=max_sources,
        mock_mode=mock_mode,
        query=query,
    )


def evidence_by_source(evidence):
    grouped = {}

    for item in evidence:
        grouped.setdefault(item["source_id"], []).append(item)

    return grouped


with st.sidebar:
    st.header("Settings")

    mode = st.selectbox(
        "Answer mode",
        [
            "Short Summary",
            "Detailed Report",
            "Bullet Points",
            "Fact Check",
            "Claim Table",
            "Study Mode",
        ],
    )

    max_sources = st.slider("Max sources", 3, 8, 5)
    bib_style = st.selectbox("Bibliography style", ["APA", "MLA"])

    mock_mode = st.checkbox(
        "Mock API mode",
        value=False,
        help="Use dummy data for demos without using external API credits.",
    )

    urls_text = st.text_area("URL-only mode, one URL per line", "")

    st.caption(f"Rate limit: {config.RATE_LIMIT_SECONDS}s between runs.")


query = st.text_input("Research question or claim")
run = st.button("Run pipeline", type="primary")


if run:
    if time.time() - st.session_state.get("last_run", 0) < config.RATE_LIMIT_SECONDS:
        st.warning("Rate limit active. Wait a few seconds.")
        st.stop()

    st.session_state.last_run = time.time()

    if not query.strip():
        st.error("Enter a research question or claim.")
        st.stop()

    user_urls = [
        url.strip()
        for url in urls_text.splitlines()
        if url.strip().startswith("http")
    ]

    try:
        with st.status("WARISE pipeline", expanded=True) as status:
            st.write("1/6 Search")

            if user_urls:
                results = [
                    {
                        "title": utils.domain(url) or url,
                        "url": url,
                        "snippet": "User URL",
                    }
                    for url in user_urls[:max_sources]
                ]
                provider = "URL-only"
            else:
                results, provider = cached_search(query, max_sources, mock_mode)

            if not results:
                status.update(label="Search failed", state="error")
                st.error(
                    "No search results. Try another query, add TAVILY_API_KEY, "
                    "or enable Mock API mode."
                )
                st.stop()

            st.write(f"Provider: {provider} | Results: {len(results)}")

            st.write("2/6 Scrape")
            pages = cached_scrape(
                tuple(item["url"] for item in results),
                max_sources,
                mock_mode,
                query,
            )

            if not pages:
                status.update(label="Scraping failed", state="error")
                st.error("No readable pages were scraped.")
                st.stop()

            st.write(f"Pages: {len(pages)}")

            st.write("3/6 Chunk")
            chunks = chunk.make_chunks(pages)

            st.write("4/6 Rank")
            evidence = rank.rank_chunks(chunks, query, top_k=6)

            if not evidence:
                status.update(label="Ranking failed", state="error")
                st.error("No relevant evidence found.")
                st.stop()

            st.write("5/6 Contradiction analysis")
            contradictions = insights.detect_contradictions(pages, query)
            confidence = insights.confidence_score(pages, evidence, contradictions)

            st.write(f"6/6 Ready | Confidence heuristic: {confidence}%")
            status.update(label="Pipeline complete", state="complete", expanded=False)

        st.session_state.result = {
            "created_at": datetime.datetime.now().isoformat(),
            "query": query,
            "mode": mode,
            "bib_style": bib_style,
            "provider": provider,
            "mock_mode": mock_mode,
            "pages": pages,
            "evidence": evidence,
            "contradictions": contradictions,
            "confidence": confidence,
            "answer": "",
        }
        st.session_state.selected_citation = None

    except Exception as exc:
        st.error(f"Pipeline error: {exc}")
        st.stop()


if st.session_state.get("result") and not st.session_state.result.get("answer"):
    result = st.session_state.result
    box = st.empty()
    full = ""

    try:
        for token in llm.stream_answer(
            result["query"],
            result["evidence"],
            result["mode"],
            result.get("mock_mode", False),
        ):
            full += token
            box.markdown(full)
    except Exception as exc:
        full = f"LLM error: {exc}"

    valid_ids = list(range(1, len(result["pages"]) + 1))
    sanitized, removed = utils.sanitize_citations(full, valid_ids)

    if removed:
        sanitized += f"\n\n> Removed unsupported citations: {removed}."

    if not utils.extract_citations(sanitized):
        sanitized += "\n\n> Warning: no citations were detected in this answer."

    if not sanitized.strip():
        sanitized = "No answer was generated."

    result["answer"] = sanitized
    st.session_state.result = result
    box.empty()

    source_records = [
        {
            "source_id": i,
            "title": page.get("title", ""),
            "url": page.get("url", ""),
            "quality": utils.source_quality(page.get("url", "")),
        }
        for i, page in enumerate(result["pages"], 1)
    ]

    db.save_session(
        result["query"],
        result["mode"],
        sanitized,
        result["confidence"],
        source_records,
    )


if st.session_state.get("result") and st.session_state.result.get("answer"):
    result = st.session_state.result
    pages = result["pages"]
    evidence = result["evidence"]
    evidence_map = evidence_by_source(evidence) 

    st.subheader("Result")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Confidence", f"{result['confidence']}%")
    col2.metric("Sources", len(pages))
    col3.metric("Evidence chunks", len(evidence))
    col4.metric("Provider", result.get("provider", "Unknown"))

    if result["contradictions"]:
        with st.expander(
            f"Contradiction detector: {len(result['contradictions'])} possible conflicts",
            expanded=True,
        ):
            for item in result["contradictions"]:
                st.warning(f"{item['source_a']} vs {item['source_b']}")
                st.write(f"Source A quote: {item['quote_a']}")
                st.write(f"Source B quote: {item['quote_b']}")
    else:
        st.success("No obvious contradictions detected by the heuristic detector.")

    st.subheader("Sources")

    for i, page in enumerate(pages, 1):
        with st.expander(
            f"[{i}] {page.get('title', 'Untitled')[:90]} | "
            f"{utils.source_quality(page.get('url', ''))}"
        ):
            st.write(page.get("url", ""))
            st.write(utils.truncate(page.get("text", ""), 700))

            for item in evidence_map.get(i, [])[:2]:
                st.markdown(
                    f"**Top evidence:** {utils.truncate(item.get('text', ''), 250)}"
                )

    st.subheader(f"Answer: {result['mode']}")
    st.markdown(result["answer"])


    st.subheader("Copy / Export")
    st.code(result["answer"], language="markdown")

    markdown_file = export.build_markdown(
        result["query"],
        result["mode"],
        result["confidence"],
        result["answer"],
        pages,
        result["contradictions"],
        result.get("bib_style", "APA"),
    )

    pdf_file = export.build_pdf(
        result["query"],
        result["mode"],
        result["confidence"],
        result["answer"],
        pages,
        result["contradictions"],
        result.get("bib_style", "APA"),
    )

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    st.download_button(
        "Download Markdown",
        markdown_file,
        file_name=f"warise_{stamp}.md",
        mime="text/markdown",
    )

    st.download_button(
        "Download PDF",
        pdf_file,
        file_name=f"warise_{stamp}.pdf",
        mime="application/pdf",
    )

    with st.expander(f"Bibliography ({result.get('bib_style', 'APA')})"):
        for item in bibliography.format_bibliography(
            pages,
            result.get("bib_style", "APA"),
        ):
            st.write(f"- {item}")


with st.expander("History"):
    history = db.load_history(10)

    st.json(
        [
            {
                "created_at": item["created_at"],
                "query": item["query"],
                "mode": item["mode"],
                "confidence": item["confidence"],
            }
            for item in history
        ]
    )

    with st.expander("Raw history"):
        st.json(history)
