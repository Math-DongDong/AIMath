
import streamlit as st
import pandas as pd
import numpy as np
import string
import os
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

st.title("🏗️ 원자력 발전소 기중기의 이동 경로 최적화")

# 탭 생성
tab1, tab2 = st.tabs(["🚚 외판원 문제 ", "🏗️ 원자력 발전소 기중기의 이동 경로"])

# -----------------------------------------------------------
# [Tab 1] 외판원 문제 (수정 없음)
# -----------------------------------------------------------
with tab1:
    # -----------------------------------------------------------
    # TSP 알고리즘 함수 (Tab 1 전용)
    # -----------------------------------------------------------
    def solve_tsp_and_display_tab1(distance_matrix, city_names):
        distance_matrix = np.asarray(distance_matrix, dtype=int)
        
        data = {
            "distance_matrix": distance_matrix,
            "num_vehicles": 1,
            "depot": 0,
        }

        manager = pywrapcp.RoutingIndexManager(
            len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
        )
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data["distance_matrix"][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )

        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            index = routing.Start(0)
            route_path = []
            while not routing.IsEnd(index):
                from_node = manager.IndexToNode(index)
                route_path.append(city_names[from_node])
                index = solution.Value(routing.NextVar(index))
            last_node = manager.IndexToNode(index)
            route_path.append(city_names[last_node])
            
            total_distance = solution.ObjectiveValue()

            st.subheader("📍 **최적 이동 경로**")
            st.code(" -> ".join(route_path), language="text")
            st.metric(label="총 이동 거리", value=total_distance)
        else:
            st.error("해를 찾지 못했습니다. 입력된 가중치행렬을 다시 확인해주세요.")

    # -----------------------------------------------------------
    # UI Layout (Tab 1)
    # -----------------------------------------------------------
    NUM_CITIES = 4
    CITY_NAMES = list(string.ascii_uppercase)[:NUM_CITIES]

    col_img, col_input = st.columns([1, 1])

    with col_img:
        st.subheader("1. 가중 그래프")
        image_path = "./기타/외판원_문제.jpg"
        if os.path.exists(image_path):
            st.image(image_path, width='stretch')
        else:
            st.warning("이미지 파일을 찾을 수 없습니다.")

    with col_input:
        header_col, btn_col = st.columns([7, 3])
        with header_col:
            st.subheader("2. 가중치행렬")
        with btn_col:
            run_btn = st.button("🚀 경로 계산하기", type="primary", width='stretch')

        st.caption(f"{NUM_CITIES}개의 도시 A, B, C, D 간의 거리를 입력해주세요.")

        if "matrix_df" not in st.session_state:
            default_matrix = np.zeros((NUM_CITIES, NUM_CITIES), dtype=int)
            st.session_state.matrix_df = pd.DataFrame(
                default_matrix, 
                columns=CITY_NAMES, 
                index=CITY_NAMES
            )

        edited_df = st.data_editor(
            st.session_state.matrix_df,
            key="editor_tab1",
            width='stretch',
            height=178,      
            num_rows="fixed" 
        )
        
        distance_matrix_input = edited_df.to_numpy()

        if run_btn:
            if np.any(np.diag(distance_matrix_input) != 0):
                st.warning("⚠️ 주의: 자기 자신으로의 거리(대각성분)가 0이 아닙니다.")
            with st.spinner("계산 중..."):
                solve_tsp_and_display_tab1(distance_matrix_input, CITY_NAMES)


