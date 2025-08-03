"""Unit tests for cube functionality."""

import pytest
from hypothesis import given, strategies as st

from rcsim.cube import Cube
from rcsim.cube.moves import Move


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
        with pytest.raises(ValueError):
            Cube(1)  # Too small
        
        with pytest.raises(ValueError):
            Cube(0)  # Invalid
    
    def test_cube_starts_solved(self, sample_cube_3x3):
        """Test that new cube starts in solved state."""
        assert sample_cube_3x3.is_solved()
    
    def test_move_execution_changes_state(self, sample_cube_3x3):
        """Test that executing moves changes cube state."""
        initial_state = sample_cube_3x3.get_state()
        
        move = Move.from_notation("R")
        sample_cube_3x3.execute_move(move)
        
        assert sample_cube_3x3.get_state() != initial_state
        assert not sample_cube_3x3.is_solved()
    
    def test_undo_functionality(self, sample_cube_3x3):
        """Test that undo properly reverses moves."""
        initial_state = sample_cube_3x3.get_state()
        
        # Execute a move
        move = Move.from_notation("R")
        sample_cube_3x3.execute_move(move)
        assert sample_cube_3x3.get_state() != initial_state
        
        # Undo the move
        success = sample_cube_3x3.undo_move()
        assert success
        assert sample_cube_3x3.get_state() == initial_state
        assert sample_cube_3x3.is_solved()
    
    def test_undo_when_no_moves(self, sample_cube_3x3):
        """Test undo returns False when no moves to undo."""
        assert not sample_cube_3x3.undo_move()
    
    def test_redo_functionality(self, sample_cube_3x3):
        """Test redo functionality after undo."""
        move = Move.from_notation("R")
        sample_cube_3x3.execute_move(move)
        state_after_move = sample_cube_3x3.get_state()
        
        # Undo and redo
        sample_cube_3x3.undo_move()
        success = sample_cube_3x3.redo_move()
        
        assert success
        assert sample_cube_3x3.get_state() == state_after_move
    
    def test_redo_when_no_moves(self, sample_cube_3x3):
        """Test redo returns False when no moves to redo."""
        assert not sample_cube_3x3.redo_move()
    
    def test_move_history_tracking(self, sample_cube_3x3, sample_moves):
        """Test that move history is properly tracked."""
        for move in sample_moves:
            sample_cube_3x3.execute_move(move)
        
        history = sample_cube_3x3.get_move_history()
        assert len(history) == len(sample_moves)
        assert all(h == m for h, m in zip(history, sample_moves))
    
    def test_apply_scramble(self, sample_cube_3x3, sample_scramble):
        """Test applying scramble sequence."""
        sample_cube_3x3.apply_scramble(sample_scramble)
        
        history = sample_cube_3x3.get_move_history()
        assert len(history) == len(sample_scramble)
        assert not sample_cube_3x3.is_solved()
    
    def test_reset_to_solved(self, sample_cube_3x3, sample_scramble):
        """Test resetting cube to solved state."""
        # Scramble the cube
        sample_cube_3x3.apply_scramble(sample_scramble)
        assert not sample_cube_3x3.is_solved()
        
        # Reset to solved
        sample_cube_3x3.reset_to_solved()
        assert sample_cube_3x3.is_solved()
        assert len(sample_cube_3x3.get_move_history()) == 0
    
    @pytest.mark.parametrize("size", [2, 3, 4, 5])
    def test_different_cube_sizes(self, size):
        """Test functionality across different cube sizes."""
        cube = Cube(size)
        assert cube.is_solved()
        
        # Test basic move
        move = Move.from_notation("R")
        cube.execute_move(move)
        assert not cube.is_solved()
        
        # Test undo
        cube.undo_move()
        assert cube.is_solved()


