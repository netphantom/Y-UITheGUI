"""Registration, login/logout (cookie sessions) and admin user management."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy import delete, func, select

from app.config import get_settings
from app.db import utcnow
from app.deps import SESSION_COOKIE, CurrentUser, DbSession, admin_user
from app.models import LoginSession, User
from app.schemas import Credentials, UserRead
from app.security import hash_password, hash_token, new_session_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def _start_session(db: DbSession, user: User, response: Response) -> None:
    settings = get_settings()
    ttl = timedelta(hours=settings.session_ttl_hours)
    token = new_session_token()
    db.add(LoginSession(token_hash=hash_token(token), user_id=user.id, expires_at=utcnow() + ttl))
    db.execute(delete(LoginSession).where(LoginSession.expires_at < utcnow()))  # housekeeping
    db.commit()
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=int(ttl.total_seconds()),
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(credentials: Credentials, db: DbSession, response: Response):
    is_first_user = db.scalar(select(func.count()).select_from(User)) == 0
    # The first account is always allowed: it becomes the admin of the instance.
    if not (is_first_user or get_settings().allow_registration):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Registration is disabled")
    if db.scalar(select(User).filter_by(username=credentials.username)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")
    user = User(
        username=credentials.username,
        password_hash=hash_password(credentials.password),
        is_admin=is_first_user,
    )
    db.add(user)
    db.commit()
    _start_session(db, user, response)
    return user


@router.post("/login", response_model=UserRead)
def login(credentials: Credentials, db: DbSession, response: Response):
    user = db.scalar(select(User).filter_by(username=credentials.username))
    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid username or password")
    _start_session(db, user, response)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(db: DbSession, response: Response, yui_session: Annotated[str | None, Cookie()] = None) -> None:
    if yui_session:
        db.execute(delete(LoginSession).where(LoginSession.token_hash == hash_token(yui_session)))
        db.commit()
    response.delete_cookie(SESSION_COOKIE)


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser):
    return user


@router.get("/users", response_model=list[UserRead], dependencies=[Depends(admin_user)])
def list_users(db: DbSession):
    return db.scalars(select(User).order_by(User.id)).all()


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: DbSession, admin: Annotated[User, Depends(admin_user)]) -> None:
    if user_id == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You cannot delete yourself")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    db.delete(user)
    db.commit()
