"""
카페24 유튜브 임베드 코드 생성기
- YouTube URL을 입력받아 카페24 상세페이지용 HTML iframe 코드 생성
- Streamlit 기반 단일 페이지 웹앱
"""

import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs

import streamlit as st
import streamlit.components.v1 as components


def log(message: str) -> None:
    """타임스탬프 포함 로그 출력 (전역 규칙: [YYYY-MM-DD HH:MM:SS] 메시지)"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {message}")


# YouTube VIDEO_ID 유효성 검증용 정규식 (영문자/숫자/하이픈/언더스코어 11자)
VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")


def extract_video_id(url: str) -> str | None:
    """
    YouTube URL에서 VIDEO_ID를 추출한다.

    지원 형식:
    - https://youtube.com/shorts/{ID}
    - https://www.youtube.com/shorts/{ID}
    - https://m.youtube.com/shorts/{ID}
    - https://youtu.be/{ID}
    - https://www.youtube.com/watch?v={ID}
    - https://m.youtube.com/watch?v={ID}
    - https://youtube.com/watch?v={ID}
    - https://www.youtube.com/embed/{ID}
    - https://www.youtube.com/v/{ID}
    - https://www.youtube.com/live/{ID}

    쿼리 파라미터(?si=, &t= 등)는 무시하고 VIDEO_ID만 반환.
    실패 시 None 반환.
    """
    if not url or not isinstance(url, str):
        return None

    url = url.strip()
    if not url:
        return None

    # 스키마가 없으면 https:// 추가 (파싱 안정성)
    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = "https://" + url

    try:
        parsed = urlparse(url)
    except Exception as e:
        log(f"[extract_video_id] URL 파싱 실패: {e}")
        return None

    host = (parsed.netloc or "").lower()
    path = parsed.path or ""

    # YouTube 도메인 필터링
    valid_hosts = (
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
        "youtu.be",
    )
    if host not in valid_hosts:
        return None

    candidate: str | None = None

    # 1) youtu.be/{ID}
    if host == "youtu.be":
        candidate = path.lstrip("/").split("/")[0] if path else None

    else:
        # 2) /watch?v={ID}
        if path == "/watch" or path.startswith("/watch/"):
            qs = parse_qs(parsed.query)
            v_list = qs.get("v")
            if v_list and v_list[0]:
                candidate = v_list[0]

        # 3) /shorts/{ID}, /embed/{ID}, /v/{ID}, /live/{ID}
        else:
            m = re.match(
                r"^/(shorts|embed|v|live)/([^/?#]+)",
                path,
                re.IGNORECASE,
            )
            if m:
                candidate = m.group(2)

    if not candidate:
        return None

    # 혹시 모를 추가 파라미터/fragment 제거
    candidate = candidate.split("?")[0].split("&")[0].split("#")[0].strip()

    # VIDEO_ID 유효성 검증 (11자, 허용된 문자만)
    if VIDEO_ID_PATTERN.match(candidate):
        return candidate

    return None


def generate_html(
    video_id: str,
    max_width: int = 720,
    margin: int = 20,
    aspect_ratio: str = "9/16",
) -> str:
    """
    VIDEO_ID와 커스텀 설정값으로 카페24 상세페이지용 iframe HTML을 생성한다.

    - 자동재생, 음소거, 무한반복, 컨트롤 숨김, 광고 최소화 파라미터 포함
    - pointer-events:none 으로 사용자 조작 차단 (상품페이지 내 배너처럼 동작)
    """
    html = (
        f'<div style="position:relative; width:100%; max-width:{max_width}px; '
        f'margin:{margin}px auto; aspect-ratio:{aspect_ratio};">\n'
        f'    <iframe\n'
        f'      src="https://www.youtube.com/embed/{video_id}'
        f'?autoplay=1&mute=1&loop=1&playlist={video_id}'
        f'&controls=0&modestbranding=1&rel=0&playsinline=1&iv_load_policy=3"\n'
        f'      style="position:absolute; top:0; left:0; width:100%; height:100%; '
        f'border:0; pointer-events:none;"\n'
        f'      allow="autoplay; encrypted-media"\n'
        f'      allowfullscreen>\n'
        f'    </iframe>\n'
        f'  </div>'
    )
    return html


def parse_aspect_ratio(label: str) -> str:
    """
    화면 비율 selectbox 라벨에서 CSS aspect-ratio 문자열을 추출한다.
    예) '9/16 (세로형 쇼츠)' -> '9/16'
    """
    m = re.match(r"^\s*(\d+\s*/\s*\d+)", label)
    if m:
        return m.group(1).replace(" ", "")
    return "9/16"


def main():
    """Streamlit UI 진입점"""
    st.set_page_config(
        page_title="카페24 유튜브 임베드 코드 생성기",
        page_icon="▶",
        layout="centered",
    )

    # 상단 타이틀
    st.title("카페24 유튜브 임베드 코드 생성기")
    st.caption(
        "유튜브 URL을 붙여넣으면 카페24 상세페이지에 바로 쓸 수 있는 HTML 코드를 만들어줍니다."
    )
    st.divider()

    # 결과 캐시 초기화 (session_state)
    # - html_output / video_id / aspect_ratio / max_width / margin 을 저장
    # - 출력 설정 변경 시에도 결과가 유지되도록 함
    if "html_output" not in st.session_state:
        st.session_state["html_output"] = None
    if "video_id" not in st.session_state:
        st.session_state["video_id"] = None
    if "result_aspect_ratio" not in st.session_state:
        st.session_state["result_aspect_ratio"] = "9/16"
    if "result_max_width" not in st.session_state:
        st.session_state["result_max_width"] = 720
    if "last_url" not in st.session_state:
        st.session_state["last_url"] = ""

    # URL 입력창
    url_input = st.text_input(
        "YouTube URL",
        key="url_input",
        placeholder="https://youtube.com/shorts/...",
    )

    # URL이 바뀌면 이전 결과 무효화 + 비율 자동 감지
    if url_input.strip() != st.session_state["last_url"]:
        if st.session_state["html_output"] is not None:
            st.session_state["html_output"] = None
            st.session_state["video_id"] = None
        st.session_state["last_url"] = url_input.strip()
        # /shorts/ URL이면 세로형, 아니면 가로형 자동 선택
        if "/shorts/" in url_input:
            st.session_state["auto_aspect_index"] = 0  # 9/16
        elif url_input.strip():
            st.session_state["auto_aspect_index"] = 1  # 16/9
        # URL 비어있으면 기존 선택 유지

    if "auto_aspect_index" not in st.session_state:
        st.session_state["auto_aspect_index"] = 0

    # 출력 설정 expander (기본 펼침)
    with st.expander("출력 설정", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            max_width = st.number_input(
                "최대 너비 (px)",
                min_value=300,
                max_value=1200,
                value=720,
                step=10,
            )
        with col2:
            margin = st.number_input(
                "여백 (margin, px)",
                min_value=0,
                max_value=100,
                value=20,
                step=1,
            )
        aspect_label = st.selectbox(
            "화면 비율 (URL 붙여넣으면 자동 선택, 수동 변경 가능)",
            options=[
                "9/16 (세로형 쇼츠)",
                "16/9 (가로형)",
                "1/1 (정사각형)",
                "4/5 (인스타형)",
            ],
            index=st.session_state["auto_aspect_index"],
        )
        aspect_ratio = parse_aspect_ratio(aspect_label)

    # 코드 생성 버튼
    generate_clicked = st.button("코드 생성하기", type="primary", use_container_width=True)

    if generate_clicked:
        # URL 비어있음
        if not url_input or not url_input.strip():
            st.warning("URL을 입력해주세요.")
            return

        # VIDEO_ID 추출
        try:
            video_id = extract_video_id(url_input)
        except Exception as e:
            log(f"[main] VIDEO_ID 추출 중 예외: {e}")
            video_id = None

        if not video_id:
            # 변환 실패 → 이전 결과도 초기화
            st.session_state["html_output"] = None
            st.session_state["video_id"] = None
            st.error("지원하지 않는 URL 형식입니다.")
            st.markdown(
                "**지원 형식**\n"
                "- `https://youtube.com/shorts/{ID}`\n"
                "- `https://www.youtube.com/shorts/{ID}`\n"
                "- `https://youtu.be/{ID}`\n"
                "- `https://www.youtube.com/watch?v={ID}`\n"
                "- `https://m.youtube.com/watch?v={ID}`\n"
                "- `https://www.youtube.com/embed/{ID}`"
            )
            return

        # 변환 성공 → HTML 생성
        try:
            html_output = generate_html(
                video_id=video_id,
                max_width=int(max_width),
                margin=int(margin),
                aspect_ratio=aspect_ratio,
            )
        except Exception as e:
            log(f"[main] HTML 생성 중 예외: {e}")
            st.error(f"HTML 생성 중 오류가 발생했습니다: {e}")
            return

        # 결과를 session_state에 캐싱 (이후 설정 변경으로 리런되어도 유지)
        st.session_state["html_output"] = html_output
        st.session_state["video_id"] = video_id
        st.session_state["result_aspect_ratio"] = aspect_ratio
        st.session_state["result_max_width"] = int(max_width)
        log(f"[main] HTML 생성 완료 (VIDEO_ID={video_id}, aspect={aspect_ratio})")

    # 결과 표시: session_state에 html_output이 있으면 항상 표시
    # (출력 설정을 건드려 리런이 발생해도 결과가 사라지지 않음)
    if st.session_state.get("html_output"):
        cached_html = st.session_state["html_output"]
        cached_video_id = st.session_state["video_id"]
        cached_aspect = st.session_state["result_aspect_ratio"]
        cached_max_width = st.session_state["result_max_width"]

        st.success(f"VIDEO_ID: {cached_video_id}")

        st.markdown("**생성된 HTML 코드 (카페24에 붙여넣기)**")
        st.code(cached_html, language="html")

        # 미리보기 - aspect_ratio 기반 동적 height 계산
        # 세로형(9:16) 영상이 500px 고정으로 잘리는 문제 수정
        st.markdown("### 미리보기")
        st.info("미리보기가 보이지 않아도 코드는 정상입니다. 카페24에 붙여넣어 확인하세요.")
        try:
            # "9/16" → w=9, h=16
            w_str, h_str = cached_aspect.split("/")
            w, h = int(w_str), int(h_str)
            preview_width = min(cached_max_width, 480)
            preview_height = int(preview_width * h / w) + 20  # 여유 20px
        except Exception as e:
            log(f"[main] 미리보기 height 계산 실패, 기본값 사용: {e}")
            preview_height = 500

        try:
            components.html(cached_html, height=preview_height)
        except Exception as e:
            log(f"[main] 미리보기 렌더링 실패: {e}")
            st.warning("미리보기 렌더링에 실패했습니다. 코드는 정상 생성되었습니다.")

        # 카페24 적용 방법 (실제 의도: 상세설명 탭의 HTML 버튼)
        with st.expander("카페24 적용 방법", expanded=False):
            st.markdown(
                "1. 위 코드를 복사합니다.\n"
                "2. 카페24 관리자 → 상품 관리 → 상품 등록/수정 → 상세설명 탭\n"
                "3. 에디터 [HTML] 버튼 클릭\n"
                "4. 원하는 위치에 코드를 붙여넣습니다.\n"
                "5. 저장 후 상품 페이지에서 확인합니다.\n\n"
                "영상은 자동재생·무한반복·음소거로 설정되어 광고 없이 재생됩니다."
            )


if __name__ == "__main__":
    main()
