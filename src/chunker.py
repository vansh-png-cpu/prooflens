
def chunk_text(pages, chunk_size=500, overlap=100):
    """
    Split extracted PDF text into overlapping chunks.
    Preserve page number and document name.
    """

    chunks = []

    for page in pages:
        text = page.get("text", "")
        page_number = page.get("page")

        if not text:
            continue

        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()

            if chunk:
                chunks.append({
                    "page": page_number,
                    "text": chunk,
                    "document": page.get("document", "Unknown document")
                })

            start += chunk_size - overlap

    return chunks
