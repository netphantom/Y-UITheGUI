"""ORM models: users, login sessions, projects and generated songs."""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, UTCDateTime


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)


class LoginSession(Base):
    __tablename__ = "login_sessions"

    # Only the SHA-256 of the cookie token is stored: a leaked DB does not leak sessions.
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime)

    user: Mapped[User] = relationship(lazy="joined")


class OwnedMixin:
    """Rows that belong to a single user. The generic repository scopes every query by owner."""

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)


class Project(OwnedMixin, Base):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")


class SongStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class PlanMode(StrEnum):
    """YuE2 symbolic planning ("cot"): full = melody + chords, melody = melody only, off = none."""

    FULL = "full"
    MELODY = "melody"
    OFF = "off"


class Song(OwnedMixin, Base):
    __tablename__ = "songs"

    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"), index=True
    )
    # The song this one was derived from (e.g. regenerated from an edited score).
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("songs.id", ondelete="SET NULL"))

    # --- Generation request --------------------------------------------------
    title: Mapped[str] = mapped_column(String(120))
    style: Mapped[str] = mapped_column(Text)
    lyrics: Mapped[str] = mapped_column(Text)
    plan_mode: Mapped[PlanMode] = mapped_column(String(16), default=PlanMode.FULL)
    seed: Mapped[int] = mapped_column(Integer)
    cfg_scale: Mapped[float | None]
    input_abc: Mapped[str | None] = mapped_column(Text)

    # --- Generation result ---------------------------------------------------
    status: Mapped[SongStatus] = mapped_column(String(16), default=SongStatus.QUEUED, index=True)
    error: Mapped[str | None] = mapped_column(Text)
    audio_file: Mapped[str | None] = mapped_column(String(255))
    score_abc: Mapped[str | None] = mapped_column(Text)
    truncated: Mapped[bool] = mapped_column(Boolean, default=False)
    engine_version: Mapped[str | None] = mapped_column(String(64))
    finished_at: Mapped[datetime | None] = mapped_column(UTCDateTime)

    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)

    @property
    def has_audio(self) -> bool:
        return self.audio_file is not None

    @property
    def has_score(self) -> bool:
        return bool(self.score_abc)