# -----------------------------------------------------------
# [Tab 2] 원자력 발전소 기중기 이동 경로 (10x10 수정됨)
# -----------------------------------------------------------
with tab2:
    # -------------------------------------------------------
    # 상수 설정: 10행 10열 (A1~A5, B1~B5)
    # -------------------------------------------------------
    NUM_ROWS_2 = 10
    
    # 라벨 생성 로직: 앞 5개는 A, 뒤 5개는 B
    LABEL_PART_A = [f"A{i+1}" for i in range(5)]
    LABEL_PART_B = [f"B{i+1}" for i in range(5)]
    
    # 행과 열 모두 동일한 라벨 적용 (거리 행렬이므로)
    ALL_LABELS = LABEL_PART_A + LABEL_PART_B # ['A1',...,'A5', 'B1',...,'B5']
    
    ROW_LABELS = ALL_LABELS
    COL_LABELS = ALL_LABELS

    # 레이아웃 분할
    t2_col_left, t2_col_right = st.columns([1, 1])

    # -------------------------------------------------------
    # 왼쪽 열: 변수 입력 + (결과 표시 영역)
    # -------------------------------------------------------
    with t2_col_left:
        st.subheader("1. 입력 설정")
        st.markdown("""
        **입력 가이드:**
        - 행렬의 각 성분에 **숫자**, **수식**, **변수**(m)를 입력할 수 있습니다.
        - 예: `np.sqrt(2)`, `10 + 5`, `m * 2` , `m`
        """)
        
        # 변수 m 입력 받기
        st.write("🔽 **변수 설정**")
        m_input_str = st.text_input("m =", value="", key="m_input", placeholder="비어있으면 0으로 처리됩니다.")
        
        # 결과가 표시될 컨테이너
        result_container = st.container()

    # -------------------------------------------------------
    # 오른쪽 열: 행렬 입력 + 버튼 + (변환된 행렬 표시)
    # -------------------------------------------------------
    with t2_col_right:
        # 헤더와 버튼 배치
        h_col_2, b_col_2 = st.columns([7, 3])
        with h_col_2:
            st.subheader("2. 가중치행렬")
        with b_col_2:
            run_btn_2 = st.button("🚀 경로 계산하기", key="btn_tab2", type="primary", width='stretch')

        st.caption("행렬 성분에 `np.sqrt(2)` 또는 `m` 같은 수식이나 변수를 입력할 수 있습니다.")

        # 데이터프레임 초기화
        if "matrix_df_2_v2" not in st.session_state: # 키 이름 변경하여 초기화 유도
            # 10x10 초기값 "0"
            default_data_2 = [["0" for _ in range(NUM_ROWS_2)] for _ in range(NUM_ROWS_2)]
            st.session_state.matrix_df_2_v2 = pd.DataFrame(
                default_data_2, 
                index=ROW_LABELS, 
                columns=COL_LABELS
            )

        # 행렬 에디터
        # 높이 조절: 10줄이므로 약 400px 정도로 설정
        edited_df_2 = st.data_editor(
            st.session_state.matrix_df_2_v2,
            key="editor_tab2_v2",
            width='stretch',
            height=400, 
            num_rows="fixed"
        )
        
        # -------------------------------------------------------
        # 계산 로직
        # -------------------------------------------------------
        if run_btn_2:
            # 1. m 변수 파싱 (비어있거나 에러 시 0 처리)
            try:
                if m_input_str.strip() == "":
                    m_val = 0.0
                else:
                    m_val = float(m_input_str)
            except ValueError:
                m_val = 0.0

            # 2. 행렬 수식 파싱
            eval_ctx = {"np": np, "sqrt": np.sqrt, "m": m_val, "__builtins__": {}}
            final_matrix = np.zeros((NUM_ROWS_2, NUM_ROWS_2), dtype=float)
            
            parse_error = False
            for r in range(NUM_ROWS_2):
                for c in range(NUM_ROWS_2):
                    cell_val = str(edited_df_2.iloc[r, c])
                    try:
                        calc_val = eval(cell_val, eval_ctx)
                        final_matrix[r, c] = float(calc_val)
                    except Exception as e:
                        st.error(f"수식 오류 ({ROW_LABELS[r]}, {COL_LABELS[c]}): {e}")
                        parse_error = True
            
            # 파싱 성공 시 TSP 수행
            if not parse_error:
                # 스케일링/정수변환 없이 Float 그대로 전달 (경고 무시)
                data = {
                    "distance_matrix": final_matrix, 
                    "num_vehicles": 1,
                    "depot": 0,
                }
                
                # 솔버 초기화
                manager = pywrapcp.RoutingIndexManager(len(final_matrix), 1, 0)
                routing = pywrapcp.RoutingModel(manager)

                def distance_callback_2(from_idx, to_idx):
                    from_n = manager.IndexToNode(from_idx)
                    to_n = manager.IndexToNode(to_idx)
                    return data["distance_matrix"][from_n][to_n]

                transit_idx = routing.RegisterTransitCallback(distance_callback_2)
                routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)

                search_params = pywrapcp.DefaultRoutingSearchParameters()
                search_params.first_solution_strategy = (
                    routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
                )

                solution = routing.SolveWithParameters(search_params)

                # 결과 출력
                if solution:
                    index = routing.Start(0)
                    route_path = []
                    while not routing.IsEnd(index):
                        node_idx = manager.IndexToNode(index)
                        route_path.append(ROW_LABELS[node_idx])
                        index = solution.Value(routing.NextVar(index))
                    route_path.append(ROW_LABELS[manager.IndexToNode(index)])
                    
                    total_dist = solution.ObjectiveValue()

                    with result_container:
                        st.subheader("📍 최적 이동 경로")
                        st.code(" -> ".join(route_path), language="text")
                        
                        st.metric("총 이동 비용", total_dist)
                        

                    st.caption("가중치행렬 수식 변환 결과")
                    st.dataframe(
                        pd.DataFrame(final_matrix, index=ROW_LABELS, columns=COL_LABELS),
                        width='stretch'
                    )
                else:
                    st.error("해를 찾을 수 없습니다.")
                
