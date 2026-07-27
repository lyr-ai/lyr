# Source passages — git commit history (excerpts)

Commit subjects/bodies the semantic records in `semantic_nodes.json` were drawn
from. Kept for provenance. Hashes are illustrative.

```
a1b2c3  Migrate public API from REST to gRPC
        Big one. All external endpoints now speak gRPC; REST gateway kept as a shim.

d4e5f6  Fix race condition in auth token refresh
091a2b  Fix auth session bug: tokens expiring early
7c8d9e  Harden auth middleware after third session-handling regression

111111  chore: bump version to 2.3.1
222222  chore: bump version to 2.3.2
333333  chore: bump version to 2.3.3

abc123  Add Redis cache in front of product catalog
def456  Revert "Add Redis cache in front of product catalog"
        Stale reads caused checkout to show wrong prices. Reverting.

merge482  Merge pull request #482: migrate public API from REST to gRPC
```
