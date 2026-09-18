"""Extraction helpers for the aggregate tables in MIMIT quarterly PDFs."""

import re
from datetime import date
from pathlib import Path

import pdfplumber

from .models import AggregateRecord

REGION_ROW = re.compile(
    r"^\d+\s+(.+?)\s+(\d+(?:\.\d{3})*)\s+(\d+,\d{2})\s+(\d+,\d{2})$"
)
SECTOR_TOTAL_ROW = re.compile(
    r"^(?:TOTALE|Totale complessivo)\s+(\d{1,3}(?:\.\d{3})*)\s+"
    r"(\d+,\d{2})\s+(\d+,\d{2})$"
)
SECTOR_INLINE_ROW = re.compile(
    r"^(.+?)\s+TOTALE\s+(\d+(?:\.\d{3})*)\s+(\d+,\d{2})\s+(\d+,\d{2})$"
)


def italian_number(value: str) -> int:
    return int(value.replace(".", ""))


def italian_percent(value: str) -> float:
    return float(value.replace(".", "").replace(",", "."))


def parse_region_table(text: str, quarter: str) -> list[AggregateRecord]:
    records: list[AggregateRecord] = []
    for line in text.splitlines():
        match = REGION_ROW.match(line.strip())
        if match:
            records.append(
                AggregateRecord(
                    quarter=quarter,
                    dimension="region",
                    name=match.group(1).strip(),
                    startup_count=italian_number(match.group(2)),
                    share_national=italian_percent(match.group(3)),
                )
            )
    return records


def parse_sector_table(text: str, quarter: str) -> list[AggregateRecord]:
    records: list[AggregateRecord] = []
    pending_name: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("Note:"):
            continue
        inline = SECTOR_INLINE_ROW.match(stripped)
        if inline:
            records.append(
                AggregateRecord(
                    quarter=quarter,
                    dimension="sector",
                    name=inline.group(1).strip(),
                    startup_count=italian_number(inline.group(2)),
                    share_national=italian_percent(inline.group(3)),
                    classification="ATECO",
                )
            )
            pending_name = None
            continue
        total = SECTOR_TOTAL_ROW.match(stripped)
        if total and pending_name:
            records.append(
                AggregateRecord(
                    quarter=quarter,
                    dimension="sector",
                    name=pending_name,
                    startup_count=italian_number(total.group(1)),
                    share_national=italian_percent(total.group(2)),
                    classification="ATECO",
                )
            )
            pending_name = None
            continue
        if stripped.startswith("Totale complessivo"):
            continue
        if not stripped.startswith(("C ", "K ", "N ")) and not re.search(
            r"\bTOTALE\s+\d", stripped
        ):
            pending_name = stripped
    return records


def extract_pdf_records(path: Path, quarter: str) -> list[AggregateRecord]:
    """Extract region and sector records from the known MIMIT report layout."""
    with pdfplumber.open(path) as pdf:
        pages = [(page.extract_text() or "") for page in pdf.pages]
    region_text = next(
        (
            page
            for page in pages
            if "Distribuzione e densità regionale" in page and "LOMBARDIA" in page
        ),
        "",
    )
    sector_text = next(
        (
            page
            for page in pages
            if "Distribuzione per settore economico" in page and "Agricoltura" in page
        ),
        "",
    )
    if not region_text or not sector_text:
        raise ValueError("MIMIT region or sector table was not found in the PDF")
    return parse_region_table(region_text, quarter) + parse_sector_table(
        sector_text, quarter
    )


def source_reference_date(path: Path) -> date | None:
    """Return the PDF modification date when the report does not expose one."""
    return date.fromtimestamp(path.stat().st_mtime) if path.exists() else None
