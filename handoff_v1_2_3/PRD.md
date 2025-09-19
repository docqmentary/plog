# PRD (vNext) — 블로그 운영 어시스턴트 MVP

## 1. 목표
의료인을 위한 다중 블로그 운영 도구를 제공한다. 핵심은 **소유권을 증명한 블로그에 협업자를 초대하고, GPT 분석으로 빠르게 포스팅을 작성**할 수 있도록 하는 것이다.

## 2. KPI
- 최초 가입~블로그 소유권 인증 완료까지 평균 1일 이내.
- 협업 초대 수락률 60% 이상.
- 지난 12개월 포스팅 분석 완료 소요 시간 30분 이내(블로그 1개 기준).

## 3. 핵심 사용자 플로우
1. **회원 가입 / 로그인**
   - 이메일+비밀번호 가입, 쿠키 기반 세션 유지.
   - 로그인 성공 시 대시보드로 이동.
2. **대시보드**
   - 인증된 블로그 목록, 초대 현황, 최근 포스팅 요약을 카드 형태로 보여준다.
   - 미완료 온보딩(소유권 인증, 12개월 분석) CTA를 강조한다.
3. **블로그 추가 & 소유권 인증**
   - 블로그 URL 입력 → 서버가 랜덤 문자열 두 개(title_code, body_code) 발급.
   - 사용자는 제목=title_code, 본문=body_code인 게시글을 발행한 뒤 "소유권 인증" 버튼을 클릭.
   - 서버는 사용자가 입력한 게시글 URL을 **직접 HTTP GET** 후 문자열 포함 여부 확인.
   - 성공 시 블로그가 사용자 계정에 소유자로 등록. 실패 시 에러 안내(재시도 가능). RSS Fallback 없음.
4. **온보딩 분석(소유자 전용)**
   - 소유권 인증 직후 지난 12개월 포스팅 URL을 수집하여 OpenAI Deep Think 모드로 메인 키워드를 추출.
   - 추출 결과는 포스팅 메타데이터로 저장되며 대시보드/작성 플로우에서 활용.
5. **협업자 관리**
   - 소유자는 이메일로 협업자 초대를 생성, 전송, 재전송, **취소**할 수 있다.
   - 초대 수신자는 링크를 통해 가입/로그인 후 수락.
   - 소유자는 언제든 협업자를 제거(disown)할 수 있다.
6. **포스팅 작성**
   - "새 글 작성" 클릭 시 사용자가 소유/협업 권한이 있는 블로그 중 하나를 선택(1개만 있으면 자동 선택).
   - 초안 입력 → GPT 기반 키워드/아웃라인/본문 생성 흐름(추후 상세화)으로 이어진다.

## 4. 기능 명세
### 4.1 인증/보안
- 이메일 가입: 비밀번호 최소 10자, 대문자/소문자/숫자 중 2종 이상 포함.
- 비밀번호는 Argon2id 해시 + 고유 salt 저장.
- 세션: HTTP-only, Secure 쿠키에 서명된 세션 토큰 저장(만료 14일, 활동 시 연장).
- 로그인 실패 5회 시 15분 잠금. 비밀번호 재설정 링크(이메일 기반) 제공.
- 이메일 인증은 MVP 범위 밖(필요 시 차기 버전 고려).

### 4.2 사용자/권한 모델
- **Owner**: 블로그 추가/삭제, 소유권 재검증, 협업자 초대·취소, 협업자 제거.
- **Collaborator**: 포스팅 작성/수정, 데이터 열람(블로그 소유자가 허용한 범위).
- 사용자는 여러 블로그에서 다양한 역할을 가질 수 있다.

### 4.3 블로그 소유권 인증
- 랜덤 문자열은 16자 base62.
- 사용자가 제출한 포스트 URL을 서버가 3회까지 재시도하며 HTTP GET.
- HTML 파싱 후 `<title>`과 `<body>` 텍스트에서 각각 문자열 검증.
- HTTPS 강제, 리다이렉트 허용(최대 3회).
- 인증 성공 시 타임스탬프와 검증 스냅샷(응답 헤더+본문 일부) 감사 로그에 저장.

