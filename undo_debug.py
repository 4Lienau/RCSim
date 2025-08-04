#!/usr/bin/env python3
"""Debug the undo logic specifically."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rcsim.cube import Cube
from rcsim.cube.moves import Move

def debug_undo_vs_inverse():
    """Test undo vs applying inverse move."""
    print("=== Debug: Undo vs Inverse Move ===")
    
    # Test 1: Apply R, then undo
    cube1 = Cube(3)
    print(f"Cube1 initial: solved={cube1.is_solved()}")
    
    cube1.apply_move("R")
    print(f"Cube1 after R: solved={cube1.is_solved()}")
    
    undone_move = cube1.undo_last_move()
    print(f"Cube1 after undo: solved={cube1.is_solved()}")
    print(f"Undone move was: {undone_move}")
    
    # Test 2: Apply R, then apply R'
    cube2 = Cube(3)
    print(f"\nCube2 initial: solved={cube2.is_solved()}")
    
    cube2.apply_move("R")
    print(f"Cube2 after R: solved={cube2.is_solved()}")
    
    cube2.apply_move("R'")
    print(f"Cube2 after R': solved={cube2.is_solved()}")
    
    # Test 3: Check what inverse move is being calculated
    r_move = Move.parse("R")
    r_inverse = r_move.inverse()
    print(f"\nR move: {r_move}")
    print(f"R inverse: {r_inverse}")
    r_prime_str = "R'"
    print(f"R inverse equals R': {str(r_inverse) == r_prime_str}")
    
    # Test 4: Apply inverse move manually
    cube3 = Cube(3)
    cube3.apply_move("R")
    cube3.apply_move(r_inverse)
    print(f"Cube3 after R and manual inverse: solved={cube3.is_solved()}")
    
    return cube1.is_solved() and cube2.is_solved() and cube3.is_solved()

def debug_move_history():
    """Debug move history during undo."""
    print("\n=== Debug: Move History ===")
    
    cube = Cube(3)
    print(f"Initial history length: {len(cube.move_history)}")
    
    cube.apply_move("R")
    print(f"After R - history length: {len(cube.move_history)}")
    print(f"History: {[str(m) for m in cube.move_history]}")
    
    cube.apply_move("U")
    print(f"After U - history length: {len(cube.move_history)}")
    print(f"History: {[str(m) for m in cube.move_history]}")
    
    undone = cube.undo_last_move()
    print(f"After undo - history length: {len(cube.move_history)}")
    print(f"History: {[str(m) for m in cube.move_history]}")
    print(f"Undone move: {undone}")
    
    # Check if we can undo again
    undone2 = cube.undo_last_move()
    print(f"After second undo - history length: {len(cube.move_history)}")
    print(f"History: {[str(m) for m in cube.move_history]}")
    print(f"Second undone move: {undone2}")
    print(f"Cube is solved: {cube.is_solved()}")
    
    return cube.is_solved()

if __name__ == "__main__":
    print("Running undo debug tests...")
    
    result1 = debug_undo_vs_inverse()
    result2 = debug_move_history()
    
    print(f"\nResults:")
    print(f"Undo vs inverse test: {'PASS' if result1 else 'FAIL'}")
    print(f"Move history test: {'PASS' if result2 else 'FAIL'}")