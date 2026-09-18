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


@app.get("/")
def dashboard(request: Request):
    with next(session()) as db:
        rows = db.scalars(
            select(AggregateSnapshot).order_by(AggregateSnapshot.quarter.desc())
        ).all()
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"rows": rows, "sample": sample_mode()},
    )


@app.get("/anomalies")
def anomalies(request: Request):
    return templates.TemplateResponse(
        request=request, name="anomalies.html", context={"sample": sample_mode()}
    )
