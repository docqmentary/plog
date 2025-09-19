from __future__ import annotations

import secrets

from sqlmodel import select

from ..db import session_scope
from ..models import User


class AuthService:
    def resolve_user(self, id_token: str | None, dev_user: str | None = None) -> User:
        email = None
        google_sub = None
        display_name = None
        if dev_user:
            email = dev_user
            google_sub = f"dev-{dev_user}"
            display_name = dev_user.split("@")[0]
        elif id_token:
            # In production this would verify the token with Google; for MVP we fallback to deterministic parsing.
            email = f"user+{id_token[:6]}@example.com"
            google_sub = id_token[:12]
            display_name = "Google User"
        else:
            raise ValueError("id_token or dev_user must be provided")

        with session_scope() as session:
            user = session.exec(select(User).where(User.email == email)).first()
            if not user:
                user = User(google_sub=google_sub, email=email, display_name=display_name)
                session.add(user)
                session.flush()
            else:
                user.display_name = display_name or user.display_name
                user.touch()
                session.add(user)
        return user

    def issue_session(self, user: User) -> dict:
        api_key = secrets.token_urlsafe(16)
        return {
            "user_id": user.id,
            "email": user.email,
            "display_name": user.display_name,
            "api_key": api_key,
        }


__all__ = ["AuthService"]
