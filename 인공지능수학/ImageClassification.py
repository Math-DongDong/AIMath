import streamlit as st
from streamlit_drawable_canvas import st_canvas
import cv2
import numpy as np
import tensorflow as tf # 데이터셋 로드용

# 2. [데이터 로드] MNIST 데이터셋 캐싱 (모델 파일 대신 원본 데이터 사용)
@st.cache_data(show_spinner="MNIST 데이터셋을 다운로드 및 로드 중입니다... (시간이 걸릴 수 있습니다)",ttl=120)
def load_mnist_data():
    # Keras를 통해 MNIST 데이터 다운로드
    (x_train, y_train), _ = tf.keras.datasets.mnist.load_data()
    
    # 해밍 거리는 0과 1의 이진 데이터 비교이므로 이진화(Binarization) 수행
    # 픽셀값(0~255) -> 127보다 크면 1, 아니면 0
    x_train_bin = np.where(x_train > 127, 1, 0).astype(np.uint8)
    
    # 계산을 위해 1줄로 쫙 폅니다 (Flatten): (60000, 28, 28) -> (60000, 784)
    x_train_flat = x_train_bin.reshape(x_train_bin.shape[0], -1)
    
    return x_train, x_train_flat, y_train

# 데이터 로드 실행
try:
    # 원본이미지(시각화용), 이진화된벡터(계산용), 정답라벨
    original_images, binary_vectors, labels = load_mnist_data()
except Exception as e:
    st.error(f"데이터 로드 중 오류 발생: {e}")
    st.stop()

# 3. [UI] 헤더 및 캔버스 설정
st.title('해밍거리를 이용한 이미지 데이터의 분류')
CANVAS_SIZE = 280 # 캔버스 크기 조금 키움

col1, sub_c1, sub_c2 = st.columns(3)
with col1:
    st.subheader("✍️ 숫자를 그려보세요")
    canvas = st_canvas(
        fill_color='#000000',
        stroke_width=20,
        stroke_color='#FFFFFF',
        background_color='#000000',
        width=CANVAS_SIZE,
        height=CANVAS_SIZE,
        drawing_mode='freedraw',
        key='canvas'
    )

# 4. [로직] 이미지 처리 및 해밍 거리 계산
if canvas.image_data is not None:
    # (1) 입력 이미지 전처리
    img = canvas.image_data.astype(np.uint8)
    
    # 28x28 리사이징 (MNIST 규격)
    img_resized = cv2.resize(img, dsize=(28, 28))
    
    # 미리보기 이미지 생성 (확대)
    preview_img = cv2.resize(img_resized, dsize=(CANVAS_SIZE, CANVAS_SIZE), interpolation=cv2.INTER_NEAREST)

    # Grayscale 변환 및 이진화 (Binarization)
    img_gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    
    # 사용자가 그린 그림도 0과 1로 변환
    img_bin = np.where(img_gray > 127, 1, 0).astype(np.uint8)
    img_flat = img_bin.flatten() # (784, ) 형태로 변환

    # (2) 해밍 거리 계산 (Hamming Distance)
    # 캔버스에 그림이 그려졌을 때만 계산 (검은색 0만 있는 경우 제외)
    if np.sum(img_flat) > 0:
        with st.spinner("비슷한 숫자를 찾는 중입니다..."):
            
            # [핵심 로직] 전체 데이터(60,000개)와 내 그림의 차이 계산
            # XOR 연산(다르면 1, 같으면 0) 후 합계 구하기 = 해밍 거리
            # numpy 브로드캐스팅을 이용해 6만개를 한 번에 계산 -> 매우 빠름
            hamming_distances = np.sum(binary_vectors != img_flat, axis=1)
            
            # 거리가 가장 작은 순서대로 인덱스 정렬 (Top 10)
            # argsort는 정렬된 값의 '인덱스'를 반환합니다.
            sorted_indices = np.argsort(hamming_distances)[:10]
            
            # 가장 가까운 데이터 정보
            best_match_idx = sorted_indices[0]
            best_match_label = labels[best_match_idx]
            min_dist = hamming_distances[best_match_idx]

        # (3) 결과 출력
            with sub_c1:
                st.subheader("내가 그린 숫자")
                st.image(preview_img, caption="해상도: 28x28", width=280)
            with sub_c2:
                st.subheader("가장 비슷한 숫자")
                # 원본 데이터셋에서 해당 인덱스의 이미지를 가져옴
                st.image(original_images[best_match_idx], caption=f"숫자: {best_match_label}, 해밍거리: {min_dist}", width=280)

        st.divider()

        # (4) Top 10 유사 데이터 시각화
        st.subheader("🏆 해밍 거리가 가장 가까운 Top 10")

        # 5개씩 2줄로 보여주기
        cols_top = st.columns(5)
        cols_bottom = st.columns(5)
        all_cols = cols_top + cols_bottom

        for i, idx in enumerate(sorted_indices):
            label = labels[idx]
            dist = hamming_distances[idx]
            img_data = original_images[idx]
            
            with all_cols[i]:
                st.image(img_data, width=80)
                st.markdown(f"**{label}** <span style='color:gray; font-size:12px'>(거리:{dist})</span>", unsafe_allow_html=True)

