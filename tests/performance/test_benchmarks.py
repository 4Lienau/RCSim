"""Performance benchmarks for Advanced Rubik's Cube Simulator."""

import pytest
import time
from typing import List

from rcsim.cube import Cube
from rcsim.cube.moves import Move, MoveSequence
from rcsim.solvers.cfop import CFOPSolver
from rcsim.solvers.layer_by_layer import LayerByLayerSolver


@pytest.mark.performance
@pytest.mark.slow
class TestCubePerformance:
    """Performance benchmarks for cube operations."""
    
    def test_cube_creation_performance(self, benchmark):
        """Benchmark cube creation across different sizes."""
        def create_cube():
            return Cube(3)
        
        result = benchmark(create_cube)
        assert result.size == 3
    
    @pytest.mark.parametrize("size", [2, 3, 4, 5, 6, 7])
    def test_cube_creation_scaling(self, benchmark, size):
        """Test cube creation performance scaling with size."""
        def create_cube():
            return Cube(size)
        
        result = benchmark(create_cube)
        assert result.size == size
    
    def test_move_execution_performance(self, benchmark, sample_cube_3x3):
        """Benchmark individual move execution."""
        move = Move.from_notation("R")
        
        def execute_move():
            sample_cube_3x3.execute_move(move)
            sample_cube_3x3.undo_move()  # Keep state consistent
        
        benchmark(execute_move)
    
    def test_move_sequence_performance(self, benchmark, sample_cube_3x3):
        """Benchmark executing move sequences."""
        moves = [Move.from_notation(m) for m in ["R", "U", "R'", "U'"] * 10]
        
        def execute_sequence():
            for move in moves:
                sample_cube_3x3.execute_move(move)
            # Undo all moves
            for move in reversed(moves):
                sample_cube_3x3.execute_move(move.inverse())
        
        benchmark(execute_sequence)
    
    def test_state_comparison_performance(self, benchmark, sample_cube_3x3):
        """Benchmark cube state comparison."""
        state1 = sample_cube_3x3.get_state()
        state2 = sample_cube_3x3.get_state()
        
        def compare_states():
            return state1 == state2
        
        result = benchmark(compare_states)
        assert result is True
    
    def test_state_cloning_performance(self, benchmark, sample_cube_3x3):
        """Benchmark cube state cloning."""
        state = sample_cube_3x3.get_state()
        
        def clone_state():
            return state.clone()
        
        result = benchmark(clone_state)
        assert result == state
    
    @pytest.mark.parametrize("size", [3, 4, 5, 6, 7])
    def test_large_cube_move_performance(self, benchmark, size):
        """Test move performance on larger cubes."""
        cube = Cube(size)
        move = Move.from_notation("R")
        
        def execute_move():
            cube.execute_move(move)
            cube.undo_move()
        
        benchmark(execute_move)
    
    def test_scramble_generation_performance(self, benchmark):
        """Benchmark scramble generation."""
        cube = Cube(3)
        
        def generate_and_apply_scramble():
            scramble = cube.generate_scramble(length=25)
            cube.apply_scramble(scramble)
            cube.reset_to_solved()
            return len(scramble)
        
        result = benchmark(generate_and_apply_scramble)
        assert result == 25


