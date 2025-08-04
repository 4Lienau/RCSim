"""Main Cube class providing the public API.

This module contains the primary Cube class that users interact with
to create, manipulate, and query Rubik's Cube instances.
"""

import math
import random
from typing import List, Dict, Optional, Union, Tuple
from copy import deepcopy

from .state import CubeState, Position, Color, Cubie, Orientation, Axis, StandardColors
from .moves import Move, MoveSequence, ParseError


class CubeError(Exception):
    """Exception raised for cube-related errors."""
    pass


class Cube:
    """Main Rubik's Cube class providing the public API.
    
    This class manages a complete Rubik's Cube simulation including
    state management, move execution, scrambling, and solving.
    
    Attributes
    ----------
    size : int
        Size of the cube (2 for 2x2, 3 for 3x3, etc.)
    state : CubeState
        Current state of the cube
    move_history : List[Move]
        History of moves applied to the cube
    """
    
    def __init__(self, size: int = 3):
        """Initialize a new cube in solved state.
        
        Parameters
        ----------
        size : int, optional
            Size of the cube (2-10), defaults to 3 for standard cube
            
        Raises
        ------
        CubeError
            If size is invalid
        """
        if not isinstance(size, int) or size < 2 or size > 10:
            raise CubeError("Cube size must be an integer between 2 and 10")
        
        self.size = size
        self.state = CubeState(size)
        self.move_history: List[Move] = []
        self._scramble_sequence: Optional[MoveSequence] = None
    
    def reset(self) -> None:
        """Reset cube to solved state and clear history."""
        self.state = CubeState(self.size)
        self.move_history.clear()
        self._scramble_sequence = None
    
    def clone(self) -> 'Cube':
        """Create a deep copy of this cube.
        
        Returns
        -------
        Cube
            Exact copy of this cube
        """
        new_cube = Cube.__new__(Cube)  # Skip __init__
        new_cube.size = self.size
        new_cube.state = self.state.clone()
        new_cube.move_history = self.move_history.copy()
        new_cube._scramble_sequence = self._scramble_sequence.copy() if self._scramble_sequence else None
        return new_cube
    
    def apply_move(self, move: Union[Move, str]) -> None:
        """Apply a single move to the cube.
        
        Parameters
        ----------
        move : Union[Move, str]
            Move to apply (Move object or notation string)
            
        Raises
        ------
        CubeError
            If move is invalid or cannot be applied
        ParseError
            If move notation cannot be parsed
        """
        if isinstance(move, str):
            try:
                move = Move.parse(move)
            except ParseError as e:
                raise CubeError(f"Invalid move notation: {e}")
        
        if not isinstance(move, Move):
            raise CubeError(f"Expected Move or str, got {type(move)}")
        
        # Apply the move to the cube state
        self._execute_move(move)
        self.move_history.append(move)
    
    def apply_sequence(self, sequence: Union[MoveSequence, str, List[Union[Move, str]]]) -> None:
        """Apply a sequence of moves to the cube.
        
        Parameters
        ----------
        sequence : Union[MoveSequence, str, List[Union[Move, str]]]
            Sequence of moves to apply
            
        Raises
        ------
        CubeError
            If any move in sequence is invalid
        ParseError
            If sequence notation cannot be parsed
        """
        if isinstance(sequence, str):
            try:
                sequence = MoveSequence.parse(sequence)
            except ParseError as e:
                raise CubeError(f"Invalid sequence notation: {e}")
        elif isinstance(sequence, list):
            sequence = MoveSequence(sequence)
        
        if not isinstance(sequence, MoveSequence):
            raise CubeError(f"Expected MoveSequence, str, or list, got {type(sequence)}")
        
        for move in sequence:
            self.apply_move(move)
    
    def _execute_move(self, move: Move) -> None:
        """Execute a move by updating the cube state.
        
        Parameters
        ----------
        move : Move
            Move to execute
        """
        # Get all positions affected by this move
        affected_positions = self._get_affected_positions(move)
        
        if not affected_positions:
            return  # No pieces to move
        
        # Calculate rotation parameters
        axis = move.get_rotation_axis()
        angle = move.get_rotation_angle()
        
        if axis is None:
            raise CubeError(f"Cannot determine rotation axis for move {move}")
        
        # Store pieces that will be moved
        moving_pieces = []
        for pos in affected_positions:
            piece = self.state.get_piece_at_position(pos)
            if piece:
                moving_pieces.append((pos, piece))
        
        # Calculate new positions and orientations for all pieces first 
        # to avoid conflicts during simultaneous movement
        piece_moves = []
        for old_pos, piece in moving_pieces:
            # Calculate new position after rotation
            new_pos = self._rotate_position(old_pos, axis, angle)
            piece_moves.append((old_pos, piece, new_pos))
        
        # Remove all moving pieces from their old positions first
        for old_pos, piece, new_pos in piece_moves:
            if old_pos in self.state._position_map:
                del self.state._position_map[old_pos]
        
        # Apply rotation and move to new positions
        for old_pos, piece, new_pos in piece_moves:
            # Update piece orientation
            piece.rotate(axis, angle)
            
            # Move piece to new position
            piece.move_to_position(new_pos)
            self.state._position_map[new_pos] = piece
    
    def _get_affected_positions(self, move: Move) -> List[Position]:
        """Get all positions affected by a move.
        
        Parameters
        ----------
        move : Move
            Move to analyze
            
        Returns
        -------
        List[Position]
            List of positions that will be moved
        """
        affected = []
        
        # Check all pieces in the cube
        for cubie in self.state.cubies:
            if move.affects_position(cubie.current_position, self.size):
                affected.append(cubie.current_position)
        
        return affected
    
    def _rotate_position(self, position: Position, axis: Axis, angle_degrees: int) -> Position:
        """Rotate a position around the given axis.
        
        Parameters
        ----------
        position : Position
            Position to rotate
        axis : Axis
            Axis of rotation
        angle_degrees : int
            Rotation angle in degrees
            
        Returns
        -------
        Position
            New position after rotation
        """
        return position.rotate_around_axis(axis.value, angle_degrees)
    
    def scramble(self, num_moves: int = 25, seed: Optional[int] = None) -> MoveSequence:
        """Generate and apply a random scramble to the cube.
        
        Parameters
        ----------
        num_moves : int, optional
            Number of moves in the scramble, defaults to 25
        seed : int, optional
            Random seed for reproducible scrambles
            
        Returns
        -------
        MoveSequence
            The scramble sequence that was applied
        """
        if seed is not None:
            random.seed(seed)
        
        if num_moves < 1:
            raise CubeError("Number of scramble moves must be at least 1")
        
        # Generate random moves
        faces = ['R', 'U', 'L', 'D', 'F', 'B']
        amounts = [1, 2, 3]  # Normal, double, prime
        
        scramble_moves = []
        last_face = None
        
        for _ in range(num_moves):
            # Avoid consecutive moves on the same face
            available_faces = [f for f in faces if f != last_face]
            
            # Also avoid opposite faces to reduce redundancy
            if last_face:
                opposite_faces = {'R': 'L', 'L': 'R', 'U': 'D', 'D': 'U', 'F': 'B', 'B': 'F'}
                opposite = opposite_faces.get(last_face)
                if opposite and opposite in available_faces:
                    available_faces.remove(opposite)
            
            face = random.choice(available_faces)
            amount = random.choice(amounts)
            
            move = Move(face=face, amount=amount)
            scramble_moves.append(move)
            last_face = face
        
        scramble_sequence = MoveSequence(scramble_moves)
        self._scramble_sequence = scramble_sequence
        
        # Apply the scramble
        self.apply_sequence(scramble_sequence)
        
        return scramble_sequence
    
    def get_scramble(self) -> Optional[MoveSequence]:
        """Get the scramble sequence used to scramble this cube.
        
        Returns
        -------
        Optional[MoveSequence]
            Scramble sequence, or None if cube wasn't scrambled
        """
        return self._scramble_sequence
    
    def solve_with_reverse(self) -> Optional[MoveSequence]:
        """Solve the cube by reversing the scramble sequence.
        
        This is a simple solving method that only works if the cube
        was scrambled using the scramble() method.
        
        Returns
        -------
        Optional[MoveSequence]
            Solution sequence, or None if no scramble to reverse
        """
        if not self._scramble_sequence:
            return None
        
        solution = self._scramble_sequence.inverse()
        self.apply_sequence(solution)
        return solution
    
    def is_solved(self) -> bool:
        """Check if the cube is in solved state.
        
        Returns
        -------
        bool
            True if cube is solved
        """
        return self.state.is_solved()
    
    def get_face_colors(self, face: str) -> List[List[Color]]:
        """Get the colors on a specific face.
        
        Parameters
        ----------
        face : str
            Face to get ('U', 'D', 'L', 'R', 'F', 'B')
            
        Returns
        -------
        List[List[Color]]
            2D array of colors on the face
            
        Raises
        ------
        CubeError
            If face is invalid
        """
        try:
            return self.state.get_face_colors(face)
        except ValueError as e:
            raise CubeError(str(e))
    
    def get_all_face_colors(self) -> Dict[str, List[List[Color]]]:
        """Get colors for all faces.
        
        Returns
        -------
        Dict[str, List[List[Color]]]
            Dictionary mapping face names to color arrays
        """
        faces = ['U', 'D', 'L', 'R', 'F', 'B']
        return {face: self.get_face_colors(face) for face in faces}
    
    def get_piece_count(self) -> Dict[str, int]:
        """Get count of pieces by type.
        
        Returns
        -------
        Dict[str, int]
            Count of corner, edge, and center pieces
        """
        corners = len(self.state.get_pieces_by_type('corner'))
        edges = len(self.state.get_pieces_by_type('edge'))
        centers = len(self.state.get_pieces_by_type('center'))
        
        return {
            'corners': corners,
            'edges': edges,
            'centers': centers,
            'total': corners + edges + centers
        }
    
    def get_move_count(self) -> int:
        """Get the number of moves applied to this cube.
        
        Returns
        -------
        int
            Number of moves in history
        """
        return len(self.move_history)
    
    def get_move_history(self) -> List[Move]:
        """Get the history of moves applied to this cube.
        
        Returns
        -------
        List[Move]
            Copy of move history
        """
        return self.move_history.copy()
    
    def undo_last_move(self) -> Optional[Move]:
        """Undo the last move applied to the cube.
        
        Returns
        -------
        Optional[Move]
            The move that was undone, or None if no moves to undo
        """
        if not self.move_history:
            return None
        
        last_move = self.move_history.pop()
        inverse_move = last_move.inverse()
        
        # Apply inverse without adding to history
        self._execute_move(inverse_move)
        
        return last_move
    
    def undo_moves(self, count: int) -> List[Move]:
        """Undo multiple moves.
        
        Parameters
        ----------
        count : int
            Number of moves to undo
            
        Returns
        -------
        List[Move]
            List of moves that were undone
        """
        if count < 0:
            raise CubeError("Count must be non-negative")
        
        undone_moves = []
        for _ in range(min(count, len(self.move_history))):
            move = self.undo_last_move()
            if move:
                undone_moves.append(move)
        
        return undone_moves
    
    def validate_state(self) -> Dict[str, bool]:
        """Validate the current cube state.
        
        Returns
        -------
        Dict[str, bool]
            Dictionary of validation results
        """
        result = {
            'valid_piece_count': True,
            'valid_colors': True,
            'valid_positions': True,
            'solvable': True
        }
        
        # Check piece counts
        expected_counts = self._get_expected_piece_counts()
        actual_counts = self.get_piece_count()
        
        for piece_type in ['corners', 'edges', 'centers']:
            if actual_counts[piece_type] != expected_counts[piece_type]:
                result['valid_piece_count'] = False
                break
        
        # Check that all pieces have valid colors
        standard_colors = set(StandardColors.get_all_colors())
        for cubie in self.state.cubies:
            for color in cubie.colors.values():
                if color not in standard_colors:
                    result['valid_colors'] = False
                    break
        
        # Check that all pieces are in valid positions
        for cubie in self.state.cubies:
            if abs(cubie.current_position.x) > (self.size - 1) / 2:
                result['valid_positions'] = False
                break
            if abs(cubie.current_position.y) > (self.size - 1) / 2:
                result['valid_positions'] = False
                break
            if abs(cubie.current_position.z) > (self.size - 1) / 2:
                result['valid_positions'] = False
                break
        
        return result
    
    def _get_expected_piece_counts(self) -> Dict[str, int]:
        """Get expected piece counts for this cube size.
        
        Returns
        -------
        Dict[str, int]
            Expected counts for each piece type
        """
        if self.size == 2:
            return {'corners': 8, 'edges': 0, 'centers': 0}
        elif self.size == 3:
            return {'corners': 8, 'edges': 12, 'centers': 6}
        else:
            # For larger cubes: 8 corners, 12*(n-2) edges, 6*(n-2)^2 centers
            edges = 12 * (self.size - 2)
            centers = 6 * (self.size - 2) ** 2
            return {'corners': 8, 'edges': edges, 'centers': centers}
    
    def get_cube_info(self) -> Dict[str, Union[int, bool, str]]:
        """Get comprehensive information about the cube.
        
        Returns
        -------
        Dict[str, Union[int, bool, str]]
            Dictionary with cube information
        """
        validation = self.validate_state()
        piece_counts = self.get_piece_count()
        
        return {
            'size': self.size,
            'is_solved': self.is_solved(),
            'move_count': self.get_move_count(),
            'total_pieces': piece_counts['total'],
            'corners': piece_counts['corners'],
            'edges': piece_counts['edges'],
            'centers': piece_counts['centers'],
            'is_valid': all(validation.values()),
            'has_scramble': self._scramble_sequence is not None,
            'scramble_length': len(self._scramble_sequence) if self._scramble_sequence else 0
        }
    
    def __eq__(self, other) -> bool:
        """Check equality with another cube.
        
        Parameters
        ----------
        other : Cube
            Other cube to compare
            
        Returns
        -------
        bool
            True if cubes have identical states
        """
        if not isinstance(other, Cube):
            return False
        
        return (self.size == other.size and 
                self.state == other.state)
    
    def __str__(self) -> str:
        """String representation of the cube."""
        status = "solved" if self.is_solved() else "scrambled"
        return f"Cube(size={self.size}, {status}, moves={len(self.move_history)})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"Cube(size={self.size}, solved={self.is_solved()}, "
                f"moves={len(self.move_history)}, "
                f"pieces={self.get_piece_count()['total']})")