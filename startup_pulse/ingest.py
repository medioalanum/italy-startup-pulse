import hashlib
import json
import os
from datetime import date
from pathlib import Path

from .db import AggregateSnapshot, init_db, session
from .models import AggregateRecord
from .pdf_source import extract_pdf_records

SAMPLE_PATH = Path(__file__).parents[1] / "sample_data" / "snapshot.json"


def load_records() -> list[dict[str, object]]:
    source_mode = os.getenv("SOURCE_MODE", "sample")
    if source_mode == "sample":
        return json.loads(SAMPLE_PATH.read_text())
    if source_mode != "live":
        raise ValueError("SOURCE_MODE must be either sample or live")
    try:
        pdf_path = Path(os.environ["SOURCE_PDF_PATH"])
        quarter = os.environ["SOURCE_QUARTER"]
    except KeyError as exc:
        raise ValueError(
            "SOURCE_PDF_PATH and SOURCE_QUARTER are required in live mode"
        ) from exc
    return [
        record.model_dump(mode="json")
        for record in extract_pdf_records(pdf_path, quarter)
    ]


def ingest() -> dict[str, int]:
    raw = load_records()
    checksum = hashlib.sha256(json.dumps(raw, sort_keys=True).encode()).hexdigest()
    accepted = rejected = duplicates = 0
    init_db()
    with next(session()) as db:
        for item in raw:
            try:
                record = AggregateRecord.model_validate(item)
            except Exception as exc:
                rejected += 1
                Path("quarantine").mkdir(exist_ok=True)
                with (
                    Path("quarantine")
                    .joinpath(f"{date.today().isoformat()}.log")
                    .open("a") as handle
                ):
                    handle.write(json.dumps({"raw": item, "error": str(exc)}) + "\n")
                continue
            exists = (
                db.query(AggregateSnapshot)
                .filter_by(
                    quarter=record.quarter, dimension=record.dimension, name=record.name
                )
                .first()
            )
            if exists:
                db.delete(exists)
                duplicates += 1
            db.add(
                AggregateSnapshot(
                    quarter=record.quarter,
                    dimension=record.dimension,
                    name=record.name,
                    startup_count=record.startup_count,
                    share_national=record.share_national,
                    source_reference_date=record.source_reference_date,
                    batch_checksum=checksum,
                )
            )
            accepted += 1
        db.commit()
    return {
        "read": len(raw),
        "accepted": accepted,
        "rejected": rejected,
        "revised": duplicates,
    }


if __name__ == "__main__":
    print(ingest())
