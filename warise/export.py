from datetime import datetime

from fpdf import FPDF

from .bibliography import format_bibliography
from .utils import source_quality


def _ascii(value):
    return str(value).encode("ascii", "ignore").decode("ascii")


def _heading(pdf, text):
    pdf.set_font("Helvetica", "B", 12)
    pdf.multi_cell(0, 8, _ascii(text))
    pdf.ln(1)


def _paragraph(pdf, text, size=11):
    pdf.set_font("Helvetica", "", size)
    pdf.multi_cell(0, 6, _ascii(text))
    pdf.ln(1)


def build_markdown(
    query,
    mode,
    confidence,
    answer,
    pages,
    contradictions,
    bib_style="APA",
):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# {query}",
        "",
        f"Generated: {stamp}",
        f"Mode: {mode}",
        f"Confidence: {confidence}%",
        "",
        "## Answer",
        answer,
        "",
    ]

    if contradictions:
        lines.append("## Contradictions")

        for item in contradictions:
            lines.append(f"- {item['source_a']} vs {item['source_b']}: {item['reason']}")

        lines.append("")

    lines.append("## Sources")

    for i, page in enumerate(pages, 1):
        title = page.get("title", "Untitled")
        url = page.get("url", "")
        quality = source_quality(url)
        lines.append(f"{i}. {title} | {quality} | {url}")

    lines.append("")
    lines.append(f"## Bibliography ({bib_style})")

    for item in format_bibliography(pages, bib_style):
        lines.append(f"- {item}")

    return "\n".join(lines)


def build_pdf(
    query,
    mode,
    confidence,
    answer,
    pages,
    contradictions,
    bib_style="APA",
):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 10, _ascii("WARISE Research Report"))
    pdf.ln(1)

    _paragraph(pdf, f"Query: {query}", size=12)
    _paragraph(pdf, f"Mode: {mode} | Confidence: {confidence}%", size=10)

    _heading(pdf, "Answer")
    _paragraph(pdf, answer)

    if contradictions:
        _heading(pdf, "Contradictions")

        for item in contradictions:
            _paragraph(
                pdf,
                f"{item['source_a']} vs {item['source_b']}: {item['reason']}",
                size=10,
            )
            _paragraph(pdf, f"A: {item['quote_a']}", size=9)
            _paragraph(pdf, f"B: {item['quote_b']}", size=9)

    _heading(pdf, "Sources")

    for i, page in enumerate(pages, 1):
        title = page.get("title", "Untitled")
        url = page.get("url", "")
        quality = source_quality(url)
        _paragraph(pdf, f"{i}. {title} | {quality} | {url}", size=10)

    _heading(pdf, f"Bibliography ({bib_style})")

    for item in format_bibliography(pages, bib_style):
        _paragraph(pdf, item, size=10)

    return bytes(pdf.output())