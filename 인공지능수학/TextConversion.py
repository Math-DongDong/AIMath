import streamlit as st
import pandas as pd
import re
from itertools import zip_longest

# ==============================================================================
# 1. 페이지 설정 및 스타일 정의
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
        min-height: 200px;
    }
    th {
        text-align: center !important;
        background-color: #e8f4f8 !important;
    }
    td {
        text-align: center !important;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧮 텍스트 데이터에서 유용한 정보 찾기")

# ==============================================================================
# 2. 초기화
# ==============================================================================
default_data = {
    "내용": [
        "경치가 좋아서 사진을 찍기가 좋은 캠핑장이라 추천해요!",
        "시설이 깨끗하고 뷰가 좋은 캠핑장이에요.",
        "온수가 잘 나오고 화장실이 깨끗해서 위생적이라 좋네요."
    ]
}

if "doc_df" not in st.session_state:
    df = pd.DataFrame(default_data, index=["A", "B", "C"])
    df.index.name = "문서명"
    st.session_state.doc_df = df

if "wide_token_df" not in st.session_state:
    st.session_state.wide_token_df = None

# 확정된 데이터 (단어 가방 및 분석용)
if "confirmed_token_df" not in st.session_state:
    st.session_state.confirmed_token_df = None

# ==============================================================================
# 3. [Step 0] 텍스트 데이터 입력
# ==============================================================================
with st.expander("📝 문서 데이터 입력 및 수정 열기/닫기", expanded=True):    
    st.caption("※ 행을 추가하거나 삭제할 수 있습니다. **문서명** 열은 각 문서의 **고유 이름**으로 작성해주세요.")
    input_df = st.data_editor(
        st.session_state.doc_df,
        num_rows="dynamic",
        use_container_width=True,
        key="input_editor"
    )
    
    if st.button("🚀 데이터 전처리", type="primary", use_container_width=True):
        st.session_state.doc_df = input_df
        
        token_lists = []
        doc_names = []
        
        for doc_name, row in input_df.iterrows():
            content = str(row["내용"])
            cleaned = re.sub(r'[^\w\s]', '', content)
            tokens = cleaned.split()
            token_lists.append(tokens)
            doc_names.append(str(doc_name))
            
        combined_tokens = list(zip_longest(*token_lists, fillvalue=None))
        wide_df = pd.DataFrame(combined_tokens, columns=doc_names)
        
        st.session_state.wide_token_df = wide_df
        st.session_state.confirmed_token_df = None # 초기화
        st.rerun()

# ==============================================================================
# 4. 분석 프로세스
# ==============================================================================
if st.session_state.wide_token_df is not None:
    col_edit, col_bag = st.columns([0.5, 0.5], gap="large")
    with col_edit:
        st.subheader("1️⃣ 불용어 제거")
        st.caption("단어를 자유롭게 수정한 뒤 아래 버튼을 눌러주세요.")
        
        # [핵심] 폼 시작
        with st.form("token_edit_form", border=False):
            # 폼 안에서는 리로드가 발생하지 않습니다.
            edited_wide_df = st.data_editor(
                st.session_state.wide_token_df,
                use_container_width=True,
                height=300,
                num_rows="dynamic",
                key="wide_editor"
            )
            
            submit_btn = st.form_submit_button("🎒 단어 가방 만들기", type="primary", use_container_width=True)
        
        # 버튼이 눌리면 데이터 확정 및 저장
        if submit_btn:
            st.session_state.wide_token_df = edited_wide_df # 에디터 상태 저장
            st.session_state.confirmed_token_df = edited_wide_df.copy() # 분석용 확정
            st.rerun()

    # --- [Step 2] 단어 가방 및 TF-IDF (확정된 데이터가 있을 때만) ---
    if st.session_state.confirmed_token_df is not None:
        
        # 데이터 준비
        target_df = st.session_state.confirmed_token_df
        doc_names = target_df.columns.tolist()
        tokens_by_doc = []
        all_valid_tokens_flat = []

        for doc in doc_names:
            col_tokens = target_df[doc].dropna().astype(str).tolist()
            valid_tokens = [t for t in col_tokens if t.strip() != "" and t != "None"]
            tokens_by_doc.append(valid_tokens)
            all_valid_tokens_flat.extend(valid_tokens)

        # 1-2. 오른쪽: 단어 가방 시각화
        with col_bag:
            st.subheader("2️⃣ 단어 가방")
            st.caption("불용어가 제거된 최종 단어 집합입니다.")
            
            all_words = sorted(list(set(all_valid_tokens_flat)))
            
            if all_words:
                html_badges = ""
                for word in all_words:
                    count = all_valid_tokens_flat.count(word)
                    html_badges += f'<span class="word-badge">{word} <small>({count})</small></span>'
                
                st.markdown(f"""
                <div class="bag-container">
                    <h4>👜 Vocabulary</h4>
                    <div style="margin-top: 15px;">
                        {html_badges}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("단어 가방이 비어있습니다.")
                st.stop()

        # --------------------------------------------------------------------------
        # [Step 2] 단어빈도 (TF)
        # --------------------------------------------------------------------------
        st.divider()
        st.subheader("3️⃣ 단어빈도 (TF: Term Frequency)")
        st.caption("각 문서에 등장하는 단어들의 빈도수입니다.")
        
        tf_rows = []
        for tokens in tokens_by_doc:
            counts = [tokens.count(word) for word in all_words]
            tf_rows.append(counts)
        
        df_tf = pd.DataFrame(tf_rows, columns=all_words, index=doc_names)
        st.table(df_tf,border="horizontal")

        # --------------------------------------------------------------------------
        # [Step 3] 문서빈도 (DF)
        # --------------------------------------------------------------------------
        st.subheader("4️⃣ 문서빈도 (DF: Document Frequency)")
        st.caption("단어별로 그 단어가 등장하는 문서의 개수입니다.")
        df_counts = []
        for word in all_words:
            count = 0
            for tokens in tokens_by_doc:
                if word in tokens:
                    count += 1
            df_counts.append(count)
            
        df_df_table = pd.DataFrame([df_counts], columns=all_words, index=["DF"])
        st.table(df_df_table,border="horizontal")

        # --------------------------------------------------------------------------
        # [Step 4] 역문서빈도 (IDF)
        # --------------------------------------------------------------------------
        st.subheader("5️⃣ 역문서빈도 (IDF: Inverse Document Frequency)")
        n_docs = len(doc_names)
        
        st.latex(r"IDF = \frac{\text{전체 문서의 개수}(n)}{\text{문서빈도}(DF)}")
        st.caption(f"현재 전체 문서의 개수(n)는 **{n_docs}**개입니다.")

        idf_values = []
        for df_val in df_counts:
            if df_val == 0:
                idf_values.append(0)
            else:
                idf_values.append(n_docs / df_val)
        
        idf_display = [f"{v:.2f}".rstrip('0').rstrip('.') if v != 0 else "0" for v in idf_values]
        df_idf = pd.DataFrame([idf_display], columns=all_words, index=["IDF"])
        st.table(df_idf,border="horizontal")

        # --------------------------------------------------------------------------
        # [Step 5] TF-IDF
        # --------------------------------------------------------------------------
        st.subheader("6️⃣ TF-IDF 구하기")
        st.latex(r"\text{TF-IDF} = \text{TF} \times \text{IDF}")

        tfidf_rows = []
        for i in range(n_docs):
            row_vals = []
            for j in range(len(all_words)):
                tf_val = tf_rows[i][j]
                idf_val = idf_values[j]
                val = tf_val * idf_val
                row_vals.append(val)
            tfidf_rows.append(row_vals)

        df_tfidf = pd.DataFrame(tfidf_rows, columns=all_words, index=doc_names)
        df_tfidf_display = df_tfidf.applymap(lambda x: f"{x:.2f}".rstrip('0').rstrip('.') if x != 0 else "0")
        
        st.table(df_tfidf_display,border="horizontal")
        
        # [인사이트]
        st.divider()
        st.subheader("💡 분석 결과 인사이트")
        
        for idx, doc_name in enumerate(doc_names):
            row_series = df_tfidf.iloc[idx]
            max_val = row_series.max()
            
            if max_val > 0:
                top_words = row_series[row_series == max_val].index.tolist()
                top_words_str = ", ".join([f"'{w}'" for w in top_words])
                st.success(f"📄 **문서 {doc_name}**의 핵심 키워드: **{top_words_str}** (점수: {max_val:.2f})")
            else:
                st.info(f"📄 문서 {doc_name}에는 특징적인 단어가 없습니다.")
    else:
        # 버튼 누르기 전 안내 문구
        with col_bag:
            st.info("👈 왼쪽에서 수정을 마치고 **'단어 가방 만들기'** 버튼을 눌러주세요.")

else:
    st.info("👆 상단의 문서 입력창을 열고 분석할 문서 내용을 입력하세요.")
