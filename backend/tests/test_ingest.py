import pytest


def test_load_file_reads_txt(app, make_txt):
    path = make_txt("a.txt", "Merhaba dünya")
    docs = app.ingest.load_file(str(path))
    assert len(docs) == 1
    assert docs[0].page_content == "Merhaba dünya"


def test_load_file_extension_is_case_insensitive(app, make_txt):
    path = make_txt("UPPER.TXT", "hello")
    docs = app.ingest.load_file(str(path))
    assert docs[0].page_content == "hello"


def test_load_file_rejects_unsupported_extension(app, tmp_path):
    path = tmp_path / "program.exe"
    path.write_bytes(b"binary")
    with pytest.raises(ValueError, match="Desteklenmeyen format"):
        app.ingest.load_file(str(path))


def test_short_text_becomes_a_single_chunk(app, make_txt):
    n = app.ingest.ingest_file(str(make_txt("short.txt", "Kısa bir metin.")), "doc-short")
    assert n == 1


def test_long_text_is_split_into_multiple_chunks(app, make_txt):
    text = "Lorem ipsum dolor sit amet. " * 200  # about 5600 characters
    n = app.ingest.ingest_file(str(make_txt("long.txt", text)), "doc-long")
    assert n > 1


def test_ingested_chunks_carry_doc_id_and_source_metadata(app, ingest_text):
    doc_id, filename = ingest_text("Yıllık izin süresi 14 gündür.", "izin.txt")
    results = app.ingest.vectorstore.similarity_search(
        "izin", k=5, filter={"doc_id": doc_id}
    )
    assert results
    assert all(r.metadata["doc_id"] == doc_id for r in results)
    assert all(r.metadata["source"] == filename for r in results)


def test_turkish_characters_survive_ingestion(app, ingest_text):
    text = "Çalışanlar yıllık izin hakkına sahiptir: ğüşöçı İ"
    doc_id, _ = ingest_text(text, "turkce.txt")
    results = app.ingest.vectorstore.similarity_search(
        "izin", k=1, filter={"doc_id": doc_id}
    )
    assert results[0].page_content == text