import streamlit as st

# 1. 페이지 레이아웃 설정
st.set_page_config(
    page_title="동동쌤의 수학모음",
    page_icon="./기타/동동이.PNG",
    layout="wide"
)

# 2. 메뉴바 설정(각 페이지의 실제 콘텐츠는 별도의 파일에 존재).
pages = {
    "인공지능 수학": [ 
        st.Page("./인공지능수학/ImageExpression.py", title="이미지 데이터의 표현"),
        st.Page("./인공지능수학/ImageConversion.py", title="이미지 데이터의 변환"),
        st.Page("./인공지능수학/ImageClassification.py", title="이미지 데이터의 분류"),
        st.Page("./인공지능수학/TextExpression.py", title="텍스트 데이터의 표현과 주제어 찾기"),
        st.Page("./인공지능수학/TextConversion.py", title="텍스트 데이터에서 유용한 정보 찾기"),

    ],
}

# 3. 네비게이션 UI 생성(메뉴바 위치)
pg = st.navigation(pages)

# 4. 사용자가 선택한 페이지 실행

pg.run()

