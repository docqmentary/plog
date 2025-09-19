from __future__ import annotations

import secrets


def generate_token(length: int = 16) -> str:
    return secrets.token_urlsafe(length)[: length + 4]


__all__ = ["generate_token"]
