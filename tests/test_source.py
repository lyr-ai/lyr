"""Source layer (M1): immutability, content-addressing, serialization."""

import pytest

from lyr import SourceRecord


def test_content_addressed_id_is_stable():
    a = SourceRecord(content="hello world", origin="doc", position=1)
    b = SourceRecord(content="hello world", origin="doc", position=1)
    assert a.id == b.id  # same content+origin+position → same id


def test_different_position_changes_id():
    a = SourceRecord(content="hello", origin="doc", position=1)
    b = SourceRecord(content="hello", origin="doc", position=2)
    assert a.id != b.id


def test_record_is_immutable():
    r = SourceRecord(content="hello", origin="doc")
    with pytest.raises(Exception):
        r.content = "changed"  # frozen dataclass


def test_rejects_empty_content():
    with pytest.raises(ValueError):
        SourceRecord(content="   ", origin="doc")


def test_rejects_empty_origin():
    with pytest.raises(ValueError):
        SourceRecord(content="hello", origin="")


def test_roundtrip_serialization():
    r = SourceRecord(content="hello", origin="doc", position=3, kind="log")
    restored = SourceRecord.from_dict(r.to_dict())
    assert restored.id == r.id
    assert restored.content == r.content
    assert restored.kind == "log"
    assert restored.created_at == r.created_at
