import base64
import io
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from PIL import Image, ImageOps
from supabase import create_client

client  = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.set_page_config(page_title="냉장고 레시피", page_icon="🍳", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] {
    font-family: 'Noto Sans KR', sans-serif !important;
    background: #F7F7F7 !important;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

.block-container {
    padding: 0 !important;
    max-width: 480px !important;
}

/* ━━━━ 히어로 ━━━━ */
.hero {
    background: #FF5722;
    padding: 56px 28px 44px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; top: -80px; right: -80px;
    width: 260px; height: 260px;
    background: rgba(255,255,255,0.07);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute; bottom: -50px; left: -50px;
    width: 180px; height: 180px;
    background: rgba(0,0,0,0.06);
    border-radius: 50%;
}
.hero-icon {
    font-size: 3rem;
    display: block;
    margin-bottom: 18px;
    position: relative; z-index: 1;
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 900;
    color: #fff;
    line-height: 1.2;
    letter-spacing: -1px;
    margin-bottom: 14px;
    position: relative; z-index: 1;
    text-shadow: 0 2px 12px rgba(0,0,0,0.15);
}
.hero-sub {
    font-size: 0.92rem;
    color: rgba(255,255,255,0.82);
    line-height: 1.7;
    position: relative; z-index: 1;
}

/* ━━━━ 콘텐츠 래퍼 ━━━━ */
.content {
    padding: 24px 20px 40px;
}

/* ━━━━ 파일 업로더 완전 숨김 ━━━━ */
[data-testid="stFileUploader"] {
    position: absolute !important;
    width: 1px !important; height: 1px !important;
    overflow: hidden !important; opacity: 0 !important;
    pointer-events: none !important;
}

/* ━━━━ 탭 ━━━━ */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1.5px solid #E8E8E8 !important;
    gap: 0 !important; padding: 0 !important;
    margin-bottom: 20px !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 0 !important;
    font-weight: 700 !important;
    color: #AAAAAA !important;
    font-size: 0.93rem !important;
    padding: 12px 18px 12px !important;
    border-bottom: 2.5px solid transparent !important;
    margin-bottom: -1.5px !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: #FF5722 !important;
    border-bottom-color: #FF5722 !important;
    background: transparent !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"],
[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }

/* ━━━━ 이미지 ━━━━ */
[data-testid="stImage"] img {
    border-radius: 16px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.1) !important;
    width: 100% !important;
}

