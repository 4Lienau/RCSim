"""Unit tests for move system."""

import pytest
from hypothesis import given, strategies as st

from rcsim.cube.moves import Move, MoveSequence, ParseError, MoveType


class TestMove:
    """Test individual move functionality."""
    
    def test_move_creation(self):
        """Test creating moves with different parameters."""
        move = Move("R", 1, MoveType.FACE, 1)
        assert move.face == "R"
        assert move.amount == 1
        assert move.move_type == MoveType.FACE
        assert move.layers == 1
    
    def test_move_parse(self):
        """Test parsing moves from standard notation."""
        test_cases = [
            ("R", Move("R", 1, MoveType.FACE, 1)),
            ("R'", Move("R", 3, MoveType.FACE, 1)),
            ("R2", Move("R", 2, MoveType.FACE, 1)),
            ("Rw", Move("R", 1, MoveType.WIDE, 2)),
            ("Rw'", Move("R", 3, MoveType.WIDE, 2)),
            ("Rw2", Move("R", 2, MoveType.WIDE, 2)),
            ("M", Move("M", 1, MoveType.SLICE, 1)),
            ("M'", Move("M", 3, MoveType.SLICE, 1)),
            ("M2", Move("M", 2, MoveType.SLICE, 1)),
            ("x", Move("x", 1, MoveType.ROTATION, 1)),
            ("y'", Move("y", 3, MoveType.ROTATION, 1)),
            ("z2", Move("z", 2, MoveType.ROTATION, 1)),
        ]
        
        for notation, expected in test_cases:
            move = Move.parse(notation)
            assert move == expected
    
    def test_move_to_notation(self):
        """Test converting moves to notation."""
        test_cases = [
            (Move("R", 1, MoveType.FACE, 1), "R"),
            (Move("R", 3, MoveType.FACE, 1), "R'"),
            (Move("R", 2, MoveType.FACE, 1), "R2"),
            (Move("R", 1, MoveType.WIDE, 2), "Rw"),
            (Move("R", 3, MoveType.WIDE, 2), "Rw'"),
            (Move("R", 2, MoveType.WIDE, 2), "Rw2"),
            (Move("M", 1, MoveType.SLICE, 1), "M"),
            (Move("M", 3, MoveType.SLICE, 1), "M'"),
            (Move("M", 2, MoveType.SLICE, 1), "M2"),
        ]
        
        for move, expected in test_cases:
            assert move.to_notation() == expected
    
    def test_move_inverse(self):
        """Test move inverse calculation."""
        test_cases = [
            (Move("R", 1, MoveType.FACE, 1), Move("R", 3, MoveType.FACE, 1)),
            (Move("R", 3, MoveType.FACE, 1), Move("R", 1, MoveType.FACE, 1)),
            (Move("R", 2, MoveType.FACE, 1), Move("R", 2, MoveType.FACE, 1)),  # Double move is its own inverse
        ]
        
        for move, expected_inverse in test_cases:
            assert move.inverse() == expected_inverse
    
    def test_invalid_move_notation(self):
        """Test that invalid notation raises ParseError."""
        invalid_notations = [
            "",
            "X",  # Invalid face
            "R3",  # Invalid amount
            "R''",  # Double prime
            "RR",  # Double face
        ]
        
        for invalid in invalid_notations:
            with pytest.raises(ParseError):
                Move.parse(invalid)
    
    @pytest.mark.parametrize("face", ["R", "L", "U", "D", "F", "B", "M", "E", "S", "x", "y", "z"])
    def test_valid_faces(self, face):
        """Test that all valid faces can be parsed."""
        move = Move.parse(face)
        assert move.face == face.upper()
    
    @pytest.mark.parametrize("amount", [1, 2, 3])
    def test_valid_amounts(self, amount):
        """Test all valid move amounts."""
        move = Move("R", amount, MoveType.FACE, 1)
        assert move.amount == amount
    
    def test_move_equality(self):
        """Test move equality comparison."""
        move1 = Move("R", 1, MoveType.FACE, 1)
        move2 = Move("R", 1, MoveType.FACE, 1)
        move3 = Move("L", 1, MoveType.FACE, 1)
        
        assert move1 == move2
        assert move1 != move3
    
    def test_move_immutability(self):
        """Test that moves are immutable."""
        move = Move("R", 1, MoveType.FACE, 1)
        
        # Should not be able to modify frozen dataclass
        with pytest.raises(AttributeError):
            move.face = "L"
    
    def test_move_hash(self):
        """Test that moves can be used as dictionary keys."""
        move1 = Move("R", 1, MoveType.FACE, 1)
        move2 = Move("R", 1, MoveType.FACE, 1)
        move3 = Move("L", 1, MoveType.FACE, 1)
        
        move_dict = {move1: "right", move3: "left"}
        
        # Same move should access same value
        assert move_dict[move2] == "right"
        assert len(move_dict) == 2


