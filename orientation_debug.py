#!/usr/bin/env python3
"""Debug orientation and solved state checking."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rcsim.cube import Cube
from rcsim.cube.moves import Move

def debug_orientation():
    """Debug piece orientations during moves."""
    print("=== Debug: Piece Orientations ===")
    
    cube = Cube(3)
    print(f"Initial state: solved={cube.is_solved()}")
    
    # Check initial orientations
    print("\nInitial piece orientations (R face pieces):")
    r_move = Move.parse("R")
    for cubie in cube.state.cubies:
        if r_move.affects_position(cubie.current_position, cube.size):
            print(f"  {cubie.current_position}: solved_pos={cubie.is_correctly_positioned()}, solved_orient={cubie.is_correctly_oriented()}, both={cubie.is_in_solved_position()}")
    
    # Apply R move
    cube.apply_move("R")
    print(f"\nAfter R move: solved={cube.is_solved()}")
    
    # Check orientations after R
    print("\nAfter R move orientations (moved pieces):")
    for cubie in cube.state.cubies:
        if not cubie.is_in_solved_position():
            print(f"  {cubie.current_position} (orig: {cubie.original_position}): pos={cubie.is_correctly_positioned()}, orient={cubie.is_correctly_oriented()}, both={cubie.is_in_solved_position()}")
    
    # Undo the move
    undone = cube.undo_last_move()
    print(f"\nUndone move: {undone}")
    print(f"After undo: solved={cube.is_solved()}")
    
    # Check final orientations
    print("\nAfter undo orientations (should all be solved):")
    unsolved_count = 0
    for cubie in cube.state.cubies:
        if not cubie.is_in_solved_position():
            print(f"  UNSOLVED: {cubie.current_position} (orig: {cubie.original_position}): pos={cubie.is_correctly_positioned()}, orient={cubie.is_correctly_oriented()}")
            unsolved_count += 1
    
    print(f"\nTotal unsolved pieces after undo: {unsolved_count}")
    
    return unsolved_count == 0

def debug_move_inverse():
    """Debug if R' is actually the inverse of R."""
    print("\n=== Debug: Move Inverse ===")
    
    cube1 = Cube(3)
    cube2 = Cube(3)
    
    # Apply R to first cube
    cube1.apply_move("R")
    
    # Apply R then R' to second cube
    cube2.apply_move("R")
    cube2.apply_move("R'")
    
    print(f"Cube1 after R: solved={cube1.is_solved()}")
    print(f"Cube2 after R R': solved={cube2.is_solved()}")
    
    # Check if states match
    states_match = cube1.state != cube2.state  # Should be different
    print(f"States are different (as expected): {states_match}")
    
    # Check if cube2 matches original solved state
    original_cube = Cube(3)
    original_matches = cube2.state == original_cube.state
    print(f"Cube2 matches original solved state: {original_matches}")
    
    return original_matches

if __name__ == "__main__":
    print("Running orientation debug tests...")
    
    result1 = debug_orientation()
    result2 = debug_move_inverse()
    
    print(f"\nResults:")
    print(f"Orientation debug: {'PASS' if result1 else 'FAIL'}")
    print(f"Move inverse debug: {'PASS' if result2 else 'FAIL'}")