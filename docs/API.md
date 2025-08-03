# API Documentation

## Table of Contents

- [Core Interfaces](#core-interfaces)
- [Domain Layer API](#domain-layer-api)
- [Application Layer API](#application-layer-api)
- [Infrastructure Layer API](#infrastructure-layer-api)
- [Data Models](#data-models)
- [Examples](#examples)

## Core Interfaces

### ICube Interface

The primary interface for interacting with Rubik's Cube state and operations.

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from .models import Move, CubeState

class ICube(ABC):
    """Abstract interface for Rubik's Cube representation"""
    
    @abstractmethod
    def execute_move(self, move: Move) -> None:
        """
        Execute a single move on the cube.
        
        Args:
            move: Move object representing the rotation to perform
            
        Raises:
            InvalidMoveError: If the move is not valid for current cube state
        """
        pass
    
    @abstractmethod
    def undo_move(self) -> bool:
        """
        Undo the last executed move.
        
        Returns:
            bool: True if undo was successful, False if no moves to undo
        """
        pass
    
    @abstractmethod
    def redo_move(self) -> bool:
        """
        Redo the next move in history.
        
        Returns:
            bool: True if redo was successful, False if no moves to redo
        """
        pass
    
    @abstractmethod
    def get_state(self) -> CubeState:
        """
        Get current cube state.
        
        Returns:
            CubeState: Complete state representation of the cube
        """
        pass
    
    @abstractmethod
    def is_solved(self) -> bool:
        """
        Check if cube is in solved state.
        
        Returns:
            bool: True if cube is solved, False otherwise
        """
        pass
    
    @abstractmethod
    def get_move_history(self) -> List[Move]:
        """
        Get complete move history.
        
        Returns:
            List[Move]: All moves executed on this cube
        """
        pass
    
    @abstractmethod
    def reset_to_solved(self) -> None:
        """Reset cube to solved state and clear history."""
        pass
    
    @abstractmethod
    def apply_scramble(self, scramble: List[Move]) -> None:
        """
        Apply a scramble sequence to the cube.
        
        Args:
            scramble: List of moves to scramble the cube
        """
        pass
```

### ISolver Interface

Interface for implementing solving algorithms.

```python
class ISolver(ABC):
    """Algorithm implementation interface"""
    
    @abstractmethod
    def solve(self, cube: ICube) -> SolutionResult:
        """
        Generate complete solution for the cube.
        
        Args:
            cube: Cube instance to solve
            
        Returns:
            SolutionResult: Complete solution with steps and analysis
        """
        pass
    
    @abstractmethod
    def get_next_step(self, cube: ICube) -> Optional[SolutionStep]:
        """
        Get next step for guided solving.
        
        Args:
            cube: Current cube state
            
        Returns:
            Optional[SolutionStep]: Next step to execute, or None if solved
        """
        pass
    
    @abstractmethod
    def analyze_cube(self, cube: ICube) -> AnalysisResult:
        """
        Analyze cube state and provide insights.
        
        Args:
            cube: Cube to analyze
            
        Returns:
            AnalysisResult: Analysis including phase, difficulty, suggestions
        """
        pass
    
    @abstractmethod
    def get_algorithm_name(self) -> str:
        """Get human-readable name of this solving method."""
        pass
    
    @abstractmethod
    def supports_cube_size(self, size: int) -> bool:
        """
        Check if this solver supports given cube size.
        
        Args:
            size: Cube size (2-10)
            
        Returns:
            bool: True if supported, False otherwise
        """
        pass
```

## Domain Layer API

### Cube Class

Main implementation of the ICube interface.

```python
class Cube(ICube):
    """Primary Rubik's Cube implementation"""
    
    def __init__(self, size: int = 3):
        """
        Initialize cube with specified size.
        
        Args:
            size: Cube size (2-10), defaults to 3x3
            
        Raises:
            ValueError: If size is not in valid range
        """
        
    def execute_move(self, move: Move) -> None:
        """Execute move and update internal state."""
        
    def get_face_colors(self, face: str) -> List[List[Color]]:
        """
        Get 2D color array for specific face.
        
        Args:
            face: Face identifier ('U', 'D', 'L', 'R', 'F', 'B')
            
        Returns:
            List[List[Color]]: 2D array of face colors
            
        Raises:
            ValueError: If face identifier is invalid
        """
        
    def set_color_scheme(self, colors: Dict[str, Color]) -> None:
        """
        Set custom color scheme.
        
        Args:
            colors: Mapping of face names to Color objects
        """
        
    def clone(self) -> 'Cube':
        """Create deep copy of cube state."""
        
    def from_state_string(self, state: str) -> None:
        """
        Load cube from state string representation.
        
        Args:
            state: State string in standard format
            
        Raises:
            InvalidStateError: If state string is malformed
        """
        
    def to_state_string(self) -> str:
        """Export cube state as string."""
```

### Move System

```python
@dataclass(frozen=True)
class Move:
    """Represents a single cube move"""
    face: str  # R, L, U, D, F, B, M, E, S, x, y, z
    direction: int  # 1 (clockwise), -1 (counter), 2 (double)
    wide: bool = False  # Wide turn modifier
    
    def inverse(self) -> 'Move':
        """Get inverse of this move."""
        
    def to_notation(self) -> str:
        """Convert to standard notation (R, R', R2, etc.)."""
        
    @classmethod
    def from_notation(cls, notation: str) -> 'Move':
        """
        Parse move from standard notation.
        
        Args:
            notation: Move in standard notation (e.g., "R", "U'", "Rw2")
            
        Returns:
            Move: Parsed move object
            
        Raises:
            ParseError: If notation is invalid
        """

class MoveSequence:
    """Represents a sequence of moves"""
    
    def __init__(self, moves: List[Move] = None):
        """Initialize with optional move list."""
        
    def add_move(self, move: Move) -> None:
        """Add move to sequence."""
        
    def optimize(self) -> 'MoveSequence':
        """
        Optimize sequence by removing redundant moves.
        
        Returns:
            MoveSequence: Optimized sequence
        """
        
    def inverse(self) -> 'MoveSequence':
        """Get inverse sequence."""
        
    def to_notation(self) -> str:
        """Convert to space-separated notation string."""
        
    @classmethod
    def from_notation(cls, notation: str) -> 'MoveSequence':
        """Parse sequence from notation string."""
```

### Solving Algorithms

```python
class CFOPSolver(ISolver):
    """Advanced CFOP solving method"""
    
    def __init__(self):
        """Initialize with complete algorithm databases."""
        
    def solve(self, cube: ICube) -> SolutionResult:
        """Execute CFOP solve with pattern recognition."""
        
    def solve_cross(self, cube: ICube) -> List[SolutionStep]:
        """Solve bottom cross."""
        
    def solve_f2l(self, cube: ICube) -> List[SolutionStep]:
        """Solve First Two Layers."""
        
    def solve_oll(self, cube: ICube) -> List[SolutionStep]:
        """Orient Last Layer using pattern recognition."""
        
    def solve_pll(self, cube: ICube) -> List[SolutionStep]:
        """Permute Last Layer using pattern recognition."""
        
    def get_oll_case(self, cube: ICube) -> Optional[OLLCase]:
        """Identify current OLL case."""
        
    def get_pll_case(self, cube: ICube) -> Optional[PLLCase]:
        """Identify current PLL case."""

class LayerByLayerSolver(ISolver):
    """Beginner-friendly layer-by-layer method"""
    
    def solve(self, cube: ICube) -> SolutionResult:
        """Execute layer-by-layer solve."""
        
    def solve_cross(self, cube: ICube) -> List[SolutionStep]:
        """Solve cross with detailed explanations."""
        
    def solve_first_layer_corners(self, cube: ICube) -> List[SolutionStep]:
        """Complete first layer."""
        
    def solve_middle_layer(self, cube: ICube) -> List[SolutionStep]:
        """Solve middle layer edges."""
        
    def solve_last_layer(self, cube: ICube) -> List[SolutionStep]:
        """Complete last layer using basic algorithms."""
```

## Application Layer API

### Game Session Management

```python
class GameSession:
    """Manages overall game state and coordination"""
    
    def __init__(self, cube_size: int = 3):
        """Initialize game session with specified cube size."""
        
    def start_session(self) -> None:
        """Start new solving session."""
        
    def end_session(self) -> SessionStats:
        """End session and return statistics."""
        
    def scramble_cube(self, length: int = None) -> List[Move]:
        """
        Generate and apply scramble.
        
        Args:
            length: Scramble length, uses default if None
            
        Returns:
            List[Move]: Applied scramble sequence
        """
        
    def start_solve(self, method: str) -> None:
        """
        Begin solving with specified method.
        
        Args:
            method: Solving method name ('cfop', 'layer-by-layer', etc.)
        """
        
    def complete_solve(self) -> SolveResult:
        """Complete current solve and record results."""
        
    def pause_solve(self) -> None:
        """Pause current solving session."""
        
    def reset_cube(self) -> None:
        """Reset cube to solved state."""
        
    def get_current_stats(self) -> SessionStats:
        """Get current session statistics."""

class TimerService:
    """Timing and performance tracking"""
    
    def start_timer(self) -> None:
        """Start solving timer."""
        
    def stop_timer(self) -> TimeResult:
        """Stop timer and return result."""
        
    def pause_timer(self) -> None:
        """Pause timer (maintains elapsed time)."""
        
    def resume_timer(self) -> None:
        """Resume paused timer."""
        
    def reset_timer(self) -> None:
        """Reset timer to zero."""
        
    def set_inspection_time(self, seconds: int) -> None:
        """Set inspection time before solve starts."""
        
    def get_current_time(self) -> float:
        """Get current elapsed time."""
        
    def record_solve(self, result: SolveResult) -> None:
        """Record completed solve in history."""
        
    def get_statistics(self) -> TimingStats:
        """Get comprehensive timing statistics."""
        
    def calculate_average(self, count: int) -> Optional[float]:
        """
        Calculate average of last N solves.
        
        Args:
            count: Number of recent solves to average
            
        Returns:
            Optional[float]: Average time, or None if insufficient data
        """
```

### Animation Management

```python
class AnimationManager:
    """Coordinates cube animations and transitions"""
    
    def animate_move(self, move: Move, duration: float = 0.3) -> AnimationHandle:
        """
        Animate single move execution.
        
        Args:
            move: Move to animate
            duration: Animation duration in seconds
            
        Returns:
            AnimationHandle: Handle for controlling animation
        """
        
    def animate_sequence(self, moves: List[Move], 
                        duration_per_move: float = 0.3) -> AnimationHandle:
        """
        Animate sequence of moves.
        
        Args:
            moves: Sequence of moves to animate
            duration_per_move: Duration for each move
            
        Returns:
            AnimationHandle: Handle for controlling animation sequence
        """
        
    def set_animation_speed(self, speed: float) -> None:
        """
        Set global animation speed multiplier.
        
        Args:
            speed: Speed multiplier (0.1 = very slow, 10.0 = very fast)
        """
        
    def is_animating(self) -> bool:
        """Check if any animations are currently running."""
        
    def cancel_all_animations(self) -> None:
        """Cancel all running animations."""
        
    def set_animation_quality(self, quality: str) -> None:
        """
        Set animation quality level.
        
        Args:
            quality: Quality level ('low', 'medium', 'high')
        """

class AnimationHandle:
    """Handle for controlling specific animation"""
    
    def pause(self) -> None:
        """Pause animation."""
        
    def resume(self) -> None:
        """Resume paused animation."""
        
    def cancel(self) -> None:
        """Cancel animation."""
        
    def set_speed(self, speed: float) -> None:
        """Set speed for this animation."""
        
    def is_complete(self) -> bool:
        """Check if animation has completed."""
        
    def get_progress(self) -> float:
        """Get animation progress (0.0 to 1.0)."""
```

## Infrastructure Layer API

### Rendering System

```python
class Renderer:
    """3D graphics rendering abstraction"""
    
    def __init__(self, window_width: int, window_height: int):
        """Initialize renderer with window dimensions."""
        
    def render_cube(self, cube: ICube, camera: Camera) -> None:
        """Render cube with current camera view."""
        
    def update_animation(self, delta_time: float) -> None:
        """Update animation state for current frame."""
        
    def set_lighting(self, config: LightingConfig) -> None:
        """Configure lighting settings."""
        
    def set_materials(self, config: MaterialConfig) -> None:
        """Configure material properties."""
        
    def set_camera(self, camera: Camera) -> None:
        """Set camera for rendering."""
        
    def resize_viewport(self, width: int, height: int) -> None:
        """Resize rendering viewport."""
        
    def capture_screenshot(self) -> Image:
        """Capture current frame as image."""
        
    def set_quality_level(self, level: str) -> None:
        """
        Set rendering quality level.
        
        Args:
            level: Quality level ('low', 'medium', 'high')
        """
        
    def enable_feature(self, feature: str) -> None:
        """
        Enable rendering feature.
        
        Args:
            feature: Feature name ('shadows', 'reflections', 'antialiasing')
        """
        
    def disable_feature(self, feature: str) -> None:
        """Disable rendering feature."""

class Camera:
    """3D camera for cube viewing"""
    
    def __init__(self):
        """Initialize camera with default position."""
        
    def rotate(self, x_angle: float, y_angle: float) -> None:
        """Rotate camera around cube."""
        
    def zoom(self, factor: float) -> None:
        """Zoom in/out by factor."""
        
    def pan(self, x_offset: float, y_offset: float) -> None:
        """Pan camera position."""
        
    def reset_position(self) -> None:
        """Reset camera to default position."""
        
    def get_distance_to_cube(self) -> float:
        """Get current distance from cube center."""
        
    def set_auto_rotate(self, enabled: bool, speed: float = 1.0) -> None:
        """Enable/disable automatic rotation."""
```

### Input Handling

```python
class InputHandler:
    """User input processing"""
    
    def register_move_callback(self, callback: Callable[[Move], None]) -> None:
        """Register callback for move input events."""
        
    def register_camera_callback(self, callback: Callable[[CameraAction], None]) -> None:
        """Register callback for camera input events."""
        
    def set_input_mode(self, mode: InputMode) -> None:
        """
        Set input handling mode.
        
        Args:
            mode: Input mode ('normal', 'algorithm_entry', 'camera_only')
        """
        
    def process_mouse_input(self, event: MouseEvent) -> None:
        """Process mouse input event."""
        
    def process_keyboard_input(self, event: KeyboardEvent) -> None:
        """Process keyboard input event."""
        
    def set_sensitivity(self, mouse: float, keyboard: float) -> None:
        """Set input sensitivity levels."""
        
    def enable_touch_input(self) -> None:
        """Enable touch input for mobile devices."""
        
    def get_key_bindings(self) -> Dict[str, str]:
        """Get current key binding configuration."""
        
    def set_key_bindings(self, bindings: Dict[str, str]) -> None:
        """Set custom key bindings."""

enum InputMode:
    NORMAL = "normal"
    ALGORITHM_ENTRY = "algorithm_entry"
    CAMERA_ONLY = "camera_only"
    DISABLED = "disabled"
```

## Data Models

### Core Data Types

```python
@dataclass(frozen=True)
class Color:
    """RGB color representation"""
    r: int  # 0-255
    g: int  # 0-255
    b: int  # 0-255
    name: str  # Human-readable name
    
    def to_hex(self) -> str:
        """Convert to hex color string."""
        
    @classmethod
    def from_hex(cls, hex_string: str) -> 'Color':
        """Create color from hex string."""

@dataclass
class SolutionStep:
    """Single step in solving process"""
    move: Move
    explanation: str
    algorithm_name: str
    phase: str
    estimated_time: float
    difficulty: int  # 1-5 scale

@dataclass
class SolutionResult:
    """Complete solution analysis"""
    steps: List[SolutionStep]
    total_moves: int
    estimated_time: float
    method: str
    efficiency_score: float
    phases: Dict[str, int]  # Move count per phase

@dataclass
class SolveResult:
    """Individual solve result"""
    time: float
    move_count: int
    tps: float  # Turns per second
    method: str
    scramble: List[Move]
    timestamp: datetime
    was_dnf: bool = False  # Did Not Finish

@dataclass
class SessionStats:
    """Session statistics"""
    total_solves: int
    best_time: float
    worst_time: float
    average_time: float
    average_of_5: Optional[float]
    average_of_12: Optional[float]
    total_time: float
    solve_history: List[SolveResult]
```

## Examples

### Basic Usage

```python
from rcsim import Cube, CFOPSolver, GameSession

# Create 3x3 cube
cube = Cube(size=3)

# Apply scramble
scramble = cube.generate_scramble(length=25)
cube.apply_scramble(scramble)

# Solve using CFOP
solver = CFOPSolver()
solution = solver.solve(cube)

print(f"Solution found in {solution.total_moves} moves")
for step in solution.steps:
    print(f"{step.move.to_notation()}: {step.explanation}")
```

### Game Session

```python
from rcsim import GameSession, TimerService

# Start game session
session = GameSession(cube_size=3)
session.start_session()

# Generate scramble and start solving
scramble = session.scramble_cube()
session.start_solve(method='cfop')

# Execute moves (from user input)
session.cube.execute_move(Move.from_notation("R"))
session.cube.execute_move(Move.from_notation("U"))

# Complete solve
result = session.complete_solve()
print(f"Solve completed in {result.time:.2f} seconds")
```

### Animation Example

```python
from rcsim import Cube, AnimationManager, Renderer

cube = Cube(3)
renderer = Renderer(800, 600)
animator = AnimationManager()

# Animate move sequence
moves = [Move.from_notation(m) for m in ["R", "U", "R'", "U'"]]
handle = animator.animate_sequence(moves, duration_per_move=0.5)

# Render loop
while not handle.is_complete():
    animator.update_animation(delta_time)
    renderer.render_cube(cube, camera)
    renderer.present_frame()
```

### Custom Solver

```python
from rcsim import ISolver, SolutionResult

class CustomSolver(ISolver):
    def solve(self, cube: ICube) -> SolutionResult:
        # Implement custom solving logic
        steps = []
        # ... solving implementation
        return SolutionResult(
            steps=steps,
            total_moves=len(steps),
            method="Custom Method",
            estimated_time=len(steps) * 0.5
        )
    
    def get_algorithm_name(self) -> str:
        return "Custom Solver"
    
    def supports_cube_size(self, size: int) -> bool:
        return size == 3  # Only 3x3 support
```

### Pattern Recognition

```python
from rcsim import Cube, OLLDatabase

cube = Cube(3)
# ... scramble and solve to last layer
oll_db = OLLDatabase()

# Recognize OLL case
case = oll_db.recognize_case(cube.get_state())
if case:
    print(f"Detected: {case.name}")
    print(f"Algorithm: {case.get_algorithm_notation()}")
    
    # Apply algorithm
    cube.apply_sequence(case.solution)
```