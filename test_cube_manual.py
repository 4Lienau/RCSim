#!/usr/bin/env python3
"""Manual testing script for the cube engine."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rcsim.cube import Cube
from rcsim.cube.moves import Move, MoveSequence, StandardAlgorithms

def test_basic_functionality():
    """Test basic cube operations."""
    print("=== Basic Functionality Test ===")
    
    # Create cube
    cube = Cube(3)
    print(f"Created 3x3 cube: {cube}")
    print(f"Is solved: {cube.is_solved()}")
    
    # Apply some moves
    print("\nApplying moves: R U R' U'")
    cube.apply_move("R")
    cube.apply_move("U")
    cube.apply_move("R'")
    cube.apply_move("U'")
    
    print(f"After moves - Is solved: {cube.is_solved()}")
    print(f"Move count: {cube.get_move_count()}")
    
    # Test undo
    print(f"\nUndoing last move: {cube.undo_last_move()}")
    print(f"Move count after undo: {cube.get_move_count()}")


def test_move_parsing():
    """Test move notation parsing."""
    print("\n=== Move Parsing Test ===")
    
    test_moves = ["R", "R'", "R2", "Rw", "Rw'", "M", "M2", "x", "y'", "z2"]
    
    for notation in test_moves:
        try:
            move = Move.parse(notation)
            print(f"{notation:3} -> {move} (type: {move.move_type.value}, amount: {move.amount})")
        except Exception as e:
            print(f"{notation:3} -> ERROR: {e}")


def test_sequences():
    """Test move sequences."""
    print("\n=== Move Sequences Test ===")
    
    # Parse sequence
    sequence = MoveSequence.parse("R U R' U R U2 R'")
    print(f"Parsed sequence: {sequence}")
    print(f"Length: {len(sequence)} moves")
    
    # Test optimization
    redundant = MoveSequence.parse("R R R U U' F F'")
    optimized = redundant.optimize()
    print(f"Redundant:  {redundant}")
    print(f"Optimized:  {optimized}")
    
    # Test inverse
    inverse = sequence.inverse()
    print(f"Original:   {sequence}")
    print(f"Inverse:    {inverse}")


def test_scrambling():
    """Test scrambling and solving."""
    print("\n=== Scrambling Test ===")
    
    cube = Cube(3)
    print(f"Initial state: {cube}")
    
    # Generate scramble
    scramble = cube.scramble(num_moves=10, seed=42)
    print(f"Scramble: {scramble}")
    print(f"After scramble: {cube}")
    
    # Solve by reversing
    if cube.get_scramble():
        solution = cube.solve_with_reverse()
        print(f"Solution: {solution}")
        print(f"After solution: {cube}")


def test_algorithms():
    """Test standard algorithms."""
    print("\n=== Algorithms Test ===")
    
    algorithms = StandardAlgorithms.get_triggers()
    
    for name, algorithm in algorithms.items():
        print(f"{name:12}: {algorithm}")


def test_cube_info():
    """Test cube information methods."""
    print("\n=== Cube Information Test ===")
    
    cube = Cube(3)
    
    # Get piece counts
    pieces = cube.get_piece_count()
    print(f"Piece counts: {pieces}")
    
    # Get comprehensive info
    info = cube.get_cube_info()
    print("Cube info:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test validation
    validation = cube.validate_state()
    print(f"Validation: {validation}")


def test_different_sizes():
    """Test different cube sizes."""
    print("\n=== Different Cube Sizes Test ===")
    
    for size in [2, 3, 4, 5]:
        cube = Cube(size)
        pieces = cube.get_piece_count()
        print(f"{size}x{size} cube: {pieces['total']} pieces "
              f"({pieces['corners']} corners, {pieces['edges']} edges, {pieces['centers']} centers)")


def test_face_colors():
    """Test face color representation."""
    print("\n=== Face Colors Test ===")
    
    cube = Cube(3)
    
    # Get colors for each face
    for face in ['U', 'D', 'L', 'R', 'F', 'B']:
        colors = cube.get_face_colors(face)
        print(f"Face {face}: {len(colors)}x{len(colors[0])} grid")
        # Print first color as example
        if colors:
            sample_color = colors[0][0]
            print(f"  Sample color: {sample_color.name} {sample_color.to_hex()}")


def test_performance():
    """Basic performance test."""
    print("\n=== Basic Performance Test ===")
    
    import time
    
    cube = Cube(3)
    
    # Test move execution speed
    start_time = time.time()
    for i in range(1000):
        cube.apply_move("R")
        cube.apply_move("U")
        cube.apply_move("R'")
        cube.apply_move("U'")
    end_time = time.time()
    
    elapsed = end_time - start_time
    moves_per_second = 4000 / elapsed if elapsed > 0 else float('inf')
    
    print(f"Executed 4000 moves in {elapsed:.3f}s")
    print(f"Performance: {moves_per_second:.0f} moves/second")
    
    # Reset cube
    cube.reset()
    print(f"Reset cube: {cube}")


if __name__ == "__main__":
    print("Advanced Rubik's Cube Simulator - Core Engine Test")
    print("=" * 50)
    
    try:
        test_basic_functionality()
        test_move_parsing()
        test_sequences()
        test_scrambling()
        test_algorithms()
        test_cube_info()
        test_different_sizes()
        test_face_colors()
        test_performance()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)