from langchain_core.prompts import ChatPromptTemplate
from backend.ingest import vectorstore
from backend.providers import get_llm

llm = get_llm()

PROMPT = ChatPromptTemplate.from_template("""
Sen bir belge asistanısın. Soruyu SADECE aşağıdaki bağlama dayanarak cevapla.
Cevap bağlamda yoksa "Bu bilgi yüklenen belgelerde bulunmuyor." de.
Bağlamın dışından bilgi ekleme.

Bağlam:
{context}

Soru: {question}

Cevap:
""")


def answer(question: str, doc_id: str | None = None, k: int = 5):
    search_kwargs = {"k": k}
    if doc_id:
        search_kwargs["filter"] = {"doc_id": doc_id}
    retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
    docs = retriever.invoke(question)

    context = "\n\n".join(d.page_content for d in docs)
    response = (PROMPT | llm).invoke({"context": context, "question": question})

    sources = [
        {
            "file": d.metadata.get("source"),
            "page": d.metadata.get("page", 0) + 1,
            "snippet": d.page_content[:200],
        }
        for d in docs
    ]
    return {"answer": response.content, "sources": sources}