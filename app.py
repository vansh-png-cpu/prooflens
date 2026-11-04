
import io
import hashlib
import streamlit as st

from src.document_loader import extract_text_from_pdf
from src.chunker import chunk_text
from src.retriever import retrieve_relevant_chunks
from src.answer_generator import (
    generate_answer,
    generate_document_overview
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

    div[data-testid="stMetric"] {
        background-color: #192231;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #29364a;
    }

    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "chunks" not in st.session_state:
    st.session_state["chunks"] = []

if "documents" not in st.session_state:
    st.session_state["documents"] = []

if "answer" not in st.session_state:
    st.session_state["answer"] = ""

if "sources" not in st.session_state:
    st.session_state["sources"] = []

if "evidence" not in st.session_state:
    st.session_state["evidence"] = []

if "last_query" not in st.session_state:
    st.session_state["last_query"] = ""

if "overview" not in st.session_state:
    st.session_state["overview"] = ""


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
# SIDEBAR - PDF UPLOAD
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
# DASHBOARD
# --------------------------------------------------

chunks = st.session_state["chunks"]
documents = st.session_state["documents"]

if chunks:

    st.markdown("## 📊 Document Dashboard")

    total_pages = sum(
        document["pages"]
        for document in documents
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

            st.write(
                f"**{document['name']}**"
            )

            st.caption(
                f"{document['pages']} pages | "
                f"{document['chunks']} chunks"
            )

    st.divider()


    # --------------------------------------------------
    # DOCUMENT OVERVIEW
    # --------------------------------------------------

    st.markdown("## 📝 Document Overview")

    if st.button(
        "Generate Document Overview",
        use_container_width=True
    ):

        try:

            with st.spinner(
                "Analysing all uploaded documents..."
            ):

                overview = generate_document_overview(chunks)

                st.session_state["overview"] = overview

        except Exception as error:

            st.error(
                f"Overview generation failed: {error}"
            )

    if st.session_state["overview"]:

        st.markdown(
            st.session_state["overview"]
        )

    st.divider()


    # --------------------------------------------------
    # QUESTION ANSWERING
    # --------------------------------------------------

    st.markdown("## 🔍 Ask Across All Documents")

    query = st.text_input(
        "Your question",
        placeholder="What are the common requirements across these documents?"
    )

    if st.button(
        "🔍 Find Answer",
        use_container_width=True
    ):

        if not query.strip():

            st.warning("Please enter a question.")

        else:

            try:

                with st.spinner(
                    "Searching across all documents..."
                ):

                    results = retrieve_relevant_chunks(
                        query,
                        chunks,
                        top_k=10
                    )

                    response = generate_answer(
                        query,
                        results
                    )

                st.session_state["answer"] = response["answer"]
                st.session_state["sources"] = response["sources"]
                st.session_state["evidence"] = results
                st.session_state["last_query"] = query

            except Exception as error:

                st.error(
                    f"Answer generation failed: {error}"
                )


    # --------------------------------------------------
    # ANSWER DISPLAY
    # --------------------------------------------------

    if st.session_state["answer"]:

        st.markdown("### 💡 ProofLens Answer")

        st.markdown(
            st.session_state["answer"]
        )

        st.divider()


        # --------------------------------------------------
        # SOURCE REFERENCES
        # --------------------------------------------------

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


        # --------------------------------------------------
        # EVIDENCE VIEWER
        # --------------------------------------------------

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


        # --------------------------------------------------
        # RETRIEVAL DIAGNOSTICS
        # --------------------------------------------------

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

                for index, item in enumerate(
                    evidence,
                    start=1
                ):

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
