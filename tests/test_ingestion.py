"""Ingestion (M1): splitting, ordering, section metadata, idempotence."""

from lyr import Document, TextIngestor


def test_splits_on_blank_lines_and_orders():
    doc = Document(text="First para.\n\nSecond para.\n\nThird para.", origin="notes")
    records = TextIngestor().ingest(doc)
    assert [r.content for r in records] == ["First para.", "Second para.", "Third para."]
    assert [r.position for r in records] == [0, 1, 2]


def test_headings_become_section_metadata_not_records():
    text = "# Introduction\n\nWe begin here.\n\n## Details\n\nAnd continue."
    records = TextIngestor().ingest(Document(text=text, origin="doc"))
    assert [r.content for r in records] == ["We begin here.", "And continue."]
    assert records[0].metadata["section"] == "Introduction"
    assert records[1].metadata["section"] == "Details"


def test_kind_propagates_when_not_default():
    doc = Document(text="line one\n\nline two", origin="trace", kind="log")
    records = TextIngestor().ingest(doc)
    assert all(r.kind == "log" for r in records)


def test_reingestion_is_idempotent():
    doc = Document(text="Alpha.\n\nBeta.", origin="doc")
    first = TextIngestor().ingest(doc)
    second = TextIngestor().ingest(doc)
    assert [r.id for r in first] == [r.id for r in second]
