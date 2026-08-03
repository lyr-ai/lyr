"""Navigation (M3.2) — organize durable knowledge for exploration.

Knowledge *Organization*, distinct from Formation (M3/M3.1) and Explanation (M4).
``form_navigation`` is the Evidence-Connectivity Baseline: one generic, deterministic
function turning durable memories into a NavigationGraph from structural facts alone —
no domain argument, no domain-specific branch.
"""

from .form import form_navigation
from .graph import (
    SHARED_SEMANTIC,
    SHARED_SOURCE,
    NavConnection,
    NavGroup,
    NavigationGraph,
)

__all__ = [
    "form_navigation",
    "NavigationGraph",
    "NavGroup",
    "NavConnection",
    "SHARED_SEMANTIC",
    "SHARED_SOURCE",
]