### 4.4 협업자 초대
- 발신자: `no-reply@placeholder.local` (MVP용). 추후 사용자 소유 도메인으로 변경 가능.
- 초대 토큰은 72시간 유효, 만료 전 취소 시 즉시 무효화.
- 초대 수락 시 해당 사용자가 자동으로 Collaborator 권한 부여.

### 4.5 온보딩 Deep Think 분석
- 소유자가 인증 완료한 각 블로그에 대해 최근 12개월 포스트 URL을 입력 받거나 RSS/사이트맵에서 자동 수집.
- 수집된 URL은 OpenAI Deep Think 모드에 전달하여 메인 키워드를 추출.
- 예산 제한 없음. 실패 시 재시도 큐에 넣고 사용자에게 상태 표시.

### 4.6 외부 API 연동
- **네이버 검색광고 API**: 이미 발급된 키로 검색량 조회.
- **네이버 검색 API**: 서비스 URL 준비 후 발급 예정. 로컬/스테이징에선 목업 또는 대체 SERP 제공자 사용.
- 개발 단계에서는 실제 키를 환경 변수로 주입하고, 배포 후 프로덕션 모드 전환.
- OpenAI Responses/Deep Think API 사용. 호출 한도 미지정.

## 5. 데이터/저장
- `users`: email, password_hash, role flags, last_login, lock info.
- `sessions`: session_id, user_id, expires_at, metadata.
- `blogs`: id, owner_id, url, title, verified_at, verification_snapshot.
- `blog_collaborators`: blog_id, user_id, role, invited_by, invited_at, accepted_at, revoked_at.
- `blog_invites`: email, blog_id, token, expires_at, status.
- `posts`: blog_id, url, main_keyword, published_at, analysis_status.
- `analysis_jobs`: blog_id, status, started_at, completed_at, retry_count.
- 감사 로그 테이블(인증 시도, 초대 취소 등) 별도 운영.

## 6. API 개요
- `POST /auth/signup` — 이메일, 비밀번호로 가입.
- `POST /auth/login` — 로그인 후 세션 쿠키 발급.
- `POST /auth/logout` — 세션 무효화.
- `POST /blogs` — 블로그 추가 및 검증 코드 발급.
- `POST /blogs/{id}/verify` — 게시글 URL 제출 후 검증.
- `POST /blogs/{id}/analysis` — 12개월 포스트 분석 시작.
- `POST /blogs/{id}/invites` — 협업자 초대 생성/전송.
- `POST /blogs/{id}/invites/{inviteId}/cancel` — 초대 취소.
- `POST /blogs/{id}/collaborators/{userId}/remove` — 협업자 제거.
- `POST /posts` — 새 포스팅 워크플로우 시작.

## 7. 프런트엔드 기본 원칙
- 미니멀한 디자인 시스템(라이트/다크 필요 없음).
- 레이아웃 우선순위: ① 대시보드 ② 블로그 추가/소유권 인증 ③ 포스팅 작성 플로우 ④ 협업자 관리.
- 반응형(데스크톱 우선, 모바일 뷰는 1열 스택).
- 와이어프레임/`docs/ui` 자산은 사용하지 않음(삭제 예정).

## 8. 배포/환경
- 개발: Docker Compose 또는 로컬 실행.
- 스테이징/프로덕션: 서비스 URL 확보 가능한 호스팅(Firebase Hosting, Supabase, Render 등)으로 배포 후 네이버 검색 API 키 신청.
- 환경 변수: `OPENAI_API_KEY`, `NAVER_SEARCHAD_ACCESS_KEY`, `NAVER_SEARCHAD_SECRET_KEY`, `NAVER_SEARCH_API_KEY`(프로덕션 발급 후 적용).

## 9. 오픈 이슈 / TBD
- 이메일 발송 인프라(SMTP vs. 외부 서비스) 확정 필요.
- 비밀번호 재설정 메일 템플릿 및 발신자 브랜드링.
- 협업자 권한 세분화(읽기 전용 등) 여부.
