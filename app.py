import base64
import io
import streamlit as st
from openai import OpenAI
from PIL import Image, ImageOps

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(
    page_title="냉장고 레시피 추천",
    page_icon="🍳",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

* { font-family: 'Noto Sans KR', sans-serif; }

/* 전체 배경 — 따뜻한 크림 */
[data-testid="stAppViewContainer"] {
    background-color: #fdf6ee;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { display: none; }
.block-container {
    padding-top: 0 !important;
    padding-bottom: 4rem;
    max-width: 720px;
}

/* ── 히어로 배너 ── */
.hero {
    background: linear-gradient(135deg, #ff6b35, #f7931e);
    border-radius: 0 0 36px 36px;
    padding: 3rem 2rem 2.5rem;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(255, 107, 53, 0.25);
}
.hero-emoji {
    font-size: 3.2rem;
    display: block;
    margin-bottom: 0.6rem;
}
.hero h1 {
    font-size: 2rem;
    font-weight: 900;
    color: #fff;
    margin: 0 0 0.5rem;
    line-height: 1.3;
    text-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.hero p {
    color: rgba(255,255,255,0.88);
    font-size: 0.95rem;
    margin: 0;
}

/* ── 섹션 제목 ── */
.section-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: #ff6b35;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}

/* ── 업로더 박스 ── */
[data-testid="stFileUploader"] > div {
    background: #fff !important;
    border: 2px dashed #f7c59f !important;
    border-radius: 20px !important;
    padding: 1.8rem !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stFileUploader"] > div:hover {
    border-color: #ff6b35 !important;
    box-shadow: 0 4px 20px rgba(255,107,53,0.15) !important;
}
[data-testid="stFileUploader"] label {
    color: #4a2e1a !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
}
[data-testid="stFileDropzoneInstructions"] {
    color: #b07a5a !important;
    font-size: 0.85rem !important;
}
[data-testid="stBaseButton-secondary"] {
    background: linear-gradient(135deg, #ff6b35, #f7931e) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    transition: all 0.2s !important;
}
[data-testid="stBaseButton-secondary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(255,107,53,0.35) !important;
}

/* ── 이미지 ── */
[data-testid="stImage"] img {
    border-radius: 20px !important;
    box-shadow: 0 8px 30px rgba(0,0,0,0.12) !important;
    width: 100% !important;
}

/* ── 분석중 ── */
[data-testid="stSpinner"] p {
    color: #ff6b35 !important;
    font-weight: 700 !important;
}

/* ── 성공 배너 ── */
.success-banner {
    background: #fff7f0;
    border-left: 4px solid #ff6b35;
    border-radius: 0 12px 12px 0;
    padding: 0.9rem 1.2rem;
    color: #c04a10;
    font-weight: 700;
    font-size: 0.95rem;
    margin: 1.5rem 0 1rem;
}

/* ── 레시피 결과 카드 ── */
.result-card {
    background: #fff;
    border-radius: 24px;
    padding: 2rem 2.2rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08);
    margin-top: 0.5rem;
}

/* 마크다운 텍스트 색상 */
.result-card .stMarkdown h2 {
    color: #ff6b35 !important;
    font-size: 1.1rem !important;
    font-weight: 900 !important;
    border-bottom: 2px solid #fde8d8 !important;
    padding-bottom: 0.4rem !important;
    margin-top: 1.4rem !important;
}
.result-card .stMarkdown h3 {
    color: #c04a10 !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
}
.result-card .stMarkdown p,
.result-card .stMarkdown li {
    color: #4a2e1a !important;
    line-height: 1.9 !important;
    font-size: 0.95rem !important;
}

/* 전체 마크다운 (result-card 밖) */
.stMarkdown h2 { color: #ff6b35 !important; }
.stMarkdown h3 { color: #c04a10 !important; }
.stMarkdown p, .stMarkdown li { color: #4a2e1a !important; line-height: 1.9; }

/* ── 하단 팁 ── */
.tip-box {
    background: #fff3e8;
    border-radius: 16px;
    padding: 1rem 1.4rem;
    margin-top: 2rem;
    display: flex;
    align-items: center;
    gap: 0.7rem;
    color: #9a5c38;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

# ── 히어로 배너 ────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <span class="hero-emoji">🍳</span>
    <h1>냉장고 속 재료로<br>오늘의 레시피를</h1>
    <p>사진 한 장이면 충분해요 — AI가 재료를 읽고 요리법을 알려드려요</p>
</div>
""", unsafe_allow_html=True)

# ── 파일 업로더 ───────────────────────────────────────────────────
st.markdown('<div class="section-label">📸 사진 업로드</div>', unsafe_allow_html=True)
사진 = st.file_uploader("냉장고 사진을 올려주세요", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

# ── 사진 올라왔을 때 ──────────────────────────────────────────────
if 사진 is not None:

    # EXIF 회전 보정 (핸드폰 세로 사진이 가로로 뜨는 문제 해결)
    이미지 = ImageOps.exif_transpose(Image.open(사진))
    버퍼 = io.BytesIO()
    이미지.save(버퍼, format="JPEG")
    버퍼.seek(0)

    # 이미지 미리보기
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.image(이미지, use_container_width=True)

    # AI 분석
    with st.spinner("🤔  AI가 재료를 열심히 분석하고 있어요..."):
        사진데이터 = base64.b64encode(버퍼.getvalue()).decode("utf-8")

        대답 = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{사진데이터}"
                            }
                        },
                        {
                            "type": "text",
                            "text": """이 냉장고 사진을 보고 아래 형식으로 대답해줘. 이모지를 풍부하게 사용해서 예쁘게 꾸며줘. 한국어로 대답해줘.

## 🥕 발견한 재료
(재료들을 이모지와 함께 나열)

## 🍽️ 추천 요리
(요리 이름과 간단한 설명)

## 📝 레시피
### 필요한 재료
(재료 목록)

### 만드는 방법
(단계별로 번호 매겨서)

## 💡 요리 팁
(맛있게 만드는 팁)"""
                        }
                    ]
                }
            ]
        )

    # 성공 메시지
    st.markdown("""
    <div class="success-banner">
        ✅ &nbsp;분석 완료! 오늘의 레시피를 가져왔어요
    </div>
    """, unsafe_allow_html=True)

    # 결과
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown(대답.choices[0].message.content)
    st.markdown('</div>', unsafe_allow_html=True)

# ── 하단 팁 ───────────────────────────────────────────────────────
st.markdown("""
<div class="tip-box">
    💡 &nbsp;냉장고 문을 열고 내부가 밝게 보이도록 찍으면 더 정확하게 인식해요!
</div>
""", unsafe_allow_html=True)
