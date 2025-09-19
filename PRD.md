# PRD (v1.2.3) — 플로그(내 병원 블로그 글 생성 어시스턴트)

## 1) 목표
초안 → 메인 키워드 1개 선택(검색량+내 실력 반영) → 내/외부 블로그 레퍼런스 선택 → 아웃라인 → 논문 자동 발췌 & 본문 생성(내 톤 + 이미지 제안 프롬프트)

## 2) KPI
- 작성 리드타임: 초안 → 본문 초안(이미지 제안 포함) 30분 이내
- 예상 순위(숫자) 적중도: 다음 커브 업데이트 시점의 실제 순위와 ±5등 이내 비율

## 3) 사용자 플로우
0. 구글 로그인
   - 별도의 회원 가입 플로우 없이 Google OAuth로 로그인
   - 최초 로그인 시 개인정보 활용 동의 등 최소 필수 항목만 요청
1. 네이버 블로그 소유권 관리(선택)
   - 내 블로그 등록 → 무작위 문자열 2개 발급(제목 토큰/본문 토큰)
   - 사용자는 네이버 블로그에 제목=토큰1, 본문=토큰2인 게시글 발행 후 URL 제출
   - “소유권 인증” 버튼 클릭 시 해당 URL을 크롤링하여 토큰 일치 여부 검증
   - 인증 성공 시 블로그를 “소유자” 권한으로 내 계정에 연결
   - 소유자는 이후 언제든 블로그 연결 해제(disown) 가능
   - 소유자는 구글 계정 이메일로 협업자(collaborator)를 초대/취소/강퇴 가능(협업자는 동일한 쓰기 권한)
   - 협업자는 초대 수락 후 블로그에 연결되며, 소유자가 해제하면 접근 불가
2. 초안 입력 → GPT: 후보 키워드 + fit(0..1) (최대 12개)
3. 검색량 조회 → 표기값: “네이버 지난 달 월간 검색수(PC+모바일 합)”
4. 내 파워 커브 업데이트(백그라운드) → 각 후보의 예상 순위(정수/1000+) 계산
5. 메인 키워드 1개 선택
6. 레퍼런스(블로그) 추천 & 선택
   - 외부 레퍼런스(옵션): 키워드로 수집한 상위 10개 URL을 읽기만(검색 OFF) 평가 → 카드 제안, 사용자는 0~3개 선택
   - 내 블로그 3개(옵션): “발행 당시 예상 순위 vs 현재 순위” 개선도 Top3 제안(톤 참고 전용) → 사용자는 0~3개 선택
7. 아웃라인 작성
   - 입력: 초안, 메인 키워드(+지난 달 검색수), **사용자가 실제 선택한 레퍼런스들만**(내/외부 혼합 가능)
   - 출력: H2~H3 아웃라인 + 섹션별 필요 근거 리스트(evidence_requests)
8. 논문 자동 발췌 & 본문 생성(한 번에)
   - 근거: 논문/가이드라인만 사용(블로그 인용 없음)
   - 출력: 제목 3안, 개요, 본문(H2 4–6), 체크리스트, FAQ, 이미지 제안(생성 모델용 프롬프트 포함), 참고 링크

## 4) 상세 기능

### 4.1 인증/협업 관리
- 구글 로그인
  - Google OAuth 2.0 기반, 이메일/프로필 기본 정보만 요청
  - 세션/토큰 만료 시 재인증 안내(로그아웃 기능 포함)
- 네이버 블로그 소유권 인증
  - 블로그 등록 시 서버가 랜덤 32자 내외 문자열 2개 생성(title_token/body_token)
  - 사용자는 지정된 토큰으로 게시글 작성 후 URL 입력 → “소유권 인증” 버튼
  - 검증 프로세스: HTTP GET → 제목/본문 토큰 일치 여부 확인 → 결과 UI 피드백(성공/실패 사유)
  - 성공 시 블로그 상태=verified, 실패 시 토큰 재발급 옵션 제공
  - 소유자는 언제든 “소유권 해제”로 블로그 연결 삭제(협업자도 자동 해제)
- 협업자(collaborator) 관리
  - 초대: 소유자가 구글 계정 이메일 입력 → 초대장 발송 → 수락 시 동일한 포스팅 권한 부여
  - 초대 취소: 수락 전 취소 가능(대기열 제거)
  - 강퇴: 이미 연결된 협업자를 제거(즉시 권한 회수)
  - 소유자와 협업자는 모두 3) 사용자 플로우 이후 단계(키워드 선정~본문 생성)를 동일하게 이용 가능


### 4.2 키워드 후보 & 표시
- GPT 출력: [{keyword, fit, why}]
- 검색량: 네이버 지난 달 월간 검색수(PC+모바일 합)
- 예상 순위: 정수(예: 7, 14, 52) 또는 1000+(Top1000 밖)
- 테이블 컬럼: 키워드 | 네이버 지난 달 월간 검색수 | fit | 예상 순위

### 4.3 내 파워 커브 & 숫자 예측(백그라운드)
- 초기 온보딩: 최근 12개월 포스트 전부 URL을 읽어 메인 키워드 자동 추출 → {post_id, url, main_keyword, published_at} 저장
- 업데이트(화면 진입 시):
  - 각 포스트 main_keyword로 네이버 블로그 검색 API 조회 → Top1000 내 정확 순위 R 찾기(없으면 R=1001 저장)
  - 각 키워드의 지난 달 검색수 V 저장
  - 경량 예측 모델로 V → R 매핑 학습(부록 참조) → 후보 키워드의 예상 순위(정수/1000+) 계산
