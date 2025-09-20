from __future__ import annotations

from datetime import datetime
from typing import List

import httpx
from sqlmodel import select

from ..db import session_scope
from ..models import (
    Blog,
    BlogCollaborator,
    BlogStatus,
    BlogVerification,
    InvitationStatus,
)
from ..schemas import BlogPayload, CollaboratorPayload
from ..settings import get_settings
from ..utils.tokens import generate_token


class BlogService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def list_blogs(self, user_id: int) -> List[BlogPayload]:
        with session_scope() as session:
            blogs = session.exec(
                select(Blog)
                .where(Blog.owner_user_id == user_id)
                .order_by(Blog.created_at.desc())
            ).all()
            payloads: List[BlogPayload] = []
            for blog in blogs:
                verification = session.exec(
                    select(BlogVerification).where(BlogVerification.blog_id == blog.id)
                ).first()
                payloads.append(
                    BlogPayload(
                        id=blog.id,
                        naver_blog_id=blog.naver_blog_id,
                        title=blog.title,
                        status=blog.status,
                        verified_at=blog.verified_at,
                        title_token=verification.title_token if verification else "",
                        body_token=verification.body_token if verification else "",
                    )
                )
            return payloads

    def create_blog(self, owner_user_id: int, naver_blog_id: str, title: str | None = None) -> BlogPayload:
        with session_scope() as session:
            blog = Blog(owner_user_id=owner_user_id, naver_blog_id=naver_blog_id, title=title)
            session.add(blog)
            session.flush()
            verification = BlogVerification(
                blog_id=blog.id,
                title_token=generate_token(),
                body_token=generate_token(),
            )
            session.add(verification)
            session.flush()
            return BlogPayload(
                id=blog.id,
                naver_blog_id=blog.naver_blog_id,
                title=blog.title,
                status=blog.status,
                verified_at=blog.verified_at,
                title_token=verification.title_token,
                body_token=verification.body_token,
            )

    def verify_blog(self, blog_id: int, user_id: int, post_url: str, title: str | None, body: str | None) -> tuple[str, str | None]:
        with session_scope() as session:
            blog = session.get(Blog, blog_id)
            if not blog:
                return "not_found", "블로그를 찾을 수 없습니다"
            if blog.owner_user_id != user_id:
                return "forbidden", "소유자만 인증할 수 있습니다"
            verification = session.exec(
                select(BlogVerification).where(BlogVerification.blog_id == blog_id)
            ).first()
            if not verification:
                return "not_found", "검증 토큰이 없습니다"

            fetched_title, fetched_body = title, body
            if (not fetched_title or not fetched_body) and self.settings.dev_allow_http_fetch:
                fetched_title, fetched_body = self._fetch_blog(post_url)
            if not fetched_title or not fetched_body:
                verification.failed_reason = "제목/본문을 확인할 수 없습니다"
                session.add(verification)
                return "failed", verification.failed_reason

            title_match = verification.title_token in fetched_title
            body_match = verification.body_token in fetched_body
            if title_match and body_match:
                blog.status = BlogStatus.VERIFIED
                blog.verified_at = datetime.utcnow()
                verification.post_url = post_url
                verification.verified_at = datetime.utcnow()
                verification.failed_reason = None
                session.add(blog)
                session.add(verification)
                return "verified", None
            else:
                verification.failed_reason = "토큰이 일치하지 않습니다"
                session.add(verification)
                return "failed", verification.failed_reason

    def disown_blog(self, blog_id: int, user_id: int) -> tuple[str, str | None]:
        with session_scope() as session:
            blog = session.get(Blog, blog_id)
            if not blog:
                return "not_found", "블로그를 찾을 수 없습니다"
            if blog.owner_user_id != user_id:
                return "forbidden", "소유자만 해제할 수 있습니다"
            blog.status = BlogStatus.DISOWNED
            blog.verified_at = None
            session.add(blog)
            collaborators = session.exec(select(BlogCollaborator).where(BlogCollaborator.blog_id == blog_id)).all()
            for collab in collaborators:
                collab.status = InvitationStatus.REVOKED
                collab.responded_at = datetime.utcnow()
                session.add(collab)
            return "disowned", None

    def invite_collaborator(self, blog_id: int, owner_id: int, email: str) -> CollaboratorPayload | tuple[str, str | None]:
        with session_scope() as session:
            blog = session.get(Blog, blog_id)
            if not blog:
                return "not_found", "블로그를 찾을 수 없습니다"
            if blog.owner_user_id != owner_id:
                return "forbidden", "소유자만 초대할 수 있습니다"
            collaborator = BlogCollaborator(
                blog_id=blog_id,
                invited_email=email,
                invited_by_user_id=owner_id,
            )
            session.add(collaborator)
            session.flush()
            return CollaboratorPayload(
                id=collaborator.id,
                email=collaborator.invited_email,
                status=collaborator.status,
                invited_at=collaborator.invited_at,
            )

    def revoke_collaborator(self, blog_id: int, owner_id: int, collab_id: int) -> tuple[str, str | None]:
        with session_scope() as session:
            blog = session.get(Blog, blog_id)
            if not blog or blog.owner_user_id != owner_id:
                return "forbidden", "권한이 없습니다"
            collaborator = session.get(BlogCollaborator, collab_id)
            if not collaborator:
                return "not_found", "협업자를 찾을 수 없습니다"
            collaborator.status = InvitationStatus.REVOKED
            collaborator.responded_at = datetime.utcnow()
            session.add(collaborator)
            return "revoked", None

    def list_collaborators(self, blog_id: int) -> List[CollaboratorPayload]:
        with session_scope() as session:
            collaborators = session.exec(select(BlogCollaborator).where(BlogCollaborator.blog_id == blog_id)).all()
            return [
                CollaboratorPayload(
                    id=collab.id,
                    email=collab.invited_email,
                    status=collab.status,
                    invited_at=collab.invited_at,
                )
                for collab in collaborators
            ]

    def _fetch_blog(self, url: str) -> tuple[str | None, str | None]:
        try:
            response = httpx.get(url, timeout=5)
            if response.status_code != 200:
                return None, None
            text = response.text
        except Exception:
            return None, None
        # naive parsing: try to extract title/body tokens
        start_title = text.find("<title>")
        end_title = text.find("</title>")
        title = text[start_title + 7 : end_title] if start_title != -1 and end_title != -1 else None
        body = text
        return title, body


__all__ = ["BlogService"]

