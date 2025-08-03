"""Unit tests for move system."""

import pytest
from hypothesis import given, strategies as st

from rcsim.cube.moves import Move, MoveSequence, ParseError


class TestMove:
    """Test individual move functionality."""
    
    def test_move_creation(self):
        """Test creating moves with different parameters."""
        move = Move("R", 1, False)
        assert move.face == "R"
        assert move.direction == 1
        assert move.wide is False
    
    def test_move_from_notation(self):
        """Test parsing moves from standard notation."""
        test_cases = [
            ("R", Move("R", 1, False)),
            ("R'", Move("R", -1, False)),
            ("R2", Move("R", 2, False)),
            ("r", Move("R", 1, True)),
            ("r'", Move("R", -1, True)),
            ("r2", Move("R", 2, True)),
            ("Rw", Move("R", 1, True)),
            ("Rw'", Move("R", -1, True)),
            ("Rw2", Move("R", 2, True)),
        ]
        
        for notation, expected in test_cases:
            move = Move.from_notation(notation)
            assert move == expected
    
    def test_move_to_notation(self):
        """Test converting moves to notation."""
        test_cases = [
            (Move("R", 1, False), "R"),
            (Move("R", -1, False), "R'"),
            (Move("R", 2, False), "R2"),
            (Move("R", 1, True), "r"),
            (Move("R", -1, True), "r'"),
            (Move("R", 2, True), "r2"),
        ]
        
        for move, expected in test_cases:
            assert move.to_notation() == expected
    
    def test_move_inverse(self):
        """Test move inverse calculation."""
        test_cases = [
            (Move("R", 1, False), Move("R", -1, False)),
            (Move("R", -1, False), Move("R", 1, False)),
            (Move("R", 2, False), Move("R", 2, False)),  # Double move is its own inverse
        ]
        
        for move, expected_inverse in test_cases:
            assert move.inverse() == expected_inverse
    
    def test_invalid_move_notation(self):
        """Test that invalid notation raises ParseError."""
        invalid_notations = [
            "",
            "X",  # Invalid face
            "R3",  # Invalid direction
            "R''",  # Double prime
            "RR",  # Double face
        ]
        
        for invalid in invalid_notations:
            with pytest.raises(ParseError):
                Move.from_notation(invalid)
    
    @pytest.mark.parametrize("face", ["R", "L", "U", "D", "F", "B", "M", "E", "S", "x", "y", "z"])
    def test_valid_faces(self, face):
        """Test that all valid faces can be parsed."""
        move = Move.from_notation(face)
        assert move.face == face.upper()
    
    @pytest.mark.parametrize("direction", [1, -1, 2])
    def test_valid_directions(self, direction):
        """Test all valid move directions."""
        move = Move("R", direction, False)
        assert move.direction == direction
    
    def test_move_equality(self):
        """Test move equality comparison."""
        move1 = Move("R", 1, False)
        move2 = Move("R", 1, False)
        move3 = Move("L", 1, False)
        
        assert move1 == move2
        assert move1 != move3
    
    def test_move_immutability(self):
        """Test that moves are immutable."""
        move = Move("R", 1, False)
        
        # Should not be able to modify frozen dataclass
        with pytest.raises(AttributeError):
            move.face = "L"
    
    def test_move_hash(self):
        """Test that moves can be used as dictionary keys."""
        move1 = Move("R", 1, False)
        move2 = Move("R", 1, False)
        move3 = Move("L", 1, False)
        
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
            Move.from_notation("R"),
            Move.from_notation("U"),
            Move.from_notation("R'"),
        ]
        sequence = MoveSequence(moves)
        assert len(sequence.moves) == 3
        assert sequence.moves == moves
    
    def test_sequence_from_notation(self):
        """Test parsing sequence from notation string."""
        notation = "R U R' U R U2 R'"
        sequence = MoveSequence.from_notation(notation)
        
        expected_moves = [Move.from_notation(m) for m in notation.split()]
        assert sequence.moves == expected_moves
    
    def test_sequence_to_notation(self):
        """Test converting sequence to notation."""
        moves = [
            Move.from_notation("R"),
            Move.from_notation("U"),
            Move.from_notation("R'"),
        ]
        sequence = MoveSequence(moves)
        assert sequence.to_notation() == "R U R'"
    
    def test_add_move(self):
        """Test adding moves to sequence."""
        sequence = MoveSequence()
        move = Move.from_notation("R")
        
        sequence.add_move(move)
        assert len(sequence.moves) == 1
        assert sequence.moves[0] == move
    
    def test_sequence_inverse(self):
        """Test sequence inverse calculation."""
        notation = "R U R'"
        sequence = MoveSequence.from_notation(notation)
        inverse = sequence.inverse()
        
        expected_notation = "R U' R'"
        assert inverse.to_notation() == expected_notation
    
    def test_sequence_optimization(self):
        """Test sequence optimization (removing redundant moves)."""
        # Test canceling moves
        notation = "R R' U"
        sequence = MoveSequence.from_notation(notation)
        optimized = sequence.optimize()
        assert optimized.to_notation() == "U"
        
        # Test combining moves
        notation = "R R R"
        sequence = MoveSequence.from_notation(notation)
        optimized = sequence.optimize()
        assert optimized.to_notation() == "R'"
        
        # Test double moves
        notation = "R R"
        sequence = MoveSequence.from_notation(notation)
        optimized = sequence.optimize()
        assert optimized.to_notation() == "R2"
    
    def test_empty_notation_parsing(self):
        """Test parsing empty or whitespace-only notation."""
        for notation in ["", "   ", "\t\n"]:
            sequence = MoveSequence.from_notation(notation)
            assert len(sequence.moves) == 0
    
    def test_sequence_equality(self):
        """Test sequence equality comparison."""
        seq1 = MoveSequence.from_notation("R U R'")
        seq2 = MoveSequence.from_notation("R U R'")
        seq3 = MoveSequence.from_notation("R U L")
        
        assert seq1 == seq2
        assert seq1 != seq3
    
    def test_complex_notation_parsing(self):
        """Test parsing complex notation with various move types."""
        notation = "R U2 D' Rw x y' z2 M E' S"
        sequence = MoveSequence.from_notation(notation)
        
        expected_moves = [Move.from_notation(m) for m in notation.split()]
        assert sequence.moves == expected_moves
        assert sequence.to_notation() == notation


