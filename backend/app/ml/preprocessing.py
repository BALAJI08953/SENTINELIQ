import re

from app.services.ingestion.normalize import normalize_text


def preprocess(text: str) -> str:
    """Lowercase, strip HTML, collapse whitespace; keep digits/currency tokens as plain text."""
    t = normalize_text(text or "").lower()
    return re.sub(r"[^a-z0-9$%\s]", " ", t).strip()
