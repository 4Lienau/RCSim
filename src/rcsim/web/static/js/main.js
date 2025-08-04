/**
 * Main Application Entry Point
 * Initializes and coordinates all components of the Rubik's Cube Simulator
 */

class RubiksCubeApp {
    constructor() {
        this.renderer = null;
        this.controller = null;
        this.solverUI = null;
        this.apiClient = null;
        this.sessionTimer = null;
        this.sessionStartTime = Date.now();
        
        this.init();
    }
    
    async init() {
        try {
            console.log('🎲 Initializing Advanced Rubik\'s Cube Simulator...');
            
            // Show loading state
            this.showLoadingState();
            
            // Initialize API client first
            await this.initializeAPI();
            
            // Initialize 3D renderer
            await this.initializeRenderer();
            
            // Initialize controller
            this.initializeController();
            
            // Initialize solver UI
            this.initializeSolverUI();
            
            // Setup global event handlers
            this.setupGlobalEvents();
            
            // Start session timer
            this.startSessionTimer();
            
            // Load initial cube state
            await this.loadInitialState();
            
            // Hide loading state
            this.hideLoadingState();
            
            console.log('✅ Application initialized successfully');
            
        } catch (error) {
            console.error('❌ Failed to initialize application:', error);
            this.showError('Failed to initialize application: ' + error.message);
        }
    }
    
    showLoadingState() {
        const loadingSpinner = document.getElementById('loading-spinner');
        if (loadingSpinner) {
            loadingSpinner.style.display = 'flex';
        }
        
        // Disable all controls
        document.querySelectorAll('.control-btn, .action-btn, select').forEach(element => {
            element.disabled = true;
        });
    }
    
    hideLoadingState() {
        const loadingSpinner = document.getElementById('loading-spinner');
        if (loadingSpinner) {
            loadingSpinner.style.display = 'none';
        }
        
        // Re-enable controls
        document.querySelectorAll('.control-btn, .action-btn, select').forEach(element => {
            element.disabled = false;
        });
    }
    
    async initializeAPI() {
        console.log('🔌 Initializing API client...');
        
        this.apiClient = new APIClient();
        
        // Setup API event listeners
        this.apiClient.on('connected', () => {
            console.log('✅ WebSocket connected');
            this.updateConnectionStatus(true);
        });
        
        this.apiClient.on('disconnected', () => {
            console.log('❌ WebSocket disconnected');
            this.updateConnectionStatus(false);
        });
        
        this.apiClient.on('cube_state_update', (state) => {
            this.handleCubeStateUpdate(state);
        });
        
        this.apiClient.on('moves_applied', (data) => {
            if (data.animate && this.renderer) {
                // Apply animation for each move
                const moves = data.moves.split(/\s+/).filter(move => move.trim());
                moves.forEach((move, index) => {
                    setTimeout(() => {
                        this.renderer.animateMove(move.trim());
                    }, index * 100);
                });
            }
        });
        
        this.apiClient.on('cube_scrambled', () => {
            console.log('🎲 Cube scrambled');
        });
        
        this.apiClient.on('cube_reset', () => {
            console.log('🔄 Cube reset');
        });
        
        this.apiClient.on('solution_found', (solution) => {
            console.log('🧠 Solution found:', solution);
        });
        
        // Start health check
        this.apiClient.startHealthCheck();
    }
    
    async initializeRenderer() {
        console.log('🎨 Initializing 3D renderer...');
        
        const canvas = document.getElementById('cube-canvas');
        if (!canvas) {
            throw new Error('Canvas element not found');
        }
        
        // Check WebGL support
        if (!this.checkWebGLSupport()) {
            throw new Error('WebGL is not supported in this browser');
        }
        
        this.renderer = new CubeRenderer(canvas);
        
        // Make renderer globally accessible for debugging
        window.cubeRenderer = this.renderer;
        
        console.log('✅ 3D renderer initialized');
    }
    
    initializeController() {
        console.log('🎮 Initializing cube controller...');
        
        this.controller = new CubeController(this.renderer, this.apiClient);
        
        // Make controller globally accessible
        window.cubeController = this.controller;
        
        console.log('✅ Cube controller initialized');
    }
    
    initializeSolverUI() {
        console.log('🧠 Initializing solver UI...');
        
        this.solverUI = new SolverUI(this.apiClient);
        
        // Make solver UI globally accessible
        window.solverUI = this.solverUI;
        
        console.log('✅ Solver UI initialized');
    }
    
    setupGlobalEvents() {
        // Handle window events
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
        
        window.addEventListener('resize', () => {
            if (this.renderer) {
                this.renderer.handleResize();
            }
        });
        
        // Handle visibility change for performance optimization
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                // Pause animations when tab is not visible
                if (this.renderer) {
                    this.renderer.config.autoRotate = false;
                }
            } else {
                // Resume animations when tab becomes visible
                // (Don't automatically resume auto-rotate)
            }
        });
        
        // Handle errors globally
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            this.showError('An unexpected error occurred');
        });
        
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.showError('An unexpected error occurred');
        });
    }
    
    startSessionTimer() {
        this.sessionTimer = setInterval(() => {
            this.updateSessionTime();
        }, 1000);
    }
    
    updateSessionTime() {
        const elapsed = Date.now() - this.sessionStartTime;
        const minutes = Math.floor(elapsed / 60000);
        const seconds = Math.floor((elapsed % 60000) / 1000);
        
        const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        const sessionTimeElement = document.getElementById('session-time');
        if (sessionTimeElement) {
            sessionTimeElement.textContent = timeString;
        }
    }
    
    async loadInitialState() {
        console.log('📊 Loading initial cube state...');
        
        try {
            const state = await this.apiClient.getCubeState();
            this.handleCubeStateUpdate(state);
        } catch (error) {
            console.error('Failed to load initial state:', error);
            // Continue anyway - WebSocket will provide updates
        }
    }
    
    handleCubeStateUpdate(state) {
        if (!state) return;
        
        console.log('🔄 Updating cube state:', state);
        
        // Update 3D renderer
        if (this.renderer) {
            this.renderer.updateCubeState(state);
        }
        
        // Update UI elements
        this.updateCubeInfo(state);
    }
    
    updateCubeInfo(state) {
        // Update status indicator
        const statusElement = document.getElementById('cube-status');
        if (statusElement) {
            statusElement.textContent = state.is_solved ? 'Solved' : 'Scrambled';
            statusElement.classList.toggle('scrambled', !state.is_solved);
        }
        
        // Update move counter in header
        const moveCounterElement = document.getElementById('move-counter');
        if (moveCounterElement) {
            moveCounterElement.textContent = `${state.move_count} moves`;
        }
        
        // Update statistics
        const totalMovesElement = document.getElementById('total-moves');
        if (totalMovesElement) {
            totalMovesElement.textContent = state.move_count.toString();
        }
        
        const cubeStateElement = document.getElementById('cube-state');
        if (cubeStateElement) {
            cubeStateElement.textContent = state.is_solved ? 'Solved' : 'Scrambled';
        }
    }
    
    updateConnectionStatus(isConnected) {
        // Could add a connection indicator to the UI
        console.log(`Connection status: ${isConnected ? 'Connected' : 'Disconnected'}`);
    }
    
    checkWebGLSupport() {
        try {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            return !!gl;
        } catch (e) {
            return false;
        }
    }
    
    showError(message) {
        console.error(message);
        
        // Create or update error toast
        let errorToast = document.getElementById('error-toast');
        if (!errorToast) {
            errorToast = document.createElement('div');
            errorToast.id = 'error-toast';
            errorToast.className = 'error-toast';
            errorToast.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: var(--danger-color);
                color: white;
                padding: 1rem;
                border-radius: var(--radius-md);
                box-shadow: var(--shadow-lg);
                z-index: 1000;
                max-width: 300px;
                display: none;
            `;
            document.body.appendChild(errorToast);
        }
        
        errorToast.textContent = message;
        errorToast.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorToast.style.display = 'none';
        }, 5000);
    }
    
    cleanup() {
        console.log('🧹 Cleaning up application...');
        
        if (this.sessionTimer) {
            clearInterval(this.sessionTimer);
        }
        
        if (this.apiClient) {
            this.apiClient.disconnect();
        }
        
        if (this.renderer) {
            this.renderer.dispose();
        }
    }
    
    // Public API methods for external access
    getAppState() {
        return {
            renderer: !!this.renderer,
            controller: !!this.controller,
            solverUI: !!this.solverUI,
            apiClient: !!this.apiClient && this.apiClient.isConnected,
            sessionTime: Date.now() - this.sessionStartTime
        };
    }
    
    async resetApplication() {
        console.log('🔄 Resetting application...');
        
        try {
            await this.apiClient.resetCube();
            
            if (this.renderer) {
                this.renderer.resetCamera();
            }
            
            if (this.solverUI) {
                this.solverUI.hideSolution();
            }
            
            console.log('✅ Application reset successfully');
            
        } catch (error) {
            console.error('❌ Failed to reset application:', error);
            this.showError('Failed to reset application');
        }
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Starting Advanced Rubik\'s Cube Simulator...');
    
    // Create global app instance
    window.rubiksCubeApp = new RubiksCubeApp();
});

// Export for debugging
window.RubiksCubeApp = RubiksCubeApp;