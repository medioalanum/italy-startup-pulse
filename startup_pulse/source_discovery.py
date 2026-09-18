"""Discover the newest quarterly MIMIT startup report."""

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import Request, urlopen

REPORTS_URL = (
    "https://www.mimit.gov.it/it/impresa/competitivita-e-nuove-imprese/"
    "start-up-innovative/relazione-annuale-e-rapporti-periodici"
)
QUARTER_RE = re.compile(r"(?P<quarter>[1-4])[_ ]trimestre[_ ](?P<year>20\d{2})", re.I)


@dataclass(frozen=True)
class SourceReport:
    url: str
    quarter: str


class _ReportLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._href:
            self.links.append((self._href, " ".join(self._text)))
            self._href = None


def discover_latest_report(html: str, base_url: str = REPORTS_URL) -> SourceReport:
    parser = _ReportLinkParser()
    parser.feed(html)
    candidates: list[SourceReport] = []
    for href, text in parser.links:
        if ".pdf" not in href.lower() or "fondo" in f"{href} {text}".lower():
            continue
        match = QUARTER_RE.search(f"{href} {text}")
        if match:
            candidates.append(
                SourceReport(
                    url=urljoin(base_url, href),
                    quarter=f"{match['year']}-Q{match['quarter']}",
                )
            )
    if not candidates:
        raise ValueError("No quarterly MIMIT startup report was found")
    return max(candidates, key=lambda item: item.quarter)


def fetch_latest_report() -> SourceReport:
    request = Request(REPORTS_URL, headers={"User-Agent": "ItalyStartupPulse/1.0"})
    with urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", "ignore")
    return discover_latest_report(html)
