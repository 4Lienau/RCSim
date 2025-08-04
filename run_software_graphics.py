#!/usr/bin/env python3
"""Run the cube simulator with software graphics."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Run the software graphics demo."""
    try:
        from rcsim.cube import Cube
        from rcsim.graphics.software_renderer import SoftwareRenderer
        
        print("Advanced Rubik's Cube Simulator - Software Graphics")
        print("=" * 55)
        
        # Create a cube and apply some moves
        cube = Cube(3)
        cube.apply_sequence("R U R' U R U2 R'")  # Sune algorithm
        
        print(f"Created cube: {cube}")
        print(f"Is solved: {cube.is_solved()}")
        
        # Create and run software renderer
        renderer = SoftwareRenderer(width=1000, height=800)
        renderer.set_cube(cube)
        
        print("\nStarting 3D software renderer...")
        renderer.run()
        
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install: pip install pygame numpy")
        sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()