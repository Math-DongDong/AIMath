import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ripser import ripser
from persim import plot_diagrams

st.markdown("""
<style>
    .step-header { font-size: 1.3rem; font-weight: bold; color: #007BFF; margin-top: 20px; margin-bottom: 10px; }            
    .info-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

st.title("🧬 의료 데이터 지속구간 다이어그램 분석")

# 탭 생성
tab1, tab2 = st.tabs(["🩸 고혈압 판정", "🍬 당뇨 판정"])

# ==============================================================================
# [TAB 1] 고혈압 판정 (2D 데이터)
# ==============================================================================
with tab1:
    # 1. 기본 데이터 입력
    empty_df_2d = pd.DataFrame({'x': pd.Series(dtype='float'), 'y': pd.Series(dtype='float')})

    with st.expander("📊 고혈압 판정 기초 데이터 입력 (정상군 / 고혈압군)", expanded=True):        
        col_set1, col_set2 = st.columns(2)
        with col_set1:
            st.markdown("**🟢 정상군 데이터 입력**")
            df_normal = st.data_editor(
                empty_df_2d, num_rows="dynamic", key="base_normal", width='stretch', height=300, hide_index=True,
                column_config={"x": st.column_config.NumberColumn("X좌표", required=True), "y": st.column_config.NumberColumn("Y좌표", required=True)}
            )
        with col_set2:
            st.markdown("**🔴 고혈압군 데이터 입력**")
            df_high_bp = st.data_editor(
                empty_df_2d, num_rows="dynamic", key="base_high_bp", width='stretch', height=300, hide_index=True,
                column_config={"x": st.column_config.NumberColumn("X좌표", required=True), "y": st.column_config.NumberColumn("Y좌표", required=True)}
            )

    # 2. 분석 및 추가 데이터
    col_control, col_display = st.columns([1, 2])

    with col_control:        
        st.markdown('<div class="step-header">분석 대상 선택 및 데이터 추가하기</div>', unsafe_allow_html=True)

        max_dim_1 = st.number_input(
            "지속구간 다이어그램의 최대 차원 설정", 
            min_value=0, 
            value=None, 
            step=1,
            key="dim_input_tab1",
            placeholder="0 이상의 정수만 적어주세요."
        )

        st.write("###### 1. 분석할 그룹 선택")
        target_group = st.radio("분석 그룹 선택", ("정상군", "고혈압군"), label_visibility="collapsed",key="radio_bp")
        
        st.write("---")
        st.write("###### 2. 데이터 추가하기")
        single_row_df = pd.DataFrame({'x': [None], 'y': [None]}, dtype='float')
        df_added = st.data_editor(
            single_row_df, num_rows="fixed", key="added_data_bp", width='stretch', hide_index=True,
            column_config={"x": st.column_config.NumberColumn("추가 X", required=True), "y": st.column_config.NumberColumn("추가 Y", required=True)}
        )
        st.caption("좌표를 입력하면 오른쪽 그래프에 반영됩니다.")

    with col_display:
        if target_group == "정상군":
            df_target = df_normal
            base_label = "정상군"
        else:
            df_target = df_high_bp
            base_label = "고혈압군"

        df_target_clean = df_target.dropna()
        
        if len(df_target_clean) < 2:
            st.warning("⚠️ 기초 데이터를 2개 이상 입력해주세요.")
        elif max_dim_1 is None: # [추가된 로직] 차원 입력 확인
            st.warning("⚠️ 지속구간 다이어그램의 최대 차원을 적어주세요")
        else:
            try:
                X_base = df_target_clean.to_numpy(dtype=float)

                if df_added.isnull().values.any():
                    X_combined = None
                else:
                    X_new_point = df_added.to_numpy(dtype=float)
                    X_combined = np.vstack([X_base, X_new_point])

                st.write(f"#### 📈 {target_group} 지속구간 다이어그램")
                col_plot1, col_plot2 = st.columns(2)

                # [수정] Ripser maxdim 설정 변수 사용
                with col_plot1:
                    dgm_base = ripser(X_base, maxdim=max_dim_1)['dgms']
                    fig1, ax1 = plt.subplots(figsize=(4, 4))
                    plot_diagrams(dgm_base, show=False, ax=ax1)
                    ax1.set_title("Original Data", fontsize=10)
                    st.pyplot(fig1)

                with col_plot2:
                    if X_combined is None:
                        st.info("👈 추가할 점의 좌표를 입력해주세요.")
                    else:
                        dgm_combined = ripser(X_combined, maxdim=max_dim_1)['dgms']
                        fig2, ax2 = plt.subplots(figsize=(4, 4))
                        plot_diagrams(dgm_combined, show=False, ax=ax2)
                        ax2.set_title("Original + Added Data", fontsize=10)
                        st.pyplot(fig2)
                
            except Exception as e:
                st.error(f"오류 발생: {e}")


# ==============================================================================
# [TAB 2] 당뇨 판정 (3D 데이터)
# ==============================================================================
with tab2:
    # 1. 기본 데이터 입력 (3차원)
    empty_df_3d = pd.DataFrame({
        'x': pd.Series(dtype='float'), 
        'y': pd.Series(dtype='float'),
        'z': pd.Series(dtype='float')
    })

    with st.expander("📊 당뇨 판정 기초 데이터 입력 (정상군 / 당뇨군)", expanded=True):
        col_set1_d, col_set2_d = st.columns(2)
        with col_set1_d:
            st.markdown("**🟢 정상군 데이터 입력**")
            df_normal_diab = st.data_editor(
                empty_df_3d, num_rows="dynamic", key="base_normal_diab", width='stretch', height=300, hide_index=True,
                column_config={
                    "x": st.column_config.NumberColumn("X좌표", required=True),
                    "y": st.column_config.NumberColumn("Y좌표", required=True),
                    "z": st.column_config.NumberColumn("Z좌표", required=True)
                }
            )
        with col_set2_d:
            st.markdown("**🔴 당뇨군 데이터 입력**")
            df_diab_group = st.data_editor(
                empty_df_3d, num_rows="dynamic", key="base_diab_group", width='stretch', height=300, hide_index=True,
                column_config={
                    "x": st.column_config.NumberColumn("X좌표", required=True),
                    "y": st.column_config.NumberColumn("Y좌표", required=True),
                    "z": st.column_config.NumberColumn("Z좌표", required=True)
                }
            )

    # 2. 분석 및 추가 데이터 (3차원)
    col_control_d, col_display_d = st.columns([1, 2])

    with col_control_d:
        st.markdown('<div class="step-header">분석 대상 선택 및 데이터 추가하기</div>', unsafe_allow_html=True)
        max_dim_2 = st.number_input(
            "지속구간 다이어그램의 최대 차원 설정", 
            min_value=0, 
            value=None, 
            step=1,
            key="dim_input_tab2",
            placeholder="0 이상의 정수만 적어주세요."
        )


        st.write("###### 1. 분석할 그룹 선택")
        target_group_diab = st.radio("분석 그룹 선택", ("정상군", "당뇨군"),label_visibility="collapsed", key="radio_diab")
        
        st.write("---")
        st.write("###### 2. 데이터 추가하기")
        single_row_df_3d = pd.DataFrame({'x': [None], 'y': [None], 'z': [None]}, dtype='float')
        df_added_diab = st.data_editor(
            single_row_df_3d, num_rows="fixed", key="added_data_diab", width='stretch', hide_index=True,
            column_config={
                "x": st.column_config.NumberColumn("추가 X", required=True),
                "y": st.column_config.NumberColumn("추가 Y", required=True),
                "z": st.column_config.NumberColumn("추가 Z", required=True)
            }
        )
        st.caption("좌표를 입력하면 오른쪽 그래프에 반영됩니다.")

    with col_display_d:
        if target_group_diab == "정상군":
            df_target_d = df_normal_diab
            base_label_d = "정상군"
        else:
            df_target_d = df_diab_group
            base_label_d = "당뇨군"

        df_target_clean_d = df_target_d.dropna()
        
        if len(df_target_clean_d) < 3:
            st.warning("⚠️ 기초 데이터를 3개 이상 입력해주세요.")
        elif max_dim_2 is None: # [추가된 로직] 차원 입력 확인
            st.warning("⚠️ 지속구간 다이어그램의 최대 차원을 적어주세요")
        else:
            try:
                X_base_d = df_target_clean_d.to_numpy(dtype=float)

                if df_added_diab.isnull().values.any():
                    X_combined_d = None
                else:
                    X_new_point_d = df_added_diab.to_numpy(dtype=float)
                    X_combined_d = np.vstack([X_base_d, X_new_point_d])

                st.write(f"#### 📈 {target_group_diab} 지속구간 다이어그램")
                col_plot1_d, col_plot2_d = st.columns(2)

                # [수정] Ripser maxdim 설정 변수 사용
                with col_plot1_d:
                    dgm_base_d = ripser(X_base_d, maxdim=max_dim_2)['dgms']
                    fig1_d, ax1_d = plt.subplots(figsize=(4, 4))
                    plot_diagrams(dgm_base_d, show=False, ax=ax1_d)
                    ax1_d.set_title("Original Data", fontsize=10)
                    st.pyplot(fig1_d)

                with col_plot2_d:
                    if X_combined_d is None:
                        st.info("👈 추가할 점의 X, Y, Z 좌표를 입력해주세요.")
                    else:
                        dgm_combined_d = ripser(X_combined_d, maxdim=max_dim_2)['dgms']
                        fig2_d, ax2_d = plt.subplots(figsize=(4, 4))
                        plot_diagrams(dgm_combined_d, show=False, ax=ax2_d)
                        ax2_d.set_title("Original + Added Data", fontsize=10)
                        st.pyplot(fig2_d)
                
            except Exception as e:
                st.error(f"오류 발생: {e}")