@pytest.mark.performance
@pytest.mark.slow
class TestSolvingPerformance:
    """Performance benchmarks for solving algorithms."""
    
    def test_layer_by_layer_solve_performance(self, benchmark):
        """Benchmark Layer-by-Layer solving performance."""
        cube = Cube(3)
        solver = LayerByLayerSolver()
        
        # Apply standard scramble
        scramble = MoveSequence.from_notation(
            "R U R' U R U2 R' F R U R' U' F'"
        )
        
        def solve_cube():
            cube.apply_scramble(scramble.moves)
            solution = solver.solve(cube)
            cube.reset_to_solved()  # Reset for next iteration
            return solution
        
        result = benchmark(solve_cube)
        assert result.method == "Layer-by-Layer"
        assert len(result.steps) > 0
    
    def test_cfop_solve_performance(self, benchmark):
        """Benchmark CFOP solving performance."""
        cube = Cube(3)
        solver = CFOPSolver()
        
        scramble = MoveSequence.from_notation(
            "D L2 F2 R2 U2 L2 U F2 U F2 D' R D2 L' B U' L F' R D2"
        )
        
        def solve_cube():
            cube.apply_scramble(scramble.moves)
            solution = solver.solve(cube)
            cube.reset_to_solved()
            return solution
        
        result = benchmark(solve_cube)
        assert result.method == "CFOP"
        assert len(result.steps) > 0
    
    def test_pattern_recognition_performance(self, benchmark):
        """Benchmark pattern recognition performance."""
        cube = Cube(3)
        solver = CFOPSolver()
        
        # Set up cube in known state for pattern recognition
        setup_moves = MoveSequence.from_notation("R U R' F R F'")
        cube.apply_scramble(setup_moves.moves)
        
        def recognize_patterns():
            state = cube.get_state()
            oll_case = solver.oll_database.recognize_case(state)
            pll_case = solver.pll_database.recognize_case(state)
            return (oll_case, pll_case)
        
        benchmark(recognize_patterns)
    
    def test_step_by_step_performance(self, benchmark):
        """Benchmark step-by-step solving performance."""
        cube = Cube(3)
        solver = LayerByLayerSolver()
        
        scramble = MoveSequence.from_notation("R U R' F R F'")
        
        def solve_step_by_step():
            cube.apply_scramble(scramble.moves)
            steps = []
            
            while not cube.is_solved() and len(steps) < 100:
                next_step = solver.get_next_step(cube)
                if next_step is None:
                    break
                
                cube.execute_move(next_step.move)
                steps.append(next_step)
            
            cube.reset_to_solved()
            return len(steps)
        
        result = benchmark(solve_step_by_step)
        assert result > 0
    
    @pytest.mark.parametrize("scramble_length", [15, 20, 25, 30])
    def test_solve_performance_vs_scramble_length(self, benchmark, scramble_length):
        """Test how solve performance varies with scramble length."""
        cube = Cube(3)
        solver = LayerByLayerSolver()
        
        def solve_with_length():
            # Generate scramble of specific length
            scramble = cube.generate_scramble(length=scramble_length)
            cube.apply_scramble(scramble)
            
            solution = solver.solve(cube)
            cube.reset_to_solved()
            
            return len(solution.steps)
        
        result = benchmark(solve_with_length)
        assert result > 0


