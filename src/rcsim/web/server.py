"""FastAPI web server for the Rubik's Cube Simulator."""

import os
import json
import asyncio
from typing import Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import our cube logic
from ..cube import Cube
from ..solvers import LayerByLayerSolver, CFOPSolver


class CubeState(BaseModel):
    """Pydantic model for cube state."""
    size: int
    is_solved: bool
    move_count: int
    face_colors: Dict[str, List[List[str]]]  # Face colors as hex strings


class MoveRequest(BaseModel):
    """Request model for applying moves."""
    moves: str
    animate: bool = True


class SolveRequest(BaseModel):
    """Request model for solving."""
    method: str = "layer_by_layer"  # or "cfop"
    max_moves: Optional[int] = None


class CubeManager:
    """Manages cube instances and operations."""
    
    def __init__(self):
        self.cubes: Dict[str, Cube] = {}
        self.default_cube_id = "main"
        self.cubes[self.default_cube_id] = Cube(3)
        
        # Initialize solvers
        self.solvers = {
            "layer_by_layer": LayerByLayerSolver(),
            "cfop": CFOPSolver()
        }
    
    def get_cube(self, cube_id: str = None) -> Cube:
        """Get cube by ID, or default cube."""
        cube_id = cube_id or self.default_cube_id
        if cube_id not in self.cubes:
            self.cubes[cube_id] = Cube(3)
        return self.cubes[cube_id]
    
    def get_cube_state(self, cube_id: str = None) -> CubeState:
        """Get current state of cube as Pydantic model."""
        cube = self.get_cube(cube_id)
        
        # Convert face colors to hex strings
        face_colors = {}
        for face, colors in cube.get_all_face_colors().items():
            face_colors[face] = [[color.to_hex() for color in row] for row in colors]
        
        return CubeState(
            size=cube.size,
            is_solved=cube.is_solved(),
            move_count=cube.get_move_count(),
            face_colors=face_colors
        )
    
    def apply_moves(self, moves: str, cube_id: str = None) -> CubeState:
        """Apply moves to cube and return new state."""
        cube = self.get_cube(cube_id)
        cube.apply_sequence(moves)
        return self.get_cube_state(cube_id)
    
    def scramble_cube(self, num_moves: int = 20, cube_id: str = None) -> CubeState:
        """Scramble cube and return new state."""
        cube = self.get_cube(cube_id)
        cube.scramble(num_moves=num_moves)
        return self.get_cube_state(cube_id)
    
    def reset_cube(self, cube_id: str = None) -> CubeState:
        """Reset cube to solved state."""
        cube = self.get_cube(cube_id)
        cube.reset()
        return self.get_cube_state(cube_id)
    
    def solve_cube(self, method: str = "layer_by_layer", cube_id: str = None) -> Dict:
        """Solve cube using specified method."""
        cube = self.get_cube(cube_id)
        solver = self.solvers.get(method)
        
        if not solver:
            raise ValueError(f"Unknown solver method: {method}")
        
        if not solver.can_solve(cube):
            raise ValueError(f"Solver {method} cannot solve this cube")
        
        # Work on a copy to get solution steps
        cube_copy = cube.clone()
        steps = solver.solve(cube_copy)
        
        # Convert steps to JSON-serializable format
        solution_steps = []
        for step in steps:
            solution_steps.append({
                "phase": step.phase.value,
                "description": step.description,
                "moves": str(step.moves),
                "explanation": step.explanation,
                "move_count": len(step.moves)
            })
        
        return {
            "method": method,
            "steps": solution_steps,
            "total_moves": solver.total_moves,
            "solve_time": solver.solve_time,
            "summary": solver.get_solution_summary()
        }


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        if self.active_connections:
            message_str = json.dumps(message)
            for connection in self.active_connections:
                try:
                    await connection.send_text(message_str)
                except:
                    # Connection may have been closed
                    pass


