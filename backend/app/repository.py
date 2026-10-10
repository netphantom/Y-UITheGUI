"""Generic, owner-scoped data access.

One class serves every per-user table, so ownership checks live in exactly one place:
a user can never read or modify another user's rows, whatever the router does.
"""

from collections.abc import Sequence
from typing import Any

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import Base


class OwnedRepository[ModelT: Base]:
    def __init__(self, model: type[ModelT], db: Session, owner_id: int):
        self.model = model
        self.db = db
        self.owner_id = owner_id

    def list(self, **filters: Any) -> Sequence[ModelT]:
        """List the owner's rows, newest first. ``None`` filter values are ignored."""
        query = select(self.model).filter_by(owner_id=self.owner_id)
        active = {key: value for key, value in filters.items() if value is not None}
        query = query.filter_by(**active).order_by(self.model.id.desc())
        return self.db.scalars(query).all()

    def get(self, item_id: int) -> ModelT:
        item = self.db.get(self.model, item_id)
        if item is None or item.owner_id != self.owner_id:
            # 404 rather than 403: do not reveal that another user's id exists.
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"{self.model.__name__} not found")
        return item

    def create(self, **values: Any) -> ModelT:
        item = self.model(owner_id=self.owner_id, **values)
        self.db.add(item)
        self.db.commit()
        return item

    def update(self, item_id: int, patch: BaseModel) -> ModelT:
        item = self.get(item_id)
        for field, value in patch.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        self.db.commit()
        return item

    def delete(self, item_id: int) -> ModelT:
        item = self.get(item_id)
        self.db.delete(item)
        self.db.commit()
        return item
