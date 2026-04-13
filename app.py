import base64
import io
import streamlit as st
import streamlit.components.v1 as components
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

[data-testid="stAppViewContainer"] { background-color: #fdf6ee; }
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
    box-shadow: 0 8px 32px rgba(255,107,53,0.25);
}
.hero-emoji { font-size: 3.2rem; display: block; margin-bottom: 0.6rem; }
.hero h1 {
    font-size: 2rem; font-weight: 900; color: #fff;
    margin: 0 0 0.5rem; line-height: 1.3;
    text-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.hero p { color: rgba(255,255,255,0.88); font-size: 0.95rem; margin: 0; }

/* ── 파일 업로더 완전히 숨기기 (기능은 유지) ── */
[data-testid="stFileUploader"] {
    visibility: hidden !important;
    height: 0 !important;
    overflow: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* ── 이미지 ── */
[data-testid="stImage"] img {
    border-radius: 20px !important;
    box-shadow: 0 8px 30px rgba(0,0,0,0.12) !important;
    width: 100% !important;
}

/* ── 분석중 ── */
[data-testid="stSpinner"] p { color: #ff6b35 !important; font-weight: 700 !important; }

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

.stMarkdown h2 { color: #ff6b35 !important; border-bottom: 2px solid #fde8d8; padding-bottom: 0.4rem; }
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

# ── 파일 업로더 2개 (숨겨놓고 JS로 트리거) ───────────────────────
# 순서 중요: gallery = inputs[0], camera = inputs[1]
사진     = st.file_uploader("gallery", key="gallery_input", type=["jpg","jpeg","png"], label_visibility="collapsed")
카메라사진 = st.file_uploader("camera",  key="camera_input",  type=["jpg","jpeg","png"], label_visibility="collapsed")

# ── 버튼 2개 (JS로 숨긴 파일 인풋을 직접 클릭) ───────────────────
components.html("""
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: transparent; font-family: 'Noto Sans KR', sans-serif; padding: 4px 0 8px; }
  .row { display: flex; gap: 14px; }
  .btn {
    flex: 1;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center; gap: 8px;
    padding: 1.5rem 1rem;
    border: none; border-radius: 22px;
    font-size: 1rem; font-weight: 700;
    cursor: pointer;
    transition: transform 0.12s, box-shadow 0.12s;
    -webkit-tap-highlight-color: transparent;
  }
  .btn:active { transform: scale(0.96); }
  .icon { font-size: 2rem; line-height: 1; }
  .camera {
    background: linear-gradient(135deg, #ff6b35, #f7931e);
    color: #fff;
    box-shadow: 0 6px 22px rgba(255,107,53,0.38);
  }
  .gallery {
    background: #fff;
    color: #ff6b35;
    border: 2.5px solid #ff6b35;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  }
</style>

<div class="row">
  <button class="btn camera" onclick="openCamera()">
    <span class="icon">📷</span>
    카메라로 찍기
  </button>
  <button class="btn gallery" onclick="openGallery()">
    <span class="icon">🖼️</span>
    사진 올리기
  </button>
</div>

<script>
  // 부모 페이지(Streamlit)의 숨겨진 파일 인풋을 찾아 직접 클릭
  function getInputs() {
    try { return window.parent.document.querySelectorAll('input[type="file"]'); }
    catch(e) { return []; }
  }

  function openCamera() {
    var inputs = getInputs();
    // inputs[1] = camera_input (두 번째로 선언된 업로더)
    var target = inputs.length >= 2 ? inputs[1] : inputs[0];
    if (!target) return;
    target.setAttribute('capture', 'environment'); // 핸드폰 후면 카메라 바로 실행
    target.setAttribute('accept', 'image/*');
    target.click();
  }

  function openGallery() {
    var inputs = getInputs();
    // inputs[0] = gallery_input (첫 번째로 선언된 업로더)
    var target = inputs[0];
    if (!target) return;
    target.removeAttribute('capture'); // capture 없으면 사진보관함/파일 선택창
    target.setAttribute('accept', 'image/*');
    target.click();
  }
</script>
""", height=120)

# ── 사진 올라왔을 때 ──────────────────────────────────────────────
입력사진 = 카메라사진 if 카메라사진 is not None else 사진

if 입력사진 is not None:

    # EXIF 회전 보정
    이미지 = ImageOps.exif_transpose(Image.open(입력사진))
    버퍼 = io.BytesIO()
    이미지.save(버퍼, format="JPEG")
    버퍼.seek(0)

    # 이미지 미리보기
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.image(이미지, caption="분석할 사진", use_container_width=True)

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
                            "image_url": {"url": f"data:image/jpeg;base64,{사진데이터}"}
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

    st.markdown("""
    <div class="success-banner">✅ &nbsp;분석 완료! 오늘의 레시피를 가져왔어요</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown(대답.choices[0].message.content)
    st.markdown('</div>', unsafe_allow_html=True)

# ── 하단 팁 ───────────────────────────────────────────────────────
st.markdown("""
<div class="tip-box">
    💡 &nbsp;냉장고 문을 열고 내부가 밝게 보이도록 찍으면 더 정확하게 인식해요!
</div>
""", unsafe_allow_html=True)
