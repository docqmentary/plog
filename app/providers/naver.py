from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Iterable

from ..settings import get_settings


class NaverSearchProvider:
    """Stub provider for Naver search volume and SERP evaluation."""

    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def is_stub(self) -> bool:
        return not bool(
            self.settings.naver_search_client_id
            and self.settings.naver_search_client_secret
        )

    def monthly_search_volume(self, keyword: str) -> dict:
        seed = int(hashlib.sha1(keyword.encode("utf-8")).hexdigest(), 16)
        base = 3000 + (seed % 7000)
        month = datetime.utcnow().strftime("%Y-%m")
        return {"month": month, "total": base}

    def evaluate_external_refs(self, keyword: str, urls: Iterable[str]) -> list[dict]:
        cards: list[dict] = []
        for idx, url in enumerate(urls):
            cards.append(
                {
                    "title": f"{keyword} 임상 인사이트 #{idx+1}",
                    "url": url,
                    "postdate": datetime.utcnow().strftime("%Y-%m-%d"),
                    "summary": f"{keyword} 관련 주요 정보를 요약한 참고 글입니다.",
                    "why": "광고성이 낮고 환자 반응이 좋은 구조",
                    "flags": ["verified"] if idx == 0 else [],
                }
            )
        return cards[:3]


__all__ = ["NaverSearchProvider"]
