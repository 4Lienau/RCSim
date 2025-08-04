"""Core cube state representation and data structures.

This module defines the fundamental data structures for representing
Rubik's Cube state, including positions, colors, orientations, and pieces.
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum
import numpy as np


@dataclass(frozen=True)
class Position:
    """Immutable 3D position in cube space.
    
    For an NxN cube, coordinates range from -(N-1)/2 to (N-1)/2.
    For a 3x3 cube: -1, 0, 1 on each axis.
    Center of cube is at (0, 0, 0).
    
    Attributes
    ----------
    x : float
        X-coordinate (right/left axis)
    y : float  
        Y-coordinate (up/down axis)
    z : float
        Z-coordinate (front/back axis)
    """
    x: float
    y: float
    z: float
    
    def __post_init__(self) -> None:
        """Validate position coordinates."""
        if not all(isinstance(coord, (int, float)) for coord in (self.x, self.y, self.z)):
            raise ValueError("Position coordinates must be numeric")
    
    def distance_from_center(self) -> float:
        """Calculate Euclidean distance from cube center."""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def manhattan_distance_from_center(self) -> int:
        """Calculate Manhattan distance from cube center."""
        return int(abs(self.x) + abs(self.y) + abs(self.z))
    
    def is_corner(self) -> bool:
        """Check if position represents a corner piece."""
        return abs(self.x) > 0 and abs(self.y) > 0 and abs(self.z) > 0
    
    def is_edge(self) -> bool:
        """Check if position represents an edge piece."""
        coords_nonzero = sum(1 for coord in (self.x, self.y, self.z) if abs(coord) > 0)
        return coords_nonzero == 2
    
    def is_center(self) -> bool:
        """Check if position represents a center piece."""
        coords_nonzero = sum(1 for coord in (self.x, self.y, self.z) if abs(coord) > 0)
        return coords_nonzero == 1
    
    def is_core(self) -> bool:
        """Check if position is the cube core (invisible)."""
        return self.x == 0 and self.y == 0 and self.z == 0
    
    def get_faces(self) -> List[str]:
        """Get list of faces this position touches.
        
        Returns
        -------
        List[str]
            List of face names ('U', 'D', 'L', 'R', 'F', 'B')
        """
        faces = []
        if self.y > 0:
            faces.append('U')  # Up
        elif self.y < 0:
            faces.append('D')  # Down
            
        if self.x > 0:
            faces.append('R')  # Right
        elif self.x < 0:
            faces.append('L')  # Left
            
        if self.z > 0:
            faces.append('F')  # Front
        elif self.z < 0:
            faces.append('B')  # Back
            
        return faces
    
    def rotate_around_axis(self, axis: str, angle_degrees: int) -> 'Position':
        """Rotate position around specified axis.
        
        Parameters
        ----------
        axis : str
            Rotation axis ('x', 'y', or 'z')
        angle_degrees : int
            Rotation angle in degrees (typically 90, 180, 270)
            
        Returns
        -------
        Position
            New position after rotation
        """
        angle_rad = math.radians(angle_degrees)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        # Round to handle floating point precision
        def round_coord(val: float) -> float:
            return round(val, 10)
        
        if axis.lower() == 'x':
            # Rotation around X-axis: Y and Z change
            new_y = round_coord(self.y * cos_a - self.z * sin_a)
            new_z = round_coord(self.y * sin_a + self.z * cos_a)
            return Position(self.x, new_y, new_z)
        elif axis.lower() == 'y':
            # Rotation around Y-axis: X and Z change
            new_x = round_coord(self.x * cos_a + self.z * sin_a)
            new_z = round_coord(-self.x * sin_a + self.z * cos_a)
            return Position(new_x, self.y, new_z)
        elif axis.lower() == 'z':
            # Rotation around Z-axis: X and Y change
            new_x = round_coord(self.x * cos_a - self.y * sin_a)
            new_y = round_coord(self.x * sin_a + self.y * cos_a)
            return Position(new_x, new_y, self.z)
        else:
            raise ValueError(f"Invalid axis: {axis}. Must be 'x', 'y', or 'z'")
    
    def __str__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"
    
    def __repr__(self) -> str:
        return f"Position(x={self.x}, y={self.y}, z={self.z})"


@dataclass(frozen=True)
class Color:
    """Immutable color representation for cube faces.
    
    Attributes
    ----------
    r : int
        Red component (0-255)
    g : int
        Green component (0-255)
    b : int
        Blue component (0-255)
    name : str
        Human-readable color name
    """
    r: int
    g: int
    b: int
    name: str
    
    def __post_init__(self) -> None:
        """Validate color components."""
        for component in (self.r, self.g, self.b):
            if not isinstance(component, int) or not 0 <= component <= 255:
                raise ValueError("Color components must be integers between 0 and 255")
        
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Color name must be a non-empty string")
    
    def to_hex(self) -> str:
        """Convert color to hexadecimal string."""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"
    
    def to_rgb_tuple(self) -> Tuple[int, int, int]:
        """Convert color to RGB tuple."""
        return (self.r, self.g, self.b)
    
    def to_normalized_rgb(self) -> Tuple[float, float, float]:
        """Convert color to normalized RGB (0.0-1.0)."""
        return (self.r / 255.0, self.g / 255.0, self.b / 255.0)
    
    @classmethod
    def from_hex(cls, hex_string: str, name: str = "") -> 'Color':
        """Create color from hexadecimal string.
        
        Parameters
        ----------
        hex_string : str
            Hex color string (e.g., "#FF0000" or "FF0000")
        name : str, optional
            Human-readable name for the color
            
        Returns
        -------
        Color
            New Color instance
        """
        hex_string = hex_string.lstrip('#')
        if len(hex_string) != 6:
            raise ValueError("Hex string must be 6 characters")
        
        try:
            r = int(hex_string[0:2], 16)
            g = int(hex_string[2:4], 16)
            b = int(hex_string[4:6], 16)
        except ValueError:
            raise ValueError("Invalid hex color string")
        
        return cls(r, g, b, name or hex_string)
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"Color(r={self.r}, g={self.g}, b={self.b}, name='{self.name}')"


# Standard WCA colors
class StandardColors:
    """Standard World Cube Association colors."""
    
    WHITE = Color(255, 255, 255, "White")
    YELLOW = Color(255, 255, 0, "Yellow")
    RED = Color(255, 0, 0, "Red")
    ORANGE = Color(255, 165, 0, "Orange")
    BLUE = Color(0, 0, 255, "Blue")
    GREEN = Color(0, 255, 0, "Green")
    
    @classmethod
    def get_standard_scheme(cls) -> Dict[str, 'Color']:
        """Get standard color scheme mapping."""
        return {
            'U': cls.WHITE,   # Up (Top)
            'D': cls.YELLOW,  # Down (Bottom)
            'L': cls.ORANGE,  # Left
            'R': cls.RED,     # Right
            'F': cls.GREEN,   # Front
            'B': cls.BLUE,    # Back
        }
    
    @classmethod
    def get_all_colors(cls) -> List['Color']:
        """Get list of all standard colors."""
        return [cls.WHITE, cls.YELLOW, cls.RED, cls.ORANGE, cls.BLUE, cls.GREEN]


class Axis(Enum):
    """Cube rotation axes."""
    X = "x"
    Y = "y" 
    Z = "z"


@dataclass(frozen=True)
class Orientation:
    """Represents the 3D orientation of a cube piece.
    
    Tracks how a piece is rotated relative to its solved orientation.
    Uses Euler angles in degrees for simplicity.
    
    Attributes
    ----------
    x_rotation : int
        Rotation around X-axis in degrees (0, 90, 180, 270)
    y_rotation : int
        Rotation around Y-axis in degrees (0, 90, 180, 270)
    z_rotation : int
        Rotation around Z-axis in degrees (0, 90, 180, 270)
    """
    x_rotation: int = 0
    y_rotation: int = 0
    z_rotation: int = 0
    
    def __post_init__(self) -> None:
        """Validate orientation angles."""
        for rotation in (self.x_rotation, self.y_rotation, self.z_rotation):
            if rotation not in (0, 90, 180, 270):
                raise ValueError("Rotations must be 0, 90, 180, or 270 degrees")
    
    @classmethod
    def identity(cls) -> 'Orientation':
        """Create identity orientation (no rotation)."""
        return cls(0, 0, 0)
    
    def rotate_around_axis(self, axis: Axis, angle_degrees: int) -> 'Orientation':
        """Apply additional rotation around specified axis.
        
        Parameters
        ----------
        axis : Axis
            Axis to rotate around
        angle_degrees : int
            Rotation angle in degrees
            
        Returns
        -------
        Orientation
            New orientation after rotation
        """
        def normalize_angle(angle: int) -> int:
            """Normalize angle to 0, 90, 180, or 270."""
            return angle % 360
        
        if axis == Axis.X:
            new_x = normalize_angle(self.x_rotation + angle_degrees)
            return Orientation(new_x, self.y_rotation, self.z_rotation)
        elif axis == Axis.Y:
            new_y = normalize_angle(self.y_rotation + angle_degrees)
            return Orientation(self.x_rotation, new_y, self.z_rotation)
        elif axis == Axis.Z:
            new_z = normalize_angle(self.z_rotation + angle_degrees)
            return Orientation(self.x_rotation, self.y_rotation, new_z)
        else:
            raise ValueError(f"Invalid axis: {axis}")
    
    def is_solved(self) -> bool:
        """Check if orientation is in solved state."""
        return all(rot == 0 for rot in (self.x_rotation, self.y_rotation, self.z_rotation))
    
    def get_face_mapping(self) -> Dict[str, str]:
        """Get mapping of original faces to current faces after rotation.
        
        Returns
        -------
        Dict[str, str]
            Mapping from original face to current face
        """
        if self.is_solved():
            return {'U': 'U', 'D': 'D', 'L': 'L', 'R': 'R', 'F': 'F', 'B': 'B'}
        
        # Apply rotations in order: X, Y, Z
        mapping = {'U': 'U', 'D': 'D', 'L': 'L', 'R': 'R', 'F': 'F', 'B': 'B'}
        
        # Apply X rotation (around X-axis)
        if self.x_rotation == 90:
            mapping = {k: {'U': 'F', 'D': 'B', 'L': 'L', 'R': 'R', 'F': 'D', 'B': 'U'}[v] for k, v in mapping.items()}
        elif self.x_rotation == 180:
            mapping = {k: {'U': 'D', 'D': 'U', 'L': 'L', 'R': 'R', 'F': 'B', 'B': 'F'}[v] for k, v in mapping.items()}
        elif self.x_rotation == 270:
            mapping = {k: {'U': 'B', 'D': 'F', 'L': 'L', 'R': 'R', 'F': 'U', 'B': 'D'}[v] for k, v in mapping.items()}
        
        # Apply Y rotation (around Y-axis)
        if self.y_rotation == 90:
            mapping = {k: {'U': 'U', 'D': 'D', 'L': 'F', 'R': 'B', 'F': 'R', 'B': 'L'}[v] for k, v in mapping.items()}
        elif self.y_rotation == 180:
            mapping = {k: {'U': 'U', 'D': 'D', 'L': 'R', 'R': 'L', 'F': 'B', 'B': 'F'}[v] for k, v in mapping.items()}
        elif self.y_rotation == 270:
            mapping = {k: {'U': 'U', 'D': 'D', 'L': 'B', 'R': 'F', 'F': 'L', 'B': 'R'}[v] for k, v in mapping.items()}
        
        # Apply Z rotation (around Z-axis)
        if self.z_rotation == 90:
            mapping = {k: {'U': 'L', 'D': 'R', 'L': 'D', 'R': 'U', 'F': 'F', 'B': 'B'}[v] for k, v in mapping.items()}
        elif self.z_rotation == 180:
            mapping = {k: {'U': 'D', 'D': 'U', 'L': 'R', 'R': 'L', 'F': 'F', 'B': 'B'}[v] for k, v in mapping.items()}
        elif self.z_rotation == 270:
            mapping = {k: {'U': 'R', 'D': 'L', 'L': 'U', 'R': 'D', 'F': 'F', 'B': 'B'}[v] for k, v in mapping.items()}
        
        return mapping
    
    def __str__(self) -> str:
        return f"({self.x_rotation}°, {self.y_rotation}°, {self.z_rotation}°)"
    
    def __repr__(self) -> str:
        return f"Orientation(x={self.x_rotation}, y={self.y_rotation}, z={self.z_rotation})"


class Cubie:
    """Represents a single piece (cubie) of the Rubik's Cube.
    
    A cubie knows its current position, orientation, and colors.
    Corner pieces have 3 visible faces, edge pieces have 2, centers have 1.
    
    Attributes
    ----------
    original_position : Position
        The position this piece belongs to when cube is solved
    current_position : Position
        Current position of this piece
    orientation : Orientation
        Current orientation relative to solved state
    colors : Dict[str, Color]
        Colors on each face of this piece {'U': Color, 'R': Color, etc.}
    piece_type : str
        Type of piece: 'corner', 'edge', 'center', or 'core'
    """
    
    def __init__(
        self, 
        original_position: Position,
        colors: Dict[str, Color],
        current_position: Optional[Position] = None,
        orientation: Optional[Orientation] = None
    ):
        """Initialize a cubie.
        
        Parameters
        ----------
        original_position : Position
            Position this piece belongs to when solved
        colors : Dict[str, Color]
            Colors on each face of this piece
        current_position : Position, optional
            Current position (defaults to original_position)
        orientation : Orientation, optional
            Current orientation (defaults to identity)
        """
        self.original_position = original_position
        self.current_position = current_position or original_position
        self.orientation = orientation or Orientation.identity()
        self.colors = colors.copy()
        
        # Determine piece type
        if original_position.is_corner():
            self.piece_type = 'corner'
        elif original_position.is_edge():
            self.piece_type = 'edge'
        elif original_position.is_center():
            self.piece_type = 'center'
        else:
            self.piece_type = 'core'
    
    def get_visible_colors(self) -> Dict[str, Color]:
        """Get colors visible on cube faces at current position.
        
        Returns
        -------
        Dict[str, Color]
            Mapping of face names to visible colors
        """
        visible = {}
        current_faces = self.current_position.get_faces()
        
        # Apply orientation to determine which original face maps to which current face
        face_mapping = self.orientation.get_face_mapping()
        
        for current_face in current_faces:
            # Find which original face is now showing on this current face
            for original_face, mapped_face in face_mapping.items():
                if mapped_face == current_face and original_face in self.colors:
                    visible[current_face] = self.colors[original_face]
                    break
        
        return visible
    
    def move_to_position(self, new_position: Position) -> None:
        """Move this cubie to a new position."""
        self.current_position = new_position
    
    def rotate(self, axis: Axis, angle_degrees: int) -> None:
        """Rotate this cubie around specified axis."""
        self.orientation = self.orientation.rotate_around_axis(axis, angle_degrees)
    
    def is_in_solved_position(self) -> bool:
        """Check if cubie is in its solved position with correct orientation."""
        return (self.current_position == self.original_position and 
                self.orientation.is_solved())
    
    def is_correctly_positioned(self) -> bool:
        """Check if cubie is in correct position (ignoring orientation)."""
        return self.current_position == self.original_position
    
    def is_correctly_oriented(self) -> bool:
        """Check if cubie has correct orientation (ignoring position)."""
        return self.orientation.is_solved()
    
    def clone(self) -> 'Cubie':
        """Create a deep copy of this cubie."""
        return Cubie(
            original_position=self.original_position,
            colors=self.colors.copy(),
            current_position=self.current_position,
            orientation=self.orientation
        )
    
    def __str__(self) -> str:
        return f"{self.piece_type.title()} at {self.current_position}"
    
    def __repr__(self) -> str:
        return (f"Cubie(original={self.original_position}, "
                f"current={self.current_position}, "
                f"orientation={self.orientation}, "
                f"type={self.piece_type})")
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Cubie):
            return False
        return (self.original_position == other.original_position and
                self.current_position == other.current_position and
                self.orientation == other.orientation and
                self.colors == other.colors)
    
    def __hash__(self) -> int:
        return hash((self.original_position, self.current_position, 
                    self.orientation, tuple(sorted(self.colors.items()))))


class CubeState:
    """Represents the complete state of a Rubik's Cube.
    
    Manages all cubies and provides efficient operations for querying
    and modifying cube state.
    
    Attributes
    ----------
    size : int
        Size of the cube (2 for 2x2, 3 for 3x3, etc.)
    cubies : List[Cubie]
        All pieces in the cube
    """
    
    def __init__(self, size: int):
        """Initialize cube state.
        
        Parameters
        ----------
        size : int
            Size of cube (2-10)
        """
        if not isinstance(size, int) or size < 2 or size > 10:
            raise ValueError("Cube size must be an integer between 2 and 10")
        
        self.size = size
        self.cubies: List[Cubie] = []
        self._position_map: Dict[Position, Cubie] = {}
        
        self._initialize_solved_state()
    
    def _initialize_solved_state(self) -> None:
        """Initialize cube in solved state."""
        self.cubies.clear()
        self._position_map.clear()
        
        # Calculate coordinate range for this cube size
        half_size = (self.size - 1) / 2
        
        # Generate all positions
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    # Convert to cube coordinates (-half_size to +half_size)
                    pos_x = x - half_size
                    pos_y = y - half_size  
                    pos_z = z - half_size
                    
                    position = Position(pos_x, pos_y, pos_z)
                    
                    # Skip internal pieces (only visible pieces matter)
                    if self._is_internal_piece(position):
                        continue
                    
                    # Create cubie with appropriate colors
                    colors = self._get_solved_colors(position)
                    cubie = Cubie(position, colors)
                    
                    self.cubies.append(cubie)
                    self._position_map[position] = cubie
    
    def _is_internal_piece(self, position: Position) -> bool:
        """Check if position is internal (not visible)."""
        half_size = (self.size - 1) / 2
        
        # A piece is internal if it doesn't touch any face
        touches_face = (
            abs(position.x) == half_size or
            abs(position.y) == half_size or
            abs(position.z) == half_size
        )
        
        return not touches_face
    
    def _get_solved_colors(self, position: Position) -> Dict[str, Color]:
        """Get colors for piece at position in solved state."""
        colors = {}
        standard_colors = StandardColors.get_standard_scheme()
        
        # Assign colors based on which faces the position touches
        faces = position.get_faces()
        for face in faces:
            colors[face] = standard_colors[face]
        
        return colors
    
    def get_piece_at_position(self, position: Position) -> Optional[Cubie]:
        """Get the cubie currently at specified position."""
        return self._position_map.get(position)
    
    def get_pieces_by_type(self, piece_type: str) -> List[Cubie]:
        """Get all pieces of specified type.
        
        Parameters
        ----------
        piece_type : str
            Type of piece: 'corner', 'edge', 'center'
            
        Returns
        -------
        List[Cubie]
            List of matching pieces
        """
        return [cubie for cubie in self.cubies if cubie.piece_type == piece_type]
    
    def get_face_colors(self, face: str) -> List[List[Color]]:
        """Get 2D array of colors for specified face.
        
        Parameters
        ----------
        face : str
            Face name ('U', 'D', 'L', 'R', 'F', 'B')
            
        Returns
        -------
        List[List[Color]]
            2D array of colors on the face
        """
        if face not in ('U', 'D', 'L', 'R', 'F', 'B'):
            raise ValueError(f"Invalid face: {face}")
        
        face_colors = [[StandardColors.WHITE for _ in range(self.size)] 
                       for _ in range(self.size)]
        
        half_size = (self.size - 1) / 2
        
        # Map 3D positions to 2D face coordinates
        for i in range(self.size):
            for j in range(self.size):
                # Calculate 3D position based on face
                if face == 'U':  # Up face (Y = +half_size)
                    pos = Position(i - half_size, half_size, j - half_size)
                elif face == 'D':  # Down face (Y = -half_size)
                    pos = Position(i - half_size, -half_size, half_size - j)
                elif face == 'F':  # Front face (Z = +half_size)
                    pos = Position(i - half_size, half_size - j, half_size)
                elif face == 'B':  # Back face (Z = -half_size)
                    pos = Position(half_size - i, half_size - j, -half_size)
                elif face == 'R':  # Right face (X = +half_size)
                    pos = Position(half_size, half_size - j, half_size - i)
                elif face == 'L':  # Left face (X = -half_size)
                    pos = Position(-half_size, half_size - j, i - half_size)
                
                # Get piece at this position and extract color
                piece = self.get_piece_at_position(pos)
                if piece:
                    visible_colors = piece.get_visible_colors()
                    if face in visible_colors:
                        face_colors[j][i] = visible_colors[face]
        
        return face_colors
    
    def is_solved(self) -> bool:
        """Check if cube is in solved state."""
        return all(cubie.is_in_solved_position() for cubie in self.cubies)
    
    def move_piece(self, from_pos: Position, to_pos: Position) -> None:
        """Move piece from one position to another."""
        piece = self._position_map.get(from_pos)
        if piece:
            # Update position mappings
            del self._position_map[from_pos]
            piece.move_to_position(to_pos)
            self._position_map[to_pos] = piece
    
    def clone(self) -> 'CubeState':
        """Create deep copy of cube state."""
        new_state = CubeState.__new__(CubeState)  # Skip __init__
        new_state.size = self.size
        new_state.cubies = [cubie.clone() for cubie in self.cubies]
        new_state._position_map = {
            cubie.current_position: cubie for cubie in new_state.cubies
        }
        return new_state
    
    def __eq__(self, other) -> bool:
        """Check equality with another cube state."""
        if not isinstance(other, CubeState):
            return False
        
        if self.size != other.size:
            return False
        
        # Compare piece positions and orientations
        for cubie in self.cubies:
            other_piece = other.get_piece_at_position(cubie.current_position)
            if not other_piece or other_piece != cubie:
                return False
        
        return True
    
    def __str__(self) -> str:
        return f"CubeState(size={self.size}, pieces={len(self.cubies)})"
    
    def __repr__(self) -> str:
        return f"CubeState(size={self.size}, solved={self.is_solved()})"