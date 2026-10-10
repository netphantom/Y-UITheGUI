"""SQLite engine, session factory and the declarative base shared by all models."""

from collections.abc import Iterator
from datetime import UTC, datetime

from sqlalchemy import DateTime, TypeDecorator, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.config import get_settings


def utcnow() -> datetime:
    return datetime.now(UTC)


class UTCDateTime(TypeDecorator):
    """SQLite drops timezone info: store UTC, and hand back timezone-aware datetimes."""

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, _dialect) -> datetime | None:
        return value.astimezone(UTC).replace(tzinfo=None) if value else None

    def process_result_value(self, value: datetime | None, _dialect) -> datetime | None:
        return value.replace(tzinfo=UTC) if value else None


class Base(DeclarativeBase):
    """Every table gets an integer primary key and a creation timestamp."""

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)


engine = create_engine(get_settings().db_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


@event.listens_for(engine, "connect")
def _configure_sqlite(dbapi_connection, _record) -> None:
    # WAL lets the generation worker write while API requests read.
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def init_db() -> None:
    from app import models  # noqa: F401  (registers the tables)

    Base.metadata.create_all(engine)


def get_db() -> Iterator[Session]:
    with SessionLocal() as db:
        yield db
