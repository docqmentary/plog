from __future__ import annotations

from ..providers.openai import OpenAIProvider


class OutlineService:
    def __init__(self) -> None:
        self.llm = OpenAIProvider()

    def create_outline(self, draft: str, keyword: str, volume: int | None, selected_refs: list[dict]) -> tuple[list[dict], list[dict]]:
        sections, evidence = self.llm.build_outline(draft, keyword, volume, selected_refs)
        outline_payload = [
            {"section_id": section.section_id, "title": section.title, "bullets": section.bullets}
            for section in sections
        ]
        evidence_payload = [
            {
                "section_id": item.section_id,
                "need": item.need,
                "queries": item.queries,
                "prefer": item.prefer,
            }
            for item in evidence
        ]
        return outline_payload, evidence_payload


__all__ = ["OutlineService"]
