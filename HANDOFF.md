# 냉장고 레시피 앱 - 핸드오프 문서

## 목표
냉장고 사진을 찍으면 AI가 재료를 인식하고 레시피를 추천해주는 앱 완성 및 발전

## 현재 진행 상황 (완료)

- VS Code 설치 완료 (한국어 설정)
- 파이썬 3.14.4 설치 완료
- OpenAI API 연결 완료 (gpt-4o-mini 사용)
- Streamlit으로 앱 화면 구현 완료
- 이모지 포함 예쁜 레시피 출력 기능 완료
- 깃허브 업로드 완료
- Streamlit Cloud 배포 완료
- 디자인 전면 개편 (따뜻한 크림/주황 테마)
- Anthropic Frontend Design Plugin 설치 완료
- Impeccable (pbakaus) 17개 스킬 설치 완료
- 카메라로 바로 찍기 기능 추가 (버튼 1번 클릭으로 기본 카메라 앱 실행)
- 사진 올리기 버튼 1번 클릭으로 사진보관함 바로 실행
- 세로 사진 가로로 뜨는 문제 수정 (EXIF 자동 회전 보정)
- 레시피 저장 기능 추가 (Supabase 연결)
- 저장된 레시피 탭 추가
- 탭 구조 개편 (카메라/사진 버튼 탭 밖, 레시피추천/저장된레시피 탭 분리)

## 앱 정보

- 배포 주소: https://recipe-app-c3eo8batqztropwmwjkqzu.streamlit.app
- 깃허브 주소: https://github.com/jinha2559-arch/recipe-app
- 로컬 경로: C:\Users\박진하\Desktop\recipe-app
- 주요 파일: app.py, requirements.txt

## API 키 관리

- OpenAI API 키는 Streamlit Cloud Secrets에 저장됨 → OPENAI_API_KEY
- Supabase URL → SUPABASE_URL (https://gqnyjsrjtpfgxcujukiv.supabase.co)
- Supabase 키 → SUPABASE_KEY
- app.py에서 st.secrets["키이름"] 으로 불러옴

## Supabase 정보

- 프로젝트명: recipe-app
- 테이블명: recipes
- 컬럼: id, title, content, created_at
- RLS: 비활성화 (SQL Editor에서 ALTER TABLE recipes DISABLE ROW LEVEL SECURITY; 실행)
- 가입: GitHub 계정으로 로그인

## 현재 앱 구조

```
히어로 배너 (주황 그라디언트)

[ 📷 카메라로 찍기 ]  [ 🖼️ 사진 올리기 ]  ← 탭 없이 바로

─────────────────────────────────
🍳 레시피 추천   │   📋 저장된 레시피
─────────────────────────────────
사진 올리면 분석 결과    저장된 목록
+ 저장 버튼              (expander로 펼치기)
```

## 설치된 패키지 (requirements.txt)

- openai
- streamlit
- Pillow
- supabase

## 잘 된 것들

- Streamlit으로 빠르게 앱 화면 구현
- gpt-4o-mini가 사진에서 재료 인식 잘 함
- 이모지 포함 프롬프트로 예쁜 출력 구현
- Streamlit Cloud로 무료 배포 성공
- 카메라 버튼 1번 클릭으로 기본 카메라 앱 직접 실행 (capture=environment)
- Supabase 무료 DB로 영구 저장 구현

## 안 된 것들 (주의사항)

- Vercel은 Streamlit 앱 배포 불가
- API 키를 코드에 직접 넣으면 보안 위험
- supabase 패키지가 Python 3.14 로컬에서 설치 안 됨 (Streamlit Cloud는 정상 작동)
- Supabase RLS 반드시 비활성화 해야 저장 가능
- 히어로 제목 가운데 정렬은 아직 미해결 (white-space: nowrap + text-align: center 적용 중)

## 다음 단계 (앞으로 할 것)

1. 히어로 제목 정렬 추가 개선 (선택사항)
2. 앱 디자인 추가 보완
3. 기타 기능 개선

## 사용자 참고사항

- 완전 초보자로 코딩 처음 시작
- 모든 설명은 한국어로, 유치원생 수준으로 쉽게
- 영어 용어는 반드시 한국어로 풀어서 설명
