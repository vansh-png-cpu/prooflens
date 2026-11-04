
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
3. Cite supporting evidence in the answer using document name and page.
4. Include ONLY pages that directly support the answer.
5. Do not include pages merely because they were retrieved.
6. If evidence is insufficient, clearly explain what is missing.
7. If documents disagree, explain the disagreement.
8. Distinguish facts from assumptions.
9. Use exact document names and page numbers from the evidence.
10. If no evidence supports the answer, return an empty sources list.

Return ONLY valid JSON in this exact structure:

{{
  "answer": "Your detailed answer with document and page citations.",
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

        # Validate AI-selected references against retrieved evidence.
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


def generate_document_overview(chunks):

    if not chunks:
        return "No readable document content found."

    batch_size = 8
    batch_summaries = []

    for start in range(0, len(chunks), batch_size):

        batch = chunks[start:start + batch_size]

        context_parts = []

        for chunk in batch:
            context_parts.append(
                f"""
Document: {chunk.get('document', 'Unknown document')}
Page: {chunk['page']}
{chunk['text']}
"""
            )

        context = "\n".join(context_parts)

        prompt = f"""
You are ProofLens, an evidence-based document analyst.

Summarize the supplied document excerpts.

RULES:
1. Use only the supplied content.
2. Identify important topics.
3. Mention important problem statements and requirements.
4. Do not invent information.
5. Keep the summary clear and concise.
6. Mention document names and relevant page numbers.
7. If multiple documents are present, distinguish their content.

DOCUMENT EXCERPTS:
{context}

SUMMARY:
"""

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        batch_summaries.append(
            response.text or "Summary unavailable."
        )

    final_prompt = f"""
You are ProofLens, an evidence-based research assistant.

Combine these partial summaries into one overview.

Include:
1. Main topics across the uploaded documents.
2. Important topics covered by each document.
3. Key requirements or findings.
4. Relevant document names and page references.
5. Common themes, if supported by the evidence.

Do not invent facts. Clearly distinguish between documents.

PARTIAL SUMMARIES:
{chr(10).join(batch_summaries)}

FINAL DOCUMENT OVERVIEW:
"""

    final_response = client.models.generate_content(
        model=MODEL_NAME,
        contents=final_prompt
    )

    return final_response.text or "Could not generate overview."
