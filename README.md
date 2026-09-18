# Italy Startup Pulse

Pipeline and dashboard for the **aggregated** quarterly evolution of Italy's registry of innovative startups.

## Current data contract

The MIMIT/InfoCamere quarterly Cruscotto publishes aggregate totals by region and by economic sector in separate tables. It does not publish company-level rows in those reports, and no region×sector cross-tab was confirmed. Registry totals are supported; new entries are unavailable; net change is computed only as the difference between comparable consecutive totals.

The current implementation uses `SOURCE_MODE=sample` with a clearly labelled fixture. Live PDF ingestion accepts `SOURCE_PDF_PATH` and `SOURCE_QUARTER`, and stores the source path, checksum, and execution summary in an `ingestion_batches` table.

## Demo deployment

The Render blueprint is ready to deploy with `SOURCE_MODE=sample`. Set `DATABASE_URL` to the Neon pooled PostgreSQL connection string, deploy from the `main` branch, and verify `/health` returns `{"status":"ok"}`. Live PDF ingestion remains a manual/local operation until a persistent source-file strategy is selected.

## Setup

Requires Python 3.12+, uv, Docker, and Docker Compose. Start local PostgreSQL with `docker compose up -d postgres`, copy `.env.example` to `.env`, set `DATABASE_URL`, then run `uv sync`.

```bash
uv run python -m startup_pulse.ingest
uv run fastapi dev startup_pulse/web/app.py
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

The MVP uses SQLAlchemy `create_all`; migrations should be introduced if the schema grows. Snapshot replacement is used when a revised quarter is ingested. A free GitHub Actions workflow checks the official MIMIT reports page monthly and can also be started manually. It runs on a short-lived hosted runner and does not keep a worker, Render service, or database process running continuously. PDF ingestion remains explicit until a stable publication URL and revision policy are confirmed.

## Sources and limitations

Source: [MIMIT quarterly reports](https://www.mimit.gov.it/it/impresa/competitivita-e-nuove-imprese/start-up-innovative/relazione-annuale-e-rapporti-periodici). Reports are PDFs and contain aggregate tables. Public reuse must preserve attribution and source links; InfoCamere API access has separate terms.
