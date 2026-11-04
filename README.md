# 🔍 ProofLens

### AI-Powered Research Assistant with Evidence-Backed Citations

ProofLens is an AI-powered research assistant that helps users explore and understand PDF documents. It uses semantic search and large language models to retrieve relevant passages, answer natural-language questions, and provide references to the original documents.

Instead of manually searching through lengthy documents, users can upload multiple PDFs, ask questions, and receive evidence-based responses.

---

## ✨ Features

- **Multi-PDF Upload:** Upload and process multiple PDF documents.
- **PDF Text Extraction:** Extract readable text while preserving page information.
- **Intelligent Chunking:** Split document content into smaller, searchable passages.
- **Semantic Search:** Retrieve relevant passages using Sentence Transformers.
- **AI-Powered Answers:** Generate natural-language answers using Google's Gemini API.
- **Cross-Document Analysis:** Compare information across multiple uploaded documents.
- **Source References:** Display relevant document names and page numbers.
- **Evidence Viewer:** Inspect retrieved passages and their similarity scores.
- **Document Overview:** Generate summaries of uploaded documents.
- **Uncertainty Handling:** Identify questions that cannot be answered using the available evidence.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web interface |
| PyPDF | PDF text extraction |
| Sentence Transformers | Semantic embeddings |
| all-MiniLM-L6-v2 | Text embedding model |
| Google Gemini API | AI-powered answer generation |
| NumPy / PyTorch | Supporting machine learning operations |

## 🏗️ Project Architecture

```text
              User
               |
               v
       Streamlit Interface
               |
               v
          PDF Upload
               |
               v
       PDF Text Extraction
               |
               v
         Text Chunking
               |
               v
       Semantic Retrieval
               |
               v
       Relevant Evidence
               |
               v
        Gemini API
               |
               v
       Generated Answer
               |
          +----+----+
          |         |
          v         v
      Citations  Evidence Viewer
```

## 📂 Project Structure

```text
prooflens/
│
├── src/
│   ├── __init__.py
│   ├── document_loader.py
│   ├── chunker.py
│   ├── retriever.py
│   └── answer_generator.py
│
├── app.py
├── .env
├── .gitignore
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/vansh-png-cpu/prooflens.git
cd prooflens
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install streamlit pypdf sentence-transformers python-dotenv google-genai pyyaml
```

### 5. Configure your Gemini API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

Replace the placeholder with your own Gemini API key.

**Important:** Never upload your `.env` file or expose your API key publicly.

### 6. Run ProofLens

```bash
python -m streamlit run app.py
```

The application will open in your browser.

## 🚀 How to Use

1. Launch the ProofLens application.
2. Upload one or more PDF documents.
3. Click **Process Documents**.
4. Generate a document overview if needed.
5. Enter a question in the question box.
6. Click **Find Answer**.
7. Explore the generated answer, source references, and retrieved evidence.

## 🧪 Testing and Validation

The application has undergone initial functional testing covering:

- Main topic identification
- Key requirements extraction
- Cross-document comparison
- Page identification
- Unsupported question handling
- Budget information extraction
- Technology stack comparison
- Contradiction detection

These tests demonstrate the core functionality of the prototype. They do not represent a formal accuracy benchmark.

## ⚠️ Current Limitations

- Scanned PDFs without readable text are not currently supported.
- Answer quality depends on document quality and retrieved evidence.
- AI-generated citations require further independent verification.
- The current application is a local Streamlit prototype.
- Large documents may require additional processing and performance optimisation.

## 🗺️ Future Roadmap

- [x] Project structure and modular code
- [x] PDF text extraction
- [x] Text chunking
- [x] Semantic retrieval
- [x] AI-powered question answering
- [x] Multi-document processing
- [x] Source reference display
- [x] Streamlit interface
- [x] Initial functional testing
- [ ] More reliable claim-level citation verification
- [ ] Support for scanned PDFs using OCR
- [ ] Formal retrieval and answer-quality evaluation
- [ ] Deployment and performance optimisation

## 👨‍💻 Author

**Vansh**

First-Year BTech Electronics and Computer Science Student

[GitHub Profile](https://github.com/vansh-png-cpu)

---

*ProofLens — Turning documents into searchable, evidence-backed knowledge.*
