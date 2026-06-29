import hashlib
import io
import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image, ImageOps

# 커스텀 CSS 적용
st.markdown("""
<style>
/* 탭1 - 표의 머릿글과 왼쪽 인덱스 숨기기*/
#tabs-bui9-tabpanel-0 .e10e2fxn5 {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# 함수정의(탭2, 탭3 공통)
def load_excel_data(file_bytes, file_name):
    cache_key = f"excel_data:{hashlib.sha256(file_bytes).hexdigest()}"
    if cache_key not in st.session_state:
        st.session_state[cache_key] = pd.read_excel(io.BytesIO(file_bytes), header=None)
    return st.session_state[cache_key]


def df_to_image(df, scale_factor=20):
    # 유효 범위(0~255) 클리핑 및 형변환
    data = df.fillna(0).clip(0, 255).to_numpy(dtype=np.uint8, copy=False)
    cache_key = f"df_to_image:{hashlib.sha256(data.tobytes()).hexdigest()}"

    if cache_key not in st.session_state:
        img = Image.fromarray(data)
        original_w, original_h = img.size

        # 화면용 이미지는 긴 변이 1000px을 넘지 않도록 제한
        long_side = max(original_w, original_h)
        if long_side > 1000:
            scale = 1000 / long_side
            target_w = max(1, round(original_w * scale))
            target_h = max(1, round(original_h * scale))
        else:
            target_w = original_w
            target_h = original_h

        # NEAREST 옵션으로 픽셀화 효과 유지
        img_resized = img.resize((target_w, target_h), Image.Resampling.NEAREST)
        st.session_state[cache_key] = (img_resized, (original_w, original_h))

    return st.session_state[cache_key]

# --- 앱 제목 ---
st.title("이미지 데이터의 변환")

# 탭 생성
tab1, tab2, tab3 = st.tabs(["🔘 그레이 필터", "💡 밝기 조절", "➕ 합성" ])
with tab1:
    # ==============================================================================
    # 업로드된 파일을 PIL 이미지 객체로 변환
    def load_image(image_bytes, max_side=1000):
        image = Image.open(io.BytesIO(image_bytes))
        image = ImageOps.exif_transpose(image).convert('RGB')

        original_w, original_h = image.size
        long_side = max(original_w, original_h)

        if long_side > max_side:
            scale = max_side / long_side
            target_w = max(1, round(original_w * scale))
            target_h = max(1, round(original_h * scale))
            image = image.resize((target_w, target_h), Image.Resampling.LANCZOS)

        return image

    # 함수 정의 (RGB 데이터 시각화)
    def display_channel_data(image_array, title_prefix):
        st.markdown(f"#### 📊 {title_prefix}의 RGB 채널")
        st.caption("좌측 상단부터 **8x8 픽셀** 영역의 숫자(0~255)입니다.")
        slice_size = 8
        
        # 배열 크기가 8보다 작을 경우 에러 방지
        rows = min(slice_size, image_array.shape[0])
        cols = min(slice_size, image_array.shape[1])

        # 채널 분리
        r_channel = image_array[:rows, :cols, 0]
        g_channel = image_array[:rows, :cols, 1]
        b_channel = image_array[:rows, :cols, 2]

        # 데이터프레임 생성
        df_r = pd.DataFrame(r_channel)
        df_g = pd.DataFrame(g_channel)
        df_b = pd.DataFrame(b_channel)

        # 3열 배치
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("🔴 Red")
            st.table(df_r)
        with c2:
            st.write("🟢 Green")
            st.table(df_g)
        with c3:
            st.write("🔵 Blue")
            st.table(df_b)

    # ==============================================================================

    # 이미지 업로드 창 생성
    with st.expander("📂 이미지 업로드 열기/닫기", expanded=True):
        uploaded_file = st.file_uploader("이미지 파일을 업로드하세요.", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image_bytes = uploaded_file.read()
        image = load_image(image_bytes)
        original_width, original_height = image.size
        image_array = np.array(image)

        # [원본 / 결과] 
        col_orig, col_res = st.columns(2, gap="medium")
        with col_orig:
            st.subheader("원본 이미지")
            st.image(image, caption=f"원본 이미지 ( 해상도: {original_width}x{original_height} px )", width='stretch')

        with col_res:
            st.subheader("그레이 필터")

            # 원본 RGB 값의 평균을 계산하고 소수점 첫째 자리에서 반올림
            gray_matrix = np.round(np.mean(image_array, axis=2)).astype(np.uint8)
            gray_stacked_arr = np.stack((gray_matrix, gray_matrix, gray_matrix), axis=2)
            gray_pil = Image.fromarray(gray_stacked_arr)

            st.image(gray_pil, caption="그레이 필터 적용", width='stretch')

        # 3. 데이터 분석 표 (하단)
        st.divider()
        
        # (1) 원본 데이터
        display_channel_data(image_array, "원본 이미지")

        st.divider()

        # (2) 변환된 데이터
        display_channel_data(gray_stacked_arr, "그레이 필터 이미지")

    else:
            st.info("👆 상단의 '이미지 업로드'를 열어 이미지 파일( png, jpg, jpeg )을 먼저 업로드해주세요.")    

    with st.container(horizontal=True):
        st.space("stretch")
        st.page_link("https://matharticle.streamlit.app/GrayScale", label="그레이 필터 이미지 데이터 다운로드", icon="🔀", width="content")
                
with tab2:
    # ==============================================================================
    # 밝기 변환 프레그먼트
    @st.fragment
    def brightness_adjustment(df, file_id):
        # 파일 변경 감지 로직 (새 파일이 들어오면 데이터 리셋)
        if "last_file_id" not in st.session_state:
            st.session_state.last_file_id = None
            st.session_state.current_df = None

        # 업로드된 파일이 바뀌었으면 데이터를 새 파일 내용으로 덮어씀
        if st.session_state.last_file_id != file_id:
            st.session_state.last_file_id = file_id
            st.session_state.current_df = df.copy()

        setting_col1, setting_col2 = st.columns(2)
        with setting_col1:
            # 연산 버튼 설정
            with st.container(horizontal=True):
                operation = st.selectbox(
                    "연산 종류",
                    ("➕ 덧셈","➖ 뺄셈","✖️ 곱셈")
                )

                number = st.number_input(
                    "연산할 값",
                    min_value=0.0,
                    max_value=30.0, # 연산값은 좀 더 자유롭게
                    value=10.0,
                    step=1.0,
                    format="%.1f"
                )
        with setting_col2:
            st.space()
            with st.container(horizontal=True):    
                if st.button("🔄 원본 불러오기", type="secondary", width='stretch'):
                    st.session_state.current_df = df.copy()

                if st.button("🚀 연산 실행", type="primary", width='stretch'):
                    df_calc = st.session_state.current_df.copy()

                    if "덧셈" in operation:
                        df_calc = df_calc + number
                    elif "뺄셈" in operation:
                        df_calc = df_calc - number
                    elif "곱셈" in operation:
                        df_calc = df_calc * number

                    # 클리핑 (0~255 유지) 및 정수 변환
                    df_calc = df_calc.clip(0, 255)
                    df_calc = np.round(df_calc, 0).astype(int)
                    
                    # 연산 결과를 '현재 데이터'로 업데이트
                    st.session_state.current_df = df_calc

        # [ Left:Image  / Right: Dataframe ]
        col_left, col_right = st.columns(2, gap="large")
        with col_left:
            st.caption("오른쪽 행렬을 기반으로 표현된 이미지입니다.")

            # 이미지 변환 함수 호출
            pixelated_img, orig_size = df_to_image(st.session_state.current_df)
            st.image(
                pixelated_img,
                width='stretch',
                clamp=True # 0-255 범위 준수
            )

        with col_right:
            curr_r, curr_c = st.session_state.current_df.shape
            st.caption(f"연산이 누적되어 적용된 행렬( {curr_r} x {curr_c} )입니다.")

            # 원본/연산 데이터를 여기서 확인
            st.dataframe(
                st.session_state.current_df,
                height=500,
                width='stretch'
            )

    # ==============================================================================

    source_df = None
    with st.expander("📂 픽셀 데이터 업로드 열기/닫기", expanded=True):
        uploaded_file = st.file_uploader(
            "그레이 필터 이미지의 픽셀 데이터(Excel) 업로드",
            type=['xlsx']
        )

    if uploaded_file is not None:
        excel_bytes = uploaded_file.read()
        source_df = load_excel_data(excel_bytes, uploaded_file.name)
        brightness_adjustment(source_df,uploaded_file.name)

    else:
        # 데이터가 없을 때 안내
        st.info("👆 상단의 '픽셀 데이터 업로드'를 열어 엑셀파일(xlxs)을 먼저 업로드해주세요.")

with tab3:
    # ==============================================================================
    # 합성 연산 프레그먼트
    @st.fragment
    def image_addition_subtraction(df1,df2):
        # 결과 세션 변수 선언
        if "final_result" not in st.session_state:
            st.session_state.final_result = None
            
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            with st.container(horizontal=True):
                scalar1 = st.number_input(
                    "행렬 A의 실수배 (k₁)", 
                    min_value=0.0,
                    value=1.0, 
                    step=0.1, 
                    format="%.1f",
                    key="scalar1"
                )

                operation = st.selectbox(
                    "연산", 
                    ("➕", "➖"), 
                    
                )

                scalar2 = st.number_input(
                    "행렬 B의 실수배 (k₂)", 
                    value=1.0, 
                    min_value=0.0,
                    step=0.1, 
                    format="%.1f", 
                    key="scalar2"
                )

        with btn_col2:
            st.space()
            with st.container(horizontal=True):
                if st.button("🚀 계산 실행: (k₁ × A) " + operation + " (k₂ × B)", type="primary", width='stretch'):
                    # 1. 실수배 적용
                    term1 = df1 * scalar1
                    term2 = df2 * scalar2
                    
                    # 2. 덧셈/뺄셈 연산
                    if operation == "➕":
                        res_df = term1 + term2
                    else:
                        res_df = term1 - term2
                        
                    # 3. 데이터 보정 (0~255 클리핑 & 정수 변환)
                    res_df = res_df.fillna(0) # NaN 방지
                    res_df = res_df.clip(0, 255)
                    res_df = np.round(res_df, 0).astype(int)
                    
                    # 4. 결과 저장
                    st.session_state.final_result = res_df

        if st.session_state.get("final_result") is not None:
            result_col1, result_col2 = st.columns(2)
            with result_col1:
                st.subheader("결과 이미지")
                img_res, orig_size = df_to_image(st.session_state.final_result)
                st.image(
                    img_res,
                    width='stretch',
                    clamp=True
                )
            with result_col2:
                st.subheader("결과 행렬")
                st.dataframe(
                    st.session_state.final_result,
                    height=500,
                    width='stretch'
                )
    # ==============================================================================

    Uploaded_df1, Uploaded_df2 = None, None
    with st.expander("📂 픽셀 데이터 2개 업로드 (행렬 A, B)", expanded=True):
        col_up1, col_up2 = st.columns(2)
        with col_up1:
            file1 = st.file_uploader("행렬 A (엑셀 파일)", type=['xlsx'], key="file1")
        with col_up2:
            file2 = st.file_uploader("행렬 B (엑셀 파일)", type=['xlsx'], key="file2")

    if file1 and file2:
        file1_bytes = file1.read()
        file2_bytes = file2.read()

        Uploaded_df1 = load_excel_data(file1_bytes, file1.name)
        Uploaded_df2 = load_excel_data(file2_bytes, file2.name)
        
        # 행렬의 크기 검증
        if Uploaded_df1.shape != Uploaded_df2.shape:
            st.error(f"⚠️ 두 행렬의 크기가 다릅니다! (A: {Uploaded_df1.shape}, B: {Uploaded_df2.shape})")
        else:
            A_col, B_col = st.columns(2)
            with A_col:
                st.subheader("🅰️ 행렬 A")
                st.dataframe(Uploaded_df1, height=300, width='stretch')
            with B_col:
                st.subheader("🅱️ 행렬 B")
                st.dataframe(Uploaded_df2, height=300, width='stretch')

            image_addition_subtraction(Uploaded_df1, Uploaded_df2)                     

    elif Uploaded_df1 is None or Uploaded_df2 is None:
        st.info("👆 위에서 두 개의 엑셀 파일(xlxs)을 모두 업로드해주세요.")

    with st.container(horizontal=True):
        st.space("stretch")
        st.page_link("https://math-dongdong.github.io/MathArticle/%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5%EC%88%98%ED%95%99/Dissolve.html", label="디졸브 효과", icon="🔀", width="content")
