import os
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from providers import PROVIDER, get_embeddings

# Embedding boyutlari saglayiciya gore farkli oldugu icin her saglayici
# kendi klasorunu kullanir; aksi halde veritabani bozulur.
vectorstore = Chroma(
    collection_name="documents",
    embedding_function=get_embeddings(),
    persist_directory=f"./chroma_db_{PROVIDER}",
)


def load_file(path: str):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return PyPDFLoader(path).load()
    if ext == ".docx":
        return Docx2txtLoader(path).load()
    if ext == ".txt":
        return TextLoader(path, encoding="utf-8").load()
    raise ValueError(f"Desteklenmeyen format: {ext}")


def ingest_file(path: str, doc_id: str):
    docs = load_file(path)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)
    for c in chunks:
        c.metadata["doc_id"] = doc_id
        c.metadata["source"] = os.path.basename(path)
    vectorstore.add_documents(chunks)
    return len(chunks)