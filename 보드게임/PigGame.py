# pig_game_app_v14_final_header_size_fix.py

import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import plotly.graph_objects as go

# [핵심 수정] .stats-header의 font-size 값을 .stats-cell과 유사한 수준으로 키워 균형을 맞춥니다.
st.markdown("""
<style>
.stats-table {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 15px;
    background-color: #fafafa;
}
.stats-header {
    text-align: center;
    font-weight: bold;
    font-size: 2em !important; /* 헤더 폰트 크기 대폭 증가 */
}
.stats-row-header {
    font-weight: bold;
    font-size: 1.2em !important; 
}
.stats-cell {
    text-align: center;
    font-size: 1.4em !important; 
    font-weight: bold; 
}
</style>
""", unsafe_allow_html=True)

st.title("🐷 Pig Game")

# --- 2. 상단 게임 설정 패널 ---
with st.expander("⚙️ 게임 설정 및 진행 방법 (클릭하여 열기/닫기)", expanded=('player_scores' not in st.session_state)):
    with st.form(key="game_setup_form"):
        col1, col2 = st.columns(2)
        with col1:
            num_players = st.slider("모둠 수", min_value=2, max_value=10, value=2)
        with col2:
            winning_score = st.number_input("목표 점수", min_value=20, max_value=100, value=100, step=10)

        st.markdown(f"""
        - **승리조건:** 먼저 **목표점수**에 도달하세요!
        - **진행:**
            1. 자기 차례가 되면 '주사위 던지기'를 계속할 수 있습니다.
            2. 나온 눈의 수가 '이번 라운드 점수'에 계속 더해집니다.
            3. **하지만 주사위 눈이 **`1`** 이 나오면...** 이번 라운드 점수는 **0점**이 되고, 즉시 다음 사람에게 차례가 넘어갑니다.
            4.  **`1`** 이 나오기 전에 '그만하기'를 누르면, 이번 라운드 점수가 '총 점수'에 더해지고 차례가 넘어갑니다.
        """)
        
        submitted = st.form_submit_button("🚀 새 게임 시작")
        
        if submitted:
            st.session_state.num_players = num_players
            st.session_state.winning_score = winning_score
            st.session_state.player_names = [f"{i+1}모둠" for i in range(num_players)]
            st.session_state.player_scores = [0] * num_players
            st.session_state.current_player = 0
            st.session_state.pending_score = 0
            st.session_state.last_roll = "🐷"
            st.session_state.game_over = False
            st.session_state.winner = None
            st.session_state.roll_history = []
            st.session_state.turn_over_message = ""
            st.rerun()


# --- 3. 핵심 게임 로직 함수 ---
def next_turn():
    st.session_state.current_player = (st.session_state.current_player + 1) % st.session_state.num_players
    st.session_state.pending_score = 0
    st.session_state.last_roll = "🐷"
    time.sleep(0.5) 

def roll_dice():
    roll = random.randint(1, 6)
    st.session_state.last_roll = roll
    st.session_state.roll_history.append(roll)
    if roll == 1:
        st.session_state.pending_score = 0
        st.session_state.turn_over_message = f"앗! 1이 나왔습니다. 점수를 모두 잃고 턴이 넘어갑니다."
        next_turn()
    else:
        st.session_state.pending_score += roll
        st.session_state.turn_over_message = ""

def hold():
    current_player_idx = st.session_state.current_player
    st.session_state.player_scores[current_player_idx] += st.session_state.pending_score
    st.session_state.turn_over_message = f"{st.session_state.pending_score}점을 획득했습니다!"
    if st.session_state.player_scores[current_player_idx] >= st.session_state.winning_score:
        st.session_state.game_over = True
        st.session_state.winner = st.session_state.player_names[current_player_idx]
    else:
        next_turn()

# --- 4. 메인 UI 렌더링 ---
if 'player_scores' not in st.session_state:
    st.info("👆 상단의 '게임 설정' 패널에서 설정을 마친 후 '새 게임 시작' 버튼을 눌러주세요.")
