# Handoff — 블로그 운영 어시스턴트 (MVP)

## 무엇을 만드나?
`PRD.md`에 정의된 기능: 이메일/비밀번호 가입 → 블로그 소유권 인증 → 지난 12개월 포스팅 GPT 분석 → 협업자 초대/관리 → 포스팅 작성 워크플로우.

## 빠른 시작
1. `.env`를 `.env.sample` 참고해 작성합니다.
2. 개발 서버를 실행합니다. (프레임워크/런타임은 자유이나 HTTP-only 쿠키 세션을 지원해야 합니다.)
3. `/api/examples.http`를 참고하여 API 시나리오를 순차적으로 호출해보세요.

## 필요한 환경 변수
- `OPENAI_API_KEY` — OpenAI Deep Think/Responses API
- `NAVER_SEARCHAD_ACCESS_KEY`, `NAVER_SEARCHAD_SECRET_KEY` — 네이버 검색광고(검색량)
- `NAVER_SEARCH_API_KEY` — 네이버 검색 API (서비스 URL 발급 이후 적용)

## 문서
- 기능 요구 사항: `PRD.md`
- 프롬프트 아카이브: `/prompts`
- OpenAPI 스펙: `/api/openapi.yaml`
- 예시 호출: `/api/examples.http`
- 엔지니어링 부록: `/docs/engineering_appendix.md`
- 수락 기준: `/tests/acceptance.md`

## 정리된 변경 사항
- `/data`의 샘플 파일 및 `docs/ui` 자산은 제거되었습니다. 필요한 초기 데이터는 별도 시드 스크립트로 관리하세요.
