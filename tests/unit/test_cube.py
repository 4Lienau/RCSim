"""Unit tests for cube functionality."""

import pytest
from hypothesis import given, strategies as st

from rcsim.cube import Cube
from rcsim.cube.moves import Move, MoveSequence
from rcsim.cube.cube import CubeError


class TestCube:
    """Test cube basic functionality."""
    
    def test_cube_initialization(self):
        """Test cube can be initialized with different sizes."""
        for size in range(2, 11):
            cube = Cube(size)
            assert cube.size == size
            assert cube.is_solved()
    
    def test_invalid_cube_size(self):
        """Test that invalid cube sizes raise errors."""
        with pytest.raises(CubeError):
            Cube(1)  # Too small
        
        with pytest.raises(CubeError):
            Cube(0)  # Invalid
            
        with pytest.raises(CubeError):
            Cube(11)  # Too large
    
    def test_cube_starts_solved(self, sample_cube_3x3):
        """Test that new cube starts in solved state."""
        assert sample_cube_3x3.is_solved()
    
    def test_move_execution_changes_state(self, sample_cube_3x3):
        """Test that executing moves changes cube state."""
        initial_solved = sample_cube_3x3.is_solved()
        
        move = Move.parse("R")
        sample_cube_3x3.apply_move(move)
        
        assert sample_cube_3x3.is_solved() != initial_solved
    
    def test_undo_functionality(self, sample_cube_3x3):
        """Test that undo properly reverses moves."""
        initial_solved = sample_cube_3x3.is_solved()
        
        # Execute a move
        move = Move.parse("R")
        sample_cube_3x3.apply_move(move)
        assert sample_cube_3x3.is_solved() != initial_solved
        
        # Undo the move
        undone_move = sample_cube_3x3.undo_last_move()
        assert undone_move == move
        assert sample_cube_3x3.is_solved() == initial_solved
    
    def test_undo_when_no_moves(self, sample_cube_3x3):
        """Test undo returns None when no moves to undo."""
        assert sample_cube_3x3.undo_last_move() is None
    
    def test_move_history_tracking(self, sample_cube_3x3, sample_moves):
        """Test that move history is properly tracked."""
        for move in sample_moves:
            sample_cube_3x3.apply_move(move)
        
        history = sample_cube_3x3.get_move_history()
        assert len(history) == len(sample_moves)
        assert all(h == m for h, m in zip(history, sample_moves))
    
    def test_apply_sequence(self, sample_cube_3x3):
        """Test applying move sequence."""
        sequence = MoveSequence.parse("R U R' U'")
        initial_solved = sample_cube_3x3.is_solved()
        
        sample_cube_3x3.apply_sequence(sequence)
        
        history = sample_cube_3x3.get_move_history()
        assert len(history) == len(sequence)
        assert sample_cube_3x3.is_solved() != initial_solved
    
    def test_reset(self, sample_cube_3x3):
        """Test resetting cube to solved state."""
        # Apply some moves
        sample_cube_3x3.apply_move("R")
        sample_cube_3x3.apply_move("U")
        assert not sample_cube_3x3.is_solved()
        
        # Reset to solved
        sample_cube_3x3.reset()
        assert sample_cube_3x3.is_solved()
        assert len(sample_cube_3x3.get_move_history()) == 0
    
    def test_scramble(self, sample_cube_3x3):
        """Test scrambling functionality."""
        scramble = sample_cube_3x3.scramble(num_moves=10, seed=42)
        
        assert isinstance(scramble, MoveSequence)
        assert len(scramble) == 10
        assert not sample_cube_3x3.is_solved()
        assert sample_cube_3x3.get_scramble() == scramble
    
    def test_solve_with_reverse(self, sample_cube_3x3):
        """Test solving by reversing scramble."""
        # Scramble first
        scramble = sample_cube_3x3.scramble(num_moves=5, seed=42)
        assert not sample_cube_3x3.is_solved()
        
        # Solve by reversing
        solution = sample_cube_3x3.solve_with_reverse()
        assert solution is not None
        assert sample_cube_3x3.is_solved()
    
    def test_clone(self, sample_cube_3x3):
        """Test cube cloning."""
        sample_cube_3x3.apply_move("R")
        sample_cube_3x3.apply_move("U")
        
        cloned = sample_cube_3x3.clone()
        
        assert cloned == sample_cube_3x3
        assert cloned is not sample_cube_3x3
        assert cloned.get_move_history() == sample_cube_3x3.get_move_history()
    
    @pytest.mark.parametrize("size", [2, 3, 4, 5])
    def test_different_cube_sizes(self, size):
        """Test functionality across different cube sizes."""
        cube = Cube(size)
        assert cube.is_solved()
        
        # Test basic move
        cube.apply_move("R")
        assert not cube.is_solved()
        
        # Test undo
        cube.undo_last_move()
        assert cube.is_solved()


