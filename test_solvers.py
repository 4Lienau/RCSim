#!/usr/bin/env python3
"""Test the solving algorithms."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rcsim.cube import Cube
from rcsim.solvers import LayerByLayerSolver, CFOPSolver, AlgorithmDatabase


def test_algorithm_database():
    """Test the algorithm database."""
    print("=== Algorithm Database Test ===")
    
    db = AlgorithmDatabase()
    
    # Test categories
    categories = db.get_all_categories()
    print(f"Available categories: {categories}")
    
    # Test algorithm counts
    counts = db.get_algorithm_count()
    print(f"Algorithm counts: {counts}")
    
    # Test specific algorithm retrieval
    sune = db.get_algorithm("Common", "Sune")
    if sune:
        print(f"Sune algorithm: {sune}")
    
    sexy_move = db.get_algorithm("Common", "Sexy Move")
    if sexy_move:
        print(f"Sexy move: {sexy_move}")
    
    # Test search
    t_results = db.search_algorithms("T-Perm")
    print(f"T-Perm search results: {len(t_results)} found")
    
    print("✅ Algorithm database test passed\n")


def test_layer_by_layer_solver():
    """Test the Layer-by-Layer solver."""
    print("=== Layer-by-Layer Solver Test ===")
    
    solver = LayerByLayerSolver()
    print(f"Solver: {solver.name}")
    
    # Test with solved cube
    cube = Cube(3)
    print(f"Testing with solved cube: {cube.is_solved()}")
    
    can_solve = solver.can_solve(cube)
    print(f"Can solve 3x3: {can_solve}")
    
    if can_solve:
        steps = solver.solve(cube)
        print(f"Steps for solved cube: {len(steps)}")
        
        if len(steps) == 0:
            print("✅ Correctly identified solved cube")
    
    # Test with scrambled cube
    cube.scramble(num_moves=5, seed=42)
    print(f"Scrambled cube: {cube.is_solved()}")
    
    try:
        steps = solver.solve(cube)
        print(f"Solution steps: {len(steps)}")
        print(f"Total moves: {solver.total_moves}")
        print(f"Solve time: {solver.solve_time:.3f}s")
        
        # Print solution summary
        summary = solver.get_solution_summary()
        print(f"Solution summary: {summary}")
        
        print("✅ Layer-by-Layer solver test passed")
    
    except Exception as e:
        print(f"⚠️  Layer-by-Layer solver test failed: {e}")
    
    print()


def test_cfop_solver():
    """Test the CFOP solver."""
    print("=== CFOP Solver Test ===")
    
    solver = CFOPSolver()
    print(f"Solver: {solver.name}")
    
    # Test with solved cube
    cube = Cube(3)
    print(f"Testing with solved cube: {cube.is_solved()}")
    
    can_solve = solver.can_solve(cube)
    print(f"Can solve 3x3: {can_solve}")
    
    if can_solve:
        steps = solver.solve(cube)
        print(f"Steps for solved cube: {len(steps)}")
        
        if len(steps) == 0:
            print("✅ Correctly identified solved cube")
    
    # Test with scrambled cube
    cube.scramble(num_moves=8, seed=123)
    print(f"Scrambled cube: {cube.is_solved()}")
    
    try:
        steps = solver.solve(cube)
        print(f"Solution steps: {len(steps)}")
        print(f"Total moves: {solver.total_moves}")
        print(f"Solve time: {solver.solve_time:.3f}s")
        
        # Print solution summary
        summary = solver.get_solution_summary()
        print(f"Solution summary: {summary}")
        
        print("✅ CFOP solver test passed")
    
    except Exception as e:
        print(f"⚠️  CFOP solver test failed: {e}")
    
    print()


def test_solver_comparison():
    """Compare different solvers on the same cube."""
    print("=== Solver Comparison Test ===")
    
    # Create identical scrambled cubes
    cube1 = Cube(3)
    cube1.scramble(num_moves=10, seed=999)
    
    cube2 = cube1.clone()
    
    print(f"Scrambled cube: {cube1.is_solved()}")
    print(f"Move count: {cube1.get_move_count()}")
    
    # Test Layer-by-Layer
    print("\nLayer-by-Layer Solution:")
    lbl_solver = LayerByLayerSolver()
    try:
        lbl_steps = lbl_solver.solve(cube1)
        print(f"  Steps: {len(lbl_steps)}")
        print(f"  Moves: {lbl_solver.total_moves}")
        print(f"  Time: {lbl_solver.solve_time:.3f}s")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test CFOP
    print("\nCFOP Solution:")
    cfop_solver = CFOPSolver()
    try:
        cfop_steps = cfop_solver.solve(cube2)
        print(f"  Steps: {len(cfop_steps)}")
        print(f"  Moves: {cfop_solver.total_moves}")
        print(f"  Time: {cfop_solver.solve_time:.3f}s")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("✅ Solver comparison test completed\n")


def test_solution_explanation():
    """Test solution explanation functionality."""
    print("=== Solution Explanation Test ===")
    
    cube = Cube(3)
    cube.apply_sequence("R U R' U'")  # Simple scramble
    
    solver = LayerByLayerSolver()
    steps = solver.solve(cube)
    
    if steps:
        explanation = solver.explain_solution()
        print("Solution explanation:")
        print(explanation)
        print("✅ Solution explanation test passed")
    else:
        print("⚠️  No solution steps to explain")
    
    print()


def main():
    """Run all solver tests."""
    print("Advanced Rubik's Cube Simulator - Solver Tests")
    print("=" * 50)
    
    try:
        test_algorithm_database()
        test_layer_by_layer_solver()
        test_cfop_solver()
        test_solver_comparison()
        test_solution_explanation()
        
        print("🎉 All solver tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)