# 카페24 유튜브 임베드 코드 생성기 — 기획 문서

작성일: 2026-04-21
작성자: Claude (시니어 기획)
버전: 1.0

---

## 프로젝트 개요

YouTube Shorts URL을 입력받아 카페24 쇼핑몰에 바로 붙여넣기 할 수 있는 HTML iframe 코드를 생성하는 Streamlit 단일 페이지 웹앱.

- 프로젝트 경로: `C:\Users\gtmin\Dropbox\5.개발\youtube-embed-converter\`
- 배포 방식: 기존 cj-shipping-converter와 동일한 Streamlit 방식
- 파일 구성: `app.py`, `requirements.txt`

---

## 1. 기능 목록

### 필수 기능

| 기능 | 설명 |
|------|------|
| URL 입력 | YouTube Shorts/일반 URL 입력창 |
| VIDEO_ID 추출 | URL 파싱 → VIDEO_ID 분리 |
| HTML 코드 생성 | 고정 템플릿에 VIDEO_ID 삽입 |
| 코드 표시 | st.code()로 코드 블록 표시 (자체 copy 버튼 포함) |
| 미리보기 | st.components.v1.html로 실제 iframe 렌더링 |
| 입력값 유효성 검사 | 지원하지 않는 URL 형식 감지 및 안내 메시지 출력 |

### 선택 기능 (v1에서는 미구현, 추후 고려)

| 기능 | 설명 |
|------|------|
| 최근 변환 이력 | 세션 내 변환한 URL 목록 표시 |
| 커스텀 옵션 | max-width, margin 수치 사용자 조정 |

---

## 2. 기술 스택

| 항목 | 선택 | 이유 |
|------|------|------|
| 프레임워크 | Streamlit | 기존 cj-shipping-converter와 동일 — 배포 노하우 보유, Python 단일 파일로 충분 |
| URL 파싱 | Python 표준 라이브러리 `urllib.parse` + `re` | 외부 의존성 없이 처리 가능, 4가지 URL 패턴 모두 커버 |
| iframe 미리보기 | `streamlit.components.v1.html` | Streamlit 내장 기능, 별도 설치 불필요 |
| 패키지 관리 | `requirements.txt` | 크로스플랫폼 호환 |

---

## 3. 데이터 구조

### URL 파싱 규칙 (지원 형식 4종)

| URL 패턴 | VIDEO_ID 추출 방법 |
|----------|-------------------|
| `https://youtube.com/shorts/{ID}` | `/shorts/` 뒤 문자열 |
| `https://www.youtube.com/shorts/{ID}` | `/shorts/` 뒤 문자열 |
| `https://youtu.be/{ID}` | 도메인 뒤 경로 |
| `https://www.youtube.com/watch?v={ID}` | 쿼리 파라미터 `v` 값 |

- VIDEO_ID 형식: 영문자·숫자·하이픈·언더스코어 조합, 11자 (YouTube 표준)
- 쿼리 파라미터나 fragment(`&t=`, `?si=` 등)는 ID 추출 후 제거

### 출력 HTML 템플릿 (고정, 수정 불가)

```html
<div style="position:relative; width:100%; max-width:720px; margin:20px auto; aspect-ratio:9/16;">
    <iframe
      src="https://www.youtube.com/embed/{VIDEO_ID}?autoplay=1&mute=1&loop=1&playlist={VIDEO_ID}&controls=0&modestbranding=1&rel=0&playsinline=1&iv_load_policy=3"
      style="position:absolute; top:0; left:0; width:100%; height:100%; border:0; pointer-events:none;"
      allow="autoplay; encrypted-media"
      allowfullscreen>
    </iframe>
  </div>
```

`{VIDEO_ID}` 자리에 추출한 ID가 2곳 모두 삽입된다.

### 내부 상태 (Streamlit session_state)

| 키 | 타입 | 설명 |
|----|------|------|
| `url_input` | str | 사용자 입력 URL |
| `video_id` | str or None | 파싱 성공 시 VIDEO_ID |
| `html_output` | str or None | 생성된 HTML 코드 |

---

## 4. 파일/폴더 구조

```
youtube-embed-converter/
├── app.py                  # Streamlit 메인 앱 (유일한 실행 파일)
├── requirements.txt        # 패키지 목록
└── plans/
    └── plan.md             # 본 기획 문서
```

### app.py 내부 함수 구성

| 함수명 | 역할 |
|--------|------|
| `extract_video_id(url: str) -> str or None` | URL 파싱 → VIDEO_ID 반환. 실패 시 None |
| `generate_html(video_id: str) -> str` | 고정 템플릿에 VIDEO_ID 삽입 → HTML 문자열 반환 |
| `main()` | Streamlit UI 렌더링 진입점 |

### requirements.txt 내용

```
streamlit
```

- `urllib.parse`, `re` 는 Python 표준 라이브러리 — 별도 설치 불필요

---

## 5. UI 레이아웃

### 전체 페이지 구조 (텍스트 기반 와이어프레임)

