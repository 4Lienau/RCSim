"""Advanced Rubik's Cube Simulator.

A realistic 3D Rubik's Cube simulator with authentic solving algorithms,
educational features, and competition-grade timing.
"""

__version__ = "0.1.0"
__author__ = "Advanced Rubik's Cube Simulator Team"
__email__ = "dev@rcsim.org"

# Core imports for easy access
from .cube.cube import Cube
from .cube.moves import Move, MoveSequence
from .cube.state import CubeState, Position, Color

__all__ = [
    "Cube",
    "Move", 
    "MoveSequence",
    "CubeState",
    "Position",
    "Color",
]