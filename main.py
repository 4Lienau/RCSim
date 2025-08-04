#!/usr/bin/env python3
"""
Advanced Rubik's Cube Simulator - Main Program
Entry point for running the cube simulator.
"""

import sys
import os
import argparse

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_demo():
    """Run the capability demo."""
    from demo import main as demo_main
    demo_main()

def run_interactive():
    """Run interactive mode."""
    from test_interactive import main as interactive_main
    interactive_main()

def run_tests():
    """Run the test suite."""
    from run_tests import run_basic_tests
    success = run_basic_tests()
    return success

def run_manual_test():
    """Run manual tests."""
    import subprocess
    result = subprocess.run([sys.executable, 'test_cube_manual.py'], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    return result.returncode == 0

def run_graphics(cube_size=3):
    """Run graphics mode with 3D visualization."""
    try:
        from rcsim.graphics import Scene, WindowConfig, RenderConfig
        from rcsim.cube import Cube
        
        print(f"Starting 3D graphics mode with {cube_size}x{cube_size} cube...")
        
        # Create a cube
        cube = Cube(cube_size)
        
        # Apply some interesting moves
        if cube_size == 3:
            cube.apply_sequence("R U R' U R U2 R'")  # Sune algorithm
        else:
            cube.scramble(num_moves=10)
        
        print(f"Cube created: {cube}")
        print(f"Solved: {cube.is_solved()}")
        
        # Configure graphics
        window_config = WindowConfig(
            width=1000,
            height=800,
            title=f"Advanced Rubik's Cube Simulator - {cube_size}x{cube_size}",
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
        
        print("3D graphics initialized successfully!")
        scene.run(target_fps=60)
        
    except ImportError as e:
        print(f"❌ Graphics dependencies missing: {e}")
        print("Install with: pip install pygame PyOpenGL numpy")
        return False
    
    except Exception as e:
        print(f"❌ Graphics error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def run_solvers():
    """Run solver demo."""
    try:
        from rcsim.cube import Cube
        from rcsim.solvers import LayerByLayerSolver, CFOPSolver
        
        print("Starting solver demonstration...")
        
        # Create and scramble a cube
        cube = Cube(3)
        scramble = cube.scramble(num_moves=8, seed=42)
        
        print(f"Scrambled cube with: {scramble}")
        print(f"Cube state: {cube}")
        print(f"Is solved: {cube.is_solved()}")
        
        # Test Layer-by-Layer solver
        print("\n" + "="*50)
        print("LAYER-BY-LAYER SOLVER")
        print("="*50)
        
        lbl_cube = cube.clone()
        lbl_solver = LayerByLayerSolver()
        
        steps = lbl_solver.solve(lbl_cube)
        print(f"Solution found in {len(steps)} steps")
        print(f"Total moves: {lbl_solver.total_moves}")
        print(f"Solve time: {lbl_solver.solve_time:.3f}s")
        print(f"Final state solved: {lbl_cube.is_solved()}")
        
        summary = lbl_solver.get_solution_summary()
        print(f"Phase breakdown: {summary['phase_breakdown']}")
        
        # Test CFOP solver
        print("\n" + "="*50)
        print("CFOP SOLVER")
        print("="*50)
        
        cfop_cube = cube.clone()
        cfop_solver = CFOPSolver()
        
        steps = cfop_solver.solve(cfop_cube)
        print(f"Solution found in {len(steps)} steps")
        print(f"Total moves: {cfop_solver.total_moves}")
        print(f"Solve time: {cfop_solver.solve_time:.3f}s")
        print(f"Final state solved: {cfop_cube.is_solved()}")
        
        summary = cfop_solver.get_solution_summary()
        print(f"Phase breakdown: {summary['phase_breakdown']}")
        
        # Comparison
        print("\n" + "="*50)
        print("SOLVER COMPARISON")
        print("="*50)
        print(f"Layer-by-Layer: {lbl_solver.total_moves} moves in {lbl_solver.solve_time:.3f}s")
        print(f"CFOP: {cfop_solver.total_moves} moves in {cfop_solver.solve_time:.3f}s")
        
        if cfop_solver.total_moves > 0:
            efficiency = lbl_solver.total_moves / cfop_solver.total_moves
            print(f"CFOP is {efficiency:.1f}x more efficient in move count")
        
        return True
        
    except Exception as e:
        print(f"❌ Solver error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Advanced Rubik\'s Cube Simulator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 main.py demo        # Show capabilities demo
  python3 main.py interactive # Interactive cube shell  
  python3 main.py test        # Run test suite
  python3 main.py manual      # Run manual tests
  python3 main.py graphics    # 3D graphics mode
  python3 main.py graphics --size 4  # 4x4 cube graphics
  python3 main.py solvers     # Solving algorithms demo

Note: Graphics mode requires: pip install pygame PyOpenGL numpy
        """
    )
    
    parser.add_argument('mode', nargs='?', default='demo',
                       choices=['demo', 'interactive', 'test', 'manual', 'graphics', 'solvers'],
                       help='Mode to run (default: demo)')
    
    parser.add_argument('--size', type=int, default=3, choices=range(2, 11),
                       metavar='2-10', help='Cube size for graphics mode (default: 3)')
    
    parser.add_argument('--version', action='version', version='0.1.0')
    
    args = parser.parse_args()
    
    print("Advanced Rubik's Cube Simulator v0.1.0")
    print("=" * 40)
    
    try:
        if args.mode == 'demo':
            print("Running capabilities demo...\n")
            run_demo()
            
        elif args.mode == 'interactive':
            print("Starting interactive mode...\n")
            run_interactive()
            
        elif args.mode == 'test':
            print("Running test suite...\n")
            success = run_tests()
            sys.exit(0 if success else 1)
            
        elif args.mode == 'manual':
            print("Running manual tests...\n")
            success = run_manual_test()
            sys.exit(0 if success else 1)
            
        elif args.mode == 'graphics':
            print("Starting 3D graphics mode...\n")
            run_graphics(args.size)
            
        elif args.mode == 'solvers':
            print("Starting solving algorithms demo...\n")
            run_solvers()
            
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()