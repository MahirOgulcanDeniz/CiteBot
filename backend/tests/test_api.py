import uuid


def upload_txt(client, name="rapor.txt", text="Toplantı notları"):
    return client.post(
        "/upload", files={"file": (name, text.encode("utf-8"), "text/plain")}
    )


def test_upload_txt_succeeds(client):
    response = upload_txt(client)
    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "rapor.txt"
    assert body["chunks"] >= 1
    uuid.UUID(body["doc_id"])  # raises if it is not a valid UUID


def test_upload_saves_the_file_in_uploads_folder(client, app):
    doc_id = upload_txt(client).json()["doc_id"]
    saved = list((app.workdir / "uploads").glob(f"{doc_id}_*"))
    assert len(saved) == 1


def test_upload_rejects_unsupported_format(client):
    response = client.post(
        "/upload", files={"file": ("virus.exe", b"binary", "application/octet-stream")}
    )
    assert response.status_code == 400
    assert "Desteklenmeyen format" in response.json()["detail"]


def test_upload_requires_a_file(client):
    assert client.post("/upload").status_code == 422


def test_upload_does_not_write_outside_uploads_folder(client, app):
    response = upload_txt(client, name="../../evil.txt")
    assert response.status_code == 200
    assert not (app.workdir / "evil.txt").exists()
    assert not (app.workdir.parent / "evil.txt").exists()


def test_ask_returns_answer_and_sources(client, app):
    doc_id = upload_txt(client, "politika.txt", "Evden çalışma haftada 2 gündür.").json()[
        "doc_id"
    ]

    response = client.post(
        "/ask", json={"question": "Evden çalışma kaç gün?", "doc_id": doc_id}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == app.fake_answer
    assert body["sources"]
    assert body["sources"][0]["file"].endswith("politika.txt")


def test_ask_requires_a_question(client):
    assert client.post("/ask", json={}).status_code == 422


def test_ask_with_unknown_doc_id_returns_empty_sources(client):
    response = client.post("/ask", json={"question": "Merhaba?", "doc_id": "unknown"})
    assert response.status_code == 200
    assert response.json()["sources"] == []


def test_openapi_lists_the_public_routes(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert "/upload" in paths
    assert "/ask" in paths


def test_cors_allows_the_local_frontend(client):
    response = client.options(
        "/ask",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_cors_blocks_unknown_origins(client):
    response = client.options(
        "/ask",
        headers={
            "Origin": "http://evil.example.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert "access-control-allow-origin" not in response.headers