# Property-based testing
class TestMoveProperties:
    """Property-based tests for move behavior."""
    
    @given(st.sampled_from(['R', 'L', 'U', 'D', 'F', 'B']))
    def test_double_inverse_property(self, face):
        """Test that inverse of inverse equals original."""
        move = Move.from_notation(face)
        double_inverse = move.inverse().inverse()
        assert move == double_inverse
    
    @given(st.lists(
        st.sampled_from(['R', 'L', 'U', 'D', 'F', 'B']).map(
            lambda f: Move.from_notation(f)
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
            sequence = MoveSequence.from_notation(notation)
            regenerated = sequence.to_notation()
            reparsed = MoveSequence.from_notation(regenerated)
            assert sequence == reparsed
        except ParseError:
            # Some random strings may not be valid notation
            pass


class TestMoveValidation:
    """Test move validation functionality."""
    
    def test_valid_move_faces(self):
        """Test that all valid move faces are accepted."""
        valid_faces = ['R', 'L', 'U', 'D', 'F', 'B', 'M', 'E', 'S', 'x', 'y', 'z']
        
        for face in valid_faces:
            move = Move(face, 1, False)
            assert move.is_valid()
    
    def test_invalid_move_faces(self):
        """Test that invalid move faces are rejected."""
        invalid_faces = ['X', 'Y', 'Z', 'A', '1', '@']
        
        for face in invalid_faces:
            move = Move(face, 1, False)
            assert not move.is_valid()
    
    def test_valid_move_directions(self):
        """Test that valid directions are accepted."""
        valid_directions = [1, -1, 2]
        
        for direction in valid_directions:
            move = Move("R", direction, False)
            assert move.is_valid()
    
    def test_invalid_move_directions(self):
        """Test that invalid directions are rejected."""
        invalid_directions = [0, 3, -2, 4]
        
        for direction in invalid_directions:
            move = Move("R", direction, False)
            assert not move.is_valid()
    
    def test_wide_move_validation(self):
        """Test wide move validation."""
        # Wide moves should be valid for face turns
        for face in ['R', 'L', 'U', 'D', 'F', 'B']:
            move = Move(face, 1, True)
            assert move.is_valid()
        
        # Wide moves should not be valid for slice moves
        for face in ['M', 'E', 'S']:
            move = Move(face, 1, True)
            assert not move.is_valid()


# Integration tests with cube
class TestMoveIntegration:
    """Test move integration with cube."""
    
    def test_move_execution_on_cube(self, sample_cube_3x3):
        """Test that moves can be executed on cube."""
        move = Move.from_notation("R")
        initial_state = sample_cube_3x3.get_state()
        
        sample_cube_3x3.execute_move(move)
        
        assert sample_cube_3x3.get_state() != initial_state
    
    def test_sequence_execution_on_cube(self, sample_cube_3x3):
        """Test that move sequences can be executed on cube."""
        sequence = MoveSequence.from_notation("R U R' U'")
        initial_state = sample_cube_3x3.get_state()
        
        for move in sequence.moves:
            sample_cube_3x3.execute_move(move)
        
        final_state = sample_cube_3x3.get_state()
        assert final_state != initial_state
    
    def test_algorithm_execution(self, sample_cube_3x3):
        """Test executing common algorithms."""
        # Sexy move (should not solve cube)
        sexy_move = MoveSequence.from_notation("R U R' U'")
        
        for move in sexy_move.moves:
            sample_cube_3x3.execute_move(move)
        
        assert not sample_cube_3x3.is_solved()
        
        # Execute 6 times (should return to solved)
        for _ in range(5):  # Already did once
            for move in sexy_move.moves:
                sample_cube_3x3.execute_move(move)
        
        assert sample_cube_3x3.is_solved()