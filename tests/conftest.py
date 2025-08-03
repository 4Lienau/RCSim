"""Pytest configuration and shared fixtures for Advanced Rubik's Cube Simulator tests."""

import os
import sys
from pathlib import Path
from typing import Generator

import pytest
import pygame

# Add src directory to Python path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Test configuration
os.environ["RCSIM_TESTING"] = "1"
os.environ["SDL_VIDEODRIVER"] = "dummy"  # Headless mode for CI


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment for graphics testing."""
    # Initialize pygame in headless mode
    pygame.init()
    pygame.display.set_mode((1, 1))  # Minimal display for testing
    
    yield
    
    # Cleanup
    pygame.quit()


@pytest.fixture
def headless_display():
    """Provide headless display for graphics tests."""
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":99"
    return True


@pytest.fixture
def sample_cube_3x3():
    """Create a sample 3x3 cube for testing."""
    from rcsim.cube import Cube
    return Cube(size=3)


@pytest.fixture
def sample_cube_2x2():
    """Create a sample 2x2 cube for testing."""
    from rcsim.cube import Cube
    return Cube(size=2)


@pytest.fixture
def sample_moves():
    """Provide sample moves for testing."""
    from rcsim.cube.moves import Move
    return [
        Move.from_notation("R"),
        Move.from_notation("U"),
        Move.from_notation("R'"),
        Move.from_notation("U'"),
    ]


@pytest.fixture
def sample_scramble():
    """Provide a sample scramble sequence."""
    from rcsim.cube.moves import Move
    scramble_notation = "R U R' U R U2 R' F R U R' U' F' R U R' U R U2 R'"
    return [Move.from_notation(move) for move in scramble_notation.split()]


@pytest.fixture
def mock_renderer():
    """Mock renderer for testing without actual graphics."""
    from unittest.mock import Mock
    
    renderer = Mock()
    renderer.render_cube = Mock()
    renderer.update_animation = Mock()
    renderer.capture_screenshot = Mock(return_value=None)
    
    return renderer


@pytest.fixture
def temp_config_file(tmp_path):
    """Create temporary configuration file for testing."""
    config_file = tmp_path / "test_config.json"
    config_data = {
        "graphics": {
            "quality": "medium",
            "vsync": False,
            "fps_limit": 60
        },
        "controls": {
            "mouse_sensitivity": 1.0,
            "keyboard_repeat": True
        },
        "colors": {
            "white": [255, 255, 255],
            "red": [255, 0, 0],
            "blue": [0, 0, 255],
            "orange": [255, 165, 0],
            "green": [0, 255, 0],
            "yellow": [255, 255, 0]
        }
    }
    
    import json
    with open(config_file, 'w') as f:
        json.dump(config_data, f)
    
    return config_file


@pytest.fixture
def timer_service():
    """Create timer service for testing."""
    from rcsim.app.timer import TimerService
    return TimerService()


@pytest.fixture
def game_session():
    """Create game session for integration testing."""
    from rcsim.app.game_session import GameSession
    return GameSession(cube_size=3)


@pytest.fixture
def cfop_solver():
    """Create CFOP solver for testing."""
    from rcsim.solvers.cfop import CFOPSolver
    return CFOPSolver()


@pytest.fixture
def layer_by_layer_solver():
    """Create Layer-by-Layer solver for testing."""
    from rcsim.solvers.layer_by_layer import LayerByLayerSolver
    return LayerByLayerSolver()


@pytest.fixture(params=[2, 3, 4, 5])
def cube_sizes(request):
    """Parametrized fixture for different cube sizes."""
    return request.param


@pytest.fixture
def solved_cube_state():
    """Provide a solved cube state for testing."""
    from rcsim.cube import Cube
    cube = Cube(3)
    return cube.get_state()


@pytest.fixture
def scrambled_cube_state(sample_cube_3x3, sample_scramble):
    """Provide a scrambled cube state for testing."""
    cube = sample_cube_3x3
    cube.apply_scramble(sample_scramble)
    return cube.get_state()


# Performance testing fixtures
@pytest.fixture
def benchmark_cube():
    """Create cube optimized for benchmarking."""
    from rcsim.cube import Cube
    return Cube(size=3)


@pytest.fixture
def performance_scramble():
    """Provide scramble for performance testing."""
    # Standard 20-move scramble
    return "D L2 F2 R2 U2 L2 U F2 U F2 D' R D2 L' B U' L F' R D2 F'"


# Mock fixtures for external dependencies
@pytest.fixture
def mock_opengl():
    """Mock OpenGL calls for testing without GPU."""
    from unittest.mock import patch, Mock
    
    with patch('moderngl.create_context') as mock_context:
        mock_ctx = Mock()
        mock_context.return_value = mock_ctx
        
        # Mock common OpenGL operations
        mock_ctx.clear = Mock()
        mock_ctx.enable = Mock()
        mock_ctx.disable = Mock()
        
        yield mock_ctx


# Hypothesis strategies for property-based testing
@pytest.fixture
def move_strategy():
    """Hypothesis strategy for generating random moves."""
    from hypothesis import strategies as st
    from rcsim.cube.moves import Move
    
    face_strategy = st.sampled_from(['R', 'L', 'U', 'D', 'F', 'B'])
    direction_strategy = st.sampled_from([1, -1, 2])
    wide_strategy = st.booleans()
    
    return st.builds(
        Move,
        face=face_strategy,
        direction=direction_strategy,
        wide=wide_strategy
    )


# Test markers and custom fixtures
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "gpu: marks tests that require GPU"
    )
    config.addinivalue_line(
        "markers", "headless: marks tests that can run headless"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    rootdir = config.rootdir
    
    for item in items:
        # Add markers based on test file location
        rel_path = item.fspath.relto(rootdir)
        
        if "test_integration" in rel_path:
            item.add_marker(pytest.mark.integration)
        elif "test_performance" in rel_path:
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
        elif "test_unit" in rel_path:
            item.add_marker(pytest.mark.unit)
        
        # Add GPU marker for graphics tests
        if "graphics" in rel_path or "render" in rel_path:
            item.add_marker(pytest.mark.gpu)
        
        # Add headless marker for tests that can run without display
        if not any(mark.name == "gpu" for mark in item.iter_markers()):
            item.add_marker(pytest.mark.headless)


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Automatically clean up temporary files after each test."""
    yield
    
    # Clean up any temporary files created during testing
    import tempfile
    import shutil
    temp_dir = Path(tempfile.gettempdir()) / "rcsim_test"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


# Database fixtures for testing statistics
@pytest.fixture
def temp_db():
    """Create temporary database for testing statistics storage."""
    import sqlite3
    from tempfile import NamedTemporaryFile
    
    with NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name
    
    # Initialize test database
    conn = sqlite3.connect(db_path)
    # Add initialization SQL here if needed
    conn.close()
    
    yield db_path
    
    # Cleanup
    os.unlink(db_path)


# Logging configuration for tests
@pytest.fixture(autouse=True)
def configure_test_logging():
    """Configure logging for tests."""
    import logging
    
    # Set up test-specific logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Suppress verbose logging from external libraries
    logging.getLogger("pygame").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    
    yield
    
    # Clean up logging handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)