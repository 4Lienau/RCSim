#!/usr/bin/env python3
"""Interactive testing script for the cube engine."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rcsim.cube import Cube
from rcsim.cube.moves import Move, MoveSequence

def print_cube_state(cube):
    """Print basic cube state information."""
    print(f"Cube: {cube}")
    print(f"Solved: {cube.is_solved()}")
    print(f"Moves: {cube.get_move_count()}")
    if cube.get_move_count() > 0:
        history = cube.get_move_history()
        recent = ' '.join(str(m) for m in history[-5:])
        if len(history) > 5:
            recent = "... " + recent
        print(f"Recent moves: {recent}")

def main():
    """Interactive testing interface."""
    print("Advanced Rubik's Cube Simulator - Interactive Test")
    print("=" * 50)
    print("Commands:")
    print("  <move>        - Apply move (e.g., R, U', R2, Rw)")
    print("  <sequence>    - Apply sequence (e.g., R U R' U')")
    print("  scramble [n]  - Generate scramble (default 20 moves)")
    print("  solve         - Solve by reversing scramble")
    print("  undo          - Undo last move")
    print("  reset         - Reset to solved state")
    print("  info          - Show cube information")
    print("  size <n>      - Create new cube of size n")
    print("  quit/exit     - Exit program")
    print()
    
    cube = Cube(3)
    print_cube_state(cube)
    print()
    
    while True:
        try:
            command = input("cube> ").strip()
            
            if not command:
                continue
                
            if command.lower() in ['quit', 'exit', 'q']:
                break
                
            elif command == 'info':
                print_cube_state(cube)
                info = cube.get_cube_info()
                pieces = cube.get_piece_count()
                print(f"Size: {info['size']}x{info['size']}")
                print(f"Pieces: {pieces['corners']} corners, {pieces['edges']} edges, {pieces['centers']} centers")
                validation = cube.validate_state()
                print(f"Valid: {all(validation.values())}")
                
            elif command == 'reset':
                cube.reset()
                print("Cube reset to solved state")
                print_cube_state(cube)
                
            elif command == 'undo':
                move = cube.undo_last_move()
                if move:
                    print(f"Undid: {move}")
                    print_cube_state(cube)
                else:
                    print("No moves to undo")
                    
            elif command.startswith('scramble'):
                parts = command.split()
                num_moves = int(parts[1]) if len(parts) > 1 else 20
                scramble = cube.scramble(num_moves=num_moves)
                print(f"Scramble: {scramble}")
                print_cube_state(cube)
                
            elif command == 'solve':
                if cube.get_scramble():
                    solution = cube.solve_with_reverse()
                    print(f"Solution: {solution}")
                    print_cube_state(cube)
                else:
                    print("No scramble to reverse. Use 'scramble' command first.")
                    
            elif command.startswith('size'):
                try:
                    size = int(command.split()[1])
                    cube = Cube(size)
                    print(f"Created {size}x{size} cube")
                    print_cube_state(cube)
                except (IndexError, ValueError):
                    print("Usage: size <number> (e.g., size 4)")
                    
            else:
                # Try to parse as move or sequence
                try:
                    if ' ' in command:
                        # Multiple moves - treat as sequence
                        sequence = MoveSequence.parse(command)
                        cube.apply_sequence(sequence)
                        print(f"Applied: {sequence}")
                    else:
                        # Single move
                        move = Move.parse(command)
                        cube.apply_move(move)
                        print(f"Applied: {move}")
                    
                    print_cube_state(cube)
                    
                except Exception as e:
                    print(f"Error: {e}")
                    print("Try 'info' for help or a valid move like R, U', R2")
                    
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()