import streamlit as st
import streamlit.components.v1 as components

st.title("🔄 회전체 탐구")
st.caption("캔버스에 마우스를 클릭하여 다각형을 그리고, '회전체 생성' 버튼을 눌러보세요.")

# 3. HTML/JS/CSS 코드 정의
# 제공해주신 코드를 그대로 활용하되, 스트림릿 컴포넌트 환경에 맞게 변수에 담습니다.
html_code = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        /* 모든 요소의 박스 모델을 border-box로 설정 */
        * { box-sizing: border-box; }
        
        /* 전체 화면 꽉 채우기 및 스크롤 방지 */
        html, body { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; }
        
        /* body 스타일 */
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; 
            background-color: #ffffff; /* 스트림릿 배경과 어울리게 흰색/투명 조정 가능 */
            color: #333; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            /* 패딩 제거: iframe 내부 공간을 최대로 활용 */
            padding: 0; 
        }
        
        /* 메인 컨테이너 */
        #container { 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            background-color: #fff; 
            border-radius: 12px; 
            border: 1px solid #e0e0e0; /* 경계선 추가 */
            /* box-shadow 제거: iframe 내부라 그림자가 잘릴 수 있음 */
            width: 100%; 
            height: 100%; 
            /* max-width 제한 해제: 스트림릿 너비에 맞춤 */
            max-width: none; 
            padding: 10px;
        }
        
        /* 캔버스 래퍼 */
        #canvas-wrapper { 
            position: relative; 
            width: 100%; 
            flex: 1 1 auto; 
            min-height: 0; 
            background-color: #fafafa;
            border-radius: 8px;
            overflow: hidden; /* 내부 캔버스 넘침 방지 */
        }
        
        /* 캔버스 공통 스타일 */
        .main-canvas { 
            position: absolute; 
            top: 0; 
            left: 0; 
            width: 100%; 
            height: 100%; 
            cursor: crosshair; 
        }
        
        /* 컨트롤 버튼 영역 */
        .top-right-controls { 
            position: absolute; 
            top: 15px; 
            right: 15px; 
            z-index: 10; 
            display: flex; 
            flex-direction: column; 
            gap: 10px; 
        }
        
        .top-right-controls button { 
            font-size: 14px; 
            padding: 8px 16px; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer; 
            background-color: #ff4b4b; /* 스트림릿 붉은색 테마 반영 */
            color: white; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
            transition: background-color 0.2s ease; 
            font-weight: bold;
        }
        
        .top-right-controls button:disabled { 
            background-color: #e0e0e0; 
            color: #a0a0a0;
            cursor: not-allowed; 
        }
        
        .top-right-controls button:hover:not(:disabled) {
            background-color: #d93e3e;
        }
        
        /* 자르기(Clipping) 컨트롤 */
        .clipping-controls { 
            display: flex; 
            flex-direction: column; 
            align-items: flex-start; 
            background: rgba(255, 255, 255, 0.9); 
            padding: 15px; 
            border-radius: 8px; 
            border: 1px solid #dee2e6; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            position: absolute;
            bottom: 15px;
            right: 15px;
            z-index: 10;
            backdrop-filter: blur(4px);
        }

        /* 모바일 대응 미디어 쿼리 */
        @media (max-width: 600px) {
            .clipping-controls {
                width: 90%;
                left: 5%;
                right: auto;
            }
        }
        
        .clip-group { 
            display: flex; 
            align-items: center; 
            margin: 5px 0; 
            width: 100%; 
            flex-wrap: wrap; 
        }
        
        .clip-group label { 
            margin: 0 10px; 
            font-size: 14px; 
            white-space: nowrap; 
        }
        
        .clip-group input[type="range"] { 
            flex-grow: 1; 
            min-width: 100px; 
        }
    </style>
</head>
<body>

    <div id="container">
        <div id="canvas-wrapper">
            <!-- 2D 드로잉 캔버스 -->
            <canvas id="drawingCanvas" class="main-canvas"></canvas>
            
            <!-- Three.js 3D 렌더링 캔버스 -->
            <canvas id="threeCanvas" class="main-canvas" style="display: none; cursor: grab;"></canvas>
            
            <!-- 오른쪽 상단 컨트롤 -->
            <div class="top-right-controls">
                <button id="revolveButton" disabled>회전체 생성</button>
                <button id="resetButton">초기화</button>
            </div>
            
            <!-- 자르기 컨트롤 -->
            <div id="clippingControls" class="clipping-controls" style="display: none;">
                <div class="clip-group">
                    <input type="radio" id="clipOff" name="clip-mode" value="off" checked>
                    <label for="clipOff">회전체 탐구</label>
                </div>
                <div class="clip-group">
                    <input type="radio" id="clipHorizontal" name="clip-mode" value="horizontal">
                    <label for="clipHorizontal">회전축에 수직인 평면</label>
                    <input type="range" id="clipHorizontalSlider" min="-200" max="200" value="0" disabled>
                </div>
                <div class="clip-group">
                    <input type="radio" id="clipVertical" name="clip-mode" value="vertical">
                    <label for="clipVertical">회전축을 포함하는 평면</label>
                </div>
            </div>
        </div>
    </div>

    <!-- 외부 라이브러리 -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/geometries/EdgesGeometry.js"></script>

    <script>
        const canvasWrapper = document.getElementById('canvas-wrapper');
        const drawingCanvas = document.getElementById('drawingCanvas');
        const threeCanvas = document.getElementById('threeCanvas');
        const ctx = drawingCanvas.getContext('2d');

        const revolveButton = document.getElementById('revolveButton');
        const resetButton = document.getElementById('resetButton');
        const clippingControlsUI = document.getElementById('clippingControls');
        const clipOffRadio = document.getElementById('clipOff');
        const clipHorizontalSlider = document.getElementById('clipHorizontalSlider');

        let points = []; 
        let isShapeClosed = false; 
        let threeApp = null; 
        let animationFrameId = null; 
        let isGenerating = false; 
        let currentAngle = 0; 
        let GRID_SIZE = 20; 

        const ROTATION_SPEED = 0.05; 
        const POINT_RADIUS = 5; 
        const CLOSING_THRESHOLD = 15; 

        const horizontalPlane = new THREE.Plane(new THREE.Vector3(0, -1, 0), 0);
        const verticalPlane = new THREE.Plane(new THREE.Vector3(-1, 0, 0), 0);
        const globalClippingPlanes = []; 

        function resizeCanvas() {
            const { width, height } = canvasWrapper.getBoundingClientRect();
            if (drawingCanvas.width !== width || drawingCanvas.height !== height) {
                drawingCanvas.width = width;
                drawingCanvas.height = height;
                threeCanvas.width = width;
                threeCanvas.height = height;
            }
            if (threeApp) {
                threeApp.renderer.setSize(width, height);
                threeApp.camera.aspect = width / height;
                threeApp.camera.updateProjectionMatrix();
            }
            GRID_SIZE = Math.max(20, Math.round(width / 40)); 
            draw2DShape();
        }

        let resizeTimeout; 
        window.addEventListener('resize', () => { 
            clearTimeout(resizeTimeout); 
            resizeTimeout = setTimeout(resizeCanvas, 100); 
        });

        function drawGrid() {
            const centerX = drawingCanvas.width / 2;
            ctx.save();
            ctx.strokeStyle = 'rgba(0,0,0,0.1)';
            ctx.lineWidth = 0.5;
            for (let x = centerX + GRID_SIZE; x < drawingCanvas.width; x += GRID_SIZE) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, drawingCanvas.height); ctx.stroke(); }
            for (let x = centerX - GRID_SIZE; x > 0; x -= GRID_SIZE) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, drawingCanvas.height); ctx.stroke(); }
            for (let y = 0; y < drawingCanvas.height; y += GRID_SIZE) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(drawingCanvas.width, y); ctx.stroke(); }
            ctx.restore();
        }

        function drawYAxis() {
            ctx.save();
            ctx.strokeStyle = 'rgba(255, 75, 75, 0.6)'; /* 축 색상 강조 */
            ctx.lineWidth = 2;
            ctx.setLineDash([5, 5]);
            ctx.beginPath();
            ctx.moveTo(drawingCanvas.width / 2, 0);
            ctx.lineTo(drawingCanvas.width / 2, drawingCanvas.height);
            ctx.stroke();
            ctx.restore();
        }
        
        function draw2DShape() {
            ctx.clearRect(0, 0, drawingCanvas.width, drawingCanvas.height);
            drawGrid();
            drawYAxis();
            if (points.length === 0) return;
            ctx.strokeStyle = '#007bff';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(points[0].x, points[0].y);
            points.forEach(p => ctx.lineTo(p.x, p.y));
            if (isShapeClosed) {
                ctx.closePath();
                ctx.fillStyle = 'rgba(0,123,255,0.2)';
                ctx.fill();
            }
            ctx.stroke();
            points.forEach((point, index) => {
                ctx.beginPath();
                ctx.fillStyle = (index === 0) ? '#28a745' : '#dc3545';
                ctx.arc(point.x, point.y, POINT_RADIUS, 0, Math.PI * 2);
                ctx.fill();
            });
        }
        
        function handleCanvasClick(event) {
            if (isShapeClosed) return;
            const rect = drawingCanvas.getBoundingClientRect();
            const mouseX = event.clientX - rect.left;
            const mouseY = event.clientY - rect.top;
            const centerX = drawingCanvas.width / 2;
            const offsetX = mouseX - centerX;
            const snappedOffsetX = Math.round(offsetX / GRID_SIZE) * GRID_SIZE;
            const snappedX = centerX + snappedOffsetX;
            const snappedY = Math.round(mouseY / GRID_SIZE) * GRID_SIZE;
            if (points.length >= 3) {
                const firstPoint = points[0];
                const distance = Math.sqrt(Math.pow(snappedX - firstPoint.x, 2) + Math.pow(snappedY - firstPoint.y, 2));
                if (distance < CLOSING_THRESHOLD) {
                    isShapeClosed = true;
                    revolveButton.disabled = false;
                    draw2DShape();
                    return;
                }
            }
            points.push({ x: snappedX, y: snappedY });
            draw2DShape();
        }

        function preparePointsFor3D() {
            const centerX = drawingCanvas.width / 2, centerY = drawingCanvas.height / 2;
            let finalPoints = [...points];
            if (isShapeClosed && finalPoints.length > 0) {
                finalPoints.push(finalPoints[0]);
            }
            return finalPoints.map(p => new THREE.Vector2(p.x - centerX, -(p.y - centerY)));
        }
        
        function init3D() {
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0xfafafa);
            const camera = new THREE.PerspectiveCamera(75, threeCanvas.width / threeCanvas.height, 0.1, 1000);
            camera.position.set(0, 150, 400);
            const renderer = new THREE.WebGLRenderer({ canvas: threeCanvas, antialias: true });
            renderer.localClippingEnabled = true;
            renderer.setSize(threeCanvas.width, threeCanvas.height);
            
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
            scene.add(ambientLight);
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(50, 50, 100);
            scene.add(directionalLight);
            
            const axisMaterial = new THREE.LineBasicMaterial({ color: 0xff4b4b });
            const axisPoints = [new THREE.Vector3(0, -500, 0), new THREE.Vector3(0, 500, 0)];
            const axisGeometry = new THREE.BufferGeometry().setFromPoints(axisPoints);
            const yAxisLine = new THREE.Line(axisGeometry, axisMaterial);
            scene.add(yAxisLine);
            
            const shapePoints = preparePointsFor3D();
            const geometry = new THREE.LatheGeometry(shapePoints, 32, 0, currentAngle);
            const baseColor = new THREE.Color(0x007bff);
            
            const surfaceMaterial = new THREE.MeshStandardMaterial({ 
                color: baseColor, 
                side: THREE.DoubleSide, 
                clippingPlanes: globalClippingPlanes, 
                clipIntersection: true, 
                transparent: true, 
                opacity: 0.7,
                roughness: 0.5,
                metalness: 0.1
            });
            
            const surfaceMesh = new THREE.Mesh(geometry, surfaceMaterial);
            const edgesGeometry = new THREE.EdgesGeometry(geometry, 20);
            const edgesMaterial = new THREE.LineBasicMaterial({ color: 0x004499, clippingPlanes: globalClippingPlanes });
            const edgesMesh = new THREE.LineSegments(edgesGeometry, edgesMaterial);
            
            const group = new THREE.Group();
            group.add(surfaceMesh);
            group.add(edgesMesh);
            scene.add(group);
            group.rotation.y = Math.PI / 2;
            
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.enabled = false;
            
            return { scene, camera, renderer, lathe: group, controls, shapePoints };
        }
        
        function animate() {
            animationFrameId = requestAnimationFrame(animate);
            if (isGenerating) {
                currentAngle += ROTATION_SPEED;
                if (currentAngle >= Math.PI * 2) {
                    currentAngle = Math.PI * 2;
                    isGenerating = false;
                    clippingControlsUI.style.display = 'flex';
                    threeApp.controls.enabled = true;
                    threeApp.lathe.children[0].material.depthWrite = true;
                }
                const newGeometry = new THREE.LatheGeometry(threeApp.shapePoints, 32, 0, currentAngle);
                const newEdgesGeometry = new THREE.EdgesGeometry(newGeometry, 20);
                const surface = threeApp.lathe.children[0];
                const edges = threeApp.lathe.children[1];
                surface.geometry.dispose();
                edges.geometry.dispose();
                surface.geometry = newGeometry;
                edges.geometry = newEdgesGeometry;
            }
            if (threeApp.controls.enabled) {
                threeApp.controls.update();
            }
            threeApp.renderer.render(threeApp.scene, threeApp.camera);
        }

        revolveButton.addEventListener('click', () => {
            if (!isShapeClosed) return;
            revolveButton.disabled = true;
            resetButton.textContent = "초기화";
            isGenerating = true;
            currentAngle = 0.01;
            drawingCanvas.style.display = 'none';
            threeCanvas.style.display = 'block';
            threeApp = init3D();
            threeApp.lathe.children[0].material.depthWrite = false;
            animate();
        });

        resetButton.addEventListener('click', () => {
            if (animationFrameId) cancelAnimationFrame(animationFrameId);
            points = []; isShapeClosed = false; threeApp = null; animationFrameId = null;
            isGenerating = false; currentAngle = 0;
            threeCanvas.style.display = 'none';
            drawingCanvas.style.display = 'block';
            clippingControlsUI.style.display = 'none';
            resizeCanvas();
            revolveButton.disabled = true;
            revolveButton.textContent = "회전체 생성";
            resetButton.textContent = "초기화";
            globalClippingPlanes.length = 0;
            clipOffRadio.checked = true;
            clipHorizontalSlider.disabled = true;
            clipHorizontalSlider.value = 0;
            horizontalPlane.constant = 0;
        });

        drawingCanvas.addEventListener('click', handleCanvasClick);

        clippingControlsUI.addEventListener('change', (e) => {
            if (!threeApp) return;
            const selectedMode = document.querySelector('input[name="clip-mode"]:checked').value;
            globalClippingPlanes.length = 0;
            clipHorizontalSlider.disabled = true;
            threeApp.controls.minAzimuthAngle = -Infinity;
            threeApp.controls.maxAzimuthAngle = Infinity;
            if (selectedMode === 'horizontal') {
                globalClippingPlanes.push(horizontalPlane);
                clipHorizontalSlider.disabled = false;
            } else if (selectedMode === 'vertical') {
                verticalPlane.constant = 0;
                globalClippingPlanes.push(verticalPlane);
                threeApp.controls.minAzimuthAngle = Math.PI / 2;
                threeApp.controls.maxAzimuthAngle = Math.PI / 2;
            }
            threeApp.controls.update();
        });

        clipHorizontalSlider.addEventListener('input', (e) => {
            horizontalPlane.constant = parseFloat(e.target.value);
        });
        
        resizeCanvas();
    </script>
</body>
</html>
"""

# 4. 스트림릿 컴포넌트로 렌더링
# height=800: iframe의 높이를 800픽셀로 고정하여 넉넉한 공간 확보
# scrolling=False: iframe 내부의 불필요한 스크롤바 제거
components.html(html_code, height=800, scrolling=False)