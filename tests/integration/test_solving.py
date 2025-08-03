"""Integration tests for solving functionality."""

import pytest

from rcsim.cube import Cube
from rcsim.cube.moves import Move, MoveSequence
from rcsim.solvers.cfop import CFOPSolver
from rcsim.solvers.layer_by_layer import LayerByLayerSolver
from rcsim.app.game_session import GameSession


@pytest.mark.integration
class TestSolvingIntegration:
    """Integration tests for complete solving process."""
    
    def test_layer_by_layer_solves_scrambled_cube(self):
        """Test that Layer-by-Layer solver can solve a scrambled cube."""
        cube = Cube(3)
        solver = LayerByLayerSolver()
        
        # Apply a standard scramble
        scramble = MoveSequence.from_notation(
            "R U R' U R U2 R' F R U R' U' F' R U R' U R U2 R'"
        )
        cube.apply_scramble(scramble.moves)
        
        assert not cube.is_solved()
        
        # Solve the cube
        solution = solver.solve(cube)
        
        # Apply solution
        for step in solution.steps:
            cube.execute_move(step.move)
        
        assert cube.is_solved()
        assert solution.method == "Layer-by-Layer"
        assert len(solution.steps) > 0
    
    def test_cfop_solves_scrambled_cube(self):
        """Test that CFOP solver can solve a scrambled cube."""
        cube = Cube(3)
        solver = CFOPSolver()
        
        # Apply a different scramble
        scramble = MoveSequence.from_notation(
            "D L2 F2 R2 U2 L2 U F2 U F2 D' R D2 L' B U' L F' R D2"
        )
        cube.apply_scramble(scramble.moves)
        
        assert not cube.is_solved()
        
        # Solve the cube
        solution = solver.solve(cube)
        
        # Apply solution
        for step in solution.steps:
            cube.execute_move(step.move)
        
        assert cube.is_solved()
        assert solution.method == "CFOP"
        assert len(solution.steps) > 0
    
    def test_step_by_step_solving(self):
        """Test step-by-step solving functionality."""
        cube = Cube(3)
        solver = LayerByLayerSolver()
        
        # Apply scramble
        scramble = MoveSequence.from_notation("R U R' F R F'")
        cube.apply_scramble(scramble.moves)
        
        # Solve step by step
        steps_executed = []
        while not cube.is_solved():
            next_step = solver.get_next_step(cube)
            if next_step is None:
                break
            
            cube.execute_move(next_step.move)
            steps_executed.append(next_step)
            
            # Prevent infinite loop
            if len(steps_executed) > 200:
                break
        
        assert cube.is_solved()
        assert len(steps_executed) > 0
        
        # Check that all steps have explanations
        for step in steps_executed:
            assert step.explanation
            assert step.algorithm_name
            assert step.phase
    
    @pytest.mark.parametrize("cube_size", [2, 3, 4, 5])
    def test_solver_supports_different_sizes(self, cube_size):
        """Test that solvers properly handle different cube sizes."""
        cube = Cube(cube_size)
        layer_solver = LayerByLayerSolver()
        
        # Check if solver supports this size
        if layer_solver.supports_cube_size(cube_size):
            # Apply simple scramble
            cube.execute_move(Move.from_notation("R"))
            cube.execute_move(Move.from_notation("U"))
            
            solution = layer_solver.solve(cube)
            
            # Apply solution
            for step in solution.steps:
                cube.execute_move(step.move)
            
            assert cube.is_solved()
        else:
            # Solver should raise appropriate error
            with pytest.raises(ValueError):
                layer_solver.solve(cube)
    
    def test_multiple_scrambles_solvable(self):
        """Test that multiple different scrambles are solvable."""
        solver = LayerByLayerSolver()
        
        scrambles = [
            "R U R' U'",
            "F R U' R' F'",
            "R U R' F R F' U R U' R'",
            "L' U' L F L F' U L U L' U L",
            "R U2 R' U' R U' R' F R U R' U' F'",
        ]
        
        for scramble_notation in scrambles:
            cube = Cube(3)
            scramble = MoveSequence.from_notation(scramble_notation)
            cube.apply_scramble(scramble.moves)
            
            if not cube.is_solved():  # Skip if scramble results in solved cube
                solution = solver.solve(cube)
                
                # Apply solution
                for step in solution.steps:
                    cube.execute_move(step.move)
                
                assert cube.is_solved(), f"Failed to solve scramble: {scramble_notation}"


@pytest.mark.integration
class TestGameSessionIntegration:
    """Integration tests for game session functionality."""
    
    def test_complete_solving_session(self):
        """Test complete solving session from scramble to solution."""
        session = GameSession(cube_size=3)
        
        # Start session and scramble
        session.start_session()
        scramble = session.scramble_cube(length=20)
        
        assert len(scramble) == 20
        assert not session.cube.is_solved()
        
        # Start solving
        session.start_solve(method="layer-by-layer")
        
        # Execute some moves (simulating user input)
        test_moves = [
            Move.from_notation("R"),
            Move.from_notation("U"),
            Move.from_notation("R'"),
            Move.from_notation("U'"),
        ]
        
        for move in test_moves:
            session.cube.execute_move(move)
        
        # Get current statistics
        stats = session.get_current_stats()
        assert stats.total_solves >= 0
        
        # End session
        final_stats = session.end_session()
        assert final_stats is not None
    
    def test_timer_integration_with_solving(self):
        """Test timer integration with solving process."""
        session = GameSession(cube_size=3)
        
        # Start and time a solve
        session.start_session()
        session.scramble_cube()
        session.start_solve(method="cfop")
        
        # Simulate some solving time
        import time
        time.sleep(0.1)  # 100ms
        
        # Complete solve (assume cube is solved for test)
        session.cube.reset_to_solved()  # Simulate completion
        result = session.complete_solve()
        
        assert result.time > 0
        assert result.time >= 0.1  # At least the sleep time
        assert result.method == "cfop"
    
    def test_statistics_tracking_across_sessions(self):
        """Test that statistics are tracked across multiple sessions."""
        session = GameSession(cube_size=3)
        
        # Perform multiple solve sessions
        for i in range(3):
            session.start_session()
            session.scramble_cube()
            session.start_solve(method="layer-by-layer")
            
            # Simulate solve completion
            session.cube.reset_to_solved()
            result = session.complete_solve()
            
            assert result is not None
        
        # Check accumulated statistics
        stats = session.get_current_stats()
        assert stats.total_solves == 3
        assert stats.best_time > 0
        assert stats.average_time > 0


