"""Generation worker: serial GPU queue persisted in the ``songs`` table.

The queue *is* the database (status = queued), so pending jobs survive restarts and no
broker is needed. One GPU runs one generation at a time, hence a single consumer.
"""

import asyncio
import logging

from sqlalchemy import func, select, update

from app.config import Settings
from app.db import SessionLocal, utcnow
from app.models import Song, SongStatus
from app.yue.engine import GenerationRequest, MusicEngine
from app.yue.updater import Updater

log = logging.getLogger(__name__)

IDLE_POLL_SECONDS = 5


class GenerationWorker:
    def __init__(self, settings: Settings, engine: MusicEngine, updater: Updater):
        self.settings = settings
        self.engine = engine
        self.updater = updater
        self.ready = False
        self.error: str | None = None
        self._wakeup = asyncio.Event()

    def notify(self) -> None:
        """Called by the API after queueing a song, so it starts without waiting for a poll."""
        self._wakeup.set()

    @staticmethod
    def queue_length() -> int:
        with SessionLocal() as db:
            pending = (SongStatus.QUEUED, SongStatus.RUNNING)
            return db.scalar(select(func.count()).where(Song.status.in_(pending))) or 0

    async def run(self) -> None:
        await self.updater.run()
        self._requeue_interrupted()
        try:
            await asyncio.to_thread(self.engine.load)
        except Exception as exc:  # missing GPU/driver, out of memory, broken install...
            log.exception("Engine failed to load: songs stay queued until a restart fixes it")
            self.error = f"{type(exc).__name__}: {exc}"
            return
        self.ready = True
        log.info("Engine %s %s ready", self.engine.name, self.engine.version)
        while True:
            song_id = self._claim_next()
            if song_id is None:
                await self._sleep_until_notified()
                continue
            await asyncio.to_thread(self._process, song_id)

    @staticmethod
    def _requeue_interrupted() -> None:
        """A song left 'running' means the process died mid-generation: try it again."""
        with SessionLocal() as db:
            db.execute(
                update(Song).where(Song.status == SongStatus.RUNNING).values(status=SongStatus.QUEUED)
            )
            db.commit()

    @staticmethod
    def _claim_next() -> int | None:
        with SessionLocal() as db:
            song = db.scalar(
                select(Song).where(Song.status == SongStatus.QUEUED).order_by(Song.id).limit(1)
            )
            if song is None:
                return None
            song.status = SongStatus.RUNNING
            db.commit()
            return song.id

    async def _sleep_until_notified(self) -> None:
        try:
            await asyncio.wait_for(self._wakeup.wait(), timeout=IDLE_POLL_SECONDS)
        except TimeoutError:
            pass
        self._wakeup.clear()

    def _process(self, song_id: int) -> None:
        with SessionLocal() as db:
            song = db.get(Song, song_id)
            if song is None:  # deleted while queued
                return
            request = GenerationRequest(
                style=song.style,
                lyrics=song.lyrics,
                cot=song.plan_mode,
                seed=song.seed,
                cfg_scale=song.cfg_scale,
                abc=song.input_abc,
            )
            out_dir = self.settings.songs_dir / str(song.id)
            try:
                result = self.engine.generate(request, out_dir)
                song.audio_file = str(result.audio_file.relative_to(self.settings.songs_dir))
                song.score_abc = result.score_abc
                song.truncated = result.truncated
                song.status = SongStatus.SUCCEEDED
            except Exception as exc:
                log.exception("Generation of song %s failed", song_id)
                song.status = SongStatus.FAILED
                song.error = str(exc)[:2000]
            song.engine_version = self.engine.version
            song.finished_at = utcnow()
            db.commit()
