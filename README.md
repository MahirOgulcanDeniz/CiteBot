# CiteBot

CiteBot, yüklediğin PDF, Word veya TXT belgelerini vektör veritabanına kaydeder ve sorularını yalnızca bu belgelerin içeriğine dayanarak yanıtlar. Her cevapla birlikte dosya adı, sayfa numarası ve ilgili metin parçası gösterilir.

## Özellikler

- PDF, DOCX ve TXT desteği
- RAG mimarisi: parçalama, embedding, benzerlik araması
- Cevaplarda kaynak gösterme (dosya, sayfa, alıntı)
- Bağlamda olmayan sorularda "bu bilgi belgelerde yok" cevabı
- Değiştirilebilir model sağlayıcısı: **OpenAI** veya **Ollama** (yerel)

## Teknolojiler

Python, FastAPI, LangChain, ChromaDB, OpenAI API / Ollama, Next.js, React

## Kurulum

### Backend

cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # içine kendi API key'ini yaz
uvicorn main:app --reload

### Frontend


npx create-next-app@latest frontend   # ilk kurulumda
cd frontend
npm run dev


`app/page.tsx` dosyasını bu repodaki sürümle değiştir. Arayüz `http://localhost:3000`, API `http://localhost:8000` adresinde çalışır.

## Model sağlayıcısını seçme

`.env` dosyasında `LLM_PROVIDER` değerini değiştir:

| Değer | Gerekenler |
|---|---|
| `openai` | `OPENAI_API_KEY` |
| `ollama` | Ollama kurulu olmalı; `ollama pull qwen2.5:7b` ve `ollama pull bge-m3` |

Sağlayıcı değiştirirsen belgeleri yeniden yüklemen gerekir (her sağlayıcı kendi vektör klasörünü kullanır).

## Nasıl çalışır?

1. Yükleme: belge okunur, 1000 karakterlik parçalara bölünür, her parça için embedding üretilip ChromaDB'ye metadata ile kaydedilir.
2. Soru-cevap: soru embedding'e çevrilir, en benzer 5 parça getirilir, model yalnızca bu parçalara dayanarak cevap üretir ve kaynaklar döndürülür.

## Yol haritası

- [ ] Belge listesi ve silme
- [ ] Streaming cevaplar
- [ ] Konuşma geçmişi
- [ ] Kullanıcı girişi
- [ ] Docker ile paketleme