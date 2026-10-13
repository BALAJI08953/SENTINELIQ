"""Source providers. External text is untrusted: it is stored as data, never executed or obeyed."""
import urllib.robotparser
from dataclasses import dataclass
from datetime import UTC, datetime
from time import mktime
from typing import Protocol
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup

from app.models import Source

USER_AGENT = "SentinelIQ/0.1 (+competitive-intelligence; respects robots.txt)"
TIMEOUT = 10


@dataclass
class RawItem:
    title: str
    body: str
    url: str | None = None
    published_at: datetime | None = None


class ProviderError(Exception):
    pass


class SourceProvider(Protocol):
    def fetch(self, source: Source) -> list[RawItem]: ...


def _get(url: str) -> requests.Response:
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp
    except requests.RequestException as exc:
        raise ProviderError(f"fetch failed: {exc}") from exc


class RSSProvider:
    def fetch(self, source: Source) -> list[RawItem]:
        feed = feedparser.parse(_get(source.url).content)
        if feed.bozo and not feed.entries:
            raise ProviderError("feed could not be parsed")
        items = []
        for e in feed.entries:
            ts = e.get("published_parsed") or e.get("updated_parsed")
            published = datetime.fromtimestamp(mktime(ts), UTC) if ts else None
            items.append(RawItem(e.get("title", "(untitled)"), e.get("summary", ""), e.get("link"), published))
        return items


class HTMLProvider:
    """Single-page snapshot. Honors robots.txt. Change detection happens via content hash."""

    def allowed(self, url: str) -> bool:
        p = urlparse(url)
        rp = urllib.robotparser.RobotFileParser()
        try:
            robots = requests.get(f"{p.scheme}://{p.netloc}/robots.txt",
                                  headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        except requests.RequestException:
            return True  # no reachable robots.txt
        if robots.status_code >= 400:
            return True
        rp.parse(robots.text.splitlines())
        return rp.can_fetch(USER_AGENT, url)

    def fetch(self, source: Source) -> list[RawItem]:
        if not self.allowed(source.url):
            raise ProviderError("blocked by robots.txt")
        soup = BeautifulSoup(_get(source.url).text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        title = soup.title.get_text(strip=True) if soup.title else source.url
        return [RawItem(f"Page snapshot: {title}", soup.get_text(" "), source.url, datetime.now(UTC))]


class DemoProvider:
    """Demo sources hold no remote content; demo observations come from the seed script."""

    def fetch(self, source: Source) -> list[RawItem]:
        return []


def provider_for(source: Source) -> SourceProvider:
    return {"rss": RSSProvider, "html": HTMLProvider, "demo": DemoProvider}[source.kind]()
