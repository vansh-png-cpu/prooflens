
import hashlib
import re

from sentence_transformers import SentenceTransformer, util


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model = None
_cached_embeddings = None
_cached_chunks_hash = None


def get_model():
    global _model

    if _model is None:
        print("Loading semantic search model...")
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def find_matching_terms(query, text):
    """Find meaningful words shared by query and evidence."""

    query_words = set(
        re.findall(r"\b[a-zA-Z0-9]+\b", query.lower())
    )

    text_words = set(
        re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
    )

    ignored_words = {
        "what", "when", "where", "which", "who",
        "why", "how", "is", "are", "was", "were",
        "the", "a", "an", "of", "in", "on", "to",
        "for", "and", "or", "does", "do", "did",
        "this", "that", "with", "from"
    }

    return sorted(
        query_words.intersection(text_words) - ignored_words
    )


def retrieve_relevant_chunks(query, chunks, top_k=10):
    global _cached_embeddings, _cached_chunks_hash

    if not query.strip() or not chunks:
        return []

    model = get_model()

    # Generate a fingerprint of all chunk contents.
    chunk_content = "|".join(
        f"{chunk.get('document', 'Unknown')}:{chunk['page']}:{chunk['text']}"
        for chunk in chunks
    )

    current_hash = hashlib.sha256(
        chunk_content.encode("utf-8")
    ).hexdigest()

    # Reuse embeddings if the documents have not changed.
    if current_hash != _cached_chunks_hash:

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        _cached_embeddings = model.encode(
            texts,
            convert_to_tensor=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        _cached_chunks_hash = current_hash

    # Convert the user's question into an embedding.
    query_embedding = model.encode(
        query,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    similarities = util.cos_sim(
        query_embedding,
        _cached_embeddings
    )[0]

    scored_results = []

    for index, similarity in enumerate(similarities):

        score = float(similarity)
        chunk = chunks[index]

        matching_terms = find_matching_terms(
            query,
            chunk["text"]
        )

        if score >= 0.50:
            relevance = "High"
        elif score >= 0.30:
            relevance = "Medium"
        else:
            relevance = "Low"

        scored_results.append({
            "document": chunk.get("document", "Unknown document"),
            "page": chunk["page"],
            "text": chunk["text"],
            "score": round(score, 4),
            "relevance": relevance,
            "matching_terms": matching_terms
        })

    scored_results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return scored_results[:top_k]
