"""FastAPI dependencies: the authenticated user and owner-scoped repositories."""

from collections.abc import Callable
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import Base, get_db, utcnow
from app.models import LoginSession, User
from app.repository import OwnedRepository
from app.security import hash_token

SESSION_COOKIE = "yui_session"

DbSession = Annotated[Session, Depends(get_db)]


def current_user(db: DbSession, yui_session: Annotated[str | None, Cookie()] = None) -> User:
    if yui_session:
        login = db.scalar(select(LoginSession).filter_by(token_hash=hash_token(yui_session)))
        if login and login.expires_at > utcnow():
            return login.user
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")


CurrentUser = Annotated[User, Depends(current_user)]


def admin_user(user: CurrentUser) -> User:
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin only")
    return user


def repository[ModelT: Base](model: type[ModelT]) -> Callable[..., OwnedRepository[ModelT]]:
    """Build a dependency that yields a repository scoped to the logged-in user."""

    def dependency(db: DbSession, user: CurrentUser) -> OwnedRepository[ModelT]:
        return OwnedRepository(model, db, user.id)

    return dependency
