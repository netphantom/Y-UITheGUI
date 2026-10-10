"""Pydantic request/response schemas (the public API contract)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import PlanMode, SongStatus


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --- Auth ----------------------------------------------------------------------


class Credentials(BaseModel):
    username: str = Field(min_length=3, max_length=64, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=8, max_length=256)


class UserRead(ORMModel):
    id: int
    username: str
    is_admin: bool
    created_at: datetime


# --- Projects ------------------------------------------------------------------


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = ""


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None


class ProjectRead(ORMModel):
    id: int
    name: str
    description: str
    created_at: datetime


# --- Songs ---------------------------------------------------------------------


class SongCreate(BaseModel):
    title: str = Field(default="Untitled", max_length=120)
    style: str = Field(min_length=1, max_length=1000)
    lyrics: str = Field(default="", max_length=20_000)
    plan_mode: PlanMode = PlanMode.FULL
    seed: int | None = None
    cfg_scale: float | None = Field(default=None, gt=0, le=20)
    abc: str | None = Field(default=None, description="Edited ABC score (needs plan_mode full or melody)")
    project_id: int | None = None
    parent_id: int | None = None
    variants: int = Field(default=1, ge=1, description="Songs created per request, each with its own seed")


class SongUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    project_id: int | None = None
    is_favorite: bool | None = None


class SongRead(ORMModel):
    id: int
    title: str
    style: str
    lyrics: str
    plan_mode: PlanMode
    seed: int
    cfg_scale: float | None
    project_id: int | None
    parent_id: int | None
    status: SongStatus
    error: str | None
    has_audio: bool
    has_score: bool
    truncated: bool
    engine_version: str | None
    is_favorite: bool
    created_at: datetime
    finished_at: datetime | None


# --- System --------------------------------------------------------------------


class UpdateInfo(BaseModel):
    state: str
    installed_version: str | None = None
    latest_version: str | None = None
    message: str | None = None
    checked_at: datetime | None = None


class SystemStatus(BaseModel):
    engine: str
    engine_ready: bool
    engine_error: str | None
    model_id: str
    queue_length: int
    allow_registration: bool
    update: UpdateInfo
