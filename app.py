import streamlit as st

# 1. 페이지 레이아웃 설정
st.set_page_config(
    page_title="동동쌤의 수학모음",
    page_icon="./기타/동동이.PNG",
    layout="wide"
)

# 2. 메뉴바 설정(각 페이지의 실제 콘텐츠는 별도의 파일에 존재).
pages = {
    "중1 수학": [
        # 그룹의 첫 번째 페이지를 default=True로 설정하면 '중1 수학' 클릭 시 이 페이지가 먼저 보입니다.
        st.Page("./중1 수학/rotation.py", title="회전체 탐구", default=True),
    ],
    "중2 수학": [
        st.Page("./중2 수학/Exponents.py", title="지수법칙"),
    ],
    "보드게임": [
        st.Page("./보드게임/Streams.py", title="스트림스"),
        st.Page("./보드게임/PigGame.py", title="Pig Game"),
        st.Page("./보드게임/Dice.py", title="주사위 모음")
    ],
    "인공지능 수학": [ 
        st.Page("./인공지능수학/ImageExpression.py", title="이미지 데이터의 표현"),
        st.Page("./인공지능수학/ImageConversion.py", title="이미지 데이터의 변환"),
        st.Page("./인공지능수학/ImageClassification.py", title="이미지 데이터의 분류"),
        st.Page("./인공지능수학/TextExpression.py", title="텍스트 데이터의 표현과 주제어 찾기"),
        st.Page("./인공지능수학/TextConversion.py", title="텍스트 데이터에서 유용한 정보 찾기"),

    ],
    "산업수학": [
        st.Page("./산업수학/MedicalData.py", title="의료 데이터와 건강 상태"),
        st.Page("./산업수학/DistanceOptimization.py", title="원자력 발전소 기중기의 이동 경로 최적화"),
    ],    
}

# 3. 네비게이션 UI 생성(메뉴바 위치)
pg = st.navigation(pages, position="top")

# 4. 사용자가 선택한 페이지 실행

pg.run()