- 1000+ 처리: 데이터 저장은 R=1001(상한값), 학습 시 상한 검열/가중치↓로 반영, 예측이 1000 초과면 UI엔 “1000+”

### 4.4 레퍼런스(블로그) 추천 & 선택
- 외부(옵션):
  - 키워드로 네이버 블로그 검색 → 정확도순 상위 URL 10개(중복 도메인 제거)
  - Deep Research 검색 OFF(읽기만)로 평가: 광고성↓·진정성↑·반응↑·최근성·구조 품질(H2/H3)·키워드 적합성
  - 카드: {title, url, postdate, summary(≤300자), why, flags[]}
  - 사용자는 0~3개 선택
- 내 블로그(옵션):
  - expected_rank_at_publish(5|15|null) vs 최근 측정 R_now → 개선도 큰 순 Top3 제안(톤 참고 전용)
  - 사용자는 0~3개 선택
- 중요: 작성 시 블로그 인용 없음(톤/구조 참고만)

### 4.5 아웃라인 작성
- 입력: 초안, 메인 키워드(+지난 달 검색수), **사용자가 선택한 레퍼런스들만**(내/외부 혼합 가능)
- 출력:
  - outline[] (H2~H3, section_id 포함)
  - evidence_requests[] (섹션별 필요 근거: 어떤 권고/리뷰/RCT, 검색문구 후보, 우선 출처 타입)

### 4.6 논문 자동 발췌 & 본문 생성(한 번에)
- Deep Research 검색 허용(PubMed/PMC/학회·가이드라인 우선)
- 내부 2스텝(단일 호출):
  1) evidence_requests[]를 충족하는 증거 번들 생성
     - {title, url/doi, pmid, pin, summary(2–3문장), (필요시) 짧은 인용, year, org}
  2) 내 톤 반영해 본문 작성(H2 4–6, 체크리스트, FAQ, 이미지 제안 포함)


#### 이미지 제안 — 생성 모델용 프롬프트 규격
- 각 섹션 1~2개:
  - section, prompt(생성 모델에 그대로 줄 문구), ratio(16:9|4:3), style(flat illustration|clean infographic|clinic environment photo-like), alt
- 프롬프트 예시:
  [교육용 일러스트]
  주제: 환절기 아토피 보습 루틴 5단계.
  구성: 손 씻기→미지근한 물 샤워→타월 톡톡 건조→3분 내 보습제→면소재 의류.
  표현: 깨끗한 라인, 단계 번호, 아이콘 위주(텍스트 최소).
  톤: 의료 과장 금지, 교육 목적.
  배경: 밝은 클리닉 톤, 브랜드/로고 없음.
  출력 비율: 4:3.

## 5) 데이터/저장
- User: id, google_sub, email, display_name
- Blog: id, owner_user_id, naver_blog_id, title, verified_at, status(pending|verified|disowned)
- BlogVerification: id, blog_id, title_token, body_token, post_url(submitted), verified_at, failed_reason
- BlogCollaborator: id, blog_id, user_id, invited_by_user_id, status(pending|accepted|revoked), invited_at, responded_at
- Post: id, url, main_keyword(초기 추출), published_at, expected_rank_at_publish(5|15|null)
- RankHistory: post_id, keyword, rank(R ∈ [1..1001]), measured_at, mode(sim)
- CurveModel: params/bins, updated_at
- KeywordVolume: keyword, month(YYYY-MM), volume_total
- RefCardExternal: {url, title, postdate, summary, why, flags}
- RefCardMyBlog: {post_id, url, title, summary, postdate}
※ 외부 블로그/논문 전문 텍스트 저장 금지(런타임 열람·요약만).

## 6) API/엔드포인트(요약)
POST /auth/google/callback        → { session }                  # OAuth 로그인(프론트는 Google SDK 사용)
POST /blogs                        → { blog }                    # 블로그 등록(토큰 발급)
POST /blogs/{id}/verify            → { status }                  # URL 검증, 실패 시 reason 포함
POST /blogs/{id}/disown            → { status }                  # 소유자 전용, 협업자 해제 포함
POST /blogs/{id}/collaborators     → { invitation }              # 소유자 전용 초대
DELETE /blogs/{id}/collaborators/{collab_id} → { status }       # 초대 취소 or 강퇴(상태에 따라 처리)
POST /keywords/extract         → { candidates:[{keyword,fit,why}] }
POST /keywords/volume          → { volumes:{키워드:{month:"YYYY-MM", total:Number}} }
GET  /curve?refresh=true       → { updated_at, model_summary, predict:{키워드: 순위숫자 | "1000+"} }
POST /references/external      → { cards:[...TopN] }      # DR 검색 OFF, 10개 URL 평가
GET  /references/myblog        → { cards:[...3개] }       # 톤 참고 전용
POST /outline/plan             → { outline:[...], evidence_requests:[...] }
POST /compose_with_research    → { titles[], overview, body, checklist, faq, image_suggestions[], references[] }
