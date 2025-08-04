/**
 * Cube Controller - Handles user input and cube manipulation
 * Manages keyboard shortcuts, mouse interactions, and move history
 */

class CubeController {
    constructor(renderer, apiClient) {
        this.renderer = renderer;
        this.apiClient = apiClient;
        this.moveHistory = [];
        this.isControlEnabled = true;
        
        // Keyboard state tracking
        this.keys = {};
        this.keyBindings = {
            // Face moves
            'KeyU': 'U',
            'KeyD': 'D', 
            'KeyL': 'L',
            'KeyR': 'R',
            'KeyF': 'F',
            'KeyB': 'B',
            
            // Special actions
            'Space': 'scramble',
            'KeyS': 'solve',
            'KeyZ': 'undo',
            'KeyY': 'redo',
            'Escape': 'reset'
        };
        
        // Mouse interaction state
        this.mouseState = {
            isDown: false,
            startX: 0,
            startY: 0,
            lastMove: null
        };
        
        this.init();
    }
    
    init() {
        this.setupKeyboardControls();
        this.setupMouseControls();
        this.setupTouchControls();
        this.setupButtonControls();
    }
    
    setupKeyboardControls() {
        document.addEventListener('keydown', (event) => {
            if (!this.isControlEnabled) return;
            
            // Prevent default for handled keys
            if (this.keyBindings[event.code]) {
                event.preventDefault();
            }
            
            this.keys[event.code] = true;
            this.handleKeyDown(event);
        });
        
        document.addEventListener('keyup', (event) => {
            this.keys[event.code] = false;
        });
        
        // Prevent context menu on right click
        this.renderer.canvas.addEventListener('contextmenu', (event) => {
            event.preventDefault();
        });
    }
    
    handleKeyDown(event) {
        const { code, shiftKey } = event;
        const binding = this.keyBindings[code];
        
        if (!binding) return;
        
        // Handle special actions
        if (binding === 'scramble') {
            this.scrambleCube();
            return;
        }
        
        if (binding === 'solve') {
            this.solveCube();
            return;
        }
        
        if (binding === 'undo') {
            this.undoMove();
            return;
        }
        
        if (binding === 'redo') {
            this.redoMove();
            return;
        }
        
        if (binding === 'reset') {
            this.resetCube();
            return;
        }
        
        // Handle face moves
        if (binding.match(/^[UDLRFB]$/)) {
            const move = shiftKey ? binding + "'" : binding;
            this.applyMove(move);
        }
    }
    
    setupMouseControls() {
        const canvas = this.renderer.canvas;
        
        // Mouse drag for face selection and rotation
        canvas.addEventListener('mousedown', (event) => {
            if (event.button === 0) { // Left mouse button
                this.mouseState.isDown = true;
                this.mouseState.startX = event.clientX;
                this.mouseState.startY = event.clientY;
            }
        });
        
        canvas.addEventListener('mousemove', (event) => {
            if (this.mouseState.isDown && this.isControlEnabled) {
                const deltaX = event.clientX - this.mouseState.startX;
                const deltaY = event.clientY - this.mouseState.startY;
                
                // Check if drag distance is significant enough
                const dragDistance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
                if (dragDistance > 30) {
                    this.handleMouseDrag(deltaX, deltaY);
                    this.mouseState.isDown = false;
                }
            }
        });
        
        canvas.addEventListener('mouseup', () => {
            this.mouseState.isDown = false;
        });
        
        // Double-click to rotate face
        canvas.addEventListener('dblclick', (event) => {
            if (!this.isControlEnabled) return;
            
            const face = this.getFaceFromClick(event);
            if (face) {
                this.applyMove(face);
            }
        });
    }
    
    setupTouchControls() {
        const canvas = this.renderer.canvas;
        let touchStartX, touchStartY;
        
        canvas.addEventListener('touchstart', (event) => {
            if (!this.isControlEnabled) return;
            event.preventDefault();
            
            const touch = event.touches[0];
            touchStartX = touch.clientX;
            touchStartY = touch.clientY;
        });
        
        canvas.addEventListener('touchmove', (event) => {
            event.preventDefault();
        });
        
        canvas.addEventListener('touchend', (event) => {
            if (!this.isControlEnabled) return;
            event.preventDefault();
            
            const touch = event.changedTouches[0];
            const deltaX = touch.clientX - touchStartX;
            const deltaY = touch.clientY - touchStartY;
            
            const swipeDistance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
            if (swipeDistance > 50) {
                this.handleSwipe(deltaX, deltaY);
            } else {
                // Tap - attempt face rotation
                const face = this.getFaceFromTouch(touch);
                if (face) {
                    this.applyMove(face);
                }
            }
        });
    }
    
