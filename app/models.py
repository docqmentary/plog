from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class TimestampedModel(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()


class User(TimestampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    google_sub: str = Field(index=True, unique=True)
    email: str = Field(index=True)
    display_name: Optional[str] = None


class BlogStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    DISOWNED = "disowned"


class Blog(TimestampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_user_id: int = Field(foreign_key="user.id")
    naver_blog_id: str
    title: Optional[str] = None
    status: BlogStatus = Field(default=BlogStatus.PENDING)
    verified_at: Optional[datetime] = None


class BlogVerification(TimestampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    blog_id: int = Field(foreign_key="blog.id")
    title_token: str
    body_token: str
    post_url: Optional[str] = None
    verified_at: Optional[datetime] = None
    failed_reason: Optional[str] = None


class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REVOKED = "revoked"


class BlogCollaborator(TimestampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    blog_id: int = Field(foreign_key="blog.id")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    invited_email: Optional[str] = None
    invited_by_user_id: int = Field(foreign_key="user.id")
    status: InvitationStatus = Field(default=InvitationStatus.PENDING)
    invited_at: datetime = Field(default_factory=datetime.utcnow)
    responded_at: Optional[datetime] = None


class Post(TimestampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    blog_id: Optional[int] = Field(default=None, foreign_key="blog.id")
    url: str
    main_keyword: Optional[str] = Field(default=None, index=True)
    published_at: Optional[datetime] = None
    expected_rank_at_publish: Optional[int] = None


class RankHistory(TimestampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="post.id")
    keyword: str
    rank: int = Field(description="1..1001 with 1001 meaning 1000+")
    measured_at: datetime = Field(default_factory=datetime.utcnow)
    mode: str = Field(default="sim")


class CurveModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    params_json: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class KeywordVolume(TimestampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    keyword: str = Field(index=True)
    month: str
    volume_total: int


class RefCardExternal(TimestampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    keyword: str = Field(index=True)
    title: str
    url: str
    postdate: Optional[str] = None
    summary: Optional[str] = None
    why: Optional[str] = None
    flags: Optional[str] = None


class RefCardMyBlog(TimestampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="post.id")
    url: str
    title: Optional[str] = None
    summary: Optional[str] = None
    postdate: Optional[str] = None

