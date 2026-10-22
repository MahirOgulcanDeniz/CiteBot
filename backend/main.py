import os, uuid, shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.ingest import ingest_file
from backend.rag import answer

app = FastAPI(title="CiteBot", description="Belgelerinle konuş, cevapları kaynaklarıyla birlikte al.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
ALLOWED = {".pdf", ".docx", ".txt"}


class Question(BaseModel):
    question: str
    doc_id: str | None = None


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED:
        raise HTTPException(400, f"Desteklenmeyen format: {ext}")
    doc_id = str(uuid.uuid4())
    path = os.path.join("uploads", f"{doc_id}_{os.path.basename(file.filename)}")
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    n = ingest_file(path, doc_id)
    return {"doc_id": doc_id, "filename": file.filename, "chunks": n}


@app.post("/ask")
async def ask(q: Question):
    return answer(q.question, q.doc_id)