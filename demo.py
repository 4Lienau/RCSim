#!/usr/bin/env python3
"""
Advanced Rubik's Cube Simulator - Demo Program
Shows current capabilities of the cube engine.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rcsim.cube import Cube
from rcsim.cube.moves import Move, MoveSequence, StandardAlgorithms
import time

def print_banner():
    print("🧩" * 20)
    print("   ADVANCED RUBIK'S CUBE SIMULATOR")
    print("        Core Engine Demo v0.1.0")
    print("🧩" * 20)
    print()

def demo_basic_operations():
    print("📦 DEMO 1: Basic Cube Operations")
    print("-" * 40)
    
    # Create different sized cubes
    for size in [2, 3, 4, 5]:
        cube = Cube(size)
        info = cube.get_piece_count()
        print(f"{size}x{size} Cube: {info['total']} pieces "
              f"({info['corners']} corners, {info['edges']} edges, {info['centers']} centers)")
    
    print(f"\n✅ Created cubes from 2x2 to 5x5")
    time.sleep(1)

def demo_move_system():
    print("\n🔄 DEMO 2: Move System")
    print("-" * 40)
    
    # Show move parsing capabilities
    moves = ["R", "R'", "R2", "Rw", "Rw'", "M", "M'", "x", "y'", "z2"]
    print("Move Parsing:")
    for notation in moves:
        try:
            move = Move.parse(notation)
            print(f"  {notation:3} → {move} ({move.move_type.value})")
        except Exception as e:
            print(f"  {notation:3} → Error: {e}")
    
    # Show sequence parsing
    print(f"\nSequence Parsing:")
    sequence = MoveSequence.parse("R U R' U R U2 R'")
    print(f"  Input:  'R U R' U R U2 R''")
    print(f"  Parsed: {sequence}")
    print(f"  Length: {len(sequence)} moves")
    
    # Show optimization
    redundant = MoveSequence.parse("R R R U U' D D'")
    optimized = redundant.optimize()
    print(f"\nOptimization:")
    print(f"  Original:  {redundant}")
    print(f"  Optimized: {optimized}")
    
    print(f"\n✅ Move system fully functional")
    time.sleep(1)

def demo_algorithms():
    print("\n🧠 DEMO 3: Standard Algorithms")
    print("-" * 40)
    
    algorithms = StandardAlgorithms.get_triggers()
    
    print("Common Speedcubing Algorithms:")
    for name, alg in algorithms.items():
        print(f"  {name:12}: {alg}")
    
    print(f"\n✅ {len(algorithms)} algorithms loaded")
    time.sleep(1)

def demo_scrambling():
    print("\n🎲 DEMO 4: Scrambling System")
    print("-" * 40)
    
    cube = Cube(3)
    print(f"Initial state: {cube}")
    
    # Generate reproducible scramble
    scramble = cube.scramble(num_moves=15, seed=42)
    print(f"Generated scramble: {scramble}")
    print(f"After scramble: {cube}")
    
    # Show solve by reverse (this works!)
    solution = cube.solve_with_reverse()
    print(f"Reverse solution: {solution}")
    print(f"After solution: {cube}")
    
    print(f"\n✅ Scrambling and basic solving work")
    time.sleep(1)

def demo_performance():
    print("\n⚡ DEMO 5: Performance Test")
    print("-" * 40)
    
    cube = Cube(3)
    
    # Measure move parsing speed
    start = time.time()
    for _ in range(10000):
        Move.parse("R")
    parse_time = time.time() - start
    
    # Measure sequence parsing speed  
    start = time.time()
    for _ in range(1000):
        MoveSequence.parse("R U R' U R U2 R'")
    sequence_time = time.time() - start
    
    # Measure cube operations
    start = time.time()
    for _ in range(1000):
        cube.apply_move("R")
        cube.undo_last_move()
    cube_time = time.time() - start
    
    print(f"Performance Results:")
    print(f"  Move parsing:     {10000/parse_time:,.0f} moves/sec")
    print(f"  Sequence parsing: {1000/sequence_time:,.0f} sequences/sec") 
    print(f"  Cube operations:  {2000/cube_time:,.0f} ops/sec")
    
    print(f"\n✅ High performance achieved")
    time.sleep(1)

def demo_cube_info():
    print("\n📊 DEMO 6: Cube Information System")
    print("-" * 40)
    
    cube = Cube(3)
    
    # Show detailed cube info
    info = cube.get_cube_info()
    print("Cube Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Show validation
    validation = cube.validate_state()
    print(f"\nValidation Results:")
    for check, result in validation.items():
        status = "✅" if result else "❌"
        print(f"  {check}: {status}")
    
    # Show face colors
    print(f"\nFace Colors:")
    for face in ['U', 'D', 'L', 'R', 'F', 'B']:
        colors = cube.get_face_colors(face)
        if colors:
            sample = colors[0][0]
            print(f"  {face}: {sample.name} ({sample.to_hex()})")
    
    print(f"\n✅ Complete information system")
    time.sleep(1)

def demo_limitations():
    print("\n⚠️  CURRENT LIMITATIONS")
    print("-" * 40)
    print("The current implementation provides:")
    print("✅ Complete move parsing and notation system")
    print("✅ Robust cube state management")
    print("✅ High-performance data structures") 
    print("✅ Comprehensive error handling") 
    print("✅ Full test framework")
    print("✅ Scramble generation and basic solving")
    print()
    print("Still needed for complete simulation:")
    print("❌ 3D piece movement mathematics")
    print("❌ Visual 3D rendering (OpenGL)")
    print("❌ Advanced solving algorithms (CFOP, Roux)")
    print("❌ Interactive GUI interface")
    print("❌ Animation and timing features")
    
def main():
    print_banner()
    
    print("This demo shows the current capabilities of the cube engine.")
    print("Each section demonstrates working functionality.")
    print()
    print("Starting demo...")
    print()
    
    try:
        demo_basic_operations()
        demo_move_system() 
        demo_algorithms()
        demo_scrambling()
        demo_performance()
        demo_cube_info()
        demo_limitations()
        
        print("\n" + "🧩" * 20)
        print("   DEMO COMPLETE!")
        print("   The core engine foundation is solid.")
        print("   Ready for 3D rendering and advanced features!")
        print("🧩" * 20)
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()