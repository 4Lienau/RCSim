#!/usr/bin/env python3
"""Debug position rotation logic."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rcsim.cube.state import Position, Axis

def test_position_rotation():
    """Test position rotation logic."""
    print("=== Debug: Position Rotation ===")
    
    # Test rotating a corner position around X-axis (R move)
    original_pos = Position(1.0, -1.0, -1.0)  # Back-bottom-right corner
    print(f"Original position: {original_pos}")
    
    # Rotate 90 degrees around X-axis (like R move)
    rotated_pos = original_pos.rotate_around_axis('x', 90)
    print(f"After 90° X rotation: {rotated_pos}")
    
    # Rotate 90 degrees more (should be 180 degrees total)
    rotated_pos2 = rotated_pos.rotate_around_axis('x', 90) 
    print(f"After another 90° X rotation: {rotated_pos2}")
    
    # Rotate back 90 degrees (should return to original)
    back_rotated = rotated_pos.rotate_around_axis('x', -90)
    print(f"After -90° X rotation: {back_rotated}")
    
    # Check if we got back to original
    positions_match = (abs(back_rotated.x - original_pos.x) < 0.001 and
                      abs(back_rotated.y - original_pos.y) < 0.001 and 
                      abs(back_rotated.z - original_pos.z) < 0.001)
    
    print(f"Positions match after reverse rotation: {positions_match}")
    
    # Test all R face positions
    print("\nTesting all R face positions:")
    r_face_positions = [
        Position(1.0, -1.0, -1.0), Position(1.0, -1.0, 0.0), Position(1.0, -1.0, 1.0),
        Position(1.0, 0.0, -1.0),  Position(1.0, 0.0, 0.0),  Position(1.0, 0.0, 1.0),
        Position(1.0, 1.0, -1.0),  Position(1.0, 1.0, 0.0),  Position(1.0, 1.0, 1.0)
    ]
    
    all_good = True
    for pos in r_face_positions:
        rotated = pos.rotate_around_axis('x', 90)
        back = rotated.rotate_around_axis('x', -90)
        
        matches = (abs(back.x - pos.x) < 0.001 and
                  abs(back.y - pos.y) < 0.001 and 
                  abs(back.z - pos.z) < 0.001)
        
        if not matches:
            print(f"  FAIL: {pos} -> {rotated} -> {back}")
            all_good = False
        else:
            print(f"  PASS: {pos} -> {rotated} -> {back}")
    
    return all_good

def test_move_angles():
    """Test if R and R' have opposite angles."""
    print("\n=== Debug: Move Angles ===")
    
    from rcsim.cube.moves import Move
    
    r_move = Move.parse("R")
    r_prime_move = Move.parse("R'")
    
    print(f"R move angle: {r_move.get_rotation_angle()}°")
    print(f"R' move angle: {r_prime_move.get_rotation_angle()}°")
    
    # R should be 90°, R' should be 270° (or -90°)
    r_angle = r_move.get_rotation_angle()
    r_prime_angle = r_prime_move.get_rotation_angle()
    
    # Check if they are opposites (accounting for 360° wrap)
    opposite = ((r_angle + r_prime_angle) % 360) == 0
    print(f"Angles are opposite: {opposite}")
    
    return opposite

if __name__ == "__main__":
    print("Running position rotation debug tests...")
    
    result1 = test_position_rotation()
    result2 = test_move_angles()
    
    print(f"\nResults:")
    print(f"Position rotation test: {'PASS' if result1 else 'FAIL'}")
    print(f"Move angles test: {'PASS' if result2 else 'FAIL'}")