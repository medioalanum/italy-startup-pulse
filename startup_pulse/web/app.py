from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from ..db import AggregateSnapshot, init_db, session

app = FastAPI(title="Italy Startup Pulse")
templates = Jinja2Templates(directory="startup_pulse/web/templates")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
def dashboard(request: Request):
    with next(session()) as db:
        rows = db.scalars(
            select(AggregateSnapshot).order_by(AggregateSnapshot.quarter.desc())
        ).all()
    return templates.TemplateResponse(
        request=request, name="dashboard.html", context={"rows": rows, "sample": True}
    )


@app.get("/anomalies")
def anomalies(request: Request):
    return templates.TemplateResponse(
        request=request, name="anomalies.html", context={"sample": True}
    )