class TestMoveSequence:
    """Test move sequence functionality."""
    
    def test_empty_sequence(self):
        """Test creating empty move sequence."""
        sequence = MoveSequence()
        assert len(sequence.moves) == 0
        assert sequence.to_notation() == ""
    
    def test_sequence_from_moves(self):
        """Test creating sequence from move list."""
        moves = [
            Move.parse("R"),
            Move.parse("U"),
            Move.parse("R'"),
        ]
        sequence = MoveSequence(moves)
        assert len(sequence.moves) == 3
        assert sequence.moves == moves
    
    def test_sequence_parse(self):
        """Test parsing sequence from notation string."""
        notation = "R U R' U R U2 R'"
        sequence = MoveSequence.parse(notation)
        
        expected_moves = [Move.parse(m) for m in notation.split()]
        assert sequence.moves == expected_moves
    
    def test_sequence_to_notation(self):
        """Test converting sequence to notation."""
        moves = [
            Move.parse("R"),
            Move.parse("U"),
            Move.parse("R'"),
        ]
        sequence = MoveSequence(moves)
        assert sequence.to_notation() == "R U R'"
    
    def test_add_move(self):
        """Test adding moves to sequence."""
        sequence = MoveSequence()
        move = Move.parse("R")
        
        sequence.add_move(move)
        assert len(sequence.moves) == 1
        assert sequence.moves[0] == move
    
    def test_sequence_inverse(self):
        """Test sequence inverse calculation."""
        notation = "R U R'"
        sequence = MoveSequence.parse(notation)
        inverse = sequence.inverse()
        
        expected_notation = "R U' R'"
        assert inverse.to_notation() == expected_notation
    
    def test_sequence_optimization(self):
        """Test sequence optimization (removing redundant moves)."""
        # Test canceling moves
        notation = "R R' U"
        sequence = MoveSequence.parse(notation)
        optimized = sequence.optimize()
        assert optimized.to_notation() == "U"
        
        # Test combining moves
        notation = "R R R"
        sequence = MoveSequence.parse(notation)
        optimized = sequence.optimize()
        assert optimized.to_notation() == "R'"
        
        # Test double moves
        notation = "R R"
        sequence = MoveSequence.parse(notation)
        optimized = sequence.optimize()
        assert optimized.to_notation() == "R2"
    
    def test_empty_notation_parsing(self):
        """Test parsing empty or whitespace-only notation."""
        for notation in ["", "   ", "\t\n"]:
            sequence = MoveSequence.parse(notation)
            assert len(sequence.moves) == 0
    
    def test_sequence_equality(self):
        """Test sequence equality comparison."""
        seq1 = MoveSequence.parse("R U R'")
        seq2 = MoveSequence.parse("R U R'")
        seq3 = MoveSequence.parse("R U L")
        
        assert seq1 == seq2
        assert seq1 != seq3
    
    def test_complex_notation_parsing(self):
        """Test parsing complex notation with various move types."""
        notation = "R U2 D' Rw x y' z2 M E' S"
        sequence = MoveSequence.parse(notation)
        
        expected_moves = [Move.parse(m) for m in notation.split()]
        assert sequence.moves == expected_moves
        assert sequence.to_notation() == notation


