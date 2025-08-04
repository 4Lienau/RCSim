"""Cube move representation and notation parsing.

This module provides classes for representing cube moves and sequences,
parsing standard WCA notation, and applying moves to cube states.
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Union, Iterator, Dict, Tuple
from enum import Enum

from .state import Position, CubeState, Axis


class ParseError(Exception):
    """Exception raised when move notation cannot be parsed."""
    pass


class MoveType(Enum):
    """Types of cube moves."""
    FACE = "face"           # R, U, L, D, F, B
    WIDE = "wide"           # Rw, Uw, Lw, Dw, Fw, Bw
    SLICE = "slice"         # M, E, S
    ROTATION = "rotation"   # x, y, z


@dataclass(frozen=True)
class Move:
    """Represents a single cube move in standard notation.
    
    Supports standard WCA notation including:
    - Basic moves: R, U, L, D, F, B
    - Prime moves: R', U', etc.
    - Double moves: R2, U2, etc.
    - Wide moves: Rw, Uw, etc.
    - Slice moves: M, E, S
    - Rotations: x, y, z
    
    Attributes
    ----------
    face : str
        Face or axis being moved ('R', 'U', 'M', 'x', etc.)
    amount : int
        Amount of rotation in 90-degree increments (1, 2, 3)
    move_type : MoveType
        Type of move (face, wide, slice, rotation)
    layers : int
        Number of layers affected (for wide moves)
    """
    
    face: str
    amount: int = 1
    move_type: MoveType = MoveType.FACE
    layers: int = 1
    
    def __post_init__(self) -> None:
        """Validate move parameters."""
        if self.amount not in (1, 2, 3):
            raise ValueError(f"Move amount must be 1, 2, or 3, got {self.amount}")
        
        if self.layers < 1:
            raise ValueError(f"Layers must be at least 1, got {self.layers}")
        
        valid_faces = {
            MoveType.FACE: {'R', 'U', 'L', 'D', 'F', 'B'},
            MoveType.WIDE: {'R', 'U', 'L', 'D', 'F', 'B'},
            MoveType.SLICE: {'M', 'E', 'S'},
            MoveType.ROTATION: {'x', 'y', 'z'}
        }
        
        if self.face not in valid_faces[self.move_type]:
            raise ValueError(f"Invalid face '{self.face}' for move type {self.move_type}")
    
    @classmethod
    def parse(cls, notation: str) -> 'Move':
        """Parse move from standard WCA notation.
        
        Parameters
        ----------
        notation : str
            Move notation (e.g., "R", "U'", "R2", "Rw", "M", "x")
            
        Returns
        -------
        Move
            Parsed move object
            
        Raises
        ------
        ParseError
            If notation cannot be parsed
        """
        notation = notation.strip()
        if not notation:
            raise ParseError("Empty move notation")
        
        # Regular expression for parsing moves
        # Captures: (layers)(face)(wide)(modifier)
        # Examples: R, R', R2, Rw, 2R, 2Rw', M, x, y2
        pattern = r"^(\d*)([RULDFBMESxyz])([w]?)([']?|2?)$"
        match = re.match(pattern, notation)
        
        if not match:
            raise ParseError(f"Invalid move notation: {notation}")
        
        layers_str, face, wide, modifier = match.groups()
        
        # Determine layers
        layers = int(layers_str) if layers_str else 1
        
        # Determine move type
        if face.upper() in 'RULDFB':
            if wide or layers > 1:
                move_type = MoveType.WIDE
                if not wide and layers > 1:
                    # For notation like "2R", treat as wide move
                    layers = layers
                else:
                    # For notation like "Rw", default to 2 layers
                    layers = 2 if layers == 1 else layers
            else:
                move_type = MoveType.FACE
        elif face.upper() in 'MES':
            move_type = MoveType.SLICE
            layers = 1  # Slice moves always affect 1 layer
        elif face.lower() in 'xyz':
            move_type = MoveType.ROTATION
            layers = 1  # Rotations don't use layers
        else:
            raise ParseError(f"Unknown face: {face}")
        
        # Determine amount
        if modifier == "'":
            amount = 3  # Counterclockwise = 3 clockwise
        elif modifier == "2":
            amount = 2
        else:
            amount = 1
        
        return cls(
            face=face.upper(),
            amount=amount,
            move_type=move_type,
            layers=layers
        )
    
    def inverse(self) -> 'Move':
        """Get the inverse of this move.
        
        Returns
        -------
        Move
            Move that undoes this move
        """
        if self.amount == 2:
            # R2 is its own inverse
            return self
        elif self.amount == 1:
            # R becomes R'
            inverse_amount = 3
        else:  # amount == 3
            # R' becomes R
            inverse_amount = 1
        
        return Move(
            face=self.face,
            amount=inverse_amount,
            move_type=self.move_type,
            layers=self.layers
        )
    
    def get_rotation_axis(self) -> Optional[Axis]:
        """Get the axis of rotation for this move.
        
        Returns
        -------
        Optional[Axis]
            Axis of rotation, or None for complex moves
        """
        axis_map = {
            'R': Axis.X, 'L': Axis.X,
            'U': Axis.Y, 'D': Axis.Y,
            'F': Axis.Z, 'B': Axis.Z,
            'M': Axis.X,  # Middle slice follows L
            'E': Axis.Y,  # Equatorial slice follows D
            'S': Axis.Z,  # Standing slice follows F
            'x': Axis.X,
            'y': Axis.Y,
            'z': Axis.Z
        }
        return axis_map.get(self.face)
    
    def get_rotation_angle(self) -> int:
        """Get rotation angle in degrees.
        
        Returns
        -------
        int
            Rotation angle (90, 180, or 270 degrees)
        """
        angle_map = {1: 90, 2: 180, 3: 270}
        base_angle = angle_map[self.amount]
        
        # Adjust for face direction
        if self.face in 'LDB':
            # L, D, B are in opposite direction
            return -base_angle % 360
        elif self.face == 'M':
            # M follows L direction
            return -base_angle % 360
        elif self.face == 'E':
            # E follows D direction  
            return -base_angle % 360
        
        return base_angle
    
    def affects_position(self, position: Position, cube_size: int) -> bool:
        """Check if this move affects a piece at the given position.
        
        Parameters
        ----------
        position : Position
            Position to check
        cube_size : int
            Size of the cube
            
        Returns
        -------
        bool
            True if the move affects this position
        """
        half_size = (cube_size - 1) / 2
        
        if self.move_type == MoveType.ROTATION:
            return True  # Rotations affect all positions
        
        # Check which layers are affected
        if self.face == 'R':
            return position.x >= half_size - self.layers + 1
        elif self.face == 'L':
            return position.x <= -half_size + self.layers - 1
        elif self.face == 'U':
            return position.y >= half_size - self.layers + 1
        elif self.face == 'D':
            return position.y <= -half_size + self.layers - 1
        elif self.face == 'F':
            return position.z >= half_size - self.layers + 1
        elif self.face == 'B':
            return position.z <= -half_size + self.layers - 1
        elif self.face == 'M':
            # Middle slice (between R and L)
            return abs(position.x) < 0.5
        elif self.face == 'E':
            # Equatorial slice (between U and D)
            return abs(position.y) < 0.5
        elif self.face == 'S':
            # Standing slice (between F and B)
            return abs(position.z) < 0.5
        
        return False
    
    def to_notation(self) -> str:
        """Convert move back to standard notation.
        
        Returns
        -------
        str
            Standard WCA notation string
        """
        notation = self.face
        
        # Add wide indicator for wide moves
        if self.move_type == MoveType.WIDE and self.layers == 2:
            notation += 'w'
        elif self.move_type == MoveType.WIDE and self.layers > 2:
            notation = f"{self.layers}{notation}"
        
        # Add modifier
        if self.amount == 2:
            notation += '2'
        elif self.amount == 3:
            notation += "'"
        
        return notation
    
    def __str__(self) -> str:
        return self.to_notation()
    
    def __repr__(self) -> str:
        return f"Move('{self.to_notation()}')"


class MoveSequence:
    """Represents a sequence of cube moves (algorithm).
    
    Provides functionality for parsing, manipulating, and optimizing
    sequences of moves.
    
    Attributes
    ----------
    moves : List[Move]
        List of moves in the sequence
    """
    
    def __init__(self, moves: Optional[List[Union[Move, str]]] = None):
        """Initialize move sequence.
        
        Parameters
        ----------
        moves : List[Union[Move, str]], optional
            List of moves or notation strings
        """
        self.moves: List[Move] = []
        
        if moves:
            for move in moves:
                if isinstance(move, str):
                    self.moves.append(Move.parse(move))
                elif isinstance(move, Move):
                    self.moves.append(move)
                else:
                    raise TypeError(f"Expected Move or str, got {type(move)}")
    
    @classmethod
    def parse(cls, notation: str) -> 'MoveSequence':
        """Parse sequence from space-separated notation.
        
        Parameters
        ----------
        notation : str
            Space-separated move notation (e.g., "R U R' U'")
            
        Returns
        -------
        MoveSequence
            Parsed move sequence
            
        Raises
        ------
        ParseError
            If any move in the sequence cannot be parsed
        """
        if not notation.strip():
            return cls()
        
        move_strings = notation.split()
        moves = []
        
        for move_str in move_strings:
            try:
                moves.append(Move.parse(move_str))
            except ParseError as e:
                raise ParseError(f"Error parsing '{move_str}' in sequence: {e}")
        
        return cls(moves)
    
    def add_move(self, move: Union[Move, str]) -> None:
        """Add a move to the sequence.
        
        Parameters
        ----------
        move : Union[Move, str]
            Move to add
        """
        if isinstance(move, str):
            self.moves.append(Move.parse(move))
        else:
            self.moves.append(move)
    
    def extend(self, other: 'MoveSequence') -> None:
        """Extend this sequence with another sequence.
        
        Parameters
        ----------
        other : MoveSequence
            Sequence to append
        """
        self.moves.extend(other.moves)
    
    def inverse(self) -> 'MoveSequence':
        """Get the inverse sequence that undoes this sequence.
        
        Returns
        -------
        MoveSequence
            Inverse sequence
        """
        inverse_moves = [move.inverse() for move in reversed(self.moves)]
        return MoveSequence(inverse_moves)
    
    def optimize(self) -> 'MoveSequence':
        """Optimize the sequence by removing redundant moves.
        
        Returns
        -------
        MoveSequence
            Optimized sequence
        """
        if not self.moves:
            return MoveSequence()
        
        optimized = []
        i = 0
        
        while i < len(self.moves):
            current_move = self.moves[i]
            
            # Look ahead for consecutive moves on the same face
            total_amount = current_move.amount
            j = i + 1
            
            while (j < len(self.moves) and 
                   self.moves[j].face == current_move.face and
                   self.moves[j].move_type == current_move.move_type and
                   self.moves[j].layers == current_move.layers):
                total_amount += self.moves[j].amount
                j += 1
            
            # Normalize amount (4 moves = no move, 5 moves = 1 move, etc.)
            final_amount = total_amount % 4
            
            if final_amount != 0:
                optimized_move = Move(
                    face=current_move.face,
                    amount=final_amount,
                    move_type=current_move.move_type,
                    layers=current_move.layers
                )
                optimized.append(optimized_move)
            
            i = j
        
        return MoveSequence(optimized)
    
    def length(self) -> int:
        """Get the number of moves in the sequence.
        
        Returns
        -------
        int
            Number of moves
        """
        return len(self.moves)
    
    def is_empty(self) -> bool:
        """Check if the sequence is empty.
        
        Returns
        -------
        bool
            True if sequence has no moves
        """
        return len(self.moves) == 0
    
    def copy(self) -> 'MoveSequence':
        """Create a copy of this sequence.
        
        Returns
        -------
        MoveSequence
            Copy of this sequence
        """
        return MoveSequence(self.moves.copy())
    
    def to_notation(self) -> str:
        """Convert sequence to standard notation string.
        
        Returns
        -------
        str
            Space-separated move notation
        """
        return ' '.join(move.to_notation() for move in self.moves)
    
    def __len__(self) -> int:
        return len(self.moves)
    
    def __iter__(self) -> Iterator[Move]:
        return iter(self.moves)
    
    def __getitem__(self, index: Union[int, slice]) -> Union[Move, 'MoveSequence']:
        if isinstance(index, slice):
            return MoveSequence(self.moves[index])
        return self.moves[index]
    
    def __add__(self, other: 'MoveSequence') -> 'MoveSequence':
        """Concatenate two sequences.
        
        Parameters
        ----------
        other : MoveSequence
            Sequence to concatenate
            
        Returns
        -------
        MoveSequence
            Combined sequence
        """
        return MoveSequence(self.moves + other.moves)
    
    def __str__(self) -> str:
        return self.to_notation()
    
    def __repr__(self) -> str:
        return f"MoveSequence('{self.to_notation()}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, MoveSequence):
            return False
        return self.moves == other.moves


# Common move sequences and algorithms
class StandardAlgorithms:
    """Collection of standard cube algorithms."""
    
    @staticmethod
    def get_triggers() -> Dict[str, MoveSequence]:
        """Get common trigger sequences.
        
        Returns
        -------
        Dict[str, MoveSequence]
            Dictionary of trigger name to sequence
        """
        return {
            'sexy_move': MoveSequence.parse("R U R' U'"),
            'sledgehammer': MoveSequence.parse("R' F R F'"),
            'sune': MoveSequence.parse("R U R' U R U2 R'"),
            'antisune': MoveSequence.parse("R U2 R' U' R U' R'"),
            'j_perm': MoveSequence.parse("R U R' F' R U R' U' R' F R2 U' R'"),
            't_perm': MoveSequence.parse("R U R' F' R U2 R' U2 R' F R U R U2 R'")
        }
    
    @staticmethod
    def get_basic_algorithms() -> Dict[str, MoveSequence]:
        """Get basic solving algorithms.
        
        Returns
        -------
        Dict[str, MoveSequence]
            Dictionary of algorithm name to sequence
        """
        algorithms = StandardAlgorithms.get_triggers()
        
        # Add more complex algorithms
        algorithms.update({
            'beginners_cross': MoveSequence.parse("F R U R' U' F'"),
            'beginners_corner': MoveSequence.parse("R U R' U' R U R' U' R U R'"),
            'four_move_cross': MoveSequence.parse("F U R U' R' F'")
        })
        
        return algorithms


def parse_scramble(scramble: str) -> MoveSequence:
    """Parse a scramble sequence from notation.
    
    Parameters
    ----------
    scramble : str
        Scramble notation
        
    Returns
    -------
    MoveSequence
        Parsed scramble sequence
        
    Raises
    ------
    ParseError
        If scramble cannot be parsed
    """
    try:
        return MoveSequence.parse(scramble)
    except ParseError as e:
        raise ParseError(f"Invalid scramble: {e}")


def generate_reverse_scramble(scramble: Union[str, MoveSequence]) -> MoveSequence:
    """Generate the reverse of a scramble (solution).
    
    Parameters
    ----------
    scramble : Union[str, MoveSequence]
        Original scramble
        
    Returns
    -------
    MoveSequence
        Reverse scramble that solves the cube
    """
    if isinstance(scramble, str):
        scramble = MoveSequence.parse(scramble)
    
    return scramble.inverse()