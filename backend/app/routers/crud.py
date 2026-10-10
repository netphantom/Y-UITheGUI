"""Router factory: standard list/get/create/update/delete endpoints for an owned model.

Resources with extra behaviour (e.g. songs) use ``include`` to keep only the generic
endpoints they need and add their own next to them.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.db import Base
from app.deps import repository
from app.repository import OwnedRepository

ALL_ACTIONS = frozenset({"list", "get", "create", "update", "delete"})


def crud_router(
    model: type[Base],
    *,
    prefix: str,
    read: type[BaseModel],
    create: type[BaseModel],
    update: type[BaseModel],
    include: frozenset[str] = ALL_ACTIONS,
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=[model.__name__])
    Repo = Annotated[OwnedRepository, Depends(repository(model))]

    # Annotations reference the schema classes passed in, so the OpenAPI docs stay typed.
    if "list" in include:

        @router.get("", response_model=list[read])
        def list_items(repo: Repo):
            return repo.list()

    if "get" in include:

        @router.get("/{item_id}", response_model=read)
        def get_item(item_id: int, repo: Repo):
            return repo.get(item_id)

    if "create" in include:

        @router.post("", response_model=read, status_code=status.HTTP_201_CREATED)
        def create_item(payload: create, repo: Repo):  # type: ignore[valid-type]
            return repo.create(**payload.model_dump())

    if "update" in include:

        @router.patch("/{item_id}", response_model=read)
        def update_item(item_id: int, payload: update, repo: Repo):  # type: ignore[valid-type]
            return repo.update(item_id, payload)

    if "delete" in include:

        @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
        def delete_item(item_id: int, repo: Repo) -> None:
            repo.delete(item_id)

    return router
