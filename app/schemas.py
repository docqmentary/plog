from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl

from .models import BlogStatus, InvitationStatus


class Candidate(BaseModel):
    keyword: str
    fit: float
    why: Optional[str] = None


class CandidatesResponse(BaseModel):
    candidates: list[Candidate] = Field(default_factory=list)


class KeywordDraftRequest(BaseModel):
    draft: str


class KeywordVolumeRequest(BaseModel):
    keywords: list[str]


class Volume(BaseModel):
    month: str
    total: int = Field(ge=0)


class KeywordVolumeResponse(BaseModel):
    volumes: dict[str, Volume]


class CurveResponse(BaseModel):
    updated_at: datetime
    model_summary: dict
    predict: dict[str, int | str]


class ExternalReferencesRequest(BaseModel):
    keyword: str
    urls: list[HttpUrl]


class RefCardExternalPayload(BaseModel):
    title: str
    url: HttpUrl
    postdate: Optional[str] = None
    summary: Optional[str] = None
    why: Optional[str] = None
    flags: list[str] = Field(default_factory=list)


class ExternalReferencesResponse(BaseModel):
    cards: list[RefCardExternalPayload]


class RefCardMyBlogPayload(BaseModel):
    post_id: int
    url: HttpUrl
    title: Optional[str] = None
    summary: Optional[str] = None
    postdate: Optional[str] = None


class MyBlogReferencesResponse(BaseModel):
    cards: list[RefCardMyBlogPayload]


class OutlineSelectedRef(BaseModel):
    title: Optional[str] = None
    url: Optional[HttpUrl] = None
    summary: Optional[str] = None


class OutlineRequest(BaseModel):
    draft: str
    keyword: str
    volume: Volume
    selected_refs: list[OutlineSelectedRef] = Field(default_factory=list)


class OutlineItem(BaseModel):
    section_id: str
    title: str
    bullets: list[str]


class EvidenceRequestPayload(BaseModel):
    section_id: str
    need: str
    queries: list[str]
    prefer: list[str]


class OutlineResponse(BaseModel):
    outline: list[OutlineItem]
    evidence_requests: list[EvidenceRequestPayload]


class ComposeRequest(BaseModel):
    draft: str
    keyword: str
    volume: Volume
    outline: list[OutlineItem]
    style_profile: Optional[dict] = None


class ComposeResponse(BaseModel):
    titles: list[str]
    overview: str
    body: str
    checklist: list[str]
    faq: list[str]
    image_suggestions: list[dict]
    references: list[dict]


class GoogleCallbackRequest(BaseModel):
    id_token: Optional[str] = None
    dev_user: Optional[str] = Field(default=None, description="Shortcut for local development")


class SessionPayload(BaseModel):
    user_id: int
    email: str
    display_name: Optional[str] = None
    api_key: str


class BlogCreateRequest(BaseModel):
    naver_blog_id: str
    title: Optional[str] = None


class BlogPayload(BaseModel):
    id: int
    naver_blog_id: str
    title: Optional[str]
    status: BlogStatus
    verified_at: Optional[datetime]
    title_token: str
    body_token: str


class BlogVerifyRequest(BaseModel):
    post_url: HttpUrl
    title: Optional[str] = None
    body: Optional[str] = None


class StatusResponse(BaseModel):
    status: str
    reason: Optional[str] = None


class CollaboratorInviteRequest(BaseModel):
    email: str


class CollaboratorPayload(BaseModel):
    id: int
    email: Optional[str] = None
    status: InvitationStatus
    invited_at: datetime


class CollaboratorResponse(BaseModel):
    invitation: CollaboratorPayload


class CollaboratorsResponse(BaseModel):
    collaborators: list[CollaboratorPayload]


__all__ = [
    "Candidate",
    "CandidatesResponse",
    "KeywordDraftRequest",
    "KeywordVolumeRequest",
    "Volume",
    "KeywordVolumeResponse",
    "CurveResponse",
    "ExternalReferencesRequest",
    "ExternalReferencesResponse",
    "RefCardExternalPayload",
    "MyBlogReferencesResponse",
    "OutlineRequest",
    "OutlineResponse",
    "OutlineItem",
    "EvidenceRequestPayload",
    "ComposeRequest",
    "ComposeResponse",
    "GoogleCallbackRequest",
    "SessionPayload",
    "BlogCreateRequest",
    "BlogPayload",
    "BlogVerifyRequest",
    "StatusResponse",
    "CollaboratorInviteRequest",
    "CollaboratorResponse",
    "CollaboratorsResponse",
]