# Initialize FastAPI app
app = FastAPI(
    title="Advanced Rubik's Cube Simulator",
    description="3D Web-based Rubik's Cube with authentic solving algorithms",
    version="1.0.0"
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
cube_manager = CubeManager()
connection_manager = ConnectionManager()

# Mount static files
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page."""
    html_file = static_path / "index.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(), status_code=200)
    else:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Advanced Rubik's Cube Simulator</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .error { color: #ff6b6b; }
            </style>
        </head>
        <body>
            <h1>Advanced Rubik's Cube Simulator</h1>
            <p class="error">Web interface is being set up...</p>
            <p>The HTML interface files are not yet created.</p>
        </body>
        </html>
        """, status_code=200)


# REST API Endpoints
@app.get("/api/cube/state")
async def get_cube_state(cube_id: Optional[str] = None):
    """Get current cube state."""
    try:
        state = cube_manager.get_cube_state(cube_id)
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cube/move")
async def apply_move(request: MoveRequest, cube_id: Optional[str] = None):
    """Apply moves to the cube."""
    try:
        state = cube_manager.apply_moves(request.moves, cube_id)
        
        # Broadcast state change to all connected clients
        await connection_manager.broadcast({
            "type": "cube_state_changed",
            "cube_id": cube_id or "main",
            "state": state.dict(),
            "moves_applied": request.moves,
            "animate": request.animate
        })
        
        return state
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/cube/scramble")
async def scramble_cube(num_moves: int = 20, cube_id: Optional[str] = None):
    """Scramble the cube."""
    try:
        state = cube_manager.scramble_cube(num_moves, cube_id)
        
        # Broadcast state change
        await connection_manager.broadcast({
            "type": "cube_scrambled",
            "cube_id": cube_id or "main",
            "state": state.dict(),
            "scramble_moves": num_moves
        })
        
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cube/reset")
async def reset_cube(cube_id: Optional[str] = None):
    """Reset cube to solved state."""
    try:
        state = cube_manager.reset_cube(cube_id)
        
        # Broadcast state change
        await connection_manager.broadcast({
            "type": "cube_reset",
            "cube_id": cube_id or "main",
            "state": state.dict()
        })
        
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cube/solve")
async def solve_cube(request: SolveRequest, cube_id: Optional[str] = None):
    """Get solution for the cube."""
    try:
        solution = cube_manager.solve_cube(request.method, cube_id)
        
        # Broadcast solution
        await connection_manager.broadcast({
            "type": "solution_found",
            "cube_id": cube_id or "main",
            "solution": solution
        })
        
        return solution
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/solvers")
async def get_available_solvers():
    """Get list of available solving methods."""
    return {
        "solvers": list(cube_manager.solvers.keys()),
        "descriptions": {
            "layer_by_layer": "Beginner's method - Layer by Layer solving",
            "cfop": "Advanced speedcubing method - CFOP (Cross, F2L, OLL, PLL)"
        }
    }


# WebSocket endpoint for real-time communication
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await connection_manager.connect(websocket)
    
    try:
        # Send initial cube state
        initial_state = cube_manager.get_cube_state()
        await websocket.send_text(json.dumps({
            "type": "initial_state",
            "state": initial_state.dict()
        }))
        
        while True:
            # Listen for client messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            
            elif message.get("type") == "get_state":
                state = cube_manager.get_cube_state()
                await websocket.send_text(json.dumps({
                    "type": "cube_state",
                    "state": state.dict()
                }))
    
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        connection_manager.disconnect(websocket)


def run_server(host: str = "127.0.0.1", port: int = 9090, debug: bool = True):
    """Run the FastAPI server."""
    print(f"🎲 Advanced Rubik's Cube Simulator")
    print(f"🌐 Starting web server at http://{host}:{port}")
    print(f"📁 Static files from: {static_path}")
    
    uvicorn.run(
        "rcsim.web.server:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )


if __name__ == "__main__":
    run_server()