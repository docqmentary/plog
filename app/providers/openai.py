from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from ..settings import get_settings

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass
class OutlineSection:
    section_id: str
    title: str
    bullets: list[str]


@dataclass
class EvidenceRequest:
    section_id: str
    need: str
    queries: list[str]
    prefer: list[str]


class OpenAIProvider:
    """Deterministic stub that mimics LLM responses when API keys are absent."""

    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def is_stub(self) -> bool:
        return not bool(self.settings.openai_api_key)

    def keyword_candidates(self, draft: str) -> list[dict]:
        draft = draft.strip()
        if not draft:
            return []
        sample_path = DATA_DIR / "sample_candidates.json"
        if sample_path.exists():
            try:
                sample = json.loads(sample_path.read_text(encoding="utf-8"))
                if sample.get("candidates"):
                    return sample["candidates"]
            except json.JSONDecodeError:
                pass
        tokens = self._extract_keywords(draft, top_k=8)
        results: list[dict] = []
        for idx, token in enumerate(tokens, start=1):
            fit = round(min(0.95, 0.55 + (0.45 * (len(tokens) - idx) / max(len(tokens) - 1, 1))), 2)
            results.append(
                {
                    "keyword": token,
                    "fit": fit,
                    "why": f"초안의 핵심 주제와 '{token}' 키워드가 밀접하게 연결됩니다.",
                }
            )
        return results

    def build_outline(
        self,
        draft: str,
        keyword: str,
        volume: int | None,
        selected_refs: Iterable[dict],
    ) -> tuple[list[OutlineSection], list[EvidenceRequest]]:
        refs = list(selected_refs)
        sections = []
        evidence: list[EvidenceRequest] = []
        seed_titles = [
            "증상 이해와 원인",
            "생활 관리 전략",
            "전문의 치료 옵션",
            "환자 교육과 예방"
        ]
        for idx, title in enumerate(seed_titles, start=1):
            section_id = f"H2-{idx:02d}"
            ref_clauses = ", ".join(ref.get("title", "외부 참고") for ref in refs[:2]) if refs else "내부 가이드"
            sections.append(
                OutlineSection(
                    section_id=section_id,
                    title=f"{keyword} {title}",
                    bullets=[
                        f"최근 초안에서 강조한 핵심 포인트 정리 ({keyword})",
                        f"검색량 {volume or '정보 부족'} 기반 환자 관심도 설명",
                        f"참고 자료: {ref_clauses}",
                    ],
                )
            )
            evidence.append(
                EvidenceRequest(
                    section_id=section_id,
                    need=f"{keyword} 관련 {title} 근거",
                    queries=[f"{keyword} guideline", f"{keyword} clinical study"],
                    prefer=["Guideline", "Review"] if idx < 3 else ["Review", "RCT"],
                )
            )
        return sections, evidence

    def compose_with_research(
        self,
        draft: str,
        keyword: str,
        outline: Iterable[OutlineSection],
    ) -> dict:
        sections = list(outline)
        now_year = datetime.utcnow().year
        body_parts: list[str] = []
        image_suggestions: list[dict] = []
        references: list[dict] = []
        for section in sections:
            heading = f"## {section.title}"
            paragraphs = [
                f"{keyword} 환자들이 자주 묻는 질문을 기반으로 최신 근거를 요약했습니다.",
                "[대한피부과학회, {year}] 권고를 참고해 실제 진료 팁을 덧붙였습니다.".format(year=now_year - 1),
            ]
            body_parts.append("\n".join([heading, "", *paragraphs]))
            image_suggestions.append(
                {
                    "section": section.title,
                    "prompt": f"의료진 관점에서 {section.title}을 시각화한 교육용 인포그래픽",
                    "ratio": "4:3" if int(section.section_id.split("-")[-1]) % 2 else "16:9",
                    "style": "clean infographic",
                    "alt": f"{section.title} 설명을 돕는 이미지",
                }
            )
            references.append(
                {
                    "title": f"{keyword} 관리 가이드라인",
                    "url": "https://pubmed.ncbi.nlm.nih.gov/000000/",
                    "pmid": "000000",
                }
            )
        return {
            "titles": [f"{keyword} 진료실 가이드", f"{keyword} 환자를 위한 체크리스트"],
            "overview": f"{keyword} 환자 상담을 준비하는 의료진을 위한 요약입니다.",
            "body": "\n\n".join(body_parts),
            "checklist": ["초기 증상 확인", "생활습관 지도", "필요시 전문 치료 연계"],
            "faq": [
                f"{keyword} 환자가 가장 걱정하는 부분은?",
                f"{keyword} 관리에서 주의할 생활 습관은?",
            ],
            "image_suggestions": image_suggestions,
            "references": references,
        }

    def _extract_keywords(self, draft: str, top_k: int = 8) -> List[str]:
        text = re.sub(r"[^0-9A-Za-z가-힣\s]", " ", draft)
        tokens = [tok for tok in text.split() if len(tok) >= 2]
        if not tokens:
            return []
        scores = Counter(tokens)
        sorted_tokens = [token for token, _ in scores.most_common(top_k)]
        # ensure keyword uniqueness and keep ordering stable
        seen: set[str] = set()
        unique_tokens: list[str] = []
        for token in sorted_tokens:
            if token not in seen:
                unique_tokens.append(token)
                seen.add(token)
        return unique_tokens[:top_k]


__all__ = ["OpenAIProvider", "OutlineSection", "EvidenceRequest"]
