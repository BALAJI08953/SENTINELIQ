import hashlib
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from bs4 import BeautifulSoup


def strip_html(text: str) -> str:
    return BeautifulSoup(text or "", "html.parser").get_text(" ")


def normalize_text(text: str, max_len: int = 20000) -> str:
    return re.sub(r"\s+", " ", strip_html(text)).strip()[:max_len]


def content_hash(title: str, body: str) -> str:
    key = f"{normalize_text(title).lower()}|{normalize_text(body).lower()}"
    return hashlib.sha256(key.encode()).hexdigest()


def normalize_url(url: str | None) -> str | None:
    if not url:
        return None
    parts = urlsplit(url.strip())
    query = urlencode(sorted(parse_qsl(parts.query, keep_blank_values=True)))
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path or "/", query, ""))
