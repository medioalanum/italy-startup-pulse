from startup_pulse.ingest import load_records
from startup_pulse.models import AggregateRecord


def test_sample_fixture_contains_valid_aggregate_records(monkeypatch) -> None:
    monkeypatch.setenv("SOURCE_MODE", "sample")
    records = load_records()
    validated = [AggregateRecord.model_validate(item) for item in records]
    assert len(validated) == 4
    assert {record.dimension for record in validated} == {"region", "sector"}


def test_live_mode_is_explicitly_unavailable(monkeypatch) -> None:
    monkeypatch.setenv("SOURCE_MODE", "live")
    try:
        load_records()
    except ValueError as exc:
        assert "SOURCE_PDF_PATH" in str(exc)
    else:
        raise AssertionError("live mode must not silently use sample data")
