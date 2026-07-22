"""Ingestion (M1): heterogeneous experiences → normalized Source Records."""

from .base import Document, Ingestor
from .text import TextIngestor

__all__ = ["Document", "Ingestor", "TextIngestor"]
