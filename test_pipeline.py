
from src.document_loader import extract_text_from_pdf
from src.chunker import chunk_text
from src.retriever import retrieve_relevant_chunks
from src.answer_generator import generate_answer

pdf_path = r"C:\Users\Asus\Downloads\sample.pdf"

with open(pdf_path, "rb") as file:
    pages = extract_text_from_pdf(file)

chunks = chunk_text(pages)

print("PDF loaded successfully!")
print("Total pages:", len(pages))
print("Total chunks:", len(chunks))

query = input("\nAsk a question about your PDF: ")

results = retrieve_relevant_chunks(query, chunks)

response = generate_answer(query, results)

print("\nPROOFLENS ANSWER:")
print(response["answer"])

print("\nSOURCE PAGES:")
for page in response["sources"]:
    print("Page:", page)
