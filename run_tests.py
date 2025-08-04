#!/usr/bin/env python3
"""Run tests without pytest - minimal test runner."""

import sys
import os
import unittest
import importlib.util

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_basic_tests():
    """Run basic functionality tests."""
    print("Running Basic Tests...")
    print("=" * 40)
    
    from rcsim.cube import Cube
    from rcsim.cube.moves import Move, MoveSequence
    
    failures = 0
    tests = 0
    
    def assert_equal(actual, expected, description):
        nonlocal tests, failures
        tests += 1
        if actual == expected:
            print(f"✅ {description}")
        else:
            print(f"❌ {description}: expected {expected}, got {actual}")
            failures += 1
    
    def assert_true(condition, description):
        assert_equal(condition, True, description)
        
    def assert_false(condition, description):
        assert_equal(condition, False, description)
    
    # Test cube creation
    cube = Cube(3)
    assert_true(cube.is_solved(), "New cube should be solved")
    assert_equal(cube.size, 3, "Cube size should be 3")
    assert_equal(cube.get_move_count(), 0, "New cube should have 0 moves")
    
    # Test move parsing
    move = Move.parse("R")
    assert_equal(str(move), "R", "Move parsing should work")
    
    move_prime = Move.parse("R'")
    assert_equal(str(move_prime), "R'", "Prime move parsing should work")
    
    # Test move application
    cube.apply_move("R")
    assert_false(cube.is_solved(), "Cube should not be solved after R")
    assert_equal(cube.get_move_count(), 1, "Should have 1 move after R")
    
    # Test undo
    undone = cube.undo_last_move()
    assert_equal(str(undone), "R", "Should undo R move")
    assert_true(cube.is_solved(), "Should be solved after undo")
    
    # Test sequence parsing
    seq = MoveSequence.parse("R U R' U'")
    assert_equal(len(seq), 4, "Sequence should have 4 moves")
    
    # Test sequence application
    cube.apply_sequence(seq)
    assert_false(cube.is_solved(), "Should not be solved after sexy move")
    
    # Test scrambling
    cube.reset()
    scramble = cube.scramble(num_moves=5, seed=42)
    assert_equal(len(scramble), 5, "Scramble should have 5 moves")
    assert_false(cube.is_solved(), "Should not be solved after scramble")
    
    # Test solving by reverse
    solution = cube.solve_with_reverse()
    assert_true(solution is not None, "Should return solution")
    assert_true(cube.is_solved(), "Should be solved after reverse solution")
    
    # Test cube sizes
    for size in [2, 3, 4, 5]:
        test_cube = Cube(size)
        assert_true(test_cube.is_solved(), f"{size}x{size} cube should start solved")
        assert_equal(test_cube.size, size, f"{size}x{size} cube should have correct size")
    
    # Test move inverse property
    cube = Cube(3)
    moves = [Move.parse(m) for m in ["R", "U", "F", "D"]]
    for move in moves:
        cube.apply_move(move)
    for move in reversed(moves):
        cube.apply_move(move.inverse())
    assert_true(cube.is_solved(), "Should be solved after applying moves and their inverses")
    
    print(f"\nResults: {tests - failures}/{tests} tests passed")
    if failures == 0:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {failures} test(s) failed")
    
    return failures == 0

if __name__ == "__main__":
    success = run_basic_tests()
    sys.exit(0 if success else 1)