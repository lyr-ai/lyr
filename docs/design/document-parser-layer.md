# Document Parser Layer

**Status:** introduced (harness-level), grounded in two real source types (novel, docs) + markdown.

## Why it exists

The 红楼梦 "segmentation bug" (an in-text `第四回中…` matched as a chapter heading) was not a regex
bug — it exposed that **segmentation is not "a splitter", it is a layer.** Every source *type* has
its own document structure:

| source | structure |
|---|---|
| novel | chapter headings (CHAPTER I / 第一回) + prose |
| paper | Abstract · Introduction · Method · Experiments · Appendix · References |
| markdown / repo docs | `#` … `######` headings |
| transcript / video | timestamps |
| podcast | speaker turns |
| forum | reply tree |

So the pipeline is:

```
Connector (gets bytes) → Document Parser (understands structure) → Sections
    → Passages (shared PassageIngestor) → Source Records → Semantic
```

**Semantic never learns whether the source was a book, a paper, or a forum** — it only sees
Section → Passage → Source Record. This mirrors the Identity Resolver evolution: a small bug forced
a new generic layer, not a special-case.

## The interface (`explorer/pipeline/parsers.py`)

```python
class DocumentParser(Protocol):
    name: str
    def parse(self, docs: list[tuple[str, str]], case_id: str) -> list[Section]: ...
```

Every parser returns the **same** `Section` shape. Implemented now, because each is grounded in a
real (or near-term) source type:

- **NovelParser** (`novel`) — chapter-heading detection, English or Chinese. The zh heading rule
  (line-start, `回/章` followed only by whitespace/EOL, short heading) is a **heading detector**,
  reusable for 三体 / War and Peace / Pride and Prejudice — that is the test of *parser improvement*
  vs *book hack*.
- **DocsParser** (`docs`) — one Section per document (report + model card + changelog + README).
- **MarkdownParser** (`markdown`) — split on `#`…`######` headings; pre-heading content is a
  `(preamble)` section.

Future parsers (paper/transcript/forum/podcast) slot in here when a real source arrives; nothing
downstream changes. **Not built speculatively** — no witness/test data yet.

## The one hard rule

The parser is chosen by the case manifest's **`parser`** field (falling back to `source_type`) —
**never by title.**

```json
{ "case_id": "…", "parser": "novel", "language": "zh" }   // ✓
if title == "红楼梦": …                                    // ✗ never
```

A parser must express a **capability** (heading detector, paragraph detector, dialogue detector),
not a document identity. If a change helps only one book, it is a hack; if it helps a *type*, it is
a parser improvement. That distinction is the whole point of this layer.
