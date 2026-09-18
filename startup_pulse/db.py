import os
from collections.abc import Generator

from sqlalchemy import Date, Float, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


def database_url() -> str:
    value = os.getenv("DATABASE_URL")
    if not value:
        raise RuntimeError("DATABASE_URL is required; SQLite is not supported")
    return value


class Base(DeclarativeBase):
    pass


class AggregateSnapshot(Base):
    __tablename__ = "aggregate_snapshots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quarter: Mapped[str] = mapped_column(String(7), index=True)
    dimension: Mapped[str] = mapped_column(String(16), index=True)
    name: Mapped[str] = mapped_column(String(255))
    startup_count: Mapped[int] = mapped_column(Integer)
    share_national: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_reference_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    batch_checksum: Mapped[str] = mapped_column(String(64))


class Anomaly(Base):
    __tablename__ = "anomalies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quarter: Mapped[str] = mapped_column(String(7), index=True)
    dimension: Mapped[str] = mapped_column(String(16))
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32))
    percent_change: Mapped[float | None] = mapped_column(Float, nullable=True)


engine = None
SessionLocal = None


def init_db() -> None:
    global engine, SessionLocal
    engine = create_engine(database_url(), pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    Base.metadata.create_all(engine)


def session() -> Generator[Session, None, None]:
    if SessionLocal is None:
        init_db()
    assert SessionLocal is not None
    with SessionLocal() as db:
        yield db


def latest_quarter(db: Session) -> str | None:
    return db.scalar(select(AggregateSnapshot.quarter).order_by(AggregateSnapshot.quarter.desc()))
