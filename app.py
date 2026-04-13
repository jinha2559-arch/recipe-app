import base64
import streamlit as st
from openai import OpenAI

client = OpenAI(api_key="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")

st.set_page_config(page_title="냉장고 레시피 추천", page_icon="🍳")
st.title("🍳 냉장고 레시피 추천")
st.write("냉장고 사진을 올리면 AI가 레시피를 추천해드려요!")

사진 = st.file_uploader("📸 사진을 올려주세요", type=["jpg", "jpeg", "png"])

if 사진 is not None:
      st.image(사진, caption="업로드한 사진", width=300)

      with st.spinner("🤔 AI가 재료를 분석중이에요..."):
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

      st.success("✅ 분석 완료!")
      st.markdown(대답.choices[0].message.content)