@pytest.mark.performance
class TestMemoryPerformance:
    """Memory usage and allocation benchmarks."""
    
    def test_cube_memory_usage(self):
        """Test memory usage of different cube sizes."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_usage = {}
        
        for size in [2, 3, 4, 5, 6, 7]:
            # Measure memory before
            before = process.memory_info().rss
            
            # Create cube
            cube = Cube(size)
            
            # Measure memory after
            after = process.memory_info().rss
            
            memory_usage[size] = after - before
            
            # Clean up
            del cube
        
        # Memory usage should scale reasonably
        for size in [3, 4, 5, 6, 7]:
            if size > 2:
                ratio = memory_usage[size] / memory_usage[2]
                # Should not use more than size^3 times the memory
                assert ratio < size ** 3, f"Memory usage scaling too high for size {size}"
    
    def test_move_history_memory(self, benchmark):
        """Test memory efficiency of move history tracking."""
        cube = Cube(3)
        moves = [Move.from_notation("R")] * 1000
        
        def execute_many_moves():
            for move in moves:
                cube.execute_move(move)
            
            history = cube.get_move_history()
            cube.reset_to_solved()  # Clear history
            
            return len(history)
        
        result = benchmark(execute_many_moves)
        assert result == 1000
    
    def test_solution_memory_efficiency(self, benchmark):
        """Test memory efficiency of solution storage."""
        cube = Cube(3)
        solver = LayerByLayerSolver()
        
        scramble = MoveSequence.from_notation(
            "R U R' U R U2 R' F R U R' U' F'"
        )
        
        def generate_multiple_solutions():
            solutions = []
            for _ in range(10):
                cube.apply_scramble(scramble.moves)
                solution = solver.solve(cube)
                solutions.append(solution)
                cube.reset_to_solved()
            
            return len(solutions)
        
        result = benchmark(generate_multiple_solutions)
        assert result == 10


@pytest.mark.performance
@pytest.mark.slow
class TestScalabilityBenchmarks:
    """Benchmarks for testing scalability across cube sizes."""
    
    @pytest.mark.parametrize("size", [2, 3, 4, 5, 6, 7, 8, 9, 10])
    def test_cube_size_scalability(self, benchmark, size):
        """Test performance scalability across all supported cube sizes."""
        def create_and_manipulate():
            cube = Cube(size)
            
            # Execute some basic moves
            cube.execute_move(Move.from_notation("R"))
            cube.execute_move(Move.from_notation("U"))
            cube.execute_move(Move.from_notation("R'"))
            cube.execute_move(Move.from_notation("U'"))
            
            # Check if solved
            is_solved = cube.is_solved()
            
            return is_solved
        
        result = benchmark(create_and_manipulate)
        assert result is True  # Should return to solved state
    
    def test_concurrent_cube_performance(self, benchmark):
        """Test performance with multiple cubes in memory."""
        def create_multiple_cubes():
            cubes = []
            for size in [2, 3, 4, 5]:
                cube = Cube(size)
                cube.execute_move(Move.from_notation("R"))
                cubes.append(cube)
            
            return len(cubes)
        
        result = benchmark(create_multiple_cubes)
        assert result == 4
    
    def test_long_sequence_performance(self, benchmark):
        """Test performance with very long move sequences."""
        cube = Cube(3)
        
        # Generate long sequence (1000 moves)
        long_sequence = []
        moves = ['R', 'L', 'U', 'D', 'F', 'B']
        for i in range(1000):
            long_sequence.append(Move.from_notation(moves[i % 6]))
        
        def execute_long_sequence():
            for move in long_sequence:
                cube.execute_move(move)
            
            # Reset by undoing all moves
            for move in reversed(long_sequence):
                cube.execute_move(move.inverse())
            
            return cube.is_solved()
        
        result = benchmark(execute_long_sequence)
        assert result is True


@pytest.mark.performance
class TestRenderingPerformanceMocks:
    """Mock tests for rendering performance (without actual graphics)."""
    
    def test_mock_rendering_performance(self, benchmark, mock_renderer):
        """Test mock rendering performance."""
        cube = Cube(3)
        
        def render_frame():
            mock_renderer.render_cube(cube, None)
            mock_renderer.update_animation(1.0/60.0)  # 60 FPS
        
        benchmark(render_frame)
        
        # Verify mock was called
        assert mock_renderer.render_cube.called
        assert mock_renderer.update_animation.called
    
    def test_animation_performance(self, benchmark):
        """Test animation calculation performance."""
        from rcsim.app.animation import AnimationManager
        
        animator = AnimationManager()
        move = Move.from_notation("R")
        
        def create_animation():
            handle = animator.animate_move(move, duration=0.3)
            return handle.is_complete()
        
        result = benchmark(create_animation)
        # Animation should not be complete immediately
        assert result is False


# Regression tests for performance
@pytest.mark.performance
class TestPerformanceRegression:
    """Tests to catch performance regressions."""
    
    def test_move_execution_under_threshold(self, benchmark):
        """Ensure move execution stays under performance threshold."""
        cube = Cube(3)
        move = Move.from_notation("R")
        
        def execute_move():
            cube.execute_move(move)
            cube.undo_move()
        
        result = benchmark(execute_move)
        
        # Should be able to execute at least 10,000 moves per second
        # This translates to max 0.0001 seconds (100 microseconds) per move
        stats = benchmark.stats
        mean_time = stats['mean']
        assert mean_time < 0.0001, f"Move execution too slow: {mean_time}s"
    
    def test_solver_performance_threshold(self, benchmark):
        """Ensure solving stays under performance threshold."""
        cube = Cube(3)
        solver = LayerByLayerSolver()
        
        scramble = MoveSequence.from_notation("R U R' F R F'")
        
        def solve_cube():
            cube.apply_scramble(scramble.moves)
            solution = solver.solve(cube)
            cube.reset_to_solved()
            return solution
        
        result = benchmark(solve_cube)
        
        # Solving should complete within reasonable time (1 second max)
        stats = benchmark.stats
        mean_time = stats['mean']
        assert mean_time < 1.0, f"Solving too slow: {mean_time}s"
        
        # Solution should be reasonable length (under 200 moves)
        assert len(result.steps) < 200, f"Solution too long: {len(result.steps)} moves"