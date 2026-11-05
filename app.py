
import io
import streamlit as st

from src.document_loader import extract_text_from_pdf
from src.chunker import chunk_text
from src.retriever import retrieve_relevant_chunks

from src.answer_generator import (
    generate_answer,
    generate_document_overview,
    generate_document_intelligence_report
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="ProofLens | AI Research Assistant",
    page_icon="🔍",
    layout="wide"
)


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #0e1117;
    color: #ffffff;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.main-title {
    font-size: 42px;
    font-weight: 800;
    color: #ffffff;
}

.subtitle {
    color: #aab4c3;
    font-size: 17px;
}

/* DASHBOARD METRIC CARDS */

div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #304b6b, #1c3049);
    padding: 22px;
    border-radius: 14px;
    border: 1px solid #648fc5;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

div[data-testid="stMetric"] label {
    color: #d5e5f8 !important;
    font-size: 15px !important;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 30px !important;
    font-weight: 800 !important;
}

/* BUTTONS */

div.stButton > button {
    background-color: #202f43;
    color: #ffffff;
    border: 1px solid #5275a5;
    border-radius: 9px;
    font-weight: 600;
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    background-color: #344d6b;
    color: #ffffff;
    border-color: #80a9df;
}

div.stButton > button:focus {
    color: #ffffff;
    border-color: #80a9df;
    box-shadow: 0 0 0 2px rgba(82,117,165,0.2);
}

/* HEADINGS */

