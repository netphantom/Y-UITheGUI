"""Application entry point: wires routers, the database and the generation worker."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import init_db
from app.models import Project
from app.routers import auth, songs, system
from app.routers.crud import crud_router
from app.schemas import ProjectCreate, ProjectRead, ProjectUpdate
from app.yue.engine import build_engine
from app.yue.updater import Updater
from app.yue.worker import GenerationWorker

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    init_db()
    worker = GenerationWorker(settings, build_engine(settings), Updater(settings))
    app.state.worker = worker
    # Update + model loading run in the background: the API (login, library) is usable meanwhile.
    task = asyncio.create_task(worker.run())
    yield
    task.cancel()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Y-UI: YuE2 backend", lifespan=lifespan)
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    api = APIRouter(prefix="/api")
    api.include_router(auth.router)
    api.include_router(
        crud_router(Project, prefix="/projects", read=ProjectRead, create=ProjectCreate, update=ProjectUpdate)
    )
    api.include_router(songs.router)
    api.include_router(system.router)
    app.include_router(api)
    return app


app = create_app()
