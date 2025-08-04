#!/usr/bin/env python3
"""Detailed debug test to see what happens during move execution."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rcsim.cube import Cube
from rcsim.cube.moves import Move
from rcsim.cube.state import Position

def debug_move_execution():
    """Debug the move execution step by step."""
    print("=== Detailed Debug: Move Execution ===")
    
    cube = Cube(3)
    print(f"Initial cube: {cube}")
    print(f"Number of cubies: {len(cube.state.cubies)}")
    
    # Check initial positions
    print("\nInitial piece positions (first 5):")
    for i, cubie in enumerate(cube.state.cubies[:5]):
        print(f"  {i}: {cubie}")
    
    # Parse R move
    r_move = Move.parse("R")
    print(f"\nParsed R move: {r_move}")
    print(f"Move type: {r_move.move_type}")
    print(f"Rotation axis: {r_move.get_rotation_axis()}")
    print(f"Rotation angle: {r_move.get_rotation_angle()}")
    
    # Check which positions are affected
    print("\nChecking which positions are affected by R move:")
    affected_positions = []
    for cubie in cube.state.cubies:
        if r_move.affects_position(cubie.current_position, cube.size):
            affected_positions.append(cubie.current_position)
            print(f"  Affected: {cubie.current_position} - {cubie}")
    
    print(f"\nTotal affected positions: {len(affected_positions)}")
    
    if len(affected_positions) == 0:
        print("❌ ERROR: No positions are affected by R move!")
        return False
    
    # Apply the move manually step by step
    print("\nApplying R move...")
    
    # Store initial state
    initial_piece_positions = {}
    for cubie in cube.state.cubies:
        initial_piece_positions[cubie.original_position] = cubie.current_position
    
    # Apply move
    cube.apply_move(r_move)
    
    # Check what changed
    print("\nAfter R move:")
    changes = 0
    for cubie in cube.state.cubies:
        if cubie.current_position != initial_piece_positions[cubie.original_position]:
            print(f"  MOVED: {cubie.original_position} -> {cubie.current_position}")
            changes += 1
    
    print(f"Total pieces that moved: {changes}")
    
    if changes == 0:
        print("❌ ERROR: No pieces moved after applying R!")
        return False
    else:
        print(f"✅ {changes} pieces moved as expected")
        return True

def debug_position_affects():
    """Debug which positions should be affected by R move."""
    print("\n=== Debug: Position Affects Logic ===")
    
    cube = Cube(3)
    r_move = Move.parse("R")
    
    print(f"Cube size: {cube.size}")
    print(f"Half size: {(cube.size - 1) / 2}")
    
    # Test specific positions that should be on R face
    test_positions = [
        Position(1, 1, 1),   # Should be affected (corner)
        Position(1, 0, 1),   # Should be affected (edge)  
        Position(1, -1, 1),  # Should be affected (corner)
        Position(1, 1, 0),   # Should be affected (edge)
        Position(1, 0, 0),   # Should be affected (center)
        Position(1, -1, 0),  # Should be affected (edge)
        Position(1, 1, -1),  # Should be affected (corner)
        Position(1, 0, -1),  # Should be affected (edge)
        Position(1, -1, -1), # Should be affected (corner)
        Position(0, 0, 0),   # Should NOT be affected
        Position(-1, 0, 0),  # Should NOT be affected
    ]
    
    print("\nTesting specific positions:")
    for pos in test_positions:
        affected = r_move.affects_position(pos, cube.size)
        print(f"  {pos}: {'AFFECTED' if affected else 'not affected'}")
    
    # Count actual pieces at R face positions
    r_face_pieces = 0
    for cubie in cube.state.cubies:
        if r_move.affects_position(cubie.current_position, cube.size):
            r_face_pieces += 1
    
    print(f"\nTotal pieces on R face: {r_face_pieces}")
    print("Expected pieces on R face for 3x3: 9 (1 center + 4 edges + 4 corners)")
    
    return r_face_pieces == 9

if __name__ == "__main__":
    print("Running detailed debug tests...")
    
    result1 = debug_position_affects()
    result2 = debug_move_execution()
    
    print(f"\nResults:")
    print(f"Position affects test: {'PASS' if result1 else 'FAIL'}")
    print(f"Move execution test: {'PASS' if result2 else 'FAIL'}")