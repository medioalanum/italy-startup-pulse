import pytest
from pydantic import ValidationError

from startup_pulse.models import AggregateRecord


def test_database_url_normalizes_generic_postgresql_scheme(monkeypatch):
    from startup_pulse.db import database_url

    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    assert database_url() == "postgresql+psycopg://user:pass@localhost/db"


def test_valid_aggregate_record() -> None:
    record = AggregateRecord(
        quarter="2025-Q3",
        dimension="region",
        name="Lombardia",
        startup_count=10,
    )
    assert record.startup_count == 10


def test_invalid_count_is_rejected() -> None:
    with pytest.raises(ValidationError):
        AggregateRecord(
            quarter="2025-Q3", dimension="region", name="Lazio", startup_count=-1
        )
