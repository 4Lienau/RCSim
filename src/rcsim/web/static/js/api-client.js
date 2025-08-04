/**
 * API Client - Handles communication with the FastAPI backend
 * Provides methods for cube manipulation, solving, and real-time updates
 */

class APIClient {
    constructor(baseUrl = '', cubeId = 'main') {
        this.baseUrl = baseUrl;
        this.cubeId = cubeId;
        this.websocket = null;
        this.eventListeners = new Map();
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        
        this.init();
    }
    
    init() {
        this.connectWebSocket();
    }
    
    // WebSocket Connection Management
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        try {
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.emit('connected');
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket connection closed');
                this.isConnected = false;
                this.emit('disconnected');
                this.handleReconnection();
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.emit('error', error);
            };
            
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.handleReconnection();
        }
    }
    
    handleReconnection() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
            
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay}ms`);
            
            setTimeout(() => {
                this.connectWebSocket();
            }, delay);
        } else {
            console.error('Max reconnection attempts reached');
            this.emit('max_reconnect_attempts_reached');
        }
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'initial_state':
            case 'cube_state':
                this.emit('cube_state_update', data.state);
                break;
                
            case 'cube_state_changed':
                this.emit('cube_state_update', data.state);
                this.emit('moves_applied', {
                    moves: data.moves_applied,
                    animate: data.animate
                });
                break;
                
            case 'cube_scrambled':
                this.emit('cube_state_update', data.state);
                this.emit('cube_scrambled', {
                    scramble_moves: data.scramble_moves
                });
                break;
                
            case 'cube_reset':
                this.emit('cube_state_update', data.state);
                this.emit('cube_reset');
                break;
                
            case 'solution_found':
                this.emit('solution_found', data.solution);
                break;
                
            case 'pong':
                // Handle ping/pong for connection health
                break;
                
            default:
                console.log('Unknown WebSocket message type:', data.type);
        }
    }
    
    sendWebSocketMessage(message) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket not connected, cannot send message');
        }
    }
    
    // Event System
    on(event, callback) {
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, []);
        }
        this.eventListeners.get(event).push(callback);
    }
    
    off(event, callback) {
        if (this.eventListeners.has(event)) {
            const listeners = this.eventListeners.get(event);
            const index = listeners.indexOf(callback);
            if (index > -1) {
                listeners.splice(index, 1);
            }
        }
    }
    
    emit(event, data = null) {
        if (this.eventListeners.has(event)) {
            this.eventListeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in event listener for ${event}:`, error);
                }
            });
        }
    }
    
    // REST API Methods
    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseUrl}/api${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        const requestOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, requestOptions);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    }
    
    // Cube State Methods
    async getCubeState() {
        return await this.makeRequest(`/cube/state?cube_id=${this.cubeId}`);
    }
    
    async applyMove(moves, animate = true) {
        return await this.makeRequest('/cube/move', {
            method: 'POST',
            body: JSON.stringify({
                moves: moves,
                animate: animate
            })
        });
    }
    
    async scrambleCube(numMoves = 20) {
        return await this.makeRequest(`/cube/scramble?num_moves=${numMoves}&cube_id=${this.cubeId}`, {
            method: 'POST'
        });
    }
    
    async resetCube() {
        return await this.makeRequest(`/cube/reset?cube_id=${this.cubeId}`, {
            method: 'POST'
        });
    }
    
    // Solver Methods
    async solveCube(method = 'layer_by_layer', maxMoves = null) {
        const body = { method };
        if (maxMoves !== null) {
            body.max_moves = maxMoves;
        }
        
        return await this.makeRequest('/cube/solve', {
            method: 'POST',
            body: JSON.stringify(body)
        });
    }
    
    async getAvailableSolvers() {
        return await this.makeRequest('/solvers');
    }
    
    // Connection Health
    ping() {
        this.sendWebSocketMessage({ type: 'ping' });
    }
    
    startHealthCheck(interval = 30000) {
        setInterval(() => {
            if (this.isConnected) {
                this.ping();
            }
        }, interval);
    }
    
    // Utility Methods
    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            websocketState: this.websocket ? this.websocket.readyState : null,
            reconnectAttempts: this.reconnectAttempts
        };
    }
    
    disconnect() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        this.isConnected = false;
    }
    
    // Batch Operations
    async applyMoveSequence(moves, animateEach = true, delayBetweenMoves = 100) {
        const moveList = moves.split(/\s+/).filter(move => move.trim());
        const results = [];
        
        for (let i = 0; i < moveList.length; i++) {
            const move = moveList[i].trim();
            
            try {
                const result = await this.applyMove(move, animateEach);
                results.push({ move, success: true, result });
                
                // Add delay between moves if specified
                if (delayBetweenMoves > 0 && i < moveList.length - 1) {
                    await new Promise(resolve => setTimeout(resolve, delayBetweenMoves));
                }
                
            } catch (error) {
                console.error(`Failed to apply move ${move}:`, error);
                results.push({ move, success: false, error: error.message });
            }
        }
        
        return results;
    }
    
    // Statistics and Monitoring
    getStatistics() {
        return {
            connectionStatus: this.getConnectionStatus(),
            reconnectAttempts: this.reconnectAttempts,
            eventListeners: Array.from(this.eventListeners.keys()),
            cubeId: this.cubeId
        };
    }
}

// Export for use in other modules
window.APIClient = APIClient;