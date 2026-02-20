import streamlit as st
import numpy as np
import pandas as pd
import streamlit.components.v1 as components
from PIL import Image
import io 

# --- 앱 제목 ---
st.title("이미지 데이터의 표현")

# 탭 생성
tab1, tab2, tab3= st.tabs(["🖼️ 이미지 해상도", "⚫ 흑백 이미지", "🎨 컬러 이미지"])
with tab1:
    #================================================================================================
    # 업로드된 파일을 PIL 이미지 객체로 변환
    @st.cache_data(show_spinner=False,ttl=300)
    def load_image(image_file):
        return Image.open(image_file)

    # 해상도 변환 프레그먼트
    @st.fragment
    def image_editor_fragment(image, original_width, original_height, filename):
        # [설정 / 변환 결과 / 원본]
        edit,result , original = st.columns([0.2, 0.4, 0.4])
        with edit:
            st.subheader("해상도 설정")
            new_width = st.number_input(
                "가로(Width) 픽셀", 
                min_value=1, 
                value=original_width, 
                step=1
            )
            new_height = st.number_input(
                "세로(Height) 픽셀", 
                min_value=1, 
                value=original_height, 
                step=1
            )

            # 이미지 처리 (NEAREST) - 픽셀화 효과를 준 이후 원본사이즈로 확대 후 다시 픽셀화
            pixelated_image = image.resize((new_width, new_height), Image.Resampling.NEAREST)
            preview_image = pixelated_image.resize((original_width, original_height), Image.Resampling.NEAREST)
            
            # 다운로드 로직
            buf = io.BytesIO()
            img_format = image.format if image.format else "PNG"
            pixelated_image.save(buf, format=img_format)
            byte_im = buf.getvalue()

            st.download_button(
                label="💾 변환된 이미지 다운로드",
                data=byte_im,
                file_name=f"pixelated_{filename}",
                mime=f"image/{img_format.lower()}",
                width='stretch'
            )

        with result:
            st.subheader("변환 이미지")
            st.image(preview_image, caption=f"변경됨: {new_width} x {new_height} px", width='stretch')

        with original:
            st.subheader("원본 이미지")
            st.image(image, caption=f"원본: {original_width} x {original_height} px", width='stretch')

    #================================================================================================
    with st.expander("📂 이미지 업로드 열기/닫기", expanded=True):
        # 1. 이미지 업로드 기능
        uploaded_file = st.file_uploader("이미지 파일을 업로드하세요.", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = load_image(uploaded_file)
        
        # 원본 이미지 정보 가져오기
        original_width, original_height = image.size

        # 이미지 편집 프레그먼트 호출
        image_editor_fragment(image, original_width, original_height, uploaded_file.name)            
                
    else:
        st.info("👆 상단의 '이미지 업로드'를 열어 이미지 파일( png, jpg, jpeg )을 먼저 업로드해주세요.")            

with tab2:
    html_code = """
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
            <script src="https://cdn.tailwindcss.com"></script>
            <style>
                /* CSS 애니메이션 */
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(-5px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .animate-fade-in {
                    animation: fadeIn 0.3s ease-out forwards;
                }

                /* [핵심 수정 1] 호버 효과 제한 */
                /* 마우스가 있는 장치(PC 등)에서만 호버 효과 적용 */
                @media (hover: hover) {
                    .grid-cell:hover {
                        background-color: #f3f4f6; /* Tailwind gray-100 */
                    }
                }

                /* [핵심 수정 2] 모바일 터치 최적화 클래스 */
                .grid-cell {
                    touch-action: manipulation; /* 더블탭 줌 방지 -> 즉시 반응 */
                    -webkit-tap-highlight-color: transparent; /* 모바일 터치 시 파란 박스 제거 */
                }

                /* 모바일에서 눌렀을 때(Active) 즉각적인 피드백 */
                .grid-cell:active {
                    background-color: #e5e7eb; /* Tailwind gray-200 */
                }
            </style>
        </head>
        <body class="bg-white font-sans text-gray-800">

            <div class="w-full px-4 py-6">
                
                <!-- 그리드 레이아웃 -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 items-start">
                    
                    <!-- [왼쪽] 입력 섹션 -->
                    <div class="flex flex-col w-full">
                        <div class="mb-2 flex items-center gap-2">
                            <span class="bg-blue-100 text-blue-800 text-xs font-bold px-2 py-1 rounded">Step 1</span> 
                            <span class="font-bold text-gray-700">그림 그리기</span>
                        </div>

                        <div class="flex flex-wrap items-center gap-3 mb-4 p-3 rounded">
                            <div class="flex items-center gap-2">
                                <label class="text-sm font-medium text-gray-600">가로 픽셀</label>
                                <input type="number" id="cols" value="7" min="1" max="10" class="w-12 p-1 border border-gray-300 rounded text-center focus:outline-none focus:border-blue-500 text-sm">
                            </div>
                            <div class="flex items-center gap-2">
                                <label class="text-sm font-medium text-gray-600">세로 픽셀</label>
                                <input type="number" id="rows" value="7" min="1" max="10" class="w-12 p-1 border border-gray-300 rounded text-center focus:outline-none focus:border-blue-500 text-sm">
                            </div>
                            <button id="create-btn" class="ml-auto bg-blue-600 hover:bg-blue-700 text-white font-bold py-1.5 px-3 rounded text-sm whitespace-nowrap">
                                새로 만들기
                            </button>
                        </div>

                        <div id="grid-container" class="flex justify-center p-4 border border-dashed border-gray-300 rounded">
                            <!-- JS로 생성됨 -->
                        </div>
                    </div>

                    <!-- [오른쪽] 결과 섹션 -->
                    <div class="flex flex-col w-full h-full">
                        <div class="mb-2 flex items-center gap-2">
                            <span class="bg-green-100 text-green-800 text-xs font-bold px-2 py-1 rounded">Step 2</span>
                            <span class="font-bold text-gray-700">행렬 표현</span>
                        </div>

                        <div class="flex items-center mb-4 p-3 h-[58px] sm:h-auto border border-transparent"> 
                            <button id="show-matrix-btn" class="w-full bg-gray-800 hover:bg-gray-900 text-white font-bold py-1.5 px-4 rounded text-sm flex items-center justify-center gap-2">
                                행렬 변환 결과 보기
                            </button>
                        </div>

                        <div class="w-full flex flex-col items-center justify-center bg-gray-50 border border-gray-200 rounded p-4 min-h-[300px] lg:h-[calc(100%-74px)]">
                            <div id="matrix-output" class="hidden flex flex-col items-center animate-fade-in w-full overflow-x-auto">
                                <div id="matrix-table-wrapper" class="p-2 bg-white rounded border border-gray-200 inline-block"></div>
                            </div>
                            <div id="placeholder-text" class="text-gray-400 text-sm text-center">
                                버튼을 누르면 행렬이 표시됩니다.
                            </div>
                        </div>
                    </div>

                </div> 
            </div>

            <script>
                document.addEventListener('DOMContentLoaded', () => {
                    const rowsInput = document.getElementById('rows');
                    const colsInput = document.getElementById('cols');
                    const createBtn = document.getElementById('create-btn');
                    const showMatrixBtn = document.getElementById('show-matrix-btn');
                    const gridContainer = document.getElementById('grid-container');
                    
                    const outputContainer = document.getElementById('matrix-output');
                    const outputWrapper = document.getElementById('matrix-table-wrapper');
                    const placeholderText = document.getElementById('placeholder-text');
                    
                    const blackCellClass = '!bg-gray-800'; // !important 효과를 위해 ! 추가 (Tailwind)

                    function createGrid() {
                        const rows = parseInt(rowsInput.value, 10);
                        const cols = parseInt(colsInput.value, 10);

                        if (isNaN(rows) || isNaN(cols) || rows <= 0 || cols <= 0) {
                            alert('1부터 10까지의 자연수를 입력해주세요.');
                            return;
                        }
                        if (rows > 10 || cols > 10) {
                            alert('가로와 세로 픽셀은 최대 10까지만 가능합니다.');
                            return;
                        }

                        gridContainer.innerHTML = '';
                        outputContainer.classList.add('hidden'); 
                        placeholderText.style.display = 'block';
                        outputWrapper.innerHTML = '';

                        const table = document.createElement('table');
                        table.className = 'border-collapse shadow-sm bg-white select-none';
                        
                        for (let r = 0; r < rows; r++) {
                            const tr = document.createElement('tr');
                            for (let c = 0; c < cols; c++) {
                                const td = document.createElement('td');
                                
                                // [수정됨] 클래스 적용: grid-cell(터치최적화) 추가, transition 제거(즉시반응)
                                // hover:bg-gray-100 제거 -> CSS @media 쿼리로 대체
                                td.className = 'grid-cell w-10 h-10 sm:w-12 sm:h-12 border border-gray-300 cursor-pointer';
                                
                                tr.appendChild(td);
                            }
                            table.appendChild(tr);
                        }
                        gridContainer.appendChild(table);
                    }

                    function showMatrix() {
                        const sourceTable = gridContainer.querySelector('table');
                        if (!sourceTable) {
                            alert("먼저 표를 만들어주세요.");
                            return;
                        }

                        outputWrapper.innerHTML = '';
                        outputContainer.classList.remove('hidden');
                        placeholderText.style.display = 'none';

                        const resultTable = document.createElement('table');
                        resultTable.className = 'border-collapse border border-gray-300';

                        for (let r = 0; r < sourceTable.rows.length; r++) {
                            const resultTr = document.createElement('tr');
                            
                            for (let c = 0; c < sourceTable.rows[r].cells.length; c++) {
                                const sourceCell = sourceTable.rows[r].cells[c];
                                const isBlack = sourceCell.classList.contains('!bg-gray-800'); // 클래스명 확인 수정
                                const value = isBlack ? 1 : 0;

                                const resultTd = document.createElement('td');
                                resultTd.textContent = value;
                                
                                let cellClass = 'w-10 h-10 sm:w-12 sm:h-12 text-center border border-gray-300 text-sm font-mono cursor-default ';
                                
                                if (value === 1) {
                                    cellClass += 'bg-gray-800 text-white font-bold';
                                } else {
                                    cellClass += 'bg-white text-gray-400';
                                }
                                
                                resultTd.className = cellClass;
                                resultTr.appendChild(resultTd);
                            }
                            resultTable.appendChild(resultTr);
                        }

                        outputWrapper.appendChild(resultTable);
                        
                        if (window.innerWidth < 1024) {
                            outputContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                        }
                    }
                    
                    function handleGridClick(e) {
                        // grid-cell 클래스를 가진 요소인지 확인
                        if (e.target.classList.contains('grid-cell')) {
                            e.target.classList.toggle('!bg-gray-800');
                        }
                    }

                    createBtn.addEventListener('click', createGrid);
                    showMatrixBtn.addEventListener('click', showMatrix);
                    gridContainer.addEventListener('click', handleGridClick);

                    createGrid();
                });
            </script>
        </body>
        </html>
    """

    # HTML 컴포넌트 렌더링
    components.html(html_code, height=800, scrolling=True)

with tab3:
    html_code2 = """
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <script src="https://cdn.tailwindcss.com"></script>
            <style>
                /* 숫자 입력 화살표 제거 */
                input[type=number]::-webkit-inner-spin-button, 
                input[type=number]::-webkit-outer-spin-button { 
                    -webkit-appearance: none; 
                    margin: 0; 
                }
            </style>
        </head>
        <body class="bg-white font-sans text-gray-800">

            <div class="w-full px-4 py-6">
                
                <!-- 컨트롤 패널 -->
                <div class="flex flex-col items-center mb-8">
                    
                    <!-- 설정 박스 -->
                    <div class="flex flex-col md:flex-row items-start md:items-center gap-4 p-4 w-full">
                        <!-- 왼쪽 그룹: 크기 입력 + 초기화 -->
                        <div class="flex flex-wrap items-center gap-2 w-full md:w-auto">
                            <div class="flex items-center gap-2">
                                <label class="text-sm font-medium text-gray-600">가로 픽셀</label>
                                <input type="number" id="cols" value="4" min="1" max="11" class="w-12 p-2 border border-gray-300 rounded text-center focus:outline-none focus:border-blue-500 text-sm">
                            </div>
                            <div class="flex items-center gap-2">
                                <label class="text-sm font-medium text-gray-600">세로 픽셀</label>
                                <input type="number" id="rows" value="4" min="1" max="11" class="w-12 p-2 border border-gray-300 rounded text-center focus:outline-none focus:border-blue-500 text-sm">
                            </div>

                            <button id="create-btn" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-5 rounded text-sm shadow transition-colors">
                                새로 만들기
                            </button>
                        </div>

                        <!-- spacer to push the right-group to the far right -->
                        <div class="hidden md:flex flex-1"></div>

                        <!-- 오른쪽 그룹: 클릭값 + 이미지 변환 -->
                        <div class="flex items-center gap-2 w-full md:w-auto">
                            <div class="flex items-center gap-2 bg-purple-50 px-3 py-1.5 rounded border border-purple-100">
                                <span class="text-lg">🖌️</span>
                                <label class="text-sm font-bold text-purple-700">클릭 값</label>
                                <input type="number" id="paint-val" value="255" min="0" max="255" class="w-14 p-2 border border-purple-300 rounded text-center text-purple-700 font-bold focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm" title="칸을 클릭할 때 이 값이 입력됩니다.">
                            </div>

                            <button id="merge-btn" class="bg-gray-800 hover:bg-black text-white text-sm font-bold py-2 px-4 rounded-lg shadow-lg transform transition active:scale-95 whitespace-nowrap">
                                이미지 변환
                            </button>
                        </div>
                    </div>
                </div>

                <!-- 메인 워크스페이스 -->
                <div class="flex flex-col sm:flex-row items-start gap-6 lg:gap-10">
                    
                    <!-- [입력 영역] -->
                    <div class="flex flex-col sm:flex-row gap-6">
                        
                        <!-- Red Channel -->
                        <div class="flex flex-col items-center group w-full sm:w-auto">
                            <div class="text-red-600 font-bold mb-2 text-sm bg-red-50 px-3 py-1 rounded border border-red-100">R (Red)</div>
                            <div id="container-r" class="border-2 border-red-100 rounded p-1 bg-white shadow-sm group-hover:border-red-300 transition-colors"></div>
                        </div>

                        <!-- Green Channel -->
                        <div class="flex flex-col items-center group w-full sm:w-auto">
                            <div class="text-green-600 font-bold mb-2 text-sm bg-green-50 px-3 py-1 rounded border border-green-100">G (Green)</div>
                            <div id="container-g" class="border-2 border-green-100 rounded p-1 bg-white shadow-sm group-hover:border-green-300 transition-colors"></div>
                        </div>

                        <!-- Blue Channel -->
                        <div class="flex flex-col items-center group w-full sm:w-auto">
                            <div class="text-blue-600 font-bold mb-2 text-sm bg-blue-50 px-3 py-1 rounded border border-blue-100">B (Blue)</div>
                            <div id="container-b" class="border-2 border-blue-100 rounded p-1 bg-white shadow-sm group-hover:border-blue-300 transition-colors"></div>
                        </div>
                    </div>

                    <!-- [합성 액션] -->
                    <!-- 제거: 버튼을 상단 컨트롤 박스에 통합하여 동일 행의 우측에 배치함 -->

                    <!-- [결과 영역] -->
                    <div class="flex flex-col items-center">
                        <div class="text-gray-800 font-bold mb-2 text-sm bg-gray-100 px-3 py-1 rounded border border-gray-200">Result (Image)</div>
                        
                        <div id="container-result" class="border border-gray-300 rounded p-1 bg-white shadow-md min-w-[120px] min-h-[120px] flex items-center justify-center relative">
                            <span class="text-xs text-gray-400">결과 대기 중</span>
                        </div>
                        
                        <!-- 안내 문구 (요청사항 반영) -->
                        <div class="mt-3 text-center">

                            <div id="pixel-info" class="text-xs font-bold mt-2 h-4 text-gray-700"></div>
                        </div>
                    </div>

                </div>
            </div>

            <script>
                document.addEventListener('DOMContentLoaded', () => {
                    const rowsInput = document.getElementById('rows');
                    const colsInput = document.getElementById('cols');
                    const paintValInput = document.getElementById('paint-val'); // 브러시 값 입력창
                    
                    const createBtn = document.getElementById('create-btn');
                    const mergeBtn = document.getElementById('merge-btn');
                    
                    const containerR = document.getElementById('container-r');
                    const containerG = document.getElementById('container-g');
                    const containerB = document.getElementById('container-b');
                    const containerResult = document.getElementById('container-result');
                    const pixelInfo = document.getElementById('pixel-info');

                    // 초기 실행
                    createAllGrids();

                    createBtn.addEventListener('click', createAllGrids);
                    mergeBtn.addEventListener('click', updateResultImage);

                    // 브러시 값 범위 체크
                    paintValInput.addEventListener('change', function() {
                        let val = parseInt(this.value);
                        if (val < 0) this.value = 0;
                        if (val > 255) this.value = 255;
                    });

                    function createAllGrids() {
                        const rows = parseInt(rowsInput.value, 10);
                        const cols = parseInt(colsInput.value, 10);

                        if (rows > 11 || cols > 11) {
                            alert('가로와 세로 픽셀은 최대 11까지만 가능합니다.');
                            return;
                        }
                        if (rows < 1 || cols < 1) {
                            alert('1부터 11까지의 자연수를 입력해주세요.');
                            return;
                        }

                        // 입력 테이블 생성 (초기값 0으로 통일하여 깔끔하게 시작)
                        createInputTable(containerR, rows, cols, 'red');
                        createInputTable(containerG, rows, cols, 'green');
                        createInputTable(containerB, rows, cols, 'blue');

                        // 결과창 초기화
                        containerResult.innerHTML = '';
                        createResultPlaceholder(rows, cols);
                        pixelInfo.innerText = '';
                    }

                    function createInputTable(container, rows, cols, colorTheme) {
                        container.innerHTML = '';
                        const table = document.createElement('table');
                        table.className = 'border-collapse';
                        // Make table responsive: width fills container and uses fixed layout
                        table.style.width = '100%';
                        table.style.tableLayout = 'fixed';

                        let inputStyleClass = '';
                        if (colorTheme === 'red') inputStyleClass = 'focus:border-red-500 text-red-700 selection:bg-red-200';
                        else if (colorTheme === 'green') inputStyleClass = 'focus:border-green-500 text-green-700 selection:bg-green-200';
                        else if (colorTheme === 'blue') inputStyleClass = 'focus:border-blue-500 text-blue-700 selection:bg-blue-200';

                        for (let r = 0; r < rows; r++) {
                            const tr = document.createElement('tr');
                            for (let c = 0; c < cols; c++) {
                                const td = document.createElement('td');
                                td.className = 'border border-gray-200 p-0.5';
                                td.style.width = `calc(100% / ${cols})`;

                                // Create a square container using the padding-top trick so height follows width
                                const square = document.createElement('div');
                                square.style.position = 'relative';
                                square.style.width = '100%';
                                square.style.paddingTop = '100%';

                                const input = document.createElement('input');
                                input.type = 'number';
                                input.min = 0;
                                input.max = 255;
                                input.placeholder = "0"; // 빈 칸일 때 0처럼 보이게 힌트
                                // absolutely position the input to fill the square
                                input.style.position = 'absolute';
                                input.style.top = '0';
                                input.style.left = '0';
                                input.style.width = '100%';
                                input.style.height = '100%';
                                input.style.boxSizing = 'border-box';
                                input.className = `text-center text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-opacity-50 font-mono transition-all ${inputStyleClass}`;
                                
                                // [핵심 기능] 클릭 시 '클릭 값'으로 자동 채우기
                                input.addEventListener('click', function() {
                                    const brushValue = paintValInput.value;
                                    // 값이 비어있거나 다를 때만 변경 (사용자 경험 고려)
                                    // 혹은 무조건 변경을 원하면 조건문 제거 가능. 여기선 무조건 변경.
                                    this.value = brushValue;
                                    
                                    // 클릭할 때 시각적 피드백 (반짝임)
                                    this.classList.add('bg-gray-100');
                                    setTimeout(() => this.classList.remove('bg-gray-100'), 150);
                                });

                                // 수동 입력 시 범위 제한
                                input.addEventListener('input', function() {
                                    if (this.value === '') return;
                                    let val = parseInt(this.value);
                                    if (val < 0) this.value = 0;
                                    if (val > 255) this.value = 255;
                                });

                                square.appendChild(input);
                                td.appendChild(square);
                                tr.appendChild(td);
                            }
                            table.appendChild(tr);
                        }
                        container.appendChild(table);
                    }

                    function createResultPlaceholder(rows, cols) {
                        const table = document.createElement('table');
                        table.className = 'border-collapse';
                        table.style.width = '100%';
                        table.style.tableLayout = 'fixed';
                        for (let r = 0; r < rows; r++) {
                            const tr = document.createElement('tr');
                            for (let c = 0; c < cols; c++) {
                                const td = document.createElement('td');
                                td.className = 'border border-gray-300 bg-gray-50 p-0'; 
                                td.style.width = `calc(100% / ${cols})`;
                                const square = document.createElement('div');
                                square.style.position = 'relative';
                                square.style.width = '100%';
                                square.style.paddingTop = '100%';

                                const inner = document.createElement('div');
                                inner.style.position = 'absolute';
                                inner.style.top = '0';
                                inner.style.left = '0';
                                inner.style.width = '100%';
                                inner.style.height = '100%';
                                inner.className = 'bg-gray-50';
                                square.appendChild(inner);
                                td.appendChild(square);
                                tr.appendChild(td);
                            }
                            table.appendChild(tr);
                        }
                        containerResult.appendChild(table);
                    }

                    function updateResultImage() {
                        const rows = parseInt(rowsInput.value);
                        const cols = parseInt(colsInput.value);

                        const inputsR = containerR.querySelectorAll('input');
                        const inputsG = containerG.querySelectorAll('input');
                        const inputsB = containerB.querySelectorAll('input');

                        containerResult.innerHTML = '';
                        const table = document.createElement('table');
                        table.className = 'border-collapse cursor-crosshair'; 
                        table.style.width = '100%';
                        table.style.tableLayout = 'fixed';

                        let index = 0;
                        for (let r = 0; r < rows; r++) {
                            const tr = document.createElement('tr');
                            for (let c = 0; c < cols; c++) {
                                const td = document.createElement('td');
                                
                                // 값이 비어있으면 0으로 처리 (|| 0)
                                const rVal = inputsR[index].value === '' ? 0 : parseInt(inputsR[index].value);
                                const gVal = inputsG[index].value === '' ? 0 : parseInt(inputsG[index].value);
                                const bVal = inputsB[index].value === '' ? 0 : parseInt(inputsB[index].value);

                                td.className = 'border border-gray-300 transition-colors duration-300 p-0';
                                td.style.width = `calc(100% / ${cols})`;

                                const square = document.createElement('div');
                                square.style.position = 'relative';
                                square.style.width = '100%';
                                square.style.paddingTop = '100%';

                                const inner = document.createElement('div');
                                inner.style.position = 'absolute';
                                inner.style.top = '0';
                                inner.style.left = '0';
                                inner.style.width = '100%';
                                inner.style.height = '100%';
                                inner.style.backgroundColor = `rgb(${rVal}, ${gVal}, ${bVal})`;
                                inner.dataset.rgb = `RGB(${rVal}, ${gVal}, ${bVal})`;
                                inner.addEventListener('mouseover', function() {
                                    pixelInfo.textContent = this.dataset.rgb;
                                    pixelInfo.style.color = 'black'; 
                                });

                                square.appendChild(inner);
                                td.appendChild(square);
                                tr.appendChild(td);
                                index++;
                            }
                            table.appendChild(tr);
                        }
                        containerResult.appendChild(table);
                        pixelInfo.textContent = "마우스를 올리면 픽셀의 RGB 값 확인 가능";
                    }
                });
            </script>
        </body>
        </html>
    """
    
    # HTML 컴포넌트 렌더링
    components.html(html_code2, height=800, scrolling=True)    