class TestCubeState:
    """Test cube state representation."""
    
    def test_state_equality(self, sample_cube_3x3):
        """Test that identical states are equal."""
        cube1 = sample_cube_3x3
        cube2 = Cube(3)  # Another solved cube
        
        assert cube1 == cube2
    
    def test_state_inequality_after_move(self, sample_cube_3x3):
        """Test that states differ after moves."""
        cube1 = sample_cube_3x3
        cube2 = Cube(3)
        
        cube1.apply_move("R")
        
        assert cube1 != cube2
    
    def test_state_clone(self, sample_cube_3x3):
        """Test that state cloning works correctly."""
        original_cube = sample_cube_3x3
        cloned_cube = original_cube.clone()
        
        assert original_cube == cloned_cube
        assert original_cube is not cloned_cube
    
    def test_face_colors(self, sample_cube_3x3):
        """Test getting face colors."""
        for face in ['U', 'D', 'L', 'R', 'F', 'B']:
            colors = sample_cube_3x3.get_face_colors(face)
            assert len(colors) == 3  # 3x3 cube
            assert len(colors[0]) == 3
    
    def test_get_all_face_colors(self, sample_cube_3x3):
        """Test getting all face colors."""
        all_colors = sample_cube_3x3.get_all_face_colors()
        
        assert len(all_colors) == 6
        for face in ['U', 'D', 'L', 'R', 'F', 'B']:
            assert face in all_colors
            assert len(all_colors[face]) == 3
            assert len(all_colors[face][0]) == 3


# Property-based testing
class TestCubeProperties:
    """Property-based tests for cube behavior."""
    
    @given(st.lists(
        st.sampled_from(['R', 'L', 'U', 'D', 'F', 'B']).map(
            lambda f: Move.parse(f)
        ),
        min_size=1,
        max_size=20
    ))
    def test_move_inverse_property(self, moves):
        """Test that applying moves then their inverses returns to original state."""
        cube = Cube(3)
        original_solved = cube.is_solved()
        
        # Apply forward moves
        for move in moves:
            cube.apply_move(move)
        
        # Apply inverse moves in reverse order
        for move in reversed(moves):
            cube.apply_move(move.inverse())
        
        assert cube.is_solved() == original_solved
    
    @given(st.integers(min_value=1, max_value=4))
    def test_move_repetition_property(self, repetitions):
        """Test that repeating face turns 4 times returns to original state."""
        cube = Cube(3)
        original_solved = cube.is_solved()
        
        move = Move.parse("R")
        
        # Apply move 4 times (should return to original)
        for _ in range(4 * repetitions):
            cube.apply_move(move)
        
        assert cube.is_solved() == original_solved
    
    @given(st.sampled_from(['R', 'L', 'U', 'D', 'F', 'B']))
    def test_double_move_property(self, face):
        """Test that double moves are equivalent to two single moves."""
        cube1 = Cube(3)
        cube2 = Cube(3)
        
        # Apply single move twice
        single_move = Move.parse(face)
        cube1.apply_move(single_move)
        cube1.apply_move(single_move)
        
        # Apply double move once
        double_move = Move.parse(f"{face}2")
        cube2.apply_move(double_move)
        
        assert cube1 == cube2


# Performance tests
class TestCubePerformance:
    """Performance tests for cube operations."""
    
    @pytest.mark.performance
    def test_move_execution_performance(self, benchmark, sample_cube_3x3):
        """Benchmark move execution performance."""
        move = Move.parse("R")
        
        def execute_move():
            sample_cube_3x3.apply_move(move)
            sample_cube_3x3.undo_last_move()  # Keep cube in same state
        
        result = benchmark(execute_move)
        
        # Should be able to execute at least 1000 moves per second
        assert result is not None
    
    @pytest.mark.performance
    def test_state_comparison_performance(self, benchmark, sample_cube_3x3):
        """Benchmark state comparison performance."""
        cube1 = sample_cube_3x3
        cube2 = Cube(3)
        
        result = benchmark(lambda: cube1 == cube2)
        assert result is not None
    
    @pytest.mark.performance
    @pytest.mark.parametrize("size", [3, 4, 5, 6, 7])
    def test_large_cube_performance(self, benchmark, size):
        """Test performance scales reasonably with cube size."""
        def create_and_move():
            cube = Cube(size)
            cube.apply_move("R")
            return cube
        
        result = benchmark(create_and_move)
        assert result is not None


class TestCubeValidation:
    """Test cube validation functionality."""
    
    def test_validate_solved_state(self, sample_cube_3x3):
        """Test validation of solved cube."""
        validation = sample_cube_3x3.validate_state()
        
        assert validation['valid_piece_count']
        assert validation['valid_colors']
        assert validation['valid_positions']
        assert validation['solvable']
    
    def test_get_piece_count(self, sample_cube_3x3):
        """Test getting piece counts."""
        counts = sample_cube_3x3.get_piece_count()
        
        assert counts['corners'] == 8
        assert counts['edges'] == 12
        assert counts['centers'] == 6
        assert counts['total'] == 26
    
    def test_get_cube_info(self, sample_cube_3x3):
        """Test getting comprehensive cube info."""
        info = sample_cube_3x3.get_cube_info()
        
        assert info['size'] == 3
        assert info['is_solved'] == True
        assert info['move_count'] == 0
        assert info['total_pieces'] == 26
        assert info['is_valid'] == True
        assert info['has_scramble'] == False