else:
    active_player_name = st.session_state.player_names[st.session_state.current_player]
    st.subheader(f"👑 현재 차례: **{active_player_name}**")
    if st.session_state.game_over:
        st.balloons(); 
        st.success(f"🎉 **게임 종료! 승자는 {st.session_state.winner} 입니다!** 🎉  새 게임을 시작하려면 상단 설정 패널에서 '새 게임 시작' 버튼을 누르세요.")
   
    main_col1, main_col2 = st.columns([0.3, 0.7])
    with main_col1:
        st.markdown(f"<p style='text-align: center; font-size: 110px; font-weight: bold; margin: 0; line-height: 1;'>{st.session_state.last_roll}</p>", unsafe_allow_html=True)
        st.metric(label="이번 라운드 점수", value=f"{st.session_state.pending_score} 점")
        btn_cols = st.columns(2)
        with btn_cols[0]: st.button("주사위 던지기", on_click=roll_dice, width='stretch', disabled=st.session_state.game_over)
        with btn_cols[1]: st.button("그만하기", on_click=hold, width='stretch', disabled=st.session_state.game_over)

    with main_col2:
        st.subheader("scoreboard")
        score_cols = st.columns(st.session_state.num_players)
        
        for i, col in enumerate(score_cols):
            with col:
                is_current_player = (i == st.session_state.current_player)
                player_name = st.session_state.player_names[i]
                header_text = f"👑 {player_name}" if is_current_player else player_name
                st.markdown(f"**{header_text}**")
                player_score = st.session_state.player_scores[i]
                delta_score = st.session_state.pending_score if is_current_player and not st.session_state.game_over else 0
                st.metric(label="총 점수", value=player_score, delta=f"{delta_score} 점" if delta_score > 0 else None)
        if st.session_state.turn_over_message: st.info(st.session_state.turn_over_message)

    st.divider()
    stats_col1, stats_col2 = st.columns(2)

    with stats_col1:
        st.subheader("📊 주사위 눈의 비율")
        if st.session_state.roll_history:
            roll_counts = pd.Series(st.session_state.roll_history).value_counts()
            full_counts = pd.Series(index=range(1, 7), data=0, dtype=int); full_counts.update(roll_counts)
            total_rolls = len(st.session_state.roll_history)
            roll_ratio = full_counts / total_rolls
            fig = go.Figure(); fig.add_trace(go.Scatter(x=roll_ratio.index, y=roll_ratio.values, mode='lines+markers', name='비율', line_shape='spline'))
            fig.update_layout(xaxis_title="주사위 눈", yaxis_title="비율", yaxis_range=[0, 1],height=300,margin=dict(l=0, r=0, t=0, b=0)); st.plotly_chart(fig, width='stretch')
        else: 
            st.caption("아직 주사위를 던지지 않았습니다.")

    with stats_col2:
        st.subheader("📈 주사위 눈의 통계표")
        if st.session_state.roll_history:
            roll_counts = pd.Series(st.session_state.roll_history).value_counts()
            full_counts = pd.Series(index=range(1, 7), data=0, dtype=int); full_counts.update(roll_counts)
            total_rolls = len(st.session_state.roll_history)
            roll_ratio = full_counts / total_rolls

            header_cols = st.columns([1, 1, 1, 1, 1, 1, 1])
            headers = ["", "🎲 1", "🎲 2", "🎲 3", "🎲 4", "🎲 5", "🎲 6"]
            for col, header in zip(header_cols, headers):
                col.markdown(f'<p class="stats-header">{header}</p>', unsafe_allow_html=True)
            
            #st.divider()

            freq_cols = st.columns([1, 1, 1, 1, 1, 1, 1])
            freq_cols[0].markdown('<p class="stats-row-header">빈도</p>', unsafe_allow_html=True)
            for i in range(1, 7):
                freq_cols[i].markdown(f'<p class="stats-cell">{full_counts.get(i, 0)}</p>', unsafe_allow_html=True)

            ratio_cols = st.columns([1, 1, 1, 1, 1, 1, 1])
            ratio_cols[0].markdown('<p class="stats-row-header">비율</p>', unsafe_allow_html=True)
            for i in range(1, 7):
                ratio_cols[i].markdown(f'<p class="stats-cell">{roll_ratio.get(i, 0.0):.3f}</p>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else: 
            st.caption("아직 주사위를 던지지 않았습니다.")

