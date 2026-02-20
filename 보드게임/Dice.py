# Dice.py (수정 완료)

import streamlit as st
import random
import time

st.title("🎲주사위 놀이")
# --- 구분선 ---
st.divider()

# --- 상태 초기화 (State Initialization) ---
if 'calculation_dice' not in st.session_state: # 연산 주사위
    st.session_state.calculation_dice = '❔'
if 'number_dice' not in st.session_state:      # 그냥 주사위
    st.session_state.number_dice = '❔'
if 'sign_dice' not in st.session_state:        # 부호있는 주사위
    st.session_state.sign_dice = '❔'

# --- 1영역: 연산 주사위 (+, -, *, /) ---
st.write("## ✖️연산 주사위➗")

if st.button("던지기", key="calculation_button"):
    placeholder = st.empty()
    start_delay = 0.05
    end_delay = 0.4
    total_steps = 15
    signs = ['➕', '➖','✖️','➗']
    
    for i in range(total_steps):
        temp_result = random.choice(signs)
        with placeholder.container():
            st.markdown(f"<p style='text-align: center; font-size: 80px;'>{temp_result}</p>", unsafe_allow_html=True)
        progress = i / total_steps
        current_delay = start_delay + (progress * (end_delay - start_delay))
        if i < total_steps - 1:
            time.sleep(current_delay)

    final_result = random.choice(signs)
    with placeholder.container():
        st.markdown(f"<p style='text-align: center; font-size: 80px;'>{final_result}</p>", unsafe_allow_html=True)
    st.session_state.calculation_dice = final_result
else:
    st.markdown(f"<p style='text-align: center; font-size: 80px;'>{st.session_state.calculation_dice}</p>", unsafe_allow_html=True)

st.divider()

# --- 2영역: 숫자 주사위 (1-6) ---
st.write("## 🔢숫자 주사위🎲")

if st.button("던지기", key="number_button"):
    placeholder = st.empty()
    start_delay = 0.05
    end_delay = 0.4
    total_steps = 15
    
    for i in range(total_steps):
        temp_result = random.randint(1, 6)
        with placeholder.container():
            st.markdown(f"<p style='text-align: center; font-size: 100px;'>{temp_result}</p>", unsafe_allow_html=True)
        progress = i / total_steps
        current_delay = start_delay + (progress * (end_delay - start_delay))
        if i < total_steps - 1:
            time.sleep(current_delay)
            
    final_result = random.randint(1, 6)
    with placeholder.container():
        st.markdown(f"<p style='text-align: center; font-size: 100px;'>{final_result}</p>", unsafe_allow_html=True)
    st.session_state.number_dice = final_result
else:
    st.markdown(f"<p style='text-align: center; font-size: 100px;'>{st.session_state.number_dice}</p>", unsafe_allow_html=True)

st.divider()

# --- 3영역: 부호 있는 주사위 (+, -) ---
st.write("## ➕부호 있는 주사위➖")

if st.button("던지기", key="sign_button"):
    placeholder = st.empty()
    start_delay = 0.05
    end_delay = 0.4
    total_steps = 15
    signs = ['+', '-']
    
    for i in range(total_steps):
        temp_result = random.choice(signs)
        NUMtemp_result = random.randint(1, 6)
        with placeholder.container():
            st.markdown(f"<p style='text-align: center; font-size: 100px;'>{temp_result}{NUMtemp_result}</p>", unsafe_allow_html=True)
        
        progress = i / total_steps
        current_delay = start_delay + (progress * (end_delay - start_delay))
        if i < total_steps - 1:
            time.sleep(current_delay)

    final_result = random.choice(signs)
    NUMfinal_result = random.randint(1, 6)
    
    # 부호와 숫자를 합친 최종 결과를 생성
    full_final_result = f"{final_result}{NUMfinal_result}"

    # 최종 결과를 화면에 표시
    with placeholder.container():
        st.markdown(f"<p style='text-align: center; font-size: 100px;'>{full_final_result}</p>", unsafe_allow_html=True)
    
    # 합쳐진 최종 결과를 session_state에 저장
    st.session_state.sign_dice = full_final_result

else:
    st.markdown(f"<p style='text-align: center; font-size: 100px;'>{st.session_state.sign_dice}</p>", unsafe_allow_html=True)