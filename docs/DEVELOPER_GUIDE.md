# Developer Guide

## Table of Contents

- [Getting Started](#getting-started)
- [Architecture Overview](#architecture-overview)
- [Core Concepts](#core-concepts)
- [Development Workflow](#development-workflow)
- [Testing Strategy](#testing-strategy)
- [Performance Guidelines](#performance-guidelines)
- [Contributing](#contributing)

## Getting Started

### Prerequisites

- Python 3.9+ with development headers
- OpenGL 3.3+ compatible graphics card
- Git for version control

### Development Setup

```bash
# Clone repository
git clone https://github.com/your-username/rcsim.git
cd rcsim

# Create development environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests to verify setup
pytest tests/
```

### Development Dependencies

```txt
# Core dependencies
numpy>=1.21.0
pygame>=2.1.0
PyOpenGL>=3.1.0
moderngl>=5.6.0

# Development tools
pytest>=7.0.0
pytest-cov>=4.0.0
black>=22.0.0
flake8>=5.0.0
mypy>=0.991
pre-commit>=2.20.0

# Documentation
sphinx>=5.0.0
sphinx-rtd-theme>=1.0.0
```

### Project Structure

```
rcsim/
├── src/
│   ├── rcsim/
│   │   ├── __init__.py
│   │   ├── cube/              # Core cube logic
│   │   │   ├── __init__.py
│   │   │   ├── cube.py        # Main Cube class
│   │   │   ├── state.py       # CubeState representation
│   │   │   ├── moves.py       # Move system
│   │   │   └── validation.py  # Move validation
│   │   ├── solvers/           # Solving algorithms
│   │   │   ├── __init__.py
│   │   │   ├── base.py        # ISolver interface
│   │   │   ├── cfop.py        # CFOP implementation
│   │   │   ├── layer_by_layer.py
│   │   │   ├── pattern_db/    # Algorithm databases
│   │   │   │   ├── oll.py     # OLL patterns
│   │   │   │   ├── pll.py     # PLL patterns
│   │   │   │   └── f2l.py     # F2L cases
│   │   │   └── utils.py       # Solving utilities
│   │   ├── graphics/          # 3D rendering
│   │   │   ├── __init__.py
│   │   │   ├── renderer.py    # Main renderer
│   │   │   ├── camera.py      # Camera system
│   │   │   ├── shaders/       # Shader programs
│   │   │   ├── models/        # 3D models
│   │   │   └── animations.py  # Animation system
│   │   ├── ui/                # User interface
│   │   │   ├── __init__.py
│   │   │   ├── main_window.py
│   │   │   ├── controls.py
│   │   │   ├── settings.py
│   │   │   └── widgets/       # UI components
│   │   ├── app/               # Application layer
│   │   │   ├── __init__.py
│   │   │   ├── game_session.py
│   │   │   ├── timer.py
│   │   │   ├── statistics.py
│   │   │   └── state_manager.py
│   │   └── utils/             # Utilities
│   │       ├── __init__.py
│   │       ├── scrambler.py
│   │       ├── notation.py
│   │       ├── config.py
│   │       └── performance.py
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   ├── fixtures/             # Test fixtures
│   └── conftest.py           # Pytest configuration
├── docs/                      # Documentation
├── assets/                    # 3D models, textures
├── examples/                  # Example scripts
├── scripts/                   # Build and utility scripts
└── requirements*.txt          # Dependencies
```

## Architecture Overview

### Layered Architecture

The simulator follows a clean architecture with four main layers:

```
┌─────────────────────────────────────────┐
│           Presentation Layer            │  ← UI components, input handling
├─────────────────────────────────────────┤
│          Application Layer              │  ← Use cases, orchestration
├─────────────────────────────────────────┤
│            Domain Layer                 │  ← Business logic, algorithms
├─────────────────────────────────────────┤
│         Infrastructure Layer            │  ← Graphics, storage, external APIs
└─────────────────────────────────────────┘
```

### Key Design Principles

1. **Separation of Concerns**: Each layer has distinct responsibilities
2. **Dependency Inversion**: Higher layers depend on abstractions, not implementations
3. **Single Responsibility**: Classes have one reason to change
4. **Open/Closed**: Open for extension, closed for modification
5. **Interface Segregation**: Clients depend only on interfaces they use

### Core Dependencies

```python
# Domain layer (no dependencies on other layers)
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict

# Application layer (depends only on domain)
from rcsim.cube import ICube, Move
from rcsim.solvers import ISolver

# Infrastructure layer (implements domain interfaces)
from rcsim.cube import ICube
from rcsim.graphics import IRenderer
```

## Core Concepts

### Cube Representation

The cube is represented using a coordinate-based system where each piece (cubie) has:

- **Position**: 3D coordinates in cube space
- **Orientation**: How the piece is rotated
- **Colors**: Face colors visible on the cube

```python
@dataclass(frozen=True)
class Position:
    x: int  # -1 to 1 for 3x3 (center = 0)
    y: int
    z: int

class Cubie:
    def __init__(self, position: Position, colors: Dict[str, Color]):
        self.position = position
        self.colors = colors  # face -> color mapping
        self.orientation = Orientation.identity()
    
    def rotate(self, axis: str, angle: int) -> None:
        """Apply rotation transformation"""
        self.position = self._rotate_position(axis, angle)
        self.orientation = self._rotate_orientation(axis, angle)
```

### Move System

Moves are represented as immutable value objects:

```python
@dataclass(frozen=True)
class Move:
    face: str      # R, L, U, D, F, B, M, E, S, x, y, z
    direction: int # 1 (CW), -1 (CCW), 2 (180°)
    wide: bool     # Wide turn modifier (r, l, u, etc.)
    
    def to_notation(self) -> str:
        """Convert to standard notation"""
        notation = self.face.lower() if self.wide else self.face
        if self.direction == -1:
            notation += "'"
        elif self.direction == 2:
            notation += "2"
        return notation
```

### Algorithm Implementation

Solving algorithms implement the `ISolver` interface:

```python
class CFOPSolver(ISolver):
    def __init__(self):
        self.cross_solver = CrossSolver()
        self.f2l_solver = F2LSolver()
        self.oll_database = OLLDatabase()
        self.pll_database = PLLDatabase()
    
    def solve(self, cube: ICube) -> SolutionResult:
        """Execute complete CFOP solve"""
        steps = []
        
        # Cross phase
        if not self.cross_solver.is_complete(cube):
            cross_steps = self.cross_solver.solve(cube)
            steps.extend(cross_steps)
        
        # F2L phase
        for _ in range(4):  # 4 F2L pairs
            pair_steps = self.f2l_solver.solve_next_pair(cube)
            steps.extend(pair_steps)
        
        # OLL phase
        oll_case = self.oll_database.recognize_case(cube)
        if oll_case:
            steps.extend(oll_case.get_solution())
        
        # PLL phase
        pll_case = self.pll_database.recognize_case(cube)
        if pll_case:
            steps.extend(pll_case.get_solution())
        
        return SolutionResult(steps=steps, method="CFOP")
```

### Pattern Recognition

Pattern recognition uses hash-based lookups for performance:

```python
class PatternMatcher:
    def __init__(self):
        self._pattern_cache = {}
        self._hash_table = self._build_hash_table()
    
    def recognize_pattern(self, cube_state: CubeState) -> Optional[Pattern]:
        """O(1) pattern recognition using hashing"""
        pattern_hash = self._hash_state(cube_state)
        
        if pattern_hash in self._pattern_cache:
            return self._pattern_cache[pattern_hash]
        
        pattern = self._hash_table.get(pattern_hash)
        if pattern:
            self._pattern_cache[pattern_hash] = pattern
        
        return pattern
    
    def _hash_state(self, state: CubeState) -> int:
        """Generate fast hash of relevant cube features"""
        # Implementation uses bit manipulation for speed
        pass
```

## Development Workflow

### Code Style and Standards

We follow PEP 8 with these specific guidelines:

```python
# Good: Clear, descriptive names
def solve_cross_efficiently(cube: ICube) -> List[SolutionStep]:
    """Solve cross using optimized algorithms."""
    pass

# Good: Type hints for all public APIs
class Cube(ICube):
    def execute_move(self, move: Move) -> None:
        pass

# Good: Docstrings with Args/Returns
def apply_algorithm(self, algorithm: str) -> ExecutionResult:
    """
    Apply algorithm sequence to cube.
    
    Args:
        algorithm: Algorithm in standard notation (e.g., "R U R' U'")
        
    Returns:
        ExecutionResult: Result of algorithm execution
        
    Raises:
        ParseError: If algorithm notation is invalid
    """
```

### Testing Strategy

#### Unit Tests

Test individual components in isolation:

```python
# tests/unit/test_cube.py
import pytest
from rcsim.cube import Cube, Move

class TestCube:
    def test_execute_move_updates_state(self):
        """Test that executing moves changes cube state"""
        cube = Cube(3)
        initial_state = cube.get_state()
        
        cube.execute_move(Move.from_notation("R"))
        
        assert cube.get_state() != initial_state
    
    def test_undo_reverses_move(self):
        """Test that undo properly reverses moves"""
        cube = Cube(3)
        initial_state = cube.get_state()
        
        cube.execute_move(Move.from_notation("R"))
        cube.undo_move()
        
        assert cube.get_state() == initial_state
    
    @pytest.mark.parametrize("notation,expected", [
        ("R", Move("R", 1, False)),
        ("R'", Move("R", -1, False)),
        ("R2", Move("R", 2, False)),
        ("r", Move("R", 1, True)),
    ])
    def test_move_parsing(self, notation, expected):
        """Test move notation parsing"""
        move = Move.from_notation(notation)
        assert move == expected
```

#### Integration Tests

Test component interactions:

```python
# tests/integration/test_solving.py
class TestSolving:
    def test_cfop_solver_solves_scrambled_cube(self):
        """Test complete CFOP solving process"""
        cube = Cube(3)
        scramble = generate_random_scramble(25)
        cube.apply_scramble(scramble)
        
        solver = CFOPSolver()
        solution = solver.solve(cube)
        
        # Apply solution
        for step in solution.steps:
            cube.execute_move(step.move)
        
        assert cube.is_solved()
    
    def test_solver_produces_valid_moves(self):
        """Test that solver only produces valid moves"""
        cube = Cube(3)
        cube.apply_scramble(generate_random_scramble(15))
        
        solver = LayerByLayerSolver()
        solution = solver.solve(cube)
        
        for step in solution.steps:
            assert step.move.is_valid()
```

#### Performance Tests

Ensure performance requirements are met:

```python
# tests/performance/test_rendering.py
import time
import pytest

class TestPerformance:
    def test_rendering_maintains_60fps(self):
        """Test that rendering maintains target framerate"""
        renderer = Renderer(800, 600)
        cube = Cube(3)
        camera = Camera()
        
        frame_times = []
        for _ in range(60):  # Test 60 frames
            start = time.time()
            renderer.render_cube(cube, camera)
            frame_time = time.time() - start
            frame_times.append(frame_time)
        
        avg_frame_time = sum(frame_times) / len(frame_times)
        fps = 1.0 / avg_frame_time
        
        assert fps >= 60, f"Rendering too slow: {fps:.1f} FPS"
    
    @pytest.mark.parametrize("cube_size", [2, 3, 4, 5, 6, 7])
    def test_solver_performance_scales(self, cube_size):
        """Test solver performance across cube sizes"""
        cube = Cube(cube_size)
        cube.apply_scramble(generate_random_scramble(20))
        
        solver = CFOPSolver()
        start = time.time()
        solution = solver.solve(cube)
        solve_time = time.time() - start
        
        # Performance should scale reasonably
        max_time = cube_size * 0.5  # 0.5s per size level
        assert solve_time < max_time
```

### Continuous Integration

Our CI pipeline runs:

1. **Code Quality Checks**
   ```bash
   # Formatting
   black --check src/ tests/
   
   # Linting
   flake8 src/ tests/
   
   # Type checking
   mypy src/
   ```

2. **Test Suite**
   ```bash
   # Unit tests with coverage
   pytest tests/unit/ --cov=src/rcsim --cov-report=xml
   
   # Integration tests
   pytest tests/integration/
   
   # Performance tests (on main branch only)
   pytest tests/performance/
   ```

3. **Documentation Build**
   ```bash
   # Sphinx documentation
   cd docs/
   make html
   
   # API documentation validation
   python scripts/validate_api_docs.py
   ```

## Performance Guidelines

### Memory Management

```python
# Good: Use object pooling for frequent allocations
class MovePool:
    def __init__(self):
        self._pool = []
    
    def get_move(self) -> Move:
        return self._pool.pop() if self._pool else Move("R", 1)
    
    def return_move(self, move: Move) -> None:
        if len(self._pool) < 1000:
            self._pool.append(move)

# Good: Use generators for large sequences
def generate_scramble_moves(length: int) -> Generator[Move, None, None]:
    """Generate scramble moves lazily"""
    for _ in range(length):
        yield random_move()

# Avoid: Creating unnecessary objects in loops
def bad_example():
    moves = []
    for i in range(1000):
        # Creates new string each iteration
        notation = f"R{i}"
        moves.append(Move.from_notation(notation))
```

### Algorithm Optimization

```python
# Good: Use bit manipulation for fast operations
def hash_cube_state(state: CubeState) -> int:
    """Fast state hashing using bit operations"""
    hash_value = 0
    for i, piece in enumerate(state.pieces):
        if piece.is_oriented():
            hash_value |= (1 << i)
    return hash_value

# Good: Cache expensive computations
class PatternDatabase:
    def __init__(self):
        self._cache = {}
    
    def recognize_pattern(self, state: CubeState) -> Optional[Pattern]:
        state_hash = hash(state)
        if state_hash in self._cache:
            return self._cache[state_hash]
        
        pattern = self._expensive_recognition(state)
        self._cache[state_hash] = pattern
        return pattern

# Good: Use appropriate data structures
class MoveHistory:
    def __init__(self):
        self._moves = deque()  # O(1) append/pop
        self._position = 0
    
    def add_move(self, move: Move) -> None:
        # Truncate future history when adding new move
        while len(self._moves) > self._position:
            self._moves.pop()
        self._moves.append(move)
        self._position += 1
```

### Rendering Optimization

```python
# Good: Batch similar operations
class BatchRenderer:
    def render_frame(self, cube: ICube):
        # Group pieces by material
        pieces_by_material = self._group_by_material(cube.pieces)
        
        for material, pieces in pieces_by_material.items():
            self._set_material(material)
            self._render_instanced(pieces)  # Single draw call

# Good: Use level-of-detail for distant objects
class LODManager:
    def get_piece_lod(self, piece: Cubie, camera: Camera) -> int:
        distance = camera.get_distance_to(piece.position)
        if distance > 20:
            return 0  # Low poly
        elif distance > 10:
            return 1  # Medium poly
        else:
            return 2  # High poly
```

## Contributing

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/algorithm-optimization
   ```

2. **Implement Changes**
   - Follow coding standards
   - Add comprehensive tests
   - Update documentation

3. **Run Quality Checks**
   ```bash
   # Format code
   black src/ tests/
   
   # Run all tests
   pytest
   
   # Check type hints
   mypy src/
   ```

4. **Submit Pull Request**
   - Clear description of changes
   - Link to related issues
   - Include performance impact assessment

### Code Review Guidelines

**For Reviewers:**
- Check algorithm correctness (especially solving logic)
- Verify performance impact
- Ensure adequate test coverage
- Review API design for consistency

**For Authors:**
- Provide context for design decisions
- Include performance benchmarks for algorithm changes
- Document any breaking changes
- Respond to feedback constructively

### Release Process

1. **Version Bumping**
   ```bash
   # Update version in setup.py and __init__.py
   python scripts/bump_version.py minor
   ```

2. **Generate Changelog**
   ```bash
   python scripts/generate_changelog.py
   ```

3. **Create Release**
   ```bash
   git tag v1.2.0
   git push origin v1.2.0
   ```

### Issue Templates

**Bug Report:**
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, graphics card)
- Screenshots/videos if applicable

**Feature Request:**
- Clear description of desired functionality
- Use cases and benefits
- Acceptance criteria
- Performance considerations

**Algorithm Enhancement:**
- Mathematical correctness proof
- Performance benchmarks
- Compatibility with existing solvers
- Educational value assessment

### Documentation Standards

- All public APIs must have docstrings
- Include code examples for complex features
- Update architecture docs for significant changes
- Maintain algorithm correctness proofs
- Keep performance benchmarks current

### Community Guidelines

- Be respectful and inclusive
- Focus on technical merit
- Provide constructive feedback
- Help newcomers understand the codebase
- Share knowledge about speedcubing algorithms