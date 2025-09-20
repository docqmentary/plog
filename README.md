# 플로그(내 병원 블로그 글 생성 어시스턴트) (MVP)

**무엇을 만드나?**  
PRD.md에 정의된 플로우: 초안 → 키워드(1개) → 레퍼런스 선택 → 아웃라인 → 논문 자동 발췌 & 본문 생성(내 톤 + 이미지 제안).

## 빠른 시작
1) `.env.sample`을 참고해 필요한 키를 `.env`에 작성하기(없으면 스텁으로 동작)
2) 의존성 설치: `pip install -e .[dev]`
3) 개발 서버 실행: `uvicorn app.main:app --reload`
4) `/api/examples.http`의 요청을 순서대로 호출해 데모 확인

## 환경변수
- `OPENAI_API_KEY` — Deep Research/Responses API
- `NAVER_SEARCHAD_ACCESS_KEY`, `NAVER_SEARCHAD_SECRET_KEY` — 네이버 검색광고(검색량) API
- `NAVER_SEARCH_CLIENT_ID`, `NAVER_SEARCH_CLIENT_SECRET` — 네이버 검색 API

## 문서
- 기능 요구: `PRD.md`
- 프롬프트: `/prompts`
- OpenAPI 스펙: `/api/openapi.yaml`
- 예시 호출: `/api/examples.http`
- 엔지니어링 부록: `/docs/engineering_appendix.md`
- UI 와이어프레임: `/docs/ui/wireframes.md`
- 수락 기준: `/tests/acceptance.md`

_Last updated: 2025-09-19_
