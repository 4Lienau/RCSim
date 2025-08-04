#!/usr/bin/env python3
"""Debug test to isolate the undo issue."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rcsim.cube import Cube
from rcsim.cube.moves import Move

def test_basic_undo():
    """Test basic move and undo functionality."""
    print("=== Debug Test: Basic Move and Undo ===")
    
    cube = Cube(3)
    print(f"Initial state: solved={cube.is_solved()}")
    
    # Get initial face colors
    initial_faces = cube.get_all_face_colors()
    print(f"Initial U face center: {initial_faces['U'][1][1]}")
    
    # Apply R move
    cube.apply_move("R")
    print(f"After R: solved={cube.is_solved()}, moves={cube.get_move_count()}")
    
    # Get face colors after R
    after_r_faces = cube.get_all_face_colors()
    print(f"After R U face center: {after_r_faces['U'][1][1]}")
    
    # Undo the move
    undone_move = cube.undo_last_move()
    print(f"Undone move: {undone_move}")
    print(f"After undo: solved={cube.is_solved()}, moves={cube.get_move_count()}")
    
    # Get face colors after undo
    after_undo_faces = cube.get_all_face_colors()
    print(f"After undo U face center: {after_undo_faces['U'][1][1]}")
    
    # Compare face colors
    faces_match = True
    for face in ['U', 'D', 'L', 'R', 'F', 'B']:
        if initial_faces[face] != after_undo_faces[face]:
            faces_match = False
            print(f"Face {face} doesn't match after undo!")
            break
    
    print(f"Face colors match: {faces_match}")
    return faces_match and cube.is_solved()

def test_move_application():
    """Test if moves are actually being applied correctly."""
    print("\n=== Debug Test: Move Application ===")
    
    cube = Cube(3)
    initial_state = str(cube.state)
    print(f"Initial state hash: {hash(str(cube.state))}")
    
    # Apply R move
    cube.apply_move("R")
    after_r_state = str(cube.state)
    print(f"After R state hash: {hash(str(cube.state))}")
    
    if initial_state == after_r_state:
        print("❌ ERROR: State didn't change after R move!")
        return False
    else:
        print("✅ State changed after R move")
    
    # Apply R'
    cube.apply_move("R'")
    after_rprime_state = str(cube.state)
    print(f"After R' state hash: {hash(str(cube.state))}")
    
    if initial_state == after_rprime_state:
        print("✅ State returned to initial after R R'")
        return True
    else:
        print("❌ ERROR: State didn't return to initial after R R'!")
        return False

if __name__ == "__main__":
    print("Running debug tests...")
    
    result1 = test_basic_undo()
    result2 = test_move_application()
    
    print(f"\nResults:")
    print(f"Basic undo test: {'PASS' if result1 else 'FAIL'}")
    print(f"Move application test: {'PASS' if result2 else 'FAIL'}")
    
    if not result1 or not result2:
        print("\n❌ Some tests failed - there's an issue with move execution or undo logic")
    else:
        print("\n✅ All debug tests passed")