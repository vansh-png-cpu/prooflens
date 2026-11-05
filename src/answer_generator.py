
import os
import json
import re

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.5-flash-lite"

MIN_RELEVANCE_SCORE = 0.20


# --------------------------------------------------
# ANSWER GENERATION
# --------------------------------------------------

def generate_answer(query, retrieved_chunks):

    if not retrieved_chunks:
        return {
            "answer": "Insufficient evidence found in the uploaded documents.",
            "sources": []
        }

    relevant_chunks = [
        chunk for chunk in retrieved_chunks
        if chunk.get("score", 0) >= MIN_RELEVANCE_SCORE
    ]

    if not relevant_chunks:
        return {
            "answer": (
                "Insufficient evidence found in the uploaded documents. "
                "The retrieved passages do not strongly match your question."
            ),
            "sources": []
        }

    relevant_chunks.sort(
        key=lambda item: item.get("score", 0),
        reverse=True
    )

    context_parts = []

    for chunk in relevant_chunks:
        context_parts.append(
            f"""
Document: {chunk.get('document', 'Unknown document')}
Page: {chunk['page']}

Evidence:
{chunk['text']}
"""
        )

    context = "\n".join(context_parts)

    prompt = f"""
You are ProofLens, an evidence-based research assistant.

Answer the user's question using ONLY the supplied evidence.

STRICT RULES:
1. Never use outside knowledge.
2. Never invent facts.
3. Cite supporting evidence using document name and page.
4. Include ONLY pages that directly support the answer.
5. Do not include pages merely because they were retrieved.
6. If evidence is insufficient, explain what is missing.
7. If documents disagree, explain the disagreement.
8. Distinguish facts from assumptions.
9. Use exact document names and page numbers.
10. If no evidence supports the answer, return an empty sources list.

Return ONLY valid JSON:

{{
  "answer": "Your detailed answer with citations.",
  "sources": [
    {{
      "document": "exact document name",
      "page": 1
    }}
  ]
}}

DOCUMENT EVIDENCE:
{context}

USER QUESTION:
{query}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    raw_response = response.text or ""

    try:
        cleaned_response = raw_response.strip()

        cleaned_response = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            cleaned_response
        ).strip()

        result = json.loads(cleaned_response)

        answer_text = result.get(
            "answer",
            "No answer generated."
        )

        available_sources = {
            (
                chunk.get("document", "Unknown document"),
                int(chunk["page"])
            )
            for chunk in relevant_chunks
        }

        verified_sources = []

        for source in result.get("sources", []):

            document = source.get("document")
            page = source.get("page")

            try:
                page = int(page)
            except (TypeError, ValueError):
                continue

            source_pair = (document, page)

            if (
                source_pair in available_sources
                and source_pair not in verified_sources
            ):
                verified_sources.append(source_pair)

        return {
            "answer": answer_text,
            "sources": verified_sources
        }

    except (json.JSONDecodeError, AttributeError, TypeError):
        return {
            "answer": raw_response or "Could not generate an answer.",
            "sources": []
        }


# --------------------------------------------------
# DOCUMENT OVERVIEW
# --------------------------------------------------

def generate_document_overview(chunks):

    if not chunks:
        return "No readable document content found."

    documents = {}

    for chunk in chunks:

        name = chunk.get("document", "Unknown document")

        if name not in documents:
            documents[name] = []

        documents[name].append(chunk)

    summaries = []

    for document_name, document_chunks in documents.items():

        # Keep the overview concise by limiting context.
        selected_chunks = document_chunks[:12]

        context = "\n".join(
            f"Page {chunk['page']}: {chunk['text']}"
            for chunk in selected_chunks
        )

        prompt = f"""
You are ProofLens, an evidence-based document assistant.

Create a SHORT and easy-to-understand overview of this PDF.

Document name: {document_name}

Use ONLY the supplied content.

Format your response in Markdown:

### Document Purpose
Explain what this document is mainly about.

### Brief Summary
Summarise its content in 4-6 clear bullet points.

### Main Subjects
List the main subjects covered.

### Document Type
Identify the type of document if its content makes this clear.

RULES:
- Keep it concise and readable.
- Do not create a detailed research report.
- Do not invent facts.
- Mention the document name.
- Use only the provided content.
- Do not assume information missing from the excerpts.

DOCUMENT CONTENT:
{context}
"""

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        summaries.append(
            f"# {document_name}\n\n"
            f"{response.text or 'Overview unavailable.'}"
        )

    if len(summaries) == 1:
        return summaries[0]

    return "\n\n---\n\n".join(summaries)


# --------------------------------------------------
# DOCUMENT INTELLIGENCE REPORT
# --------------------------------------------------

def generate_document_intelligence_report(chunks):

    if not chunks:
        return "No readable document content found."

    documents = {}

    for chunk in chunks:

        document_name = chunk.get(
            "document",
            "Unknown document"
        )

        if document_name not in documents:
            documents[document_name] = []

        documents[document_name].append(chunk)

    document_reports = []

    for document_name, document_chunks in documents.items():

        batch_size = 8
        batch_summaries = []

        for start in range(0, len(document_chunks), batch_size):

            batch = document_chunks[start:start + batch_size]

            context = "\n".join(
                f"Page {chunk['page']}:\n{chunk['text']}"
                for chunk in batch
            )

            prompt = f"""
You are ProofLens, an expert evidence-based document analyst.

Analyse these excerpts from:
{document_name}

Use ONLY the supplied content.

Identify:
- Important findings
- Main topics
- Facts, figures and dates
- Requirements and recommendations
- Relevant page references

Do not invent information or page references.

DOCUMENT EXCERPTS:
{context}

ANALYSIS:
"""

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            batch_summaries.append(
                response.text or "Analysis unavailable."
            )

        combined_context = "\n\n".join(batch_summaries)

        final_document_prompt = f"""
You are ProofLens, an evidence-based research analyst.

Create a detailed research report for:

{document_name}

Use ONLY the supplied analysis.

Include these sections:

### 1. Executive Summary
### 2. Key Findings
### 3. Main Topics
### 4. Important Facts and Figures
### 5. Requirements and Recommendations
### 6. Important Page References

Rules:
- Do not invent facts.
- Do not invent page references.
- Distinguish facts from assumptions.
- Keep the report structured and readable.

DOCUMENT ANALYSIS:
{combined_context}

FINAL REPORT:
"""

        final_document_response = client.models.generate_content(
            model=MODEL_NAME,
            contents=final_document_prompt
        )

        document_reports.append(
            f"# {document_name}\n\n"
            f"{final_document_response.text or 'Report unavailable.'}"
        )

    if len(document_reports) == 1:
        return document_reports[0]

    combined_prompt = f"""
You are ProofLens, an evidence-based research analyst.

Create a combined intelligence report using ONLY the
individual document reports below.

Include:

## 1. Overall Executive Summary
## 2. Key Findings Across Documents
## 3. Common Themes
## 4. Differences Between Documents
## 5. Important Facts and Figures
## 6. Document-wise Summary
## 7. Important Page References

Rules:
- Do not invent facts or references.
- Do not treat unrelated topics as contradictions.
- Clearly distinguish individual documents.
- Mention exact document names.
- Keep the report structured.

INDIVIDUAL REPORTS:
{chr(10).join(document_reports)}

COMBINED INTELLIGENCE REPORT:
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=combined_prompt
    )

    return response.text or "Could not generate intelligence report."