/* ━━━━ 스피너 ━━━━ */
[data-testid="stSpinner"] p { color: #FF5722 !important; font-weight: 700 !important; }

/* ━━━━ 배너 ━━━━ */
.banner {
    border-radius: 0 12px 12px 0;
    padding: 12px 16px;
    font-weight: 700;
    font-size: 0.88rem;
    margin: 14px 0 10px;
}
.banner-success { background:#FFF2EE; border-left:3px solid #FF5722; color:#CC3300; }
.banner-save    { background:#EDFFF5; border-left:3px solid #00B96B; color:#007A47; }

/* ━━━━ 레시피 카드 ━━━━ */
.recipe-card {
    background: #fff;
    border-radius: 20px;
    padding: 24px 20px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.07);
    margin-top: 4px;
}

/* ━━━━ 마크다운 ━━━━ */
.stMarkdown h2 {
    color: #FF5722 !important;
    font-size: 1rem !important;
    font-weight: 800 !important;
    margin-top: 22px !important;
    padding-bottom: 6px !important;
    border-bottom: 1.5px solid #FFE4DC !important;
}
.stMarkdown h3 { color: #333 !important; font-size: 0.94rem !important; font-weight: 700 !important; }
.stMarkdown p, .stMarkdown li { color: #444 !important; line-height: 1.85 !important; font-size: 0.91rem !important; }

/* ━━━━ 저장 버튼 ━━━━ */
[data-testid="stBaseButton-primary"] {
    background: #FF5722 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    height: 52px !important;
    width: 100% !important;
    margin-top: 8px !important;
    box-shadow: 0 4px 16px rgba(255,87,34,0.3) !important;
}

/* ━━━━ Expander ━━━━ */
[data-testid="stExpander"] {
    background: #fff !important;
    border: 1.5px solid #EFEFEF !important;
    border-radius: 14px !important;
    margin-bottom: 10px !important;
    overflow: hidden !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.04) !important;
}
[data-testid="stExpander"] summary {
    font-weight: 700 !important; color: #1A1A1A !important;
    font-size: 0.92rem !important; padding: 16px !important;
}

/* ━━━━ 빈 상태 ━━━━ */
.empty {
    text-align: center; padding: 48px 20px;
}
.empty-icon { font-size: 3rem; display: block; margin-bottom: 12px; }
.empty p { color: #BBBBBB; font-size: 0.88rem; line-height: 1.6; }

/* ━━━━ 팁 ━━━━ */
.tip { background:#FFF2EE; border-radius:12px; padding:14px 16px; margin-top:16px; color:#AA4422; font-size:0.82rem; line-height:1.6; }
</style>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 히어로 — <div> 사용 (h1 금지: Streamlit이 파란박스+링크 달아버림)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<div class="hero">
    <span class="hero-icon">🍳</span>
    <div class="hero-title">냉장고 속 재료로<br>오늘의 레시피를</div>
    <div class="hero-sub">
        사진 한 장이면 충분해요<br>
        AI가 재료를 읽고 요리법을 알려드려요
    </div>
</div>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 숨겨진 파일 업로더 (JS로 트리거)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
사진      = st.file_uploader("gallery", key="gallery_input", type=["jpg","jpeg","png"], label_visibility="collapsed")
카메라사진  = st.file_uploader("camera",  key="camera_input",  type=["jpg","jpeg","png"], label_visibility="collapsed")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 카메라 / 사진 버튼
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
components.html("""
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: transparent; font-family: 'Noto Sans KR', sans-serif; padding: 20px 20px 0; }
  .row { display: flex; gap: 12px; }
  .btn {
    flex: 1; display: flex; flex-direction: column;
    align-items: center; justify-content: center; gap: 8px;
    padding: 20px 12px; border: none; border-radius: 18px;
    font-size: 0.92rem; font-weight: 700; cursor: pointer;
    transition: transform 0.12s, box-shadow 0.12s;
    -webkit-tap-highlight-color: transparent;
    font-family: 'Noto Sans KR', sans-serif;
  }
  .btn:active { transform: scale(0.95); }
  .icon { font-size: 1.9rem; line-height: 1; }
  .cam {
    background: #FF5722; color: #fff;
    box-shadow: 0 4px 18px rgba(255,87,34,0.38);
  }
  .gal {
    background: #fff; color: #FF5722;
    border: 2px solid #FF5722;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
  }
</style>
<div class="row">
  <button class="btn cam" onclick="openCamera()">
    <span class="icon">📷</span>카메라로 찍기
  </button>
  <button class="btn gal" onclick="openGallery()">
    <span class="icon">🖼️</span>사진 올리기
  </button>
</div>
<script>
  function inputs() {
    try { return window.parent.document.querySelectorAll('input[type="file"]'); }
    catch(e) { return []; }
  }
  function openCamera() {
    var ii = inputs();
    var t = ii.length >= 2 ? ii[1] : ii[0];
    if (!t) return;
    t.setAttribute('capture','environment');
    t.setAttribute('accept','image/*');
    t.click();
  }
  function openGallery() {
    var ii = inputs();
    var t = ii[0]; if (!t) return;
    t.removeAttribute('capture');
    t.setAttribute('accept','image/*');
    t.click();
  }
</script>
""", height=110)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 탭 : 레시피 추천 | 저장된 레시피
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown('<div style="padding: 0 20px">', unsafe_allow_html=True)
탭_분석, 탭_저장 = st.tabs(["🍳  레시피 추천", "📋  저장된 레시피"])

# ── 탭 1 ──────────────────────────────────────────────────────────
with 탭_분석:
    입력사진 = 카메라사진 if 카메라사진 is not None else 사진

    if 입력사진 is None:
        st.markdown("""
        <div class="empty">
            <span class="empty-icon">☝️</span>
            <p>위 버튼으로 냉장고 사진을 올려주세요<br>AI가 재료를 읽고 레시피를 추천해드려요</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        이미지 = ImageOps.exif_transpose(Image.open(입력사진))
        버퍼   = io.BytesIO()
        이미지.save(버퍼, format="JPEG")
        버퍼.seek(0)

        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            st.image(이미지, use_container_width=True)

        with st.spinner("🤔  AI가 재료를 분석하고 있어요..."):
            사진데이터 = base64.b64encode(버퍼.getvalue()).decode("utf-8")
            대답 = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":[
                    {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{사진데이터}"}},
                    {"type":"text","text":"""이 냉장고 사진을 보고 아래 형식으로 대답해줘. 이모지를 풍부하게 사용해서 예쁘게 꾸며줘. 한국어로 대답해줘.

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
                ]}]
            )

        레시피내용 = 대답.choices[0].message.content

        제목 = "레시피"
        for 줄 in 레시피내용.split("\n"):
            if "추천 요리" in 줄 or "🍽️" in 줄: continue
            if 줄.strip() and not 줄.startswith("#") and not 줄.startswith("-"):
                후보 = 줄.strip().lstrip("*").strip()
                if len(후보) > 1: 제목 = 후보[:30]; break

        st.markdown('<div class="banner banner-success">✅ 분석 완료! 오늘의 레시피예요</div>', unsafe_allow_html=True)
        st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
        st.markdown(레시피내용)
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("💾  이 레시피 저장하기", type="primary"):
            try:
                supabase.table("recipes").insert({"title":제목,"content":레시피내용}).execute()
                st.markdown('<div class="banner banner-save">✅ 저장 완료! 저장된 레시피 탭에서 확인하세요</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"저장 오류: {e}")

    st.markdown('<div class="tip">💡 냉장고 문을 열고 내부가 밝게 보이도록 찍으면 더 정확하게 인식해요!</div>', unsafe_allow_html=True)

# ── 탭 2 ──────────────────────────────────────────────────────────
with 탭_저장:
    try:
        결과 = supabase.table("recipes").select("*").order("created_at", desc=True).execute()
        목록 = 결과.data
    except Exception as e:
        st.error(f"불러오기 오류: {e}"); 목록 = []

    if not 목록:
        st.markdown("""
        <div class="empty">
            <span class="empty-icon">📋</span>
            <p>아직 저장된 레시피가 없어요<br>레시피 추천 탭에서 저장해보세요!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='color:#AAA;font-size:0.82rem;margin-bottom:12px'>총 {len(목록)}개 저장됨</p>", unsafe_allow_html=True)
        for r in 목록:
            날짜 = r["created_at"][:10] if r.get("created_at") else ""
            with st.expander(f"🍽️  {r['title']}  ·  {날짜}"):
                st.markdown(r["content"])

st.markdown('</div>', unsafe_allow_html=True)
