/**
 * Solver UI - Manages solving interface and algorithm display
 * Handles solver selection, solution visualization, and step-by-step execution
 */

class SolverUI {
    constructor(apiClient) {
        this.apiClient = apiClient;
        this.currentSolution = null;
        this.currentStepIndex = 0;
        this.isApplyingSolution = false;
        
        this.init();
    }
    
    init() {
        this.setupSolverControls();
        this.loadAvailableSolvers();
    }
    
    async loadAvailableSolvers() {
        try {
            const solvers = await this.apiClient.getAvailableSolvers();
            this.populateSolverDropdown(solvers);
        } catch (error) {
            console.error('Failed to load solvers:', error);
        }
    }
    
    populateSolverDropdown(solvers) {
        const dropdown = document.getElementById('solver-method');
        if (!dropdown || !solvers.descriptions) return;
        
        dropdown.innerHTML = '';
        
        Object.entries(solvers.descriptions).forEach(([key, description]) => {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = description;
            dropdown.appendChild(option);
        });
    }
    
    setupSolverControls() {
        const solveBtn = document.getElementById('solve-btn');
        const applySolutionBtn = document.getElementById('apply-solution-btn');
        
        if (solveBtn) {
            solveBtn.addEventListener('click', () => this.handleSolveRequest());
        }
        
        if (applySolutionBtn) {
            applySolutionBtn.addEventListener('click', () => this.handleApplySolution());
        }
        
        // Step-by-step controls (if we add them later)
        this.setupStepControls();
    }
    
