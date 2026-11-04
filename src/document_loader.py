
from pypdf import PdfReader


def extract_text_from_pdf(pdf_file):
    """
    Extract text from every page of an uploaded PDF.
    Returns page-wise extracted text.
    """

    try:
        reader = PdfReader(pdf_file)

        if reader.is_encrypted:
            raise ValueError("This PDF is password-protected.")

        extracted_pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            extracted_pages.append({
                "page": page_number,
                "text": text.strip()
            })

        if not any(page["text"] for page in extracted_pages):
            raise ValueError(
                "No readable text found. This PDF may contain scanned images."
            )

        return extracted_pages

    except Exception as error:
        raise ValueError(
            f"Could not read PDF: {error}"
        ) from error
