import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from ..db import AggregateSnapshot, init_db, session

templates = Jinja2Templates(directory="startup_pulse/web/templates")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Italy Startup Pulse", lifespan=lifespan)


def sample_mode() -> bool:
    return os.getenv("SOURCE_MODE", "sample") == "sample"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def dashboard(request: Request):
    with next(session()) as db:
        rows = db.scalars(
            select(AggregateSnapshot).order_by(AggregateSnapshot.quarter.desc())
        ).all()
    quarters = sorted({row.quarter for row in rows}, reverse=True)
    latest = quarters[0] if quarters else None
    previous = quarters[1] if len(quarters) > 1 else None
    latest_rows = [row for row in rows if row.quarter == latest]
    previous_values = {
        (row.dimension, row.name): row.startup_count
        for row in rows
        if row.quarter == previous
    }
    regional = [row for row in latest_rows if row.dimension == "region"]
    sectors = [row for row in latest_rows if row.dimension == "sector"]
    net_changes = {
        f"{row.dimension}:{row.name}": row.startup_count
        - previous_values.get((row.dimension, row.name), row.startup_count)
        for row in latest_rows
    }
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "rows": rows,
            "sample": sample_mode(),
            "latest": latest,
            "previous": previous,
            "regional": regional,
            "sectors": sectors,
            "net_changes": net_changes,
        },
    )


@app.get("/anomalies")
def anomalies(request: Request):
    return templates.TemplateResponse(
        request=request, name="anomalies.html", context={"sample": sample_mode()}
    )
