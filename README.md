<p align="center">
  <img src="./docs/images/italy-startup-pulse-logo.png" width="720" alt="Italy Startup Pulse logo" />
</p>

<p align="center">
  <a href="https://github.com/medioalanum/italy-startup-pulse/actions/workflows/ci.yml"><img src="https://github.com/medioalanum/italy-startup-pulse/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/medioalanum/italy-startup-pulse/actions/workflows/monthly-source-check.yml"><img src="https://img.shields.io/badge/source_check-monthly-38b2ac?style=flat-square&logo=githubactions&logoColor=white" alt="Monthly source check"></a>
  <a href="https://italy-startup-pulse.onrender.com/"><img src="https://img.shields.io/badge/demo-live-38b2ac?style=flat-square" alt="Live demo"></a>
  <a href="https://www.mimit.gov.it/it/impresa/competitivita-e-nuove-imprese/start-up-innovative/relazione-annuale-e-rapporti-periodici"><img src="https://img.shields.io/badge/source-MIMIT-102a43?style=flat-square" alt="MIMIT source"></a>
</p>

# Italy Startup Pulse

An analytical data product for exploring quarterly trends in Italy's innovative startup registry.

**[Live demo](https://italy-startup-pulse.onrender.com/)** · [Health check](https://italy-startup-pulse.onrender.com/health)

## Why this exists

Public startup statistics are available, but the source reports are designed for publication rather than comparison. Italy Startup Pulse turns those quarterly reports into a small, readable dashboard for product, market, and ecosystem questions: where registered startups are concentrated, which sectors are largest, and how totals change between comparable snapshots.

## What it does

- Discovers the newest official MIMIT quarterly report.
- Extracts aggregate totals by region and economic sector.
- Stores each validated snapshot in PostgreSQL with source metadata and checksums.
- Presents the latest snapshot and period-over-period comparisons in a responsive dashboard.
- Runs a monthly source check on a short-lived GitHub Actions runner.

## Product decisions

- **Aggregate-first:** the product reports the dimensions the source actually publishes; it does not invent company-level or region×sector data.
- **Source traceability:** every ingestion records the source path, quarter, checksum, and execution summary.
- **Snapshot replacement:** a revised report for the same quarter replaces that quarter's rows so corrections do not create duplicates.
- **Small free-tier footprint:** monthly discovery runs in GitHub Actions rather than keeping a worker active.

## Data contract

The MIMIT/InfoCamere quarterly Cruscotto publishes aggregate totals by region and by economic sector in separate tables. It does not publish company-level rows in those reports, and no region×sector cross-tab was confirmed. Registry totals are supported; new entries are unavailable; net change is computed only as the difference between comparable consecutive totals.

The production demo uses `SOURCE_MODE=live` and reads the latest validated snapshot from Neon. The repository also keeps a labelled fixture for local development and CI. Live PDF ingestion accepts `SOURCE_PDF_PATH` and `SOURCE_QUARTER`, and stores the source path, checksum, and execution summary in an `ingestion_batches` table.

## Demo deployment

The Render demo runs with `SOURCE_MODE=live` and a Neon pooled PostgreSQL connection string. The public dashboard is available at the [live demo](https://italy-startup-pulse.onrender.com/); `/health` should return `{"status":"ok"}`. The monthly workflow discovers, validates, and ingests the newest report into Neon.

## Setup

Requires Python 3.12+, uv, Docker, and Docker Compose. Start local PostgreSQL with `docker compose up -d postgres`, copy `.env.example` to `.env`, set `DATABASE_URL`, then run `uv sync`.

```bash
uv run python -m startup_pulse.ingest
uv run fastapi dev startup_pulse/web/app.py
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

The MVP uses SQLAlchemy `create_all`; migrations should be introduced if the schema grows. The GitHub Actions workflow runs on the first day of each month at 09:17 UTC and can also be started manually. When the `DATABASE_URL` GitHub secret is configured, it ingests the validated snapshot into Neon on a short-lived hosted runner.

## Limitations

- MIMIT reports publish aggregate tables, not company-level rows or a region×sector cross-tab.
- New registrations are not available; net change is only the difference between comparable totals.
- The dashboard currently contains one official snapshot, so historical change becomes available when an earlier quarter is ingested.
- Source publication dates and PDF layouts can change.

## Roadmap

1. Add a second historical snapshot when the next comparable report is published.
2. Add a source freshness indicator and ingestion history to the dashboard.
3. Introduce database migrations and a small operational alert for failed monthly runs.

## Data sources

Source: [MIMIT quarterly reports](https://www.mimit.gov.it/it/impresa/competitivita-e-nuove-imprese/start-up-innovative/relazione-annuale-e-rapporti-periodici). Reports are PDFs and contain aggregate tables. Public reuse must preserve attribution and source links; InfoCamere API access has separate terms.