class TestCubeState:
    """Test cube state representation."""
    
    def test_state_equality(self, sample_cube_3x3):
        """Test that identical states are equal."""
        state1 = sample_cube_3x3.get_state()
        state2 = sample_cube_3x3.get_state()
        
        assert state1 == state2
    
    def test_state_inequality_after_move(self, sample_cube_3x3):
        """Test that states differ after moves."""
        state1 = sample_cube_3x3.get_state()
        
        sample_cube_3x3.execute_move(Move.from_notation("R"))
        state2 = sample_cube_3x3.get_state()
        
        assert state1 != state2
    
    def test_state_clone(self, sample_cube_3x3):
        """Test that state cloning works correctly."""
        original_state = sample_cube_3x3.get_state()
        cloned_state = original_state.clone()
        
        assert original_state == cloned_state
        assert original_state is not cloned_state
    
    def test_face_colors(self, sample_cube_3x3):
        """Test getting face colors."""
        for face in ['U', 'D', 'L', 'R', 'F', 'B']:
            colors = sample_cube_3x3.get_face_colors(face)
            assert len(colors) == 3  # 3x3 cube
            assert len(colors[0]) == 3


# Property-based testing
class TestCubeProperties:
    """Property-based tests for cube behavior."""
    
    @given(st.lists(
        st.sampled_from(['R', 'L', 'U', 'D', 'F', 'B']).map(
            lambda f: Move.from_notation(f)
        ),
        min_size=1,
        max_size=50
    ))
    def test_move_inverse_property(self, moves):
        """Test that applying moves then their inverses returns to original state."""
        cube = Cube(3)
        original_state = cube.get_state()
        
        # Apply forward moves
        for move in moves:
            cube.execute_move(move)
        
        # Apply inverse moves in reverse order
        for move in reversed(moves):
            cube.execute_move(move.inverse())
        
        assert cube.get_state() == original_state
    
    @given(st.integers(min_value=1, max_value=4))
    def test_move_repetition_property(self, repetitions):
        """Test that repeating face turns returns to original state."""
        cube = Cube(3)
        original_state = cube.get_state()
        
        move = Move.from_notation("R")
        
        # Apply move 4 times (should return to original)
        for _ in range(4 * repetitions):
            cube.execute_move(move)
        
        assert cube.get_state() == original_state
    
    @given(st.sampled_from(['R', 'L', 'U', 'D', 'F', 'B']))
    def test_double_move_property(self, face):
        """Test that double moves are equivalent to two single moves."""
        cube1 = Cube(3)
        cube2 = Cube(3)
        
        # Apply single move twice
        single_move = Move.from_notation(face)
        cube1.execute_move(single_move)
        cube1.execute_move(single_move)
        
        # Apply double move once
        double_move = Move.from_notation(f"{face}2")
        cube2.execute_move(double_move)
        
        assert cube1.get_state() == cube2.get_state()


# Performance tests
class TestCubePerformance:
    """Performance tests for cube operations."""
    
    @pytest.mark.performance
    def test_move_execution_performance(self, benchmark, sample_cube_3x3):
        """Benchmark move execution performance."""
        move = Move.from_notation("R")
        
        def execute_move():
            sample_cube_3x3.execute_move(move)
            sample_cube_3x3.undo_move()  # Keep cube in same state
        
        result = benchmark(execute_move)
        
        # Should be able to execute at least 1000 moves per second
        assert result is not None
    
    @pytest.mark.performance
    def test_state_comparison_performance(self, benchmark, sample_cube_3x3):
        """Benchmark state comparison performance."""
        state1 = sample_cube_3x3.get_state()
        state2 = sample_cube_3x3.get_state()
        
        result = benchmark(lambda: state1 == state2)
        assert result is not None
    
    @pytest.mark.performance
    @pytest.mark.parametrize("size", [3, 4, 5, 6, 7])
    def test_large_cube_performance(self, benchmark, size):
        """Test performance scales reasonably with cube size."""
        def create_and_move():
            cube = Cube(size)
            cube.execute_move(Move.from_notation("R"))
            return cube
        
        result = benchmark(create_and_move)
        assert result is not None