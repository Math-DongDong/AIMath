import streamlit as st
import pandas as pd
import re
from itertools import zip_longest
from wordcloud import WordCloud     # 워드클라우드 라이브러리
import matplotlib.pyplot as plt     # 시각화 라이브러리
import os # 맨 위에 import 추가 필요

# ==============================================================================
# 1. 페이지 설정 및 스타일
# ==============================================================================
st.markdown("""
<style>
    .word-badge {
        display: inline-block;
        background-color: #f0f2f6;
        color: #31333F;
        border: 1px solid #d6d6d8;
        border-radius: 15px; 
        padding: 5px 12px;
        margin: 4px;
        font-size: 14px;
        font-weight: 500;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .word-badge:hover {
        transform: scale(1.05); 
        background-color: #e0e2e6;
        border-color: #ff4b4b; 
        cursor: pointer;
    }
    .bag-container {
        border: 2px dashed #ff4b4b;
        border-radius: 10px;
        padding: 20px;
        background-color: #fff9f9;
        text-align: center;
        min-height: 150px;
    }
    th {
        text-align: center !important;
        background-color: #e8f4f8 !important;
    }
    td {
        text-align: center !important;
        font-family: 'Courier New', monospace; /* 벡터 느낌 */
        font-weight: bold;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

st.title("👜 텍스트 데이터의 표현과 주제어 찾기")

# ==============================================================================
# 2. 세션 상태 초기화
# ==============================================================================
if "combined_df" not in st.session_state:
    st.session_state.combined_df = None

if "confirmed_df" not in st.session_state:
    st.session_state.confirmed_df = None

# ==============================================================================
# 3. 텍스트 입력 폼 
# ==============================================================================
with st.expander("🔍 텍스트 데이터 입력 열기/닫기", expanded=True):
    with st.form("three_text_form", border=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            text_a = st.text_area("텍스트 A", value="풍미 깊은 음식과 편안하고 아늑한 분위기가 조화롭게 어우러지는 특별하게 만들어주는 곳이에요.", height=80)
        with c2:
            text_b = st.text_area("텍스트 B", value="맛은 정말 훌륭했지만, 직원의 응대가 다소 미숙하고 주문한 음식이 늦게 나와서 실망스러웠어요~", height=80)
        with c3:
            text_c = st.text_area("텍스트 C", value="강력 추천! 음식이 기대 이상이었고, 특히 정성이 느껴지는 플레이팅은 감동 그 자체였습니다.", height=80)
        
        submitted = st.form_submit_button("🚀 데이터 전처리", type="primary", width="stretch")

        if submitted:
            def tokenize(text):
                cleaned = re.sub(r'[^\w\s]', '', text) 
                return cleaned.split()

            tokens_a = tokenize(text_a)
            tokens_b = tokenize(text_b)
            tokens_c = tokenize(text_c)

            combined_data = list(zip_longest(tokens_a, tokens_b, tokens_c, fillvalue=None))
            
            df = pd.DataFrame(combined_data, columns=["텍스트 A", "텍스트 B", "텍스트 C"])
            df.index = df.index + 1
            
            # 데이터 초기화
            st.session_state.combined_df = df
            st.session_state.confirmed_df = None 
            st.rerun()

# ==============================================================================
# 4. 메인 화면
# ==============================================================================
if st.session_state.combined_df is not None:
    
    col_left, col_right = st.columns([0.5, 0.5], gap="large")
    
    # --- [왼쪽] 에디터 (폼 적용) ---
    with col_left:
        st.subheader("1️⃣ 불용어 제거")
        st.caption("단어를 자유롭게 수정한 뒤 아래 버튼을 눌러주세요.")
        
        with st.form("editor_form", border=False):
            edited_snapshot = st.data_editor(
                st.session_state.combined_df,
                num_rows="delete",
                height=300, 
                key="main_editor"
            )
            
            make_bag_btn = st.form_submit_button("🎒 단어 가방 만들기", type="primary", width="stretch")

        if make_bag_btn:
            st.session_state.combined_df = edited_snapshot
            st.session_state.confirmed_df = edited_snapshot.copy()
            st.rerun()

    # --- [오른쪽] 단어 가방 ---
    with col_right:
        if st.session_state.confirmed_df is not None:
            st.subheader("2️⃣ 단어 가방")
            st.caption("불용어가 제거된 최종 단어 집합입니다.")

            target_df = st.session_state.confirmed_df
            
            all_tokens = target_df.stack().dropna().tolist()
            valid_tokens = [t for t in all_tokens if str(t).strip() != ""]
            vocab = sorted(list(set(valid_tokens)))
            
            if vocab:
                html_badges = ""
                for word in vocab:
                    count = valid_tokens.count(word)
                    html_badges += f'<span class="word-badge">{word} <small>({count})</small></span>'
                
                st.markdown(f"""
                <div class="bag-container">
                    <h4>👜Bag of Words</h4>
                    <div style="margin-top: 15px;">
                        {html_badges}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("단어 가방이 비어있습니다.")
        
        else:
            st.info("👈 왼쪽에서 수정을 마치고 **'단어 가방 만들기'** 버튼을 눌러주세요.")

    # ==========================================================================
    # 5. 하단 벡터 표현 및 워드 클라우드
    # ==========================================================================
    if st.session_state.confirmed_df is not None:
        target_df = st.session_state.confirmed_df
        
        all_tokens = target_df.stack().dropna().tolist()
        valid_tokens = [t for t in all_tokens if str(t).strip() != ""]
        vocab = sorted(list(set(valid_tokens)))

        if vocab:
            st.divider()
            
            # --- 공통 데이터 준비 ---
            def get_column_tokens(column_name):
                col_data = target_df[column_name].dropna().tolist()
                return [t for t in col_data if str(t).strip() != ""]

            tokens_list_a = get_column_tokens("텍스트 A")
            tokens_list_b = get_column_tokens("텍스트 B")
            tokens_list_c = get_column_tokens("텍스트 C")

            # --- [섹션 A] 원-핫 벡터 (존재 여부 1/0) ---
            st.subheader("3️⃣ 원-핫 벡터 표현 (One-Hot Vector)")
            st.caption("단어 가방의 단어가 포함되어 있으면 1, 없으면 0으로 표시합니다.")

            def make_one_hot(tokens, vocabulary):
                return [1 if word in tokens else 0 for word in vocabulary]

            df_onehot = pd.DataFrame(
                [make_one_hot(tokens_list_a, vocab), 
                 make_one_hot(tokens_list_b, vocab), 
                 make_one_hot(tokens_list_c, vocab)],
                columns=vocab,
                index=["A", "B", "C"]
            )

            # [시각화 함수] 벡터 스타일 (괄호 및 쉼표) 적용
            def format_vector_df(df):
                df_str = df.astype(str)
                for col in df_str.columns[:-1]:
                    df_str[col] = df_str[col] + ","
                df_str.insert(0, " ", "(")
                df_str.insert(len(df_str.columns), "  ", ")")
                return df_str

            st.table(format_vector_df(df_onehot),border="horizontal")

            st.divider()

            st.subheader("4️⃣ 빈도수 벡터 표현 (Frequency Vector)")
            st.caption("각 단어가 문장에 몇 번 등장했는지를 통해 주제어를 찾을 수 있습니다.")

            def make_count_vector(tokens, vocabulary):
                return [tokens.count(word) for word in vocabulary]

            df_count = pd.DataFrame(
                [make_count_vector(tokens_list_a, vocab), 
                    make_count_vector(tokens_list_b, vocab), 
                    make_count_vector(tokens_list_c, vocab)],
                columns=vocab,
                index=["A", "B", "C"]
            )
            
            # 원-핫 벡터와 동일한 스타일 적용
            st.table(format_vector_df(df_count),border="horizontal")

            with st.container(horizontal=True):
                st.space("stretch")
                with st.popover("워드클라우드 보기",help="단어들의 빈도수를 시각적으로 표현합니다.",type ="secondary",width="content"):
                    
                    # 워드 클라우드 생성
                    try:
                        # 빈도수 딕셔너리 생성
                        total_counts = {word: valid_tokens.count(word) for word in vocab}

                        # 폰트 설정
                        # 1. 현재 파일의 위치 ( .../mathzip/인공지능수학 )
                        current_dir = os.path.dirname(os.path.abspath(__file__))
                        
                        # 2. 한 단계 위로 올라가기 ( .../mathzip )
                        parent_dir = os.path.dirname(current_dir)
                        
                        # 3. 거기서 'fonts' 폴더 안으로 들어가기
                        font_path = os.path.join(parent_dir, "기타", "나눔고딕 D2coding.ttf")
                        
                        wc = WordCloud(
                            width=400, 
                            height=300, 
                            background_color='white',
                            font_path=font_path 
                        ).generate_from_frequencies(total_counts)
                        
                        # matplotlib로 이미지 변환
                        fig, ax = plt.subplots()
                        ax.imshow(wc, interpolation='bilinear')
                        ax.axis('off')
                        st.pyplot(fig)
                        
                    except Exception as e:
                        # 폰트 에러 등이 발생할 경우 대비
                        st.error("워드 클라우드 생성 중 오류가 발생했습니다 (폰트 문제일 수 있습니다).")
                        st.write(e)

else:
    st.info("👆 상단의 텍스트 입력창을 열고 분석할 텍스트를 입력하세요.")



