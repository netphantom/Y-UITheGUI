"""Songs: queue generations, browse the library, stream audio and download scores."""

import secrets
import shutil
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse, PlainTextResponse

from app.config import get_settings
from app.deps import CurrentUser, DbSession, repository
from app.models import PlanMode, Project, Song, SongStatus
from app.repository import OwnedRepository
from app.schemas import SongCreate, SongRead, SongUpdate

router = APIRouter(prefix="/songs", tags=["Song"])

Songs = Annotated[OwnedRepository[Song], Depends(repository(Song))]


def _check_project(db: DbSession, user: CurrentUser, project_id: int | None) -> None:
    """Reject references to projects the user does not own."""
    if project_id is not None:
        OwnedRepository(Project, db, user.id).get(project_id)


@router.get("", response_model=list[SongRead])
def list_songs(
    songs: Songs,
    project_id: int | None = None,
    is_favorite: bool | None = None,
    status: SongStatus | None = None,
):
    return songs.list(project_id=project_id, is_favorite=is_favorite, status=status)


@router.post("", response_model=list[SongRead], status_code=status.HTTP_201_CREATED)
def create_songs(payload: SongCreate, songs: Songs, db: DbSession, user: CurrentUser, request: Request):
    settings = get_settings()
    if payload.variants > settings.max_variants:
        raise HTTPException(422, f"At most {settings.max_variants} variants")
    if payload.abc and payload.plan_mode == PlanMode.OFF:
        raise HTTPException(422, "An ABC score needs plan mode 'full' or 'melody'")
    _check_project(db, user, payload.project_id)
    if payload.parent_id is not None:
        songs.get(payload.parent_id)

    base_seed = payload.seed if payload.seed is not None else secrets.randbelow(2**31)
    fields = payload.model_dump(exclude={"variants", "seed", "abc"})
    created = [
        songs.create(**fields, input_abc=payload.abc, seed=base_seed + offset)
        for offset in range(payload.variants)
    ]
    request.app.state.worker.notify()
    return created


@router.get("/{song_id}", response_model=SongRead)
def get_song(song_id: int, songs: Songs):
    return songs.get(song_id)


@router.patch("/{song_id}", response_model=SongRead)
def update_song(song_id: int, payload: SongUpdate, songs: Songs, db: DbSession, user: CurrentUser):
    _check_project(db, user, payload.project_id)
    return songs.update(song_id, payload)


@router.delete("/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_song(song_id: int, songs: Songs) -> None:
    if songs.get(song_id).status == SongStatus.RUNNING:
        raise HTTPException(status.HTTP_409_CONFLICT, "The song is being generated, try again when it is done")
    songs.delete(song_id)
    shutil.rmtree(get_settings().songs_dir / str(song_id), ignore_errors=True)


@router.get("/{song_id}/audio")
def song_audio(song_id: int, songs: Songs, download: bool = False):
    song = songs.get(song_id)
    if not song.audio_file:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Audio not available yet")
    path = get_settings().songs_dir / song.audio_file
    filename = f"{song.title}{path.suffix}" if download else None
    return FileResponse(path, filename=filename)


@router.get("/{song_id}/score", response_class=PlainTextResponse)
def song_score(song_id: int, songs: Songs):
    song = songs.get(song_id)
    if not song.score_abc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "This song has no score")
    return song.score_abc