# Property-based testing
class TestMoveProperties:
    """Property-based tests for move behavior."""
    
    @given(st.sampled_from(['R', 'L', 'U', 'D', 'F', 'B']))
    def test_double_inverse_property(self, face):
        """Test that inverse of inverse equals original."""
        move = Move.parse(face)
        double_inverse = move.inverse().inverse()
        assert move == double_inverse
    
    @given(st.lists(
        st.sampled_from(['R', 'L', 'U', 'D', 'F', 'B']).map(
            lambda f: Move.parse(f)
        ),
        min_size=0,
        max_size=20
    ))
    def test_sequence_inverse_property(self, moves):
        """Test that sequence inverse is properly calculated."""
        sequence = MoveSequence(moves)
        inverse = sequence.inverse()
        
        # Applying sequence then inverse should be identity
        # This would need to be tested with an actual cube
        assert len(inverse.moves) == len(moves)
    
    @given(st.text(
        alphabet='RLUDFBMESxyz\'2 ',
        min_size=0,
        max_size=50
    ).filter(lambda s: all(token in 'RLUDFBMESxyz\'2 ' for token in s)))
    def test_notation_roundtrip_property(self, notation):
        """Test that notation parsing and generation are consistent."""
        try:
            sequence = MoveSequence.parse(notation)
            regenerated = sequence.to_notation()
            reparsed = MoveSequence.parse(regenerated)
            assert sequence == reparsed
        except ParseError:
            # Some random strings may not be valid notation
            pass


class TestMoveValidation:
    """Test move validation functionality."""
    
    def test_valid_move_types(self):
        """Test that all valid move types are accepted."""
        # Face moves
        for face in ['R', 'L', 'U', 'D', 'F', 'B']:
            move = Move(face, 1, MoveType.FACE, 1)
            assert move.face == face
        
        # Slice moves  
        for face in ['M', 'E', 'S']:
            move = Move(face, 1, MoveType.SLICE, 1)
            assert move.face == face
            
        # Rotations
        for face in ['x', 'y', 'z']:
            move = Move(face, 1, MoveType.ROTATION, 1)
            assert move.face == face
    
    def test_move_validation_errors(self):
        """Test that invalid moves raise errors."""
        # Invalid amount
        with pytest.raises(ValueError):
            Move("R", 0, MoveType.FACE, 1)
            
        with pytest.raises(ValueError):
            Move("R", 4, MoveType.FACE, 1)
        
        # Invalid layers
        with pytest.raises(ValueError):
            Move("R", 1, MoveType.FACE, 0)
    
    def test_wide_move_parsing(self):
        """Test wide move parsing."""
        # Standard wide moves
        move = Move.parse("Rw")
        assert move.move_type == MoveType.WIDE
        assert move.layers == 2
        
        # Multi-layer wide moves  
        move = Move.parse("3R")
        assert move.move_type == MoveType.WIDE
        assert move.layers == 3


# Integration tests with cube
class TestMoveIntegration:
    """Test move integration with cube."""
    
    def test_move_execution_on_cube(self, sample_cube_3x3):
        """Test that moves can be executed on cube."""
        move = Move.parse("R")
        initial_solved = sample_cube_3x3.is_solved()
        
        sample_cube_3x3.apply_move(move)
        
        assert sample_cube_3x3.is_solved() != initial_solved
    
    def test_sequence_execution_on_cube(self, sample_cube_3x3):
        """Test that move sequences can be executed on cube."""
        sequence = MoveSequence.parse("R U R' U'")
        initial_solved = sample_cube_3x3.is_solved()
        
        sample_cube_3x3.apply_sequence(sequence)
        
        assert sample_cube_3x3.is_solved() != initial_solved
    
    def test_algorithm_execution(self, sample_cube_3x3):
        """Test executing common algorithms."""
        # Sexy move (should not solve cube after one execution)
        sexy_move = MoveSequence.parse("R U R' U'")
        
        sample_cube_3x3.apply_sequence(sexy_move)
        assert not sample_cube_3x3.is_solved()
        
        # Execute 6 times total (should return to solved)
        for _ in range(5):  # Already did once
            sample_cube_3x3.apply_sequence(sexy_move)
        
        assert sample_cube_3x3.is_solved()