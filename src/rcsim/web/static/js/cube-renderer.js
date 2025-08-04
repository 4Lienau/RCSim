/**
 * Three.js WebGL Cube Renderer for Advanced Rubik's Cube Simulator
 * Provides hardware-accelerated 3D visualization with realistic lighting
 */

class CubeRenderer {
    constructor(canvasElement) {
        this.canvas = canvasElement;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.cubeGroup = null;
        this.cubePieces = [];
        this.animationQueue = [];
        this.isAnimating = false;
        
        // Configuration
        this.config = {
            cubeSize: 3,
            pieceSize: 0.95,
            pieceGap: 0.05,
            animationSpeed: 1.0,
            autoRotate: false,
            showWireframe: false
        };
        
        // Colors matching standard Rubik's cube
        this.colors = {
            'W': 0xffffff, // White
            'Y': 0xffff00, // Yellow  
            'R': 0xff0000, // Red
            'O': 0xff8800, // Orange
            'B': 0x0000ff, // Blue
            'G': 0x00ff00  // Green
        };
        
        // Performance tracking
        this.stats = {
            fps: 0,
            frameCount: 0,
            lastTime: performance.now()
        };
        
        this.init();
    }
    
    init() {
        this.setupScene();
        this.setupLighting();
        this.setupCamera();
        this.setupRenderer();
        this.setupControls();
        this.createCube();
        this.startRenderLoop();
        
        // Handle window resize
        window.addEventListener('resize', () => this.handleResize());
    }
    
