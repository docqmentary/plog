from __future__ import annotations

from typing import Iterable

from sqlmodel import select

from ..db import session_scope
from ..models import RefCardExternal, RefCardMyBlog
from ..providers.naver import NaverSearchProvider


class ReferenceService:
    def __init__(self) -> None:
        self.naver = NaverSearchProvider()

    def external_cards(self, keyword: str, urls: Iterable[str]) -> list[dict]:
        cards = self.naver.evaluate_external_refs(keyword, urls)
        with session_scope() as session:
            for card in cards:
                record = session.exec(select(RefCardExternal).where(RefCardExternal.url == card["url"])).first()
                if not record:
                    record = RefCardExternal(
                        keyword=keyword,
                        title=card["title"],
                        url=card["url"],
                        postdate=card.get("postdate"),
                        summary=card.get("summary"),
                        why=card.get("why"),
                        flags=",".join(card.get("flags", [])),
                    )
                    session.add(record)
                else:
                    record.title = card["title"]
                    record.summary = card.get("summary")
                    record.why = card.get("why")
                    record.flags = ",".join(card.get("flags", []))
                    session.add(record)
        return cards

    def my_blog_cards(self, limit: int = 3) -> list[dict]:
        with session_scope() as session:
            results = session.exec(
                select(RefCardMyBlog).order_by(RefCardMyBlog.updated_at.desc()).limit(limit)
            ).all()
            return [
                {
                    "post_id": card.post_id,
                    "url": card.url,
                    "title": card.title,
                    "summary": card.summary,
                    "postdate": card.postdate,
                }
                for card in results
            ]


__all__ = ["ReferenceService"]
