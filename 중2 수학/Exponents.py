import streamlit as st
import random

# --- [핵심] 스타일 정의 ---
# 이 스타일은 앱 전체에 적용됩니다. st.latex로 표시되는 수식의 폰트 크기를 키웁니다.
st.markdown("""
<style>
/* 메인에 표시되는 큰 수식 (st.latex) */
.stMarkdown .katex-display .katex {
    font-size: 4em; /* 화면에 맞게 폰트 크기 조절 (예: 4em) */
    text-align: center;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)


def initialize_exponent_game():
    """
    지수법칙 문제 게임의 상태를 초기화하는 함수입니다.
    st.session_state를 사용하여 앱의 상태를 관리합니다.
    """
    # 1. 문제 은행: 이미지에 있는 14개의 지수법칙 문제를 LaTeX 문자열 리스트로 정의합니다.
    problems = [
        r"(a^3)^5 \times a^2",
        r"x^3 \times y^5 \times x \times y^4",
        r"(25^2)^3 = 5^a \text{ 를 만족하는 자연수 } a?",
        r"y \div y^7",
        r"a^{11} \div a^3 \div a^4",
        r"a^\Box \div a^4 = a^5 \text{ 를 만족하는 자연수 } \Box?",
        r"3x^2y \times 4xy^3 \div 2x^4y^2",
        r"64^3 \div 2^7 = 2^a \text{ 를 만족하는 자연수 } a?",
        r"(x^2y^3)^6",
        r"(-x^3y)^4",
        r"\left(\frac{2y}{x}\right)^3",
        r"-\left(\frac{x^2}{y}\right)^4",
        r"72^3 = 2^a \times 3^6 \text{ 을 만족시키는 자연수 } a?",
        r"2^{10} \times 5^6 \text{은 } n\text{자리의 자연수일 때, } n?"
    ]
    
    # 2. 문제 섞기: 문제 순서를 무작위로 섞어 매번 다른 순서로 출제되도록 합니다.
    random.shuffle(problems)
    
    # 3. 세션 상태 초기화: 게임에 필요한 변수들을 st.session_state에 저장합니다.
    # 이 값들은 사용자가 앱과 상호작용하는 동안 계속 유지됩니다.
    st.session_state.problem_pool = problems     # 앞으로 뽑을 문제들이 담긴 리스트
    st.session_state.draw_count = 0              # 현재까지 뽑은 문제의 개수
    st.session_state.current_problem = "❔"      # 화면에 표시될 현재 문제
    st.session_state.drawn_history = []          # 이미 뽑았던 문제들의 기록
    st.session_state.total_problems = len(problems) # 전체 문제 개수 저장

# --------------------------------------------------------------------------
# --- 앱 UI(사용자 인터페이스) 시작 ---
# --------------------------------------------------------------------------

# 앱의 제목을 설정합니다.
st.title("🔢 지수법칙 문제 뽑기")
st.divider() # 시각적인 구분을 위한 가로선

# st.session_state에 'problem_pool'이 없으면 (즉, 앱을 처음 켰을 때) 게임을 초기화합니다.
if 'problem_pool' not in st.session_state:
    initialize_exponent_game()

# 버튼들을 가로로 배치하기 위해 st.columns를 사용합니다.
# 비율을 [1, 2, 1]로 주어 양쪽에 버튼을, 가운데에 공간을 만듭니다.
col1, col_spacer, col2 = st.columns([1, 2, 1])

with col1:
    # '처음부터 다시하기' 버튼입니다. 누르면 게임 상태가 초기화됩니다.
    if st.button("🔄️ 처음부터 다시하기", type="primary", width='stretch'):
        initialize_exponent_game() # 게임 상태 초기화 함수 호출
        st.rerun()                 # 스크립트를 다시 실행하여 화면을 즉시 새로고침

with col2:
    # 모든 문제를 다 뽑았는지 확인하여 버튼을 비활성화(disabled)할지 결정합니다.
    is_disabled = (st.session_state.draw_count >= st.session_state.total_problems)
    
    # '다음 문제 뽑기' 버튼입니다.
    if st.button("➡️ 다음 문제 뽑기", disabled=is_disabled, width='stretch'):
        # 뽑을 문제가 남아있는 경우에만 실행됩니다.
        if st.session_state.problem_pool:
            st.session_state.draw_count += 1
            new_problem = st.session_state.problem_pool.pop() # 문제 리스트에서 하나를 뽑아냅니다.
            st.session_state.current_problem = new_problem      # 현재 문제로 설정
            st.session_state.drawn_history.append(new_problem)  # 뽑은 내역에 추가

# --- 문제 표시 영역 ---

# 게임의 진행 상태에 따라 다른 헤더 메시지를 보여줍니다.
if st.session_state.draw_count == 0:
    st.header("첫 번째 문제를 뽑아주세요.")
elif st.session_state.draw_count >= st.session_state.total_problems:
    st.header("🏁 모든 문제를 다 뽑았습니다! 🏁")
else:
    st.header(f"{st.session_state.draw_count}번째 문제")

# 현재 뽑힌 문제를 화면 중앙에 크게 표시합니다.
if st.session_state.current_problem == "❔":
    # 아직 문제를 뽑기 전이면 큰 물음표를 보여줍니다.
    st.markdown("<p style='text-align: center; font-size: 150px; font-weight: bold;'>❔</p>", unsafe_allow_html=True)
else:
    # 문제를 뽑았다면, st.latex를 사용하여 수학 수식을 아름답게 렌더링합니다.
    st.latex(st.session_state.current_problem)

st.divider() # 가로선

# --- 뽑은 내역 표시 영역 ---

history_title = "**※ 지금까지 뽑은 문제들:**"
if st.session_state.drawn_history:
    # 뽑은 내역을 세로로 나열합니다. 각 항목을 인라인 수식으로 감싸고
    # Markdown 리스트 형태로 만들면 한 항목씩 세로로 표시됩니다.
    history_values = "\n\n".join([f"- ${p}$" for p in st.session_state.drawn_history])
else:
    history_values = "아직 뽑은 문제가 없습니다."

# st.info를 사용하여 깔끔한 정보 상자 안에 뽑은 내역을 보여줍니다.
st.info(f"{history_title}\n\n{history_values}")