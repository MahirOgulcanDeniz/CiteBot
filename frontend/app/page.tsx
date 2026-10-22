"use client";
import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Source = { file: string; page: number; snippet: string };
type Result = { answer: string; sources: Source[] };

export default function Home() {
  const [docId, setDocId] = useState<string | null>(null);
  const [fileName, setFileName] = useState("");
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API}/upload`, { method: "POST", body: form });
      if (!res.ok) throw new Error((await res.json()).detail ?? "Yükleme başarısız");
      const data = await res.json();
      setDocId(data.doc_id);
      setFileName(data.filename);
      setResult(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Bir hata oluştu");
    } finally {
      setLoading(false);
    }
  }

  async function handleAsk() {
    if (!question.trim() || !docId) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, doc_id: docId }),
      });
      if (!res.ok) throw new Error("Cevap alınamadı");
      setResult(await res.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Bir hata oluştu");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="max-w-2xl mx-auto p-8 space-y-6">
      <header>
        <h1 className="text-3xl font-bold">CiteBot</h1>
        <p className="text-gray-500">
          Belgeni yükle, sor; cevabı kaynağıyla birlikte al.
        </p>
      </header>

      <input type="file" accept=".pdf,.docx,.txt" onChange={handleUpload} />
      {fileName && <p className="text-sm text-gray-500">Yüklendi: {fileName}</p>}

      <div className="flex gap-2">
        <input
          className="flex-1 border rounded p-2"
          placeholder="Belgeyle ilgili bir soru sor..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAsk()}
        />
        <button
          className="bg-black text-white px-4 rounded disabled:opacity-50"
          onClick={handleAsk}
          disabled={loading || !docId}
        >
          {loading ? "..." : "Sor"}
        </button>
      </div>

      {error && <p className="text-red-600 text-sm">{error}</p>}

      {result && (
        <div className="space-y-4">
          <p className="whitespace-pre-wrap">{result.answer}</p>
          <div>
            <h2 className="font-semibold">Kaynaklar</h2>
            {result.sources.map((s, i) => (
              <div key={i} className="text-sm border-l-2 pl-3 my-2">
                <b>{s.file}</b> (sayfa {s.page})
                <p className="text-gray-500">{s.snippet}...</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </main>
  );
}