h2, h3 {
    color: #e8eef7 !important;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

defaults = {
    "chunks": [],
    "documents": [],
    "answer": "",
    "sources": [],
    "evidence": [],
    "last_query": "",
    "overview": "",
    "intelligence_report": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🔍 ProofLens</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'An AI-powered research assistant that answers questions '
    'from documents with evidence-backed citations.'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.title("📁 Document Manager")

    uploaded_files = st.file_uploader(
        "Upload your PDF documents",
        type=["pdf"],
        accept_multiple_files=True
    )

    process_button = st.button(
        "⚙️ Process Documents",
        use_container_width=True
    )

    st.caption(
        "Upload one or more PDFs to begin analysing your documents."
    )

    if uploaded_files:

        st.write("**Uploaded files:**")

        for file in uploaded_files:
            st.write(f"📄 {file.name}")


# --------------------------------------------------
# DOCUMENT PROCESSING
# --------------------------------------------------

if process_button:

    if not uploaded_files:

        st.warning("Please upload at least one PDF.")

    else:

        all_chunks = []
        processed_documents = []
        document_errors = []

        progress_bar = st.progress(0)
        status_text = st.empty()

        for index, uploaded_file in enumerate(uploaded_files):

            try:

                status_text.write(
                    f"Processing {uploaded_file.name}..."
                )

                pdf_bytes = uploaded_file.getvalue()
                pdf_file = io.BytesIO(pdf_bytes)

                pages = extract_text_from_pdf(pdf_file)

                document_chunks = chunk_text(pages)

                for chunk in document_chunks:
                    chunk["document"] = uploaded_file.name

                all_chunks.extend(document_chunks)

                processed_documents.append({
                    "name": uploaded_file.name,
                    "pages": len(pages),
                    "chunks": len(document_chunks),
                    "size": len(pdf_bytes)
                })

            except Exception as error:

                document_errors.append(
                    f"{uploaded_file.name}: {error}"
                )

            progress_bar.progress(
                (index + 1) / len(uploaded_files)
            )

        status_text.empty()
        progress_bar.empty()

        if all_chunks:

            st.session_state["chunks"] = all_chunks

            st.session_state["documents"] = processed_documents

            st.session_state["answer"] = ""
            st.session_state["sources"] = []
            st.session_state["evidence"] = []
            st.session_state["last_query"] = ""
            st.session_state["overview"] = ""
            st.session_state["intelligence_report"] = ""

            st.success(
                f"Successfully processed "
                f"{len(processed_documents)} document(s)!"
            )

        else:

            st.session_state["chunks"] = []
            st.session_state["documents"] = []

            st.error(
                "No readable document content could be processed."
            )

        for error in document_errors:
            st.warning(error)


# --------------------------------------------------
# MAIN APPLICATION
# --------------------------------------------------

chunks = st.session_state["chunks"]
documents = st.session_state["documents"]


if chunks:

    # ==================================================
    # 1. DOCUMENT DASHBOARD
    # ==================================================

    st.markdown("## 📊 Document Dashboard")

    total_pages = sum(
        document["pages"] for document in documents
    )

    total_chunks = len(chunks)

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Documents Processed",
        len(documents)
    )

    col2.metric(
        "Total Pages",
        total_pages
    )

    col3.metric(
        "Evidence Chunks",
        total_chunks
    )

    with st.expander("📚 View Processed Documents"):

        for document in documents:

            st.write(f"**{document['name']}**")

            st.caption(
                f"{document['pages']} pages | "
                f"{document['chunks']} chunks"
            )

    st.divider()


    # ==================================================
    # 2. DOCUMENT OVERVIEW
    # ==================================================

    st.markdown("## 📝 Document Overview")

    st.caption(
        "Get a quick understanding of what your documents contain."
    )

    if st.button(
        "📄 Generate Document Overview",
        use_container_width=True,
        key="generate_overview"
    ):

        try:

            with st.spinner(
                "Generating document overview..."
            ):

                overview = generate_document_overview(chunks)

                st.session_state["overview"] = overview

        except Exception as error:

            st.error(
                f"Overview generation failed: {error}"
            )

    if st.session_state["overview"]:

        with st.container(border=True):

            st.markdown(
                st.session_state["overview"]
            )

    st.divider()


    # ==================================================
    # 3. DOCUMENT INTELLIGENCE REPORT
    # ==================================================

    st.markdown("## 🧠 Document Intelligence Report")

    st.caption(
        "Generate a detailed research report with findings, "
        "topics, facts, requirements and page references."
    )

    if st.button(
        "✨ Generate Intelligence Report",
        use_container_width=True,
        key="generate_intelligence"
    ):

        try:

            with st.spinner(
                "Analysing documents and preparing intelligence report..."
            ):

                report = generate_document_intelligence_report(chunks)

                st.session_state["intelligence_report"] = report

        except Exception as error:

            st.error(
                f"Intelligence report generation failed: {error}"
            )

    if st.session_state["intelligence_report"]:

        with st.container(border=True):

            st.markdown(
                st.session_state["intelligence_report"]
            )

    st.divider()


    # ==================================================
    # 4. ASK QUESTIONS ABOUT YOUR PDF
    # ==================================================

    st.markdown("## 💬 Ask Questions About Your PDF")

    st.caption(
        "Ask questions about your uploaded documents. "
        "ProofLens retrieves relevant evidence and generates "
        "answers with source references."
    )

    query = st.text_input(
        "Enter your question",
        placeholder="Example: What is the main topic of this document?",
        key="user_query"
    )

    if st.button(
        "🔍 Ask ProofLens",
        use_container_width=True,
        key="ask_question"
    ):

        if not query.strip():

            st.warning("Please enter a question first.")

        else:

            try:

                with st.spinner(
                    "Searching documents and analysing evidence..."
                ):

                    retrieved_chunks = retrieve_relevant_chunks(
                        query,
                        chunks
                    )

                    result = generate_answer(
                        query,
                        retrieved_chunks
                    )

                    st.session_state["answer"] = result["answer"]

                    st.session_state["sources"] = result["sources"]

                    st.session_state["evidence"] = retrieved_chunks

                    st.session_state["last_query"] = query

            except Exception as error:

                st.error(
                    f"Question answering failed: {error}"
                )


    # ==================================================
    # 5. ANSWER DISPLAY
    # ==================================================

    if st.session_state["answer"]:

        st.divider()

        st.markdown("### 💡 ProofLens Answer")

        st.markdown(
            st.session_state["answer"]
        )

        st.divider()


        # ---------------- SOURCE REFERENCES ----------------

        st.markdown("### 📌 Source References")

        sources = st.session_state["sources"]

        if sources:

            for document_name, page_number in sources:

                st.write(
                    f"📄 **{document_name}** — Page {page_number}"
                )

        else:

            st.info(
                "No verified source references are available "
                "for this answer."
            )


        # ---------------- EVIDENCE VIEWER ----------------

        st.markdown("### 📖 Evidence Viewer")

        evidence = st.session_state["evidence"]

        if evidence:

            for index, item in enumerate(evidence, start=1):

                with st.expander(
                    f"Evidence {index} | "
                    f"{item.get('document', 'Unknown')} | "
                    f"Page {item['page']} | "
                    f"Score: {item.get('score', 0):.4f}"
                ):

                    st.write(
                        "**Document:**",
                        item.get("document", "Unknown")
                    )

                    st.write(
                        "**Page:**",
                        item["page"]
                    )

                    st.write(
                        "**Similarity Score:**",
                        item.get("score", 0)
                    )

                    st.write(
                        "**Relevance:**",
                        item.get("relevance", "Unknown")
                    )

                    st.write(
                        "**Matching Terms:**",
                        ", ".join(
                            item.get("matching_terms", [])
                        ) or "None"
                    )

                    st.write("**Evidence Text:**")

                    st.write(item["text"])


        # ---------------- RETRIEVAL DIAGNOSTICS ----------------

        with st.expander("🧪 Retrieval Diagnostics"):

            st.write(
                "Question:",
                st.session_state["last_query"]
            )

            st.write(
                "Retrieved chunks:",
                len(evidence)
            )

            if evidence:

                for index, item in enumerate(evidence, start=1):

                    st.write(f"**Evidence {index}**")

                    st.write(
                        "Document:",
                        item.get("document", "Unknown")
                    )

                    st.write(
                        "Page:",
                        item["page"]
                    )

                    st.write(
                        "Similarity Score:",
                        item.get("score")
                    )

                    st.write(
                        "Text:",
                        item["text"][:300]
                    )

                    st.divider()


else:

    st.info(
        "👈 Upload your PDF documents from the sidebar "
        "and click Process Documents to get started."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "ProofLens | AI-powered, evidence-based document research"
)
