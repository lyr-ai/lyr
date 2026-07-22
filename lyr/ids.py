"""Content-addressed identity.

LYR leans on content-addressing for two of its core principles:

- **Minimal change** — re-ingesting the same observation must produce the same
  ``SourceRecord`` id, so nothing downstream churns. A content id is a pure
  function of the bytes that define the thing.
- **Knowledge identity** — a piece of knowledge keeps a stable *identity* across
  revisions (Durable Memory #17 stays #17 as it goes v1 → v2 → v3). Identity is
  derived from *what the knowledge is about*, deliberately excluding the parts
  that change between versions (evidence, timestamps, attributes).

Ids are short hex digests with a human-readable prefix, so they stay greppable
in logs and traceable by eye: ``src_9f2a...``, ``sem_1c40...``, ``idn_be71...``.
"""

from __future__ import annotations

import hashlib

_SEP = "\x1f"  # unit separator — unambiguous join, never appears in real text


def content_id(prefix: str, *parts: object, length: int = 12) -> str:
    """A stable id derived from ``parts``.

    Same parts → same id, always. Different parts → different id (up to the
    birthday bound of a ``length``-nibble digest, which is astronomically small
    at the scales LYR operates on). ``prefix`` is cosmetic — it labels the kind
    of thing without affecting the hash.
    """
    joined = _SEP.join(str(p) for p in parts)
    digest = hashlib.sha256(joined.encode("utf-8")).hexdigest()[:length]
    return f"{prefix}_{digest}"


def normalize(text: str) -> str:
    """Fold a label to its identity form.

    Two mentions of "the Payments Service" and "Payments service" describe the
    same entity; identity must not fork on casing or surrounding whitespace.
    This is intentionally conservative — it does not stem or lemmatize, because
    over-normalizing would silently merge genuinely distinct things.
    """
    return " ".join(text.strip().casefold().split())