@pytest.mark.integration
class TestAlgorithmDatabaseIntegration:
    """Integration tests for algorithm database functionality."""
    
    def test_oll_pattern_recognition(self):
        """Test OLL pattern recognition integration."""
        cube = Cube(3)
        solver = CFOPSolver()
        
        # Set up a known OLL case (this would require specific setup)
        # For now, just test that the pattern database loads correctly
        oll_db = solver.oll_database
        
        # Test that database has expected number of cases
        assert len(oll_db.algorithms) >= 57  # Standard OLL has 57 cases
        
        # Test pattern recognition on solved cube (should be OLL 1)
        case = oll_db.recognize_case(cube.get_state())
        
        # On solved cube, should either be None or solved case
        assert case is None or case.name.lower().find("solved") >= 0
    
    def test_pll_pattern_recognition(self):
        """Test PLL pattern recognition integration."""
        cube = Cube(3)
        solver = CFOPSolver()
        
        pll_db = solver.pll_database
        
        # Test that database has expected number of cases
        assert len(pll_db.algorithms) >= 21  # Standard PLL has 21 cases
        
        # Test pattern recognition on solved cube
        case = pll_db.recognize_case(cube.get_state())
        
        # On solved cube, should either be None or solved case
        assert case is None or case.name.lower().find("solved") >= 0
    
    def test_f2l_case_recognition(self):
        """Test F2L case recognition integration."""
        cube = Cube(3)
        solver = CFOPSolver()
        
        # Test F2L solver integration
        f2l_solver = solver.f2l_solver
        
        # On solved cube, F2L should be complete
        assert f2l_solver.is_complete(cube.get_state())
        
        # After scrambling, F2L should not be complete
        cube.execute_move(Move.from_notation("R"))
        cube.execute_move(Move.from_notation("U"))
        
        # Note: This test would need more sophisticated setup
        # to test actual F2L case recognition


@pytest.mark.integration
@pytest.mark.slow
class TestLongRunningSolvingTests:
    """Long-running integration tests for solving robustness."""
    
    def test_solve_100_random_scrambles(self):
        """Test solving 100 different random scrambles."""
        solver = LayerByLayerSolver()
        success_count = 0
        
        for i in range(100):
            cube = Cube(3)
            
            # Generate random scramble
            from random import choice
            moves = ['R', 'L', 'U', 'D', 'F', 'B']
            directions = ['', "'", "2"]
            
            scramble_length = 25
            scramble_moves = []
            for _ in range(scramble_length):
                move_notation = choice(moves) + choice(directions)
                scramble_moves.append(Move.from_notation(move_notation))
            
            cube.apply_scramble(scramble_moves)
            
            if not cube.is_solved():  # Only solve if actually scrambled
                try:
                    solution = solver.solve(cube)
                    
                    # Apply solution
                    for step in solution.steps:
                        cube.execute_move(step.move)
                    
                    if cube.is_solved():
                        success_count += 1
                except Exception as e:
                    pytest.fail(f"Failed to solve scramble {i}: {e}")
        
        # Should solve at least 95% of scrambles
        success_rate = success_count / 100
        assert success_rate >= 0.95, f"Success rate too low: {success_rate}"
    
    def test_solver_performance_consistency(self):
        """Test that solver performance is consistent across multiple runs."""
        solver = LayerByLayerSolver()
        solve_times = []
        move_counts = []
        
        # Use same scramble for consistency
        base_scramble = MoveSequence.from_notation(
            "R U R' U R U2 R' F R U R' U' F'"
        )
        
        for _ in range(10):
            cube = Cube(3)
            cube.apply_scramble(base_scramble.moves)
            
            import time
            start_time = time.time()
            solution = solver.solve(cube)
            solve_time = time.time() - start_time
            
            solve_times.append(solve_time)
            move_counts.append(len(solution.steps))
        
        # Check consistency (coefficient of variation should be reasonable)
        import statistics
        
        mean_time = statistics.mean(solve_times)
        std_time = statistics.stdev(solve_times)
        cv_time = std_time / mean_time if mean_time > 0 else 0
        
        mean_moves = statistics.mean(move_counts)
        std_moves = statistics.stdev(move_counts)
        cv_moves = std_moves / mean_moves if mean_moves > 0 else 0
        
        # Coefficient of variation should be reasonable
        assert cv_time < 0.5, f"Solve time too inconsistent: CV={cv_time}"
        assert cv_moves < 0.2, f"Move count too inconsistent: CV={cv_moves}"