    setupStepControls() {
        // Add step-by-step navigation buttons
        const solutionInfo = document.getElementById('solution-info');
        if (!solutionInfo) return;
        
        // Create step navigation if it doesn't exist
        let stepNav = solutionInfo.querySelector('.step-navigation');
        if (!stepNav) {
            stepNav = document.createElement('div');
            stepNav.className = 'step-navigation';
            stepNav.style.display = 'none';
            stepNav.innerHTML = `
                <div class="step-controls">
                    <button id="prev-step-btn" class="action-btn secondary">← Previous</button>
                    <span id="step-indicator">Step 1 of 1</span>
                    <button id="next-step-btn" class="action-btn secondary">Next →</button>
                </div>
                <div class="step-progress">
                    <div id="step-progress-bar" class="progress-bar"></div>
                </div>
            `;
            
            // Insert before apply button
            const applyBtn = document.getElementById('apply-solution-btn');
            if (applyBtn) {
                solutionInfo.insertBefore(stepNav, applyBtn);
            } else {
                solutionInfo.appendChild(stepNav);
            }
        }
        
        // Setup step navigation events
        const prevBtn = document.getElementById('prev-step-btn');
        const nextBtn = document.getElementById('next-step-btn');
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.previousStep());
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.nextStep());
        }
    }
    
    async handleSolveRequest() {
        const solveBtn = document.getElementById('solve-btn');
        const solverMethod = document.getElementById('solver-method')?.value || 'layer_by_layer';
        
        if (!solveBtn) return;
        
        try {
            // Show loading state
            solveBtn.disabled = true;
            solveBtn.textContent = '🧠 Solving...';
            
            // Hide previous solution
            this.hideSolution();
            
            // Request solution from API
            const solution = await this.apiClient.solveCube(solverMethod);
            
            // Display the solution
            this.displaySolution(solution);
            this.currentSolution = solution;
            this.currentStepIndex = 0;
            
        } catch (error) {
            console.error('Failed to solve cube:', error);
            this.showError('Failed to solve cube: ' + error.message);
        } finally {
            // Reset button state
            solveBtn.disabled = false;
            solveBtn.textContent = '🚀 Solve';
        }
    }
    
    displaySolution(solution) {
        if (!solution) return;
        
        const solutionInfo = document.getElementById('solution-info');
        const solutionSteps = document.getElementById('solution-steps');
        const solutionMoves = document.getElementById('solution-moves');
        const solutionTime = document.getElementById('solution-time');
        
        if (!solutionInfo) return;
        
        // Show solution panel
        solutionInfo.style.display = 'block';
        
        // Update summary statistics
        if (solutionMoves) {
            solutionMoves.textContent = `${solution.total_moves} moves`;
        }
        
        if (solutionTime) {
            const timeText = solution.solve_time ? `${solution.solve_time.toFixed(2)}s` : 'N/A';
            solutionTime.textContent = timeText;
        }
        
        // Display solution steps
        this.displaySolutionSteps(solution.steps);
        
        // Show step navigation if multiple steps
        if (solution.steps && solution.steps.length > 1) {
            this.showStepNavigation(solution.steps.length);
        }
        
        // Add method-specific information
        this.displayMethodInfo(solution);
    }
    
    displaySolutionSteps(steps) {
        const solutionSteps = document.getElementById('solution-steps');
        if (!solutionSteps || !steps) return;
        
        solutionSteps.innerHTML = '';
        
        steps.forEach((step, index) => {
            const stepElement = document.createElement('div');
            stepElement.className = 'solution-step';
            stepElement.dataset.stepIndex = index;
            
            // Create step content
            const phaseElement = document.createElement('div');
            phaseElement.className = 'step-phase';
            phaseElement.textContent = step.phase;
            
            const descElement = document.createElement('div');
            descElement.className = 'step-description';
            descElement.textContent = step.description || '';
            
            const movesElement = document.createElement('div');
            movesElement.className = 'step-moves';
            movesElement.textContent = step.moves;
            
            const countElement = document.createElement('div');
            countElement.className = 'step-count';
            countElement.textContent = `${step.move_count} moves`;
            
            stepElement.appendChild(phaseElement);
            if (step.description) {
                stepElement.appendChild(descElement);
            }
            stepElement.appendChild(movesElement);
            stepElement.appendChild(countElement);
            
            // Add explanation if available
            if (step.explanation) {
                const explanationElement = document.createElement('div');
                explanationElement.className = 'step-explanation';
                explanationElement.textContent = step.explanation;
                explanationElement.style.display = 'none'; // Hidden by default
                stepElement.appendChild(explanationElement);
                
                // Add expand/collapse button
                const toggleButton = document.createElement('button');
                toggleButton.className = 'step-toggle';
                toggleButton.textContent = 'Show Details';
                toggleButton.onclick = () => this.toggleStepDetails(stepElement);
                stepElement.appendChild(toggleButton);
            }
            
            // Make step clickable to highlight
            stepElement.addEventListener('click', () => {
                this.highlightStep(index);
            });
            
            solutionSteps.appendChild(stepElement);
        });
    }
    
    displayMethodInfo(solution) {
        // Add method-specific information panel
        let methodInfo = document.querySelector('.method-info');
        if (!methodInfo) {
            methodInfo = document.createElement('div');
            methodInfo.className = 'method-info';
            
            const solutionInfo = document.getElementById('solution-info');
            if (solutionInfo) {
                solutionInfo.appendChild(methodInfo);
            }
        }
        
        let infoContent = `<h4>Method: ${solution.method.toUpperCase()}</h4>`;
        
        if (solution.summary) {
            infoContent += `<p>${solution.summary}</p>`;
        }
        
        // Add method-specific statistics
        if (solution.method === 'cfop') {
            infoContent += this.getCFOPStats(solution.steps);
        } else if (solution.method === 'layer_by_layer') {
            infoContent += this.getLayerByLayerStats(solution.steps);
        }
        
        methodInfo.innerHTML = infoContent;
    }
    
    getCFOPStats(steps) {
        const phases = ['Cross', 'F2L', 'OLL', 'PLL'];
        let stats = '<div class="method-stats">';
        
        phases.forEach(phase => {
            const phaseSteps = steps.filter(step => step.phase.includes(phase));
            const totalMoves = phaseSteps.reduce((sum, step) => sum + step.move_count, 0);
            
            stats += `<div class="phase-stat">
                <span class="phase-name">${phase}:</span>
                <span class="phase-moves">${totalMoves} moves</span>
            </div>`;
        });
        
        stats += '</div>';
        return stats;
    }
    
    getLayerByLayerStats(steps) {
        const layers = ['Bottom Cross', 'Bottom Corners', 'Middle Layer', 'Top Cross', 'Top Face', 'Final Layer'];
        let stats = '<div class="method-stats">';
        
        steps.forEach((step, index) => {
            stats += `<div class="phase-stat">
                <span class="phase-name">${step.phase}:</span>
                <span class="phase-moves">${step.move_count} moves</span>
            </div>`;
        });
        
        stats += '</div>';
        return stats;
    }
    
    showStepNavigation(totalSteps) {
        const stepNav = document.querySelector('.step-navigation');
        if (stepNav) {
            stepNav.style.display = 'block';
            this.updateStepIndicator(0, totalSteps);
        }
    }
    
    updateStepIndicator(currentStep, totalSteps) {
        const indicator = document.getElementById('step-indicator');
        const progressBar = document.getElementById('step-progress-bar');
        const prevBtn = document.getElementById('prev-step-btn');
        const nextBtn = document.getElementById('next-step-btn');
        
        if (indicator) {
            indicator.textContent = `Step ${currentStep + 1} of ${totalSteps}`;
        }
        
        if (progressBar) {
            const progress = ((currentStep + 1) / totalSteps) * 100;
            progressBar.style.width = `${progress}%`;
        }
        
        if (prevBtn) {
            prevBtn.disabled = currentStep === 0;
        }
        
        if (nextBtn) {
            nextBtn.disabled = currentStep === totalSteps - 1;
        }
    }
    
    previousStep() {
        if (this.currentStepIndex > 0) {
            this.currentStepIndex--;
            this.highlightStep(this.currentStepIndex);
        }
    }
    
    nextStep() {
        if (this.currentSolution && this.currentStepIndex < this.currentSolution.steps.length - 1) {
            this.currentStepIndex++;
            this.highlightStep(this.currentStepIndex);
        }
    }
    
    highlightStep(stepIndex) {
        // Remove previous highlights
        document.querySelectorAll('.solution-step').forEach(step => {
            step.classList.remove('highlighted');
        });
        
        // Highlight current step
        const stepElement = document.querySelector(`[data-step-index="${stepIndex}"]`);
        if (stepElement) {
            stepElement.classList.add('highlighted');
            stepElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
        
        // Update navigation
        if (this.currentSolution) {
            this.updateStepIndicator(stepIndex, this.currentSolution.steps.length);
        }
        
        this.currentStepIndex = stepIndex;
    }
    
    toggleStepDetails(stepElement) {
        const explanation = stepElement.querySelector('.step-explanation');
        const toggleButton = stepElement.querySelector('.step-toggle');
        
        if (explanation && toggleButton) {
            const isVisible = explanation.style.display !== 'none';
            explanation.style.display = isVisible ? 'none' : 'block';
            toggleButton.textContent = isVisible ? 'Show Details' : 'Hide Details';
        }
    }
    
    async handleApplySolution() {
        if (!this.currentSolution || this.isApplyingSolution) return;
        
        const applyBtn = document.getElementById('apply-solution-btn');
        if (applyBtn) {
            applyBtn.disabled = true;
            applyBtn.textContent = '▶ Applying...';
        }
        
        try {
            this.isApplyingSolution = true;
            
            // Apply solution through the controller
            // This assumes we have access to the controller instance
            if (window.cubeController) {
                await window.cubeController.applySolution(this.currentSolution);
            } else {
                // Fallback: apply moves directly
                await this.applySolutionDirect();
            }
            
        } catch (error) {
            console.error('Failed to apply solution:', error);
            this.showError('Failed to apply solution');
        } finally {
            this.isApplyingSolution = false;
            
            if (applyBtn) {
                applyBtn.disabled = false;
                applyBtn.textContent = '▶ Apply Solution';
            }
        }
    }
    
    async applySolutionDirect() {
        if (!this.currentSolution || !this.currentSolution.steps) return;
        
        for (const step of this.currentSolution.steps) {
            const moves = step.moves.split(' ').filter(move => move.trim());
            
            for (const move of moves) {
                await this.apiClient.applyMove(move.trim(), true);
                await this.sleep(200); // Small delay between moves
            }
        }
    }
    
    hideSolution() {
        const solutionInfo = document.getElementById('solution-info');
        if (solutionInfo) {
            solutionInfo.style.display = 'none';
        }
        
        const stepNav = document.querySelector('.step-navigation');
        if (stepNav) {
            stepNav.style.display = 'none';
        }
        
        this.currentSolution = null;
        this.currentStepIndex = 0;
    }
    
    showError(message) {
        console.error(message);
        
        // Create or update error display
        let errorElement = document.querySelector('.solver-error');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'solver-error';
            
            const solverSection = document.querySelector('.control-section h3[textContent*="Solver"]')?.parentElement;
            if (solverSection) {
                solverSection.appendChild(errorElement);
            }
        }
        
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorElement.style.display = 'none';
        }, 5000);
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Export for use in other modules
window.SolverUI = SolverUI;