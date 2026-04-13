import base64
import io
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from PIL import Image, ImageOps
from supabase import create_client

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

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
    display: flex;
    flex-direction: column;
    align-items: center;
}
.hero-emoji { font-size: 3.2rem; display: block; margin-bottom: 0.6rem; }
.hero h1 {
    font-size: 2rem; font-weight: 900; color: #fff;
    margin: 0 0 0.5rem; line-height: 1.3;
    text-shadow: 0 2px 8px rgba(0,0,0,0.15);
    text-align: left;
    white-space: nowrap;
}
.hero p { color: rgba(255,255,255,0.88); font-size: 0.95rem; margin: 0; word-break: keep-all; }

/* ── 파일 업로더 숨기기 ── */
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

/* ── 저장 완료 배너 ── */
.save-banner {
    background: #f0fff4;
    border-left: 4px solid #38a169;
    border-radius: 0 12px 12px 0;
    padding: 0.9rem 1.2rem;
    color: #276749;
    font-weight: 700;
    font-size: 0.95rem;
    margin: 0.5rem 0;
}

/* ── 레시피 결과 카드 ── */
.result-card {
    background: #fff;
    border-radius: 24px;
    padding: 2rem 2.2rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08);
    margin-top: 0.5rem;
}

/* ── 저장된 레시피 카드 ── */
.saved-card {
    background: #fff;
    border-radius: 18px;
    padding: 1.2rem 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    margin-bottom: 1rem;
    border-left: 4px solid #ff6b35;
}
.saved-card .title {
    font-size: 1rem;
    font-weight: 700;
    color: #4a2e1a;
    margin-bottom: 0.3rem;
}
.saved-card .date {
    font-size: 0.78rem;
    color: #b07a5a;
}

/* ── 탭 스타일 (밑줄 방식) ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 2px solid #f0e6dc !important;
    gap: 0 !important;
    padding: 0 !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 0 !important;
    font-weight: 700 !important;
    color: #b07a5a !important;
    font-size: 0.95rem !important;
    padding: 0.7rem 1.2rem !important;
    border-bottom: 3px solid transparent !important;
    margin-bottom: -2px !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: transparent !important;
    color: #ff6b35 !important;
    border-bottom: 3px solid #ff6b35 !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { display: none !important; }
[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }

.stMarkdown h2 { color: #ff6b35 !important; border-bottom: 2px solid #fde8d8; padding-bottom: 0.4rem; }
.stMarkdown h3 { color: #c04a10 !important; }
.stMarkdown p, .stMarkdown li { color: #4a2e1a !important; line-height: 1.9; }

/* ── 저장 버튼 ── */
[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #ff6b35, #f7931e) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.7rem 2rem !important;
    width: 100% !important;
    box-shadow: 0 4px 16px rgba(255,107,53,0.3) !important;
}

/* ── 하단 팁 ── */
.tip-box {
    background: #fff3e8;
    border-radius: 16px;
    padding: 1rem 1.4rem;
    margin-top: 2rem;
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
    <p>사진 한 장이면 충분해요</p>
    <p style="margin-top:0.3rem;">AI가 재료를 읽고 요리법을 알려드려요</p>
</div>
""", unsafe_allow_html=True)

# ── 숨겨진 파일 업로더 2개 ──────────────────────────────────────
사진     = st.file_uploader("gallery", key="gallery_input", type=["jpg","jpeg","png"], label_visibility="collapsed")
카메라사진 = st.file_uploader("camera",  key="camera_input",  type=["jpg","jpeg","png"], label_visibility="collapsed")

# ── 카메라 / 사진 버튼 (탭 없이 바로 등장) ───────────────────────
components.html("""
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: transparent; font-family: 'Noto Sans KR', sans-serif; padding: 4px 0 8px; }
  .row { display: flex; gap: 14px; }
  .btn {
    flex: 1; display: flex; flex-direction: column;
    align-items: center; justify-content: center; gap: 8px;
    padding: 1.5rem 1rem; border: none; border-radius: 22px;
    font-size: 1rem; font-weight: 700; cursor: pointer;
    transition: transform 0.12s; -webkit-tap-highlight-color: transparent;
  }
  .btn:active { transform: scale(0.96); }
  .icon { font-size: 2rem; line-height: 1; }
  .camera {
    background: linear-gradient(135deg, #ff6b35, #f7931e);
    color: #fff; box-shadow: 0 6px 22px rgba(255,107,53,0.38);
  }
  .gallery {
    background: #fff; color: #ff6b35;
    border: 2.5px solid #ff6b35; box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  }
</style>
<div class="row">
  <button class="btn camera" onclick="openCamera()">
    <span class="icon">📷</span>카메라로 찍기
  </button>
  <button class="btn gallery" onclick="openGallery()">
    <span class="icon">🖼️</span>사진 올리기
  </button>
</div>
<script>
  function getInputs() {
    try { return window.parent.document.querySelectorAll('input[type="file"]'); }
    catch(e) { return []; }
  }
  function openCamera() {
    var inputs = getInputs();
    var t = inputs.length >= 2 ? inputs[1] : inputs[0];
    if (!t) return;
    t.setAttribute('capture', 'environment');
    t.setAttribute('accept', 'image/*');
    t.click();
  }
  function openGallery() {
    var inputs = getInputs();
    var t = inputs[0];
    if (!t) return;
    t.removeAttribute('capture');
    t.setAttribute('accept', 'image/*');
    t.click();
  }
</script>
""", height=120)

st.markdown("<div style='margin-top:0.5rem'></div>", unsafe_allow_html=True)

# ── 탭 2개 ────────────────────────────────────────────────────────
탭_분석, 탭_저장 = st.tabs(["🍳  레시피 추천", "📋  저장된 레시피"])

# ══════════════════════════════════════════════════════════════════
# 탭 1: 레시피 추천
# ══════════════════════════════════════════════════════════════════
with 탭_분석:

    입력사진 = 카메라사진 if 카메라사진 is not None else 사진

    if 입력사진 is None:
        st.markdown("""
        <div style="text-align:center; padding: 2.5rem 1rem; color: #b07a5a;">
            <div style="font-size:2.5rem; margin-bottom:0.8rem;">☝️</div>
            <div style="font-weight:700; font-size:1rem; color:#4a2e1a;">위 버튼으로 사진을 올려주세요</div>
            <div style="font-size:0.85rem; margin-top:0.4rem;">사진을 올리면 AI가 재료를 분석하고 레시피를 추천해드려요</div>
        </div>
        """, unsafe_allow_html=True)

    if 입력사진 is not None:

        이미지 = ImageOps.exif_transpose(Image.open(입력사진))
        버퍼 = io.BytesIO()
        이미지.save(버퍼, format="JPEG")
        버퍼.seek(0)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            st.image(이미지, caption="분석할 사진", use_container_width=True)

        with st.spinner("🤔  AI가 재료를 열심히 분석하고 있어요..."):
            사진데이터 = base64.b64encode(버퍼.getvalue()).decode("utf-8")
            대답 = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{사진데이터}"}},
                        {"type": "text", "text": """이 냉장고 사진을 보고 아래 형식으로 대답해줘. 이모지를 풍부하게 사용해서 예쁘게 꾸며줘. 한국어로 대답해줘.

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
(맛있게 만드는 팁)"""}
                    ]
                }]
            )

        레시피내용 = 대답.choices[0].message.content

        # 추천 요리 이름 추출 (저장 제목용)
        제목 = "레시피"
        for 줄 in 레시피내용.split("\n"):
            if "추천 요리" in 줄 or "🍽️" in 줄:
                continue
            if 줄.strip() and not 줄.startswith("#") and not 줄.startswith("-"):
                제목후보 = 줄.strip().lstrip("*").strip()
                if len(제목후보) > 1:
                    제목 = 제목후보[:30]
                    break

        st.markdown('<div class="success-banner">✅ &nbsp;분석 완료! 오늘의 레시피를 가져왔어요</div>', unsafe_allow_html=True)

        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown(레시피내용)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 저장 버튼
        if st.button("💾  이 레시피 저장하기", type="primary"):
            try:
                supabase.table("recipes").insert({
                    "title": 제목,
                    "content": 레시피내용
                }).execute()
                st.markdown('<div class="save-banner">✅ &nbsp;저장 완료! 저장된 레시피 탭에서 확인하세요</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"저장 중 오류가 발생했어요: {e}")

    st.markdown('<div class="tip-box">💡 &nbsp;냉장고 문을 열고 내부가 밝게 보이도록 찍으면 더 정확하게 인식해요!</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# 탭 2: 저장된 레시피
# ══════════════════════════════════════════════════════════════════
with 탭_저장:

    try:
        결과 = supabase.table("recipes").select("*").order("created_at", desc=True).execute()
        레시피목록 = 결과.data
    except Exception as e:
        st.error(f"저장된 레시피를 불러오는 중 오류가 발생했어요: {e}")
        레시피목록 = []

    if not 레시피목록:
        st.markdown("""
        <div style="text-align:center; padding: 3rem 1rem; color: #b07a5a;">
            <div style="font-size:3rem; margin-bottom:1rem;">📋</div>
            <div style="font-weight:700; font-size:1rem;">아직 저장된 레시피가 없어요</div>
            <div style="font-size:0.85rem; margin-top:0.5rem;">레시피 추천 탭에서 저장해보세요!</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='color:#b07a5a; font-size:0.85rem; margin-bottom:1rem;'>총 {len(레시피목록)}개의 레시피가 저장되어 있어요</div>", unsafe_allow_html=True)

        for 레시피 in 레시피목록:
            날짜 = 레시피["created_at"][:10] if 레시피.get("created_at") else ""
            with st.expander(f"🍽️  {레시피['title']}  ·  {날짜}"):
                st.markdown(레시피["content"])
