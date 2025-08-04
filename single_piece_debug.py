#!/usr/bin/env python3
"""Debug single piece movement in detail."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rcsim.cube import Cube
from rcsim.cube.state import Position

def track_single_piece():
    """Track a single piece through R and R' moves."""
    print("=== Debug: Single Piece Tracking ===")
    
    cube = Cube(3)
    
    # Find the back-bottom-right corner piece
    target_pos = Position(1.0, -1.0, -1.0)
    target_piece = None
    
    for cubie in cube.state.cubies:
        if cubie.current_position == target_pos:
            target_piece = cubie
            break
    
    if not target_piece:
        print("ERROR: Could not find target piece!")
        return False
    
    print(f"Tracking piece: {target_piece}")
    print(f"Original position: {target_piece.original_position}")
    print(f"Current position: {target_piece.current_position}")
    print(f"Orientation: {target_piece.orientation}")
    print(f"Colors: {target_piece.colors}")
    
    # Apply R move
    print(f"\nApplying R move...")
    cube.apply_move("R")
    
    print(f"After R:")
    print(f"Current position: {target_piece.current_position}")
    print(f"Orientation: {target_piece.orientation}")
    print(f"In solved position: {target_piece.is_in_solved_position()}")
    print(f"Correctly positioned: {target_piece.is_correctly_positioned()}")
    print(f"Correctly oriented: {target_piece.is_correctly_oriented()}")
    
    # Expected position after 90° X rotation: (1.0, 1.0, -1.0)
    expected_after_r = Position(1.0, 1.0, -1.0)
    position_correct = target_piece.current_position == expected_after_r
    print(f"Position is as expected: {position_correct}")
    
    # Apply R' move
    print(f"\nApplying R' move...")
    cube.apply_move("R'")
    
    print(f"After R':")
    print(f"Current position: {target_piece.current_position}")
    print(f"Orientation: {target_piece.orientation}")
    print(f"In solved position: {target_piece.is_in_solved_position()}")
    print(f"Correctly positioned: {target_piece.is_correctly_positioned()}")
    print(f"Correctly oriented: {target_piece.is_correctly_oriented()}")
    
    # Should be back to original position
    back_to_original = target_piece.current_position == target_pos
    orientation_solved = target_piece.orientation.is_solved()
    
    print(f"Back to original position: {back_to_original}")
    print(f"Orientation is solved: {orientation_solved}")
    
    return back_to_original and orientation_solved

def debug_position_map():
    """Debug the position mapping in cube state."""
    print("\n=== Debug: Position Mapping ===")
    
    cube = Cube(3)
    
    # Check position map consistency
    print(f"Total cubies: {len(cube.state.cubies)}")
    print(f"Position map entries: {len(cube.state._position_map)}")
    
    # Check that every cubie is in the position map
    map_consistent = True
    for cubie in cube.state.cubies:
        mapped_piece = cube.state._position_map.get(cubie.current_position)
        if mapped_piece != cubie:
            print(f"ERROR: Position map inconsistent for {cubie}")
            map_consistent = False
    
    print(f"Position map is consistent: {map_consistent}")
    
    # Apply R move and check again
    cube.apply_move("R")
    
    print(f"\nAfter R move:")
    print(f"Total cubies: {len(cube.state.cubies)}")
    print(f"Position map entries: {len(cube.state._position_map)}")
    
    # Check consistency again
    for cubie in cube.state.cubies:
        mapped_piece = cube.state._position_map.get(cubie.current_position)
        if mapped_piece != cubie:
            print(f"ERROR: Position map inconsistent for {cubie} after R")
            map_consistent = False
    
    print(f"Position map is consistent after R: {map_consistent}")
    
    return map_consistent

if __name__ == "__main__":
    print("Running single piece debug tests...")
    
    result1 = track_single_piece()
    result2 = debug_position_map()
    
    print(f"\nResults:")
    print(f"Single piece tracking: {'PASS' if result1 else 'FAIL'}")
    print(f"Position map debug: {'PASS' if result2 else 'FAIL'}")