    setupButtonControls() {
        // Face move buttons
        document.querySelectorAll('.control-btn[data-move]').forEach(button => {
            button.addEventListener('click', (event) => {
                if (!this.isControlEnabled) return;
                
                const move = event.target.dataset.move;
                this.applyMove(move);
                
                // Visual feedback
                button.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    button.style.transform = '';
                }, 100);
            });
        });
        
        // Action buttons
        document.getElementById('scramble-btn')?.addEventListener('click', () => {
            this.scrambleCube();
        });
        
        document.getElementById('reset-btn')?.addEventListener('click', () => {
            this.resetCube();
        });
        
        document.getElementById('undo-btn')?.addEventListener('click', () => {
            this.undoMove();
        });
        
        document.getElementById('solve-btn')?.addEventListener('click', () => {
            this.solveCube();
        });
        
        // Camera controls
        document.getElementById('reset-camera-btn')?.addEventListener('click', () => {
            this.renderer.resetCamera();
        });
        
        document.getElementById('auto-rotate-btn')?.addEventListener('click', (event) => {
            const isActive = event.target.classList.contains('active');
            this.renderer.setAutoRotate(!isActive);
            event.target.classList.toggle('active');
        });
        
        // Camera sliders
        document.getElementById('zoom-slider')?.addEventListener('input', (event) => {
            const zoom = parseFloat(event.target.value);
            this.renderer.setZoom(zoom);
        });
        
        document.getElementById('speed-slider')?.addEventListener('input', (event) => {
            const speed = parseFloat(event.target.value);
            this.renderer.setAnimationSpeed(speed);
        });
    }
    
    handleMouseDrag(deltaX, deltaY) {
        // Determine move based on drag direction
        const absX = Math.abs(deltaX);
        const absY = Math.abs(deltaY);
        
        if (absX > absY) {
            // Horizontal drag
            const move = deltaX > 0 ? 'R' : "L'";
            this.applyMove(move);
        } else {
            // Vertical drag  
            const move = deltaY > 0 ? 'D' : 'U';
            this.applyMove(move);
        }
    }
    
    handleSwipe(deltaX, deltaY) {
        const absX = Math.abs(deltaX);
        const absY = Math.abs(deltaY);
        
        if (absX > absY) {
            // Horizontal swipe
            const move = deltaX > 0 ? 'R' : 'L';
            this.applyMove(move);
        } else {
            // Vertical swipe
            const move = deltaY > 0 ? 'D' : 'U';
            this.applyMove(move);
        }
    }
    
    getFaceFromClick(event) {
        // Simplified face detection - in a real implementation,
        // this would use raycasting to determine which face was clicked
        const rect = this.renderer.canvas.getBoundingClientRect();
        const x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        const y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        
        // Simple quadrant-based face selection
        if (Math.abs(x) > Math.abs(y)) {
            return x > 0 ? 'R' : 'L';
        } else {
            return y > 0 ? 'U' : 'D';
        }
    }
    
    getFaceFromTouch(touch) {
        const rect = this.renderer.canvas.getBoundingClientRect();
        const x = ((touch.clientX - rect.left) / rect.width) * 2 - 1;
        const y = -((touch.clientY - rect.top) / rect.height) * 2 + 1;
        
        if (Math.abs(x) > Math.abs(y)) {
            return x > 0 ? 'R' : 'L';
        } else {
            return y > 0 ? 'U' : 'D';
        }
    }
    
    async applyMove(move) {
        if (!this.isControlEnabled) return;
        
        try {
            // Add to move history
            this.moveHistory.push(move);
            
            // Apply move through API
            const response = await this.apiClient.applyMove(move, true);
            
            // Animate the move
            const animationDuration = 500 / this.renderer.config.animationSpeed;
            this.renderer.animateMove(move, animationDuration);
            
            // Update statistics
            this.updateMoveCounter();
            this.updateCubeStatus(response.is_solved);
            
        } catch (error) {
            console.error('Failed to apply move:', error);
            this.showError('Failed to apply move: ' + move);
            
            // Remove from history if it failed
            this.moveHistory.pop();
        }
    }
    
    async scrambleCube() {
        if (!this.isControlEnabled) return;
        
        try {
            this.setControlsEnabled(false);
            
            const response = await this.apiClient.scrambleCube(20);
            
            // Clear move history on scramble
            this.moveHistory = [];
            
            // Update display
            this.updateMoveCounter();
            this.updateCubeStatus(false);
            
            // Show scrambled status
            const statusElement = document.getElementById('cube-status');
            if (statusElement) {
                statusElement.textContent = 'Scrambled';
                statusElement.classList.add('scrambled');
            }
            
        } catch (error) {
            console.error('Failed to scramble:', error);
            this.showError('Failed to scramble cube');
        } finally {
            this.setControlsEnabled(true);
        }
    }
    
    async resetCube() {
        if (!this.isControlEnabled) return;
        
        try {
            await this.apiClient.resetCube();
            
            // Clear move history
            this.moveHistory = [];
            
            // Update display
            this.updateMoveCounter();
            this.updateCubeStatus(true);
            
        } catch (error) {
            console.error('Failed to reset:', error);
            this.showError('Failed to reset cube');
        }
    }
    
    async solveCube() {
        if (!this.isControlEnabled) return;
        
        try {
            this.setControlsEnabled(false);
            
            const method = document.getElementById('solver-method')?.value || 'layer_by_layer';
            const solution = await this.apiClient.solveCube(method);
            
            // Display solution
            this.displaySolution(solution);
            
        } catch (error) {
            console.error('Failed to solve:', error);
            this.showError('Failed to solve cube');
        } finally {
            this.setControlsEnabled(true);
        }
    }
    
    undoMove() {
        if (this.moveHistory.length === 0) return;
        
        const lastMove = this.moveHistory.pop();
        const inverseMove = this.getInverseMove(lastMove);
        
        // Apply inverse move without adding to history
        this.applyMoveWithoutHistory(inverseMove);
    }
    
    redoMove() {
        // TODO: Implement redo functionality with separate redo stack
        console.log('Redo not yet implemented');
    }
    
    getInverseMove(move) {
        if (move.includes("'")) {
            return move.replace("'", "");
        } else if (move.includes("2")) {
            return move; // Double moves are their own inverse
        } else {
            return move + "'";
        }
    }
    
    async applyMoveWithoutHistory(move) {
        try {
            const response = await this.apiClient.applyMove(move, true);
            const animationDuration = 500 / this.renderer.config.animationSpeed;
            this.renderer.animateMove(move, animationDuration);
            
            this.updateMoveCounter();
            this.updateCubeStatus(response.is_solved);
            
        } catch (error) {
            console.error('Failed to apply move:', error);
        }
    }
    
    displaySolution(solution) {
        const solutionInfo = document.getElementById('solution-info');
        const solutionSteps = document.getElementById('solution-steps');
        const solutionMoves = document.getElementById('solution-moves');
        const solutionTime = document.getElementById('solution-time');
        
        if (!solutionInfo || !solution) return;
        
        // Show solution panel
        solutionInfo.style.display = 'block';
        
        // Update summary
        if (solutionMoves) {
            solutionMoves.textContent = `${solution.total_moves} moves`;
        }
        
        if (solutionTime) {
            solutionTime.textContent = `${solution.solve_time.toFixed(2)}s`;
        }
        
        // Display steps
        if (solutionSteps && solution.steps) {
            solutionSteps.innerHTML = '';
            
            solution.steps.forEach((step, index) => {
                const stepElement = document.createElement('div');
                stepElement.className = 'solution-step';
                stepElement.innerHTML = `
                    <div class="step-phase">${step.phase}</div>
                    <div class="step-moves">${step.moves}</div>
                `;
                solutionSteps.appendChild(stepElement);
            });
        }
        
        // Setup apply solution button
        const applyBtn = document.getElementById('apply-solution-btn');
        if (applyBtn) {
            applyBtn.onclick = () => this.applySolution(solution);
        }
    }
    
    async applySolution(solution) {
        if (!solution || !solution.steps) return;
        
        try {
            this.setControlsEnabled(false);
            
            // Apply each step with animation
            for (const step of solution.steps) {
                const moves = step.moves.split(' ').filter(move => move.trim());
                
                for (const move of moves) {
                    await this.applyMove(move.trim());
                    
                    // Wait for animation to complete
                    const animationDuration = 500 / this.renderer.config.animationSpeed;
                    await this.sleep(animationDuration + 100);
                }
            }
            
        } catch (error) {
            console.error('Failed to apply solution:', error);
            this.showError('Failed to apply solution');
        } finally {
            this.setControlsEnabled(true);
        }
    }
    
    updateMoveCounter() {
        const counter = document.getElementById('move-counter');
        const totalMoves = document.getElementById('total-moves');
        const count = this.moveHistory.length;
        
        if (counter) {
            counter.textContent = `${count} moves`;
        }
        
        if (totalMoves) {
            totalMoves.textContent = count.toString();
        }
    }
    
    updateCubeStatus(isSolved) {
        const statusElement = document.getElementById('cube-status');
        const stateElement = document.getElementById('cube-state');
        
        const status = isSolved ? 'Solved' : 'Scrambled';
        
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.classList.toggle('scrambled', !isSolved);
        }
        
        if (stateElement) {
            stateElement.textContent = status;
        }
    }
    
    setControlsEnabled(enabled) {
        this.isControlEnabled = enabled;
        
        // Update button states
        document.querySelectorAll('.control-btn, .action-btn').forEach(button => {
            button.disabled = !enabled;
        });
        
        // Show/hide loading state
        const loadingSpinner = document.getElementById('loading-spinner');
        if (loadingSpinner) {
            loadingSpinner.style.display = enabled ? 'none' : 'flex';
        }
    }
    
    showError(message) {
        // Simple error display - could be enhanced with toast notifications
        console.error(message);
        alert(message);
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Export for use in other modules
window.CubeController = CubeController;