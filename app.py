"""
app.py — WARISE Main Application
Run with: streamlit run app.py
"""

import streamlit as st
import config
from services.search_service import search_web
from services.ai_service import synthesize_report_long
from utils.exporter import build_markdown, get_filename

# ─────────────────────────────────────────────
# Page Setup
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="WARISE — AI Research Engine",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 WARISE")
st.caption("Web Augmented Research Intelligence and Synthesis Engine")

# ─────────────────────────────────────────────
# Validate API Keys
# ─────────────────────────────────────────────
missing_keys = config.validate_keys()
if missing_keys:
    st.error(f"⚠️ Missing API keys: {', '.join(missing_keys)}. "
             f"Add them to `.streamlit/secrets.toml` (local) "
             f"or the Secrets manager (Streamlit Cloud).")
    st.stop()

# ─────────────────────────────────────────────
# Input Section
# ─────────────────────────────────────────────
st.subheader("📝 Research Query")

col1, col2 = st.columns([3, 1])
with col1:
    question = st.text_input(
        "Enter your research question:",
        placeholder="e.g., What is the impact of AI on healthcare?"
    )
with col2:
    max_sources = st.slider("Sources", min_value=2, max_value=6, value=6)

generate_btn = st.button("🚀 Generate Report", type="primary", use_container_width=True)

# ─────────────────────────────────────────────
# Main Logic
# ─────────────────────────────────────────────
if generate_btn and question.strip():

    # Step 1: Search the web
    with st.spinner("🔍 Searching the web..."):
        sources = search_web(question, max_results=max_sources)

    if not sources:
        st.error("No search results found. Try rephrasing your question.")
        st.stop()

    # Step 2: Display sources
    st.subheader("🔗 Sources Found")
    for i, src in enumerate(sources, 1):
        with st.expander(f"Source {i}: {src['title']}"):
            st.write(f"**URL:** [{src['url']}]({src['url']})")
            st.write(f"**Snippet:** {src['content'][:300]}...")

    st.divider()

    # Step 3: Generate long AI report (streamed, section-wise)
    st.subheader("📄 Synthesized Report")

    report_placeholder = st.empty()
    full_report = ""

    for chunk in synthesize_report_long(question, sources):
        full_report += chunk
        report_placeholder.markdown(full_report + "▌")  # Cursor effect

    report_placeholder.markdown(full_report)  # Final clean render

    st.divider()

    # Step 4: Export / Download
    st.subheader("💾 Export")

    markdown_content = build_markdown(question, full_report, sources)
    filename = get_filename(question)

    st.download_button(
        label="📥 Download as Markdown",
        data=markdown_content,
        file_name=filename,
        mime="text/markdown",
        use_container_width=True
    )

elif generate_btn and not question.strip():
    st.warning("Please enter a research question first.")
