import hashlib
import json
import os
from datetime import date
from pathlib import Path

from .db import AggregateSnapshot, init_db, session
from .models import AggregateRecord

SAMPLE_PATH = Path(__file__).parents[1] / "sample_data" / "snapshot.json"


def load_records() -> list[dict[str, object]]:
    if os.getenv("SOURCE_MODE", "sample") != "sample":
        raise NotImplementedError("Live PDF ingestion is not enabled yet")
    return json.loads(SAMPLE_PATH.read_text())


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
