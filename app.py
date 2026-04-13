import base64
import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(
    page_title="냉장고 레시피 추천",
    page_icon="🍳",
    layout="centered"
)

# ── 전체 디자인 CSS ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');

/* 전체 배경 */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
    font-family: 'Noto Sans KR', sans-serif;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { display: none; }
.block-container { padding-top: 2rem; padding-bottom: 4rem; }

/* 히어로 헤더 */
.hero {
    text-align: center;
    padding: 3rem 1rem 2rem;
}
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    color: #c9b8ff;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    padding: 6px 18px;
    border-radius: 50px;
    margin-bottom: 1.2rem;
}
.hero h1 {
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(90deg, #fff 0%, #c9b8ff 50%, #ff9a9e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin: 0 0 1rem;
}
.hero p {
    color: rgba(255,255,255,0.6);
    font-size: 1.1rem;
    margin: 0;
}

/* 구분선 */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(201,184,255,0.4), transparent);
    margin: 2rem 0;
}

/* 업로드 카드 */
.upload-card {
    background: rgba(255,255,255,0.05);
    border: 1.5px dashed rgba(201,184,255,0.4);
    border-radius: 20px;
    padding: 2.5rem 2rem;
    text-align: center;
    transition: all 0.3s ease;
}
.upload-card:hover {
    border-color: rgba(201,184,255,0.8);
    background: rgba(255,255,255,0.08);
}
.upload-label {
    color: rgba(255,255,255,0.5);
    font-size: 0.85rem;
    margin-top: 0.8rem;
    display: block;
}

/* 파일 업로더 스타일 오버라이드 */
[data-testid="stFileUploader"] {
    background: transparent !important;
}
[data-testid="stFileUploader"] > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1.5px dashed rgba(201,184,255,0.4) !important;
    border-radius: 20px !important;
    padding: 1.5rem !important;
}
[data-testid="stFileUploader"] label {
    color: rgba(255,255,255,0.8) !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
}
[data-testid="stFileDropzoneInstructions"] {
    color: rgba(255,255,255,0.4) !important;
}
[data-testid="stBaseButton-secondary"] {
    background: linear-gradient(135deg, #7c3aed, #c026d3) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s !important;
}
[data-testid="stBaseButton-secondary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(124,58,237,0.5) !important;
}

/* 이미지 카드 */
.image-wrapper {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 1.2rem;
    text-align: center;
    margin: 1.5rem 0;
}
.image-caption {
    color: rgba(255,255,255,0.4);
    font-size: 0.8rem;
    margin-top: 0.8rem;
}

/* 분석중 배너 */
.analyzing-box {
    background: linear-gradient(135deg, rgba(124,58,237,0.2), rgba(192,38,211,0.2));
    border: 1px solid rgba(201,184,255,0.3);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    color: #c9b8ff;
    font-weight: 700;
    font-size: 1.1rem;
    margin: 1rem 0;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

/* 성공 배너 */
.success-banner {
    background: linear-gradient(135deg, rgba(16,185,129,0.2), rgba(5,150,105,0.2));
    border: 1px solid rgba(16,185,129,0.4);
    border-radius: 16px;
    padding: 1rem 1.5rem;
    color: #6ee7b7;
    font-weight: 700;
    font-size: 1rem;
    margin: 1rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* 레시피 결과 카드 */
.result-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 24px;
    padding: 2rem 2.5rem;
    margin-top: 1.5rem;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}
.result-card h2, .result-card h3 {
    color: #c9b8ff !important;
}
.result-card p, .result-card li {
    color: rgba(255,255,255,0.85) !important;
    line-height: 1.8;
}
.result-card strong {
    color: #ff9a9e !important;
}

/* 마크다운 전체 텍스트 색상 */
.stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown h1,
.stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
    color: rgba(255,255,255,0.85) !important;
}
.stMarkdown h2 { color: #c9b8ff !important; border-bottom: 1px solid rgba(201,184,255,0.2); padding-bottom: 0.4rem; }
.stMarkdown h3 { color: #ff9a9e !important; }

/* 이미지 둥근 모서리 */
[data-testid="stImage"] img {
    border-radius: 16px !important;
    box-shadow: 0 20px 60px rgba(0,0,0,0.4) !important;
}

/* 스피너 */
[data-testid="stSpinner"] {
    color: #c9b8ff !important;
}
[data-testid="stSpinner"] > div {
    border-top-color: #c9b8ff !important;
}

/* 하단 안내 텍스트 */
.tip-text {
    text-align: center;
    color: rgba(255,255,255,0.3);
    font-size: 0.8rem;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(255,255,255,0.08);
}
</style>
""", unsafe_allow_html=True)

# ── 히어로 헤더 ───────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">✨ AI 레시피 추천</div>
    <h1>냉장고 속 재료로<br>오늘의 요리를</h1>
    <p>사진 한 장이면 충분해요 — AI가 재료를 읽고 레시피를 알려드려요</p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

# ── 파일 업로더 ───────────────────────────────────────────────────
사진 = st.file_uploader("📸 냉장고 사진을 올려주세요", type=["jpg", "jpeg", "png"])

# ── 사진 올라왔을 때 ──────────────────────────────────────────────
if 사진 is not None:

    # 이미지 미리보기
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image(사진, caption="업로드한 사진", use_container_width=True)

    # AI 분석
    with st.spinner("🤔  AI가 재료를 열심히 살펴보는 중이에요..."):
        사진데이터 = base64.b64encode(사진.read()).decode("utf-8")

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

    # 결과 카드
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown(대답.choices[0].message.content)
    st.markdown('</div>', unsafe_allow_html=True)

# ── 하단 안내 ─────────────────────────────────────────────────────
st.markdown("""
<div class="tip-text">
    냉장고 사진이 밝고 선명할수록 더 정확하게 재료를 읽을 수 있어요 🔍
</div>
""", unsafe_allow_html=True)
