import pytest
from pydantic import ValidationError

from startup_pulse.models import AggregateRecord


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
