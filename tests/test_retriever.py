from src.config import get_settings
from src.retriever import Retriever


def test_tfidf_finds_the_right_document():
    settings = get_settings()
    settings.retriever = "tfidf"
    r = Retriever(settings)
    hits = r.search("How much cash can I bring into the country?", top_k=2)
    assert hits[0]["doc_id"] == "currency_reporting"
    hits = r.search("How long is Global Entry valid?", top_k=2)
    assert hits[0]["doc_id"] == "global_entry"


def test_chunks_have_doc_ids_and_text():
    settings = get_settings()
    settings.retriever = "tfidf"
    r = Retriever(settings)
    hits = r.search("duty-free exemption", top_k=4)
    assert hits and all(h["doc_id"] and len(h["text"]) > 40 for h in hits)
