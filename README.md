# CiteBot

Chat with your documents and get answers with sources.

CiteBot lets you upload PDF, Word, or TXT files, stores them in a vector database, and answers your questions **using only the content of those documents**. Every answer comes with the file name, page number, and the exact text snippet it was based on.

> **Note:** the user interface and the assistant's prompt are written in Turkish. To localize the app, edit the UI strings in `frontend/app/page.tsx` and the prompt in `backend/rag.py`.

## Features

- PDF, DOCX, and TXT support
- Retrieval-Augmented Generation (RAG): chunking, embeddings, similarity search
- Source citations on every answer (file, page, snippet)
- Grounded answers: if the information is not in the document, CiteBot says so instead of guessing
- Switchable model provider: **OpenAI** or **Ollama** (fully local)

## Tech stack

Python, FastAPI, LangChain, ChromaDB, OpenAI API / Ollama, Next.js, React, Tailwind CSS

## How it works

1. **Ingestion:** the file is parsed, split into 1000-character chunks, embedded, and stored in ChromaDB together with metadata (file name, page number).
2. **Question answering:** the question is embedded, the 5 most similar chunks are retrieved, and the model answers using only those chunks. The retrieved sources are returned with the answer.

## Getting started

Requirements: Python 3.10+, Node.js 18+, and an OpenAI API key (or Ollama).

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate           # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your own API key. Then start the server:

```bash
python -m uvicorn main:app --reload
```

Interactive API docs: http://localhost:8000/docs

### 2. Frontend

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Choosing a model provider

Set `LLM_PROVIDER` in `backend/.env`:

| Value | Requirements |
|---|---|
| `openai` | `OPENAI_API_KEY` |
| `ollama` | Ollama installed, then `ollama pull qwen2.5:7b` and `ollama pull bge-m3` |

If you switch providers, re-upload your documents. Each provider uses its own vector store folder because embedding dimensions differ.

## API

| Endpoint | Description |
|---|---|
| `POST /upload` | Upload a PDF, DOCX, or TXT file. Returns a `doc_id`. |
| `POST /ask` | Ask a question: `{ "question": "...", "doc_id": "..." }`. Returns the answer and its sources. |

## Security

API keys live in `.env`, which is excluded from the repository via `.gitignore`. Never commit your own key.

## Roadmap

- [ ] Document list and deletion
- [ ] Streaming answers
- [ ] Conversation history
- [ ] User authentication
- [ ] OCR for scanned PDFs
- [ ] Docker setup