    setupScene() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0f172a); // Match CSS background
        
        // Add subtle fog for depth
        this.scene.fog = new THREE.Fog(0x0f172a, 10, 50);
    }
    
    setupLighting() {
        // Ambient light for overall illumination
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        this.scene.add(ambientLight);
        
        // Main directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(5, 5, 5);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);
        
        // Fill light from opposite side
        const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
        fillLight.position.set(-3, -3, -3);
        this.scene.add(fillLight);
        
        // Rim light for edge definition
        const rimLight = new THREE.DirectionalLight(0x4080ff, 0.2);
        rimLight.position.set(0, 0, -5);
        this.scene.add(rimLight);
    }
    
    setupCamera() {
        const aspect = this.canvas.clientWidth / this.canvas.clientHeight;
        this.camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 100);
        this.camera.position.set(8, 8, 8);
        this.camera.lookAt(0, 0, 0);
    }
    
    setupRenderer() {
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true,
            alpha: false,
            powerPreference: "high-performance"
        });
        
        this.renderer.setSize(this.canvas.clientWidth, this.canvas.clientHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.outputEncoding = THREE.sRGBEncoding;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.0;
    }
    
    setupControls() {
        this.controls = new THREE.OrbitControls(this.camera, this.canvas);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.screenSpacePanning = false;
        this.controls.minDistance = 3;
        this.controls.maxDistance = 15;
        this.controls.maxPolarAngle = Math.PI;
        this.controls.autoRotate = false;
        this.controls.autoRotateSpeed = 0.5;
    }
    
    createCube() {
        // Remove existing cube if any
        if (this.cubeGroup) {
            this.scene.remove(this.cubeGroup);
        }
        
        this.cubeGroup = new THREE.Group();
        this.cubePieces = [];
        
        const size = this.config.cubeSize;
        const pieceSize = this.config.pieceSize;
        const gap = this.config.pieceGap;
        const offset = (size - 1) * (pieceSize + gap) / 2;
        
        // Create geometry and materials
        const geometry = new THREE.BoxGeometry(pieceSize, pieceSize, pieceSize);
        const materials = this.createMaterials();
        
        // Create each piece
        for (let x = 0; x < size; x++) {
            for (let y = 0; y < size; y++) {
                for (let z = 0; z < size; z++) {
                    // Skip internal pieces (not visible)
                    if (x > 0 && x < size - 1 && 
                        y > 0 && y < size - 1 && 
                        z > 0 && z < size - 1) continue;
                    
                    const piece = this.createPiece(geometry, materials, x, y, z);
                    piece.position.set(
                        x * (pieceSize + gap) - offset,
                        y * (pieceSize + gap) - offset,
                        z * (pieceSize + gap) - offset
                    );
                    
                    // Store piece info for animations
                    piece.userData = {
                        gridPosition: { x, y, z },
                        originalPosition: piece.position.clone(),
                        faces: this.getPieceFaces(x, y, z, size)
                    };
                    
                    this.cubePieces.push(piece);
                    this.cubeGroup.add(piece);
                }
            }
        }
        
        this.scene.add(this.cubeGroup);
    }
    
    createMaterials() {
        const materials = {};
        
        for (const [colorKey, colorValue] of Object.entries(this.colors)) {
            materials[colorKey] = new THREE.MeshPhongMaterial({
                color: colorValue,
                shininess: 30,
                specular: 0x222222
            });
        }
        
        // Black material for hidden faces
        materials.black = new THREE.MeshPhongMaterial({
            color: 0x000000,
            shininess: 5
        });
        
        return materials;
    }
    
    createPiece(geometry, materials, x, y, z) {
        const size = this.config.cubeSize;
        const faceMaterials = [];
        
        // Determine which faces are visible and their colors
        // Right (+X), Left (-X), Top (+Y), Bottom (-Y), Front (+Z), Back (-Z)
        const faceColors = [
            x === size - 1 ? 'R' : 'black', // Right
            x === 0 ? 'O' : 'black',        // Left  
            y === size - 1 ? 'W' : 'black', // Top
            y === 0 ? 'Y' : 'black',        // Bottom
            z === size - 1 ? 'G' : 'black', // Front
            z === 0 ? 'B' : 'black'         // Back
        ];
        
        faceColors.forEach(color => {
            faceMaterials.push(materials[color]);
        });
        
        const piece = new THREE.Mesh(geometry, faceMaterials);
        piece.castShadow = true;
        piece.receiveShadow = true;
        
        return piece;
    }
    
    getPieceFaces(x, y, z, size) {
        const faces = [];
        if (x === size - 1) faces.push('R');
        if (x === 0) faces.push('L');
        if (y === size - 1) faces.push('U');
        if (y === 0) faces.push('D');
        if (z === size - 1) faces.push('F');
        if (z === 0) faces.push('B');
        return faces;
    }
    
    updateCubeState(cubeState) {
        if (!cubeState || !cubeState.face_colors) return;
        
        const size = cubeState.size;
        const faceColors = cubeState.face_colors;
        
        // Update piece colors based on cube state
        this.cubePieces.forEach((piece, index) => {
            const { gridPosition, faces } = piece.userData;
            const { x, y, z } = gridPosition;
            
            // Update material for each visible face
            faces.forEach((face, faceIndex) => {
                let faceX, faceY;
                
                // Map grid position to face coordinates
                switch(face) {
                    case 'R': // Right face
                        faceX = z;
                        faceY = size - 1 - y;
                        break;
                    case 'L': // Left face  
                        faceX = size - 1 - z;
                        faceY = size - 1 - y;
                        break;
                    case 'U': // Up face
                        faceX = x;
                        faceY = z;
                        break;
                    case 'D': // Down face
                        faceX = x;
                        faceY = size - 1 - z;
                        break;
                    case 'F': // Front face
                        faceX = x;
                        faceY = size - 1 - y;
                        break;
                    case 'B': // Back face
                        faceX = size - 1 - x;
                        faceY = size - 1 - y;
                        break;
                }
                
                if (faceColors[face] && faceColors[face][faceY] && faceColors[face][faceY][faceX]) {
                    const colorHex = faceColors[face][faceY][faceX];
                    const color = parseInt(colorHex.replace('#', ''), 16);
                    
                    // Find the corresponding face material index
                    const materialIndex = this.getFaceMaterialIndex(face);
                    if (materialIndex !== -1 && piece.material[materialIndex]) {
                        piece.material[materialIndex].color.setHex(color);
                    }
                }
            });
        });
    }
    
    getFaceMaterialIndex(face) {
        const faceMap = { 'R': 0, 'L': 1, 'U': 2, 'D': 3, 'F': 4, 'B': 5 };
        return faceMap[face] || -1;
    }
    
    animateMove(move, duration = 500) {
        if (this.isAnimating) {
            this.animationQueue.push({ move, duration });
            return;
        }
        
        this.isAnimating = true;
        const pieces = this.getPiecesForMove(move);
        const axis = this.getRotationAxis(move);
        const angle = this.getRotationAngle(move);
        
        // Create rotation group
        const rotationGroup = new THREE.Group();
        this.scene.add(rotationGroup);
        
        // Move pieces to rotation group
        pieces.forEach(piece => {
            this.cubeGroup.remove(piece);
            rotationGroup.add(piece);
        });
        
        // Animate rotation
        const startTime = performance.now();
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeProgress = this.easeInOutCubic(progress);
            
            rotationGroup.rotation[axis] = angle * easeProgress;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                // Animation complete - move pieces back to cube group
                pieces.forEach(piece => {
                    rotationGroup.remove(piece);
                    this.cubeGroup.add(piece);
                });
                this.scene.remove(rotationGroup);
                
                this.isAnimating = false;
                
                // Process next animation in queue
                if (this.animationQueue.length > 0) {
                    const next = this.animationQueue.shift();
                    this.animateMove(next.move, next.duration);
                }
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    getPiecesForMove(move) {
        const face = move.charAt(0);
        const size = this.config.cubeSize;
        const layer = 0; // For now, only outer layer moves
        
        return this.cubePieces.filter(piece => {
            const { x, y, z } = piece.userData.gridPosition;
            
            switch(face) {
                case 'R': return x === size - 1;
                case 'L': return x === 0;
                case 'U': return y === size - 1;
                case 'D': return y === 0;
                case 'F': return z === size - 1;
                case 'B': return z === 0;
                default: return false;
            }
        });
    }
    
    getRotationAxis(move) {
        const face = move.charAt(0);
        const axisMap = {
            'R': 'x', 'L': 'x',
            'U': 'y', 'D': 'y', 
            'F': 'z', 'B': 'z'
        };
        return axisMap[face] || 'y';
    }
    
    getRotationAngle(move) {
        const isPrime = move.includes("'");
        const face = move.charAt(0);
        
        let baseAngle = Math.PI / 2;
        
        // Adjust for face orientation
        if (face === 'L' || face === 'D' || face === 'B') {
            baseAngle = -baseAngle;
        }
        
        return isPrime ? -baseAngle : baseAngle;
    }
    
    easeInOutCubic(t) {
        return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }
    
    setAnimationSpeed(speed) {
        this.config.animationSpeed = Math.max(0.1, Math.min(3.0, speed));
    }
    
    setAutoRotate(enabled) {
        this.config.autoRotate = enabled;
        this.controls.autoRotate = enabled;
    }
    
    resetCamera() {
        this.camera.position.set(8, 8, 8);
        this.camera.lookAt(0, 0, 0);
        this.controls.reset();
    }
    
    setZoom(distance) {
        const direction = this.camera.position.clone().normalize();
        this.camera.position.copy(direction.multiplyScalar(distance));
    }
    
    handleResize() {
        const width = this.canvas.clientWidth;
        const height = this.canvas.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }
    
    updateFPS() {
        this.stats.frameCount++;
        const currentTime = performance.now();
        
        if (currentTime >= this.stats.lastTime + 1000) {
            this.stats.fps = Math.round((this.stats.frameCount * 1000) / (currentTime - this.stats.lastTime));
            this.stats.frameCount = 0;
            this.stats.lastTime = currentTime;
            
            // Update FPS display
            const fpsElement = document.getElementById('fps-counter');
            if (fpsElement) {
                fpsElement.textContent = `${this.stats.fps} FPS`;
            }
        }
    }
    
    startRenderLoop() {
        const render = () => {
            requestAnimationFrame(render);
            
            // Update controls
            this.controls.update();
            
            // Update FPS
            this.updateFPS();
            
            // Render scene
            this.renderer.render(this.scene, this.camera);
        };
        
        render();
    }
    
    dispose() {
        // Clean up resources
        if (this.renderer) {
            this.renderer.dispose();
        }
        
        if (this.controls) {
            this.controls.dispose();
        }
        
        // Dispose geometries and materials
        this.scene.traverse((object) => {
            if (object.geometry) {
                object.geometry.dispose();
            }
            if (object.material) {
                if (Array.isArray(object.material)) {
                    object.material.forEach(material => material.dispose());
                } else {
                    object.material.dispose();
                }
            }
        });
    }
}

// Export for use in other modules
window.CubeRenderer = CubeRenderer;