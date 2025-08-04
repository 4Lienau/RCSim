"""Software-based cube renderer for environments without OpenGL."""

import pygame
import math
import numpy as np
from typing import Dict, List, Tuple, Optional

from ..cube import Cube
from ..cube.state import Position, Color


class SoftwareRenderer:
    """Software-based 3D cube renderer using pygame."""
    
    def __init__(self, width: int = 800, height: int = 600):
        """Initialize the software renderer.
        
        Parameters
        ----------
        width : int
            Screen width
        height : int
            Screen height
        """
        self.width = width
        self.height = height
        self.screen = None
        self.cube = None
        
        # Camera parameters
        self.camera_distance = 8.0
        self.camera_rotation_x = 30.0
        self.camera_rotation_y = 45.0
        
        # Projection parameters
        self.fov = 60.0
        self.near = 0.1
        self.far = 100.0
    
    def initialize(self) -> bool:
        """Initialize pygame and create screen.
        
        Returns
        -------
        bool
            True if successful
        """
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Advanced Rubik's Cube Simulator")
            return True
        except Exception as e:
            print(f"Failed to initialize software renderer: {e}")
            return False
    
    def set_cube(self, cube: Cube) -> None:
        """Set the cube to render.
        
        Parameters
        ----------
        cube : Cube
            Cube instance to render
        """
        self.cube = cube
    
    def project_point(self, point: np.ndarray) -> Tuple[int, int]:
        """Project 3D point to 2D screen coordinates.
        
        Parameters
        ----------
        point : np.ndarray
            3D point [x, y, z]
            
        Returns
        -------
        Tuple[int, int]
            Screen coordinates (x, y)
        """
        # Apply camera rotation
        x, y, z = point
        
        # Rotate around Y axis
        angle_y = math.radians(self.camera_rotation_y)
        cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
        x_rot = x * cos_y - z * sin_y
        z_rot = x * sin_y + z * cos_y
        
        # Rotate around X axis
        angle_x = math.radians(self.camera_rotation_x)
        cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
        y_rot = y * cos_x - z_rot * sin_x
        z_final = y * sin_x + z_rot * cos_x
        
        # Move away from camera
        z_final += self.camera_distance
        
        # Perspective projection
        if z_final <= 0:
            return (self.width // 2, self.height // 2)
        
        fov_rad = math.radians(self.fov)
        scale = 1.0 / math.tan(fov_rad / 2.0)
        
        screen_x = int(self.width // 2 + x_rot * scale * self.height / (2.0 * z_final))
        screen_y = int(self.height // 2 - y_rot * scale * self.height / (2.0 * z_final))
        
        return (screen_x, screen_y)
    
    def render_cube_face(self, corners: List[np.ndarray], color: Color) -> None:
        """Render a cube face as a polygon.
        
        Parameters
        ----------
        corners : List[np.ndarray]
            4 corner points of the face
        color : Color
            Face color
        """
        # Project corners to screen space
        screen_points = [self.project_point(corner) for corner in corners]
        
        # Check if face is visible (simple back-face culling)
        if len(screen_points) >= 3:
            # Calculate normal using cross product
            v1 = np.array(screen_points[1]) - np.array(screen_points[0])
            v2 = np.array(screen_points[2]) - np.array(screen_points[0])
            normal_z = v1[0] * v2[1] - v1[1] * v2[0]
            
            if normal_z > 0:  # Face is visible
                pygame_color = (color.r, color.g, color.b)
                pygame.draw.polygon(self.screen, pygame_color, screen_points)
                pygame.draw.polygon(self.screen, (0, 0, 0), screen_points, 2)  # Border
    
    def render(self) -> None:
        """Render the current cube."""
        if not self.cube or not self.screen:
            return
        
        # Clear screen
        self.screen.fill((50, 50, 70))  # Dark blue background
        
        # Get cube size and calculate piece positions
        cube_size = self.cube.size
        piece_size = 0.9
        gap = 0.1
        half_cube = (cube_size - 1) / 2.0
        
        # Render each piece
        for cubie in self.cube.state.cubies:
            pos = cubie.current_position
            
            # Calculate world position
            world_x = pos.x * (piece_size + gap)
            world_y = pos.y * (piece_size + gap)
            world_z = pos.z * (piece_size + gap)
            
            # Get visible colors
            visible_colors = cubie.get_visible_colors()
            
            # Render each visible face
            for face_name, face_color in visible_colors.items():
                self.render_piece_face(world_x, world_y, world_z, 
                                     face_name, face_color, piece_size)
    
    def render_piece_face(self, x: float, y: float, z: float, 
                         face: str, color: Color, size: float) -> None:
        """Render a single face of a piece.
        
        Parameters
        ----------
        x, y, z : float
            World position of piece center
        face : str
            Face name ('U', 'D', 'L', 'R', 'F', 'B')
        color : Color
            Face color
        size : float
            Size of the face
        """
        half_size = size / 2.0
        
        # Define face corners based on face name
        if face == 'F':  # Front
            corners = [
                np.array([x - half_size, y - half_size, z + half_size]),
                np.array([x + half_size, y - half_size, z + half_size]),
                np.array([x + half_size, y + half_size, z + half_size]),
                np.array([x - half_size, y + half_size, z + half_size])
            ]
        elif face == 'B':  # Back
            corners = [
                np.array([x + half_size, y - half_size, z - half_size]),
                np.array([x - half_size, y - half_size, z - half_size]),
                np.array([x - half_size, y + half_size, z - half_size]),
                np.array([x + half_size, y + half_size, z - half_size])
            ]
        elif face == 'U':  # Up
            corners = [
                np.array([x - half_size, y + half_size, z - half_size]),
                np.array([x - half_size, y + half_size, z + half_size]),
                np.array([x + half_size, y + half_size, z + half_size]),
                np.array([x + half_size, y + half_size, z - half_size])
            ]
        elif face == 'D':  # Down
            corners = [
                np.array([x - half_size, y - half_size, z + half_size]),
                np.array([x - half_size, y - half_size, z - half_size]),
                np.array([x + half_size, y - half_size, z - half_size]),
                np.array([x + half_size, y - half_size, z + half_size])
            ]
        elif face == 'R':  # Right
            corners = [
                np.array([x + half_size, y - half_size, z + half_size]),
                np.array([x + half_size, y - half_size, z - half_size]),
                np.array([x + half_size, y + half_size, z - half_size]),
                np.array([x + half_size, y + half_size, z + half_size])
            ]
        elif face == 'L':  # Left
            corners = [
                np.array([x - half_size, y - half_size, z - half_size]),
                np.array([x - half_size, y - half_size, z + half_size]),
                np.array([x - half_size, y + half_size, z + half_size]),
                np.array([x - half_size, y + half_size, z - half_size])
            ]
        else:
            return
        
        self.render_cube_face(corners, color)
    
    def handle_input(self, event) -> bool:
        """Handle input events.
        
        Parameters
        ----------
        event : pygame.Event
            Input event
            
        Returns
        -------
        bool
            True to continue, False to quit
        """
        if event.type == pygame.QUIT:
            return False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            
            # Camera controls
            elif event.key == pygame.K_LEFT:
                self.camera_rotation_y -= 15
            elif event.key == pygame.K_RIGHT:
                self.camera_rotation_y += 15
            elif event.key == pygame.K_UP:
                self.camera_rotation_x -= 15
            elif event.key == pygame.K_DOWN:
                self.camera_rotation_x += 15
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                self.camera_distance = max(3.0, self.camera_distance - 1.0)
            elif event.key == pygame.K_MINUS:
                self.camera_distance = min(15.0, self.camera_distance + 1.0)
            
            # Cube controls
            elif self.cube:
                move_map = {
                    pygame.K_u: "U",
                    pygame.K_d: "D",
                    pygame.K_l: "L",
                    pygame.K_r: "R",
                    pygame.K_f: "F",
                    pygame.K_b: "B"
                }
                
                if event.key in move_map:
                    move = move_map[event.key]
                    
                    # Check for modifiers
                    mods = pygame.key.get_pressed()
                    if mods[pygame.K_LSHIFT] or mods[pygame.K_RSHIFT]:
                        move += "'"
                    elif mods[pygame.K_LCTRL] or mods[pygame.K_RCTRL]:
                        move += "2"
                    
                    try:
                        self.cube.apply_move(move)
                        print(f"Applied move: {move}")
                    except Exception as e:
                        print(f"Error applying move: {e}")
                
                elif event.key == pygame.K_SPACE:
                    self.cube.scramble()
                    print("Scrambled cube")
                
                elif event.key == pygame.K_BACKSPACE:
                    self.cube.reset()
                    print("Reset cube")
        
        return True
    
    def run(self) -> None:
        """Run the software renderer main loop."""
        if not self.initialize():
            return
        
        clock = pygame.time.Clock()
        running = True
        
        print("\n" + "="*50)
        print("🎲 CUBE SIMULATOR - SOFTWARE RENDERER")
        print("="*50)
        print("Controls:")
        print("  Arrow Keys  - Rotate camera")
        print("  +/-         - Zoom in/out")
        print("  U/D/L/R/F/B - Cube moves")
        print("  Shift+Move  - Prime moves")
        print("  Ctrl+Move   - Double moves")
        print("  Space       - Scramble")
        print("  Backspace   - Reset")
        print("  ESC         - Quit")
        print("="*50)
        
        while running:
            for event in pygame.event.get():
                if not self.handle_input(event):
                    running = False
            
            self.render()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if pygame.get_init():
            pygame.quit()