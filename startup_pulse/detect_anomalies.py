"""Net-change calculations; alerts are intentionally disabled by default."""

from sqlalchemy import select

from .db import AggregateSnapshot, init_db, session


def net_changes() -> list[dict[str, object]]:
    init_db()
    with next(session()) as db:
        rows = db.scalars(select(AggregateSnapshot).order_by(AggregateSnapshot.quarter)).all()
    grouped: dict[tuple[str, str], list[AggregateSnapshot]] = {}
    for row in rows:
        grouped.setdefault((row.dimension, row.name), []).append(row)
    result = []
    for (dimension, name), values in grouped.items():
        for previous, current in zip(values, values[1:]):
            result.append({"quarter": current.quarter, "dimension": dimension, "name": name,
                           "net_change": current.startup_count - previous.startup_count})
    return result


if __name__ == "__main__":
    print(net_changes())
