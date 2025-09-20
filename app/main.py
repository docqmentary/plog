from __future__ import annotations

from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from sqlmodel import select

from .bootstrap import bootstrap_sample_data
from .db import init_db, session_scope
from .models import User
from .schemas import (
    BlogCreateRequest,
    BlogPayload,
    BlogVerifyRequest,
    CandidatesResponse,
    CollaboratorInviteRequest,
    CollaboratorResponse,
    CollaboratorsResponse,
    ComposeRequest,
    ComposeResponse,
    CurveResponse,
    ExternalReferencesRequest,
    ExternalReferencesResponse,
    GoogleCallbackRequest,
    KeywordDraftRequest,
    KeywordVolumeRequest,
    KeywordVolumeResponse,
    MyBlogReferencesResponse,
    OutlineRequest,
    OutlineResponse,
    SessionPayload,
    StatusResponse,
)
from .services.auth import AuthService
from .services.blogs import BlogService
from .services.compose import ComposeService
from .services.curve import CurveService
from .services.keywords import KeywordService
from .services.outline import OutlineService
from .services.references import ReferenceService

app = FastAPI(title="Plog API", version="0.1.0")

api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    bootstrap_sample_data()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_current_user(api_key: Optional[str] = Depends(api_key_scheme)) -> User:
    with session_scope() as session:
        user = session.exec(select(User).order_by(User.id.asc())).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="사용자를 찾을 수 없습니다")
        return user


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.post("/auth/google/callback", response_model=SessionPayload)
def google_callback(payload: GoogleCallbackRequest) -> SessionPayload:
    service = AuthService()
    user = service.resolve_user(payload.id_token, payload.dev_user)
    session_payload = service.issue_session(user)
    return SessionPayload(**session_payload)


@app.get("/blogs", response_model=list[BlogPayload])
def list_blogs(current_user: User = Depends(get_current_user)) -> list[BlogPayload]:
    service = BlogService()
    return service.list_blogs(current_user.id)


@app.post("/blogs", response_model=BlogPayload)
def create_blog(payload: BlogCreateRequest, current_user: User = Depends(get_current_user)) -> BlogPayload:
    service = BlogService()
    return service.create_blog(current_user.id, payload.naver_blog_id, payload.title)


@app.post("/blogs/{blog_id}/verify", response_model=StatusResponse)
def verify_blog(
    blog_id: int,
    payload: BlogVerifyRequest,
    current_user: User = Depends(get_current_user),
) -> StatusResponse:
    service = BlogService()
    status_value, reason = service.verify_blog(
        blog_id=blog_id,
        user_id=current_user.id,
        post_url=str(payload.post_url),
        title=payload.title,
        body=payload.body,
    )
    return StatusResponse(status=status_value, reason=reason)


@app.post("/blogs/{blog_id}/disown", response_model=StatusResponse)
def disown_blog(blog_id: int, current_user: User = Depends(get_current_user)) -> StatusResponse:
    service = BlogService()
    status_value, reason = service.disown_blog(blog_id, current_user.id)
    return StatusResponse(status=status_value, reason=reason)


@app.post("/blogs/{blog_id}/collaborators", response_model=CollaboratorResponse)
def invite_collaborator(
    blog_id: int,
    payload: CollaboratorInviteRequest,
    current_user: User = Depends(get_current_user),
) -> CollaboratorResponse:
    service = BlogService()
    result = service.invite_collaborator(blog_id, current_user.id, payload.email)
    if isinstance(result, tuple):
        status_value, reason = result
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=reason or status_value)
    return CollaboratorResponse(invitation=result)


@app.delete("/blogs/{blog_id}/collaborators/{collab_id}", response_model=StatusResponse)
def revoke_collaborator(
    blog_id: int,
    collab_id: int,
    current_user: User = Depends(get_current_user),
) -> StatusResponse:
    service = BlogService()
    status_value, reason = service.revoke_collaborator(blog_id, current_user.id, collab_id)
    if status_value == "forbidden":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=reason)
    return StatusResponse(status=status_value, reason=reason)


@app.get("/blogs/{blog_id}/collaborators", response_model=CollaboratorsResponse)
def list_collaborators(blog_id: int, current_user: User = Depends(get_current_user)) -> CollaboratorsResponse:
    service = BlogService()
    collaborators = service.list_collaborators(blog_id)
    return CollaboratorsResponse(collaborators=collaborators)


@app.post("/keywords/extract", response_model=CandidatesResponse)
def keywords_extract(payload: KeywordDraftRequest, current_user: User = Depends(get_current_user)) -> CandidatesResponse:
    service = KeywordService()
    candidates = service.extract_candidates(payload.draft)
    return CandidatesResponse(candidates=candidates)


@app.post("/keywords/volume", response_model=KeywordVolumeResponse)
def keywords_volume(payload: KeywordVolumeRequest, current_user: User = Depends(get_current_user)) -> KeywordVolumeResponse:
    service = KeywordService()
    volumes = service.volumes(payload.keywords)
    return KeywordVolumeResponse(volumes=volumes)


@app.get("/curve", response_model=CurveResponse)
def curve(
    refresh: bool = Query(default=False),
    keywords: Optional[str] = Query(default=None, description="Comma separated keyword list"),
    current_user: User = Depends(get_current_user),
) -> CurveResponse:
    service = CurveService()
    keywords_list = [kw.strip() for kw in keywords.split(",") if kw.strip()] if keywords else []
    model, params, predictions = service.refresh_and_predict(keywords_list, force_refresh=refresh)
    return CurveResponse(updated_at=model.updated_at, model_summary=params, predict=predictions)


@app.post("/references/external", response_model=ExternalReferencesResponse)
def references_external(
    payload: ExternalReferencesRequest,
    current_user: User = Depends(get_current_user),
) -> ExternalReferencesResponse:
    service = ReferenceService()
    cards = service.external_cards(payload.keyword, [str(url) for url in payload.urls])
    return ExternalReferencesResponse(cards=cards)


@app.get("/references/myblog", response_model=MyBlogReferencesResponse)
def references_myblog(current_user: User = Depends(get_current_user)) -> MyBlogReferencesResponse:
    service = ReferenceService()
    cards = service.my_blog_cards()
    return MyBlogReferencesResponse(cards=cards)


@app.post("/outline/plan", response_model=OutlineResponse)
def outline_plan(payload: OutlineRequest, current_user: User = Depends(get_current_user)) -> OutlineResponse:
    service = OutlineService()
    outline, evidence = service.create_outline(
        draft=payload.draft,
        keyword=payload.keyword,
        volume=payload.volume.total,
        selected_refs=[ref.model_dump(exclude_none=True) for ref in payload.selected_refs],
    )
    return OutlineResponse(outline=outline, evidence_requests=evidence)


@app.post("/compose_with_research", response_model=ComposeResponse)
def compose_with_research(payload: ComposeRequest, current_user: User = Depends(get_current_user)) -> ComposeResponse:
    service = ComposeService()
    result = service.compose(payload.draft, payload.keyword, [item.model_dump() for item in payload.outline])
    return ComposeResponse(**result)


__all__ = ["app"]
