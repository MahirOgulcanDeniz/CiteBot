def test_answer_returns_llm_answer_and_sources(app, ingest_text, prompts):
    doc_id, filename = ingest_text("Deneme süresi 2 aydır.", "sozlesme.txt")

    result = app.rag.answer("Deneme süresi ne kadar?", doc_id=doc_id)

    assert result["answer"] == app.fake_answer
    assert len(result["sources"]) >= 1
    source = result["sources"][0]
    assert source["file"] == filename
    assert source["page"] == 1  # .txt files have no pages, so it defaults to 1
    assert "Deneme süresi" in source["snippet"]


def test_prompt_contains_document_text_question_and_grounding_rule(
    app, ingest_text, prompts
):
    marker = "ZEBRA-4711 kodlu madde"
    doc_id, _ = ingest_text(f"{marker} ödeme koşullarını belirler.")

    app.rag.answer("Ödeme koşulları nelerdir?", doc_id=doc_id)

    sent = prompts[-1]
    assert marker in sent                       # retrieved context reached the model
    assert "Ödeme koşulları nelerdir?" in sent  # the question reached the model
    assert "SADECE" in sent                     # the "answer only from context" rule


def test_search_is_limited_to_the_given_document(app, ingest_text, prompts):
    id_a, file_a = ingest_text("Alfa belgesi: kırmızı kelimesi geçer.", "alfa.txt")
    ingest_text("Beta belgesi: mavi kelimesi geçer.", "beta.txt")

    result = app.rag.answer("Hangi renk geçiyor?", doc_id=id_a)

    assert {s["file"] for s in result["sources"]} == {file_a}
    assert "mavi" not in prompts[-1]


def test_unknown_doc_id_returns_no_sources(app, prompts):
    result = app.rag.answer("Herhangi bir soru", doc_id="does-not-exist")
    assert result["sources"] == []


def test_snippets_are_at_most_200_characters(app, ingest_text):
    doc_id, _ = ingest_text("Uzun cümle. " * 300)
    result = app.rag.answer("soru", doc_id=doc_id)
    assert result["sources"]
    assert all(len(s["snippet"]) <= 200 for s in result["sources"])


def test_k_limits_the_number_of_sources(app, ingest_text):
    doc_id, _ = ingest_text("Lorem ipsum dolor sit amet. " * 200)
    result = app.rag.answer("soru", doc_id=doc_id, k=2)
    assert len(result["sources"]) == 2