# Italy Startup Pulse

Pipeline and dashboard for the **aggregated** quarterly evolution of Italy's registry of innovative startups.

## Current data contract

The MIMIT/InfoCamere quarterly Cruscotto publishes aggregate totals by region and by economic sector in separate tables. It does not publish company-level rows in those reports, and no region×sector cross-tab was confirmed. Registry totals are supported; new entries are unavailable; net change is computed only as the difference between comparable consecutive totals.

The current implementation uses `SOURCE_MODE=sample` with a clearly labelled fixture. Live PDF ingestion is intentionally not enabled until the extraction and reuse conditions are verified.

## Setup

Requires Python 3.12+, uv, and PostgreSQL. Copy `.env.example` to `.env`, set `DATABASE_URL`, then run `uv sync`.

```bash
uv run python -m startup_pulse.ingest
uv run fastapi dev startup_pulse/web/app.py
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

The MVP uses SQLAlchemy `create_all`; migrations should be introduced if the schema grows. Snapshot replacement is used when a revised quarter is ingested. Phase 2 scheduling and Phase 3 JSON API remain roadmap items.

## Sources and limitations

Source: [MIMIT quarterly reports](https://www.mimit.gov.it/it/impresa/competitivita-e-nuove-imprese/start-up-innovative/relazione-annuale-e-rapporti-periodici). Reports are PDFs and contain aggregate tables. Public reuse must preserve attribution and source links; InfoCamere API access has separate terms.