```
┌─────────────────────────────────────────────────┐
│  카페24 유튜브 임베드 코드 생성기                │
│  YouTube Shorts URL을 붙여넣으면                 │
│  카페24에 바로 쓸 수 있는 HTML 코드를 만들어줍니다│
├─────────────────────────────────────────────────┤
│                                                  │
│  YouTube URL 입력                                │
│  ┌───────────────────────────────────────────┐  │
│  │ https://youtube.com/shorts/Y8pG2HxI9AU   │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
│  [  코드 생성하기  ]  ← st.button               │
│                                                  │
├─────────────────────────────────────────────────┤
│  (변환 성공 시 표시)                             │
│                                                  │
│  ✅ VIDEO_ID: Y8pG2HxI9AU                       │
│                                                  │
│  생성된 HTML 코드 (카페24에 붙여넣기)            │
│  ┌───────────────────────────────────────────┐  │
│  │ <div style="position:relative; ...       │  │
│  │   <iframe                                 │  │
│  │     src="https://www.youtube.com/embed/  │  │
│  │     ...                                   │  │
│  │ </div>                              [복사]│  │
│  └───────────────────────────────────────────┘  │
│  ← st.code() (언어: html, 자체 복사 버튼 포함)  │
│                                                  │
│  미리보기                                        │
│  ┌───────────────────────────────────────────┐  │
│  │                                           │  │
│  │       [실제 Shorts 영상 재생]             │  │
│  │       9:16 비율 렌더링                    │  │
│  │                                           │  │
│  └───────────────────────────────────────────┘  │
│  ← st.components.v1.html()                      │
│                                                  │
├─────────────────────────────────────────────────┤
│  (변환 실패 시 표시)                             │
│  ❌ 지원하지 않는 URL 형식입니다.               │
│     지원 형식: youtube.com/shorts/...,          │
│     youtu.be/..., youtube.com/watch?v=...       │
└─────────────────────────────────────────────────┘
```

### 사용자 플로우

```
[앱 접속]
    │
    ▼
[URL 입력창에 URL 붙여넣기]
    │
    ▼
[코드 생성하기 버튼 클릭]
    │
    ├─ URL이 비어있음 ──────────────▶ [경고: URL을 입력해주세요]
    │
    ├─ URL 파싱 실패 ───────────────▶ [에러: 지원하지 않는 URL 형식]
    │                                  + 지원 형식 안내 표시
    │
    └─ URL 파싱 성공
            │
            ▼
       [VIDEO_ID 추출]
            │
            ▼
       [HTML 코드 생성]
            │
            ▼
       [st.code()로 코드 표시]
            │
            ▼
       [st.components.v1.html()로 미리보기 렌더링]
            │
            ▼
       [사용자: 코드 복사 → 카페24 HTML 에디터에 붙여넣기]
```

---

## 6. 예상 에러 시나리오

| # | 에러 상황 | 발생 조건 | 처리 방법 |
|---|-----------|-----------|-----------|
| 1 | URL 미입력 | 버튼 클릭 시 입력창이 비어있음 | `st.warning("URL을 입력해주세요.")` 표시. 코드 블록 미표시 |
| 2 | 지원하지 않는 URL 형식 | 파싱 함수가 None 반환 (예: `https://vimeo.com/...`) | `st.error("지원하지 않는 URL 형식입니다. 아래 형식을 확인해주세요.")` + 지원 형식 목록 표시 |
| 3 | URL에 불필요한 파라미터 포함 | `?si=abc123`, `&t=10s` 등 추가 파라미터 포함된 URL | 파싱 시 VIDEO_ID만 추출, 나머지 파라미터는 무시 — 사용자에게 별도 안내 불필요 |
| 4 | 모바일 단축 URL | `https://youtube.com/shorts/ID?si=...` 형태 | ID 추출 후 `?` 이전까지만 사용 — 정상 처리 |
| 5 | 미리보기 렌더링 실패 | 브라우저 정책으로 iframe 차단 (CSP 등) | st.components는 별도 iframe 환경이므로 일반적으로 정상 동작. 실패해도 코드 생성 자체에는 영향 없음. 미리보기 영역 위에 안내 문구 추가: "미리보기가 표시되지 않으면 직접 카페24에서 확인하세요." |
| 6 | 영상 비공개/삭제 | VIDEO_ID는 추출되지만 영상 자체가 없음 | 코드 생성은 정상 완료. 미리보기에 유튜브 에러 화면이 보임. 코드 블록 위에 안내: "코드는 정상 생성되었습니다. 영상이 미리보기에 보이지 않으면 URL을 확인하세요." |

---

## 7. 카페24 적용 안내 (앱 내 표시)

코드 생성 후 하단에 접기/펼치기(expander) 형태로 카페24 적용 방법을 안내한다.

```
▶ 카페24에 적용하는 방법
  1. 위 코드를 복사합니다.
  2. 카페24 관리자 → 디자인 → HTML 에디터를 엽니다.
  3. 원하는 위치에 코드를 붙여넣습니다.
  4. 저장 후 쇼핑몰 화면에서 확인합니다.
```

---

다음 단계: developer 에이전트로 구현 진행
