from __future__ import annotations

from typing import Iterable

from sqlmodel import select

from ..db import session_scope
from ..models import KeywordVolume
from ..providers.openai import OpenAIProvider
from ..providers.naver import NaverSearchProvider


class KeywordService:
    def __init__(self) -> None:
        self.llm = OpenAIProvider()
        self.naver = NaverSearchProvider()

    def extract_candidates(self, draft: str) -> list[dict]:
        return self.llm.keyword_candidates(draft)

    def volumes(self, keywords: Iterable[str]) -> dict[str, dict]:
        response: dict[str, dict] = {}
        with session_scope() as session:
            for keyword in keywords:
                volume = self.naver.monthly_search_volume(keyword)
                record = session.exec(
                    select(KeywordVolume)
                    .where(KeywordVolume.keyword == keyword, KeywordVolume.month == volume["month"])
                    .limit(1)
                ).first()
                if not record:
                    record = KeywordVolume(keyword=keyword, month=volume["month"], volume_total=volume["total"])
                    session.add(record)
                    session.flush()
                response[keyword] = {"month": record.month, "total": record.volume_total}
        return response


__all__ = ["KeywordService"]
