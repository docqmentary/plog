from __future__ import annotations

from ..providers.openai import OpenAIProvider, OutlineSection


class ComposeService:
    def __init__(self) -> None:
        self.llm = OpenAIProvider()

    def compose(self, draft: str, keyword: str, outline: list[dict]) -> dict:
        sections = [
            OutlineSection(section_id=item["section_id"], title=item["title"], bullets=item.get("bullets", []))
            for item in outline
        ]
        return self.llm.compose_with_research(draft, keyword, sections)


__all__ = ["ComposeService"]
