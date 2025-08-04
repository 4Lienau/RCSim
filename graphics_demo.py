#!/usr/bin/env python3
"""Graphics demo for the Advanced Rubik's Cube Simulator."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rcsim.cube import Cube
from rcsim.graphics import Scene, WindowConfig, RenderConfig


def main():
    """Run the graphics demo."""
    print("Starting Advanced Rubik's Cube Simulator Graphics Demo...")
    
    try:
        # Create a 3x3 cube
        cube = Cube(3)
        
        # Apply a few moves to make it interesting
        cube.apply_sequence("R U R' U R U2 R'")  # Sune algorithm
        
        print(f"Created cube: {cube}")
        print(f"Cube is solved: {cube.is_solved()}")
        
        # Configure window and rendering
        window_config = WindowConfig(
            width=1000,
            height=800,
            title="Advanced Rubik's Cube Simulator - Graphics Demo",
            vsync=True,
            msaa_samples=4
        )
        
        render_config = RenderConfig(
            piece_size=0.95,
            gap_size=0.05,
            sticker_inset=0.02,
            enable_shadows=True
        )
        
        # Create and run scene
        scene = Scene(window_config, render_config)
        scene.set_cube(cube)
        
        print("Graphics initialized successfully!")
        print("Starting main loop...")
        
        scene.run(target_fps=60)
        
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install graphics dependencies:")
        print("  pip install pygame PyOpenGL numpy")
        sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        print("Graphics demo finished.")


if __name__ == "__main__":
    main()