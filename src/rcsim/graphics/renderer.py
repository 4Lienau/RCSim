"""3D cube renderer using OpenGL."""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math

from OpenGL.GL import *
from OpenGL.arrays import vbo

from ..cube import Cube
from ..cube.state import Position, Color


@dataclass
class RenderConfig:
    """Configuration for the cube renderer."""
    piece_size: float = 0.95  # Size of each piece (< 1.0 for gaps)
    gap_size: float = 0.05    # Gap between pieces
    corner_radius: float = 0.1  # Radius for rounded corners
    sticker_inset: float = 0.02  # Inset for stickers
    enable_shadows: bool = True
    enable_reflections: bool = False
    wireframe_mode: bool = False
    show_internal_pieces: bool = False


class CubeRenderer:
    """OpenGL-based 3D renderer for Rubik's Cubes."""
    
    def __init__(self, config: Optional[RenderConfig] = None):
        """Initialize the renderer.
        
        Parameters
        ----------
        config : RenderConfig, optional
            Renderer configuration
        """
        self.config = config or RenderConfig()
        self.cube: Optional[Cube] = None
        
        # OpenGL resources
        self._cube_vao = None
        self._cube_vbo = None
        self._initialized = False
        
        # Geometry cache
        self._cube_vertices = None
        self._cube_indices = None
        self._sticker_vertices = {}
        
        # Animation state
        self.animation_progress = 0.0
        self.animating_move = None
        self.animation_axis = None
        self.animation_angle = 0.0
    
    def initialize(self) -> None:
        """Initialize OpenGL resources."""
        if self._initialized:
            return
        
        # Generate cube geometry
        self._generate_cube_geometry()
        
        # Set up basic lighting
        self._setup_lighting()
        
        self._initialized = True
    
    def _generate_cube_geometry(self) -> None:
        """Generate vertices and indices for cube pieces."""
        vertices = []
        indices = []
        
        # Generate geometry for a single cube piece
        size = self.config.piece_size / 2.0
        
        # Cube vertices (8 corners)
        cube_verts = [
            [-size, -size, -size],  # 0: back-bottom-left
            [ size, -size, -size],  # 1: back-bottom-right
            [ size,  size, -size],  # 2: back-top-right
            [-size,  size, -size],  # 3: back-top-left
            [-size, -size,  size],  # 4: front-bottom-left
            [ size, -size,  size],  # 5: front-bottom-right
            [ size,  size,  size],  # 6: front-top-right
            [-size,  size,  size],  # 7: front-top-left
        ]
        
        # Face indices (6 faces, 2 triangles each)
        face_indices = [
            # Back face
            [0, 1, 2], [0, 2, 3],
            # Front face  
            [4, 7, 6], [4, 6, 5],
            # Left face
            [0, 3, 7], [0, 7, 4],
            # Right face
            [1, 5, 6], [1, 6, 2],
            # Bottom face
            [0, 4, 5], [0, 5, 1],
            # Top face
            [3, 2, 6], [3, 6, 7],
        ]
        
        # Face normals
        face_normals = [
            [0, 0, -1],  # Back
            [0, 0,  1],  # Front
            [-1, 0, 0],  # Left
            [ 1, 0, 0],  # Right
            [0, -1, 0],  # Bottom
            [0,  1, 0],  # Top
        ]
        
        # Build vertex data (position + normal + color)
        for i, face_group in enumerate([face_indices[j:j+2] for j in range(0, len(face_indices), 2)]):
            normal = face_normals[i]
            for face in face_group:
                for vertex_idx in face:
                    vertex = cube_verts[vertex_idx]
                    vertices.extend(vertex)  # Position
                    vertices.extend(normal)  # Normal
                    vertices.extend([1.0, 1.0, 1.0])  # Color (white default)
        
        self._cube_vertices = np.array(vertices, dtype=np.float32)
        
        # Indices are just sequential since we're using separate vertices per face
        self._cube_indices = np.arange(len(vertices) // 9, dtype=np.uint32)
    
    def _setup_lighting(self) -> None:
        """Set up basic OpenGL lighting."""
        # Enable lighting
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        # Light properties
        light_position = [2.0, 2.0, 2.0, 1.0]  # Positional light
        light_ambient = [0.2, 0.2, 0.2, 1.0]
        light_diffuse = [0.8, 0.8, 0.8, 1.0]
        light_specular = [1.0, 1.0, 1.0, 1.0]
        
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
        
        # Material properties
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 50.0)
        
        # Enable color material
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    
    def set_cube(self, cube: Cube) -> None:
        """Set the cube to render.
        
        Parameters
        ----------
        cube : Cube
            Cube instance to render
        """
        self.cube = cube
    
    def render(self) -> None:
        """Render the current cube."""
        if not self.cube or not self._initialized:
            return
        
        glPushMatrix()
        
        # Render each piece
        self._render_pieces()
        
        glPopMatrix()
    
    def _render_pieces(self) -> None:
        """Render all cube pieces."""
        if not self.cube:
            return
        
        cube_size = self.cube.size
        half_size = (cube_size - 1) / 2.0
        piece_spacing = 1.0
        
        for cubie in self.cube.state.cubies:
            pos = cubie.current_position
            
            # Skip internal pieces if not enabled
            if not self.config.show_internal_pieces and not self._is_visible_piece(pos, cube_size):
                continue
            
            # Calculate world position
            world_pos = [
                pos.x * piece_spacing,
                pos.y * piece_spacing, 
                pos.z * piece_spacing
            ]
            
            self._render_piece(cubie, world_pos)
    
    def _is_visible_piece(self, position: Position, cube_size: int) -> bool:
        """Check if a piece is visible (on the surface)."""
        half_size = (cube_size - 1) / 2.0
        return (abs(position.x) == half_size or 
                abs(position.y) == half_size or 
                abs(position.z) == half_size)
    
    def _render_piece(self, cubie, world_pos: List[float]) -> None:
        """Render a single cube piece.
        
        Parameters
        ----------
        cubie : Cubie
            The piece to render
        world_pos : List[float]
            World position [x, y, z]
        """
        glPushMatrix()
        
        # Translate to piece position
        glTranslatef(world_pos[0], world_pos[1], world_pos[2])
        
        # Apply piece rotation if animating
        if self.animating_move and self._piece_affected_by_animation(cubie):
            self._apply_animation_transform()
        
        # Render the base cube (black/gray)
        self._render_base_cube()
        
        # Render colored stickers on visible faces
        visible_colors = cubie.get_visible_colors()
        for face, color in visible_colors.items():
            self._render_sticker(face, color)
        
        glPopMatrix()
    
    def _piece_affected_by_animation(self, cubie) -> bool:
        """Check if piece is affected by current animation."""
        if not self.animating_move:
            return False
        
        return self.animating_move.affects_position(cubie.current_position, self.cube.size)
    
    def _apply_animation_transform(self) -> None:
        """Apply animation transform to current piece."""
        if not self.animation_axis:
            return
        
        angle = self.animation_angle * self.animation_progress
        
        if self.animation_axis == 'x':
            glRotatef(angle, 1, 0, 0)
        elif self.animation_axis == 'y':
            glRotatef(angle, 0, 1, 0)  
        elif self.animation_axis == 'z':
            glRotatef(angle, 0, 0, 1)
    
    def _render_base_cube(self) -> None:
        """Render the base black cube."""
        # Set black color
        glColor3f(0.1, 0.1, 0.1)
        
        # Render cube using immediate mode (for simplicity)
        size = self.config.piece_size / 2.0
        
        glBegin(GL_QUADS)
        
        # Back face
        glNormal3f(0, 0, -1)
        glVertex3f(-size, -size, -size)
        glVertex3f( size, -size, -size) 
        glVertex3f( size,  size, -size)
        glVertex3f(-size,  size, -size)
        
        # Front face
        glNormal3f(0, 0, 1)
        glVertex3f(-size, -size, size)
        glVertex3f(-size,  size, size)
        glVertex3f( size,  size, size)
        glVertex3f( size, -size, size)
        
        # Left face
        glNormal3f(-1, 0, 0)
        glVertex3f(-size, -size, -size)
        glVertex3f(-size,  size, -size)
        glVertex3f(-size,  size,  size)
        glVertex3f(-size, -size,  size)
        
        # Right face
        glNormal3f(1, 0, 0)
        glVertex3f(size, -size, -size)
        glVertex3f(size, -size,  size)
        glVertex3f(size,  size,  size)
        glVertex3f(size,  size, -size)
        
        # Bottom face
        glNormal3f(0, -1, 0)
        glVertex3f(-size, -size, -size)
        glVertex3f(-size, -size,  size)
        glVertex3f( size, -size,  size)
        glVertex3f( size, -size, -size)
        
        # Top face
        glNormal3f(0, 1, 0)
        glVertex3f(-size, size, -size)
        glVertex3f( size, size, -size)
        glVertex3f( size, size,  size)
        glVertex3f(-size, size,  size)
        
        glEnd()
    
    def _render_sticker(self, face: str, color: Color) -> None:
        """Render a colored sticker on a face.
        
        Parameters
        ----------
        face : str
            Face name ('U', 'D', 'L', 'R', 'F', 'B')
        color : Color
            Sticker color
        """
        # Set sticker color
        r, g, b = color.to_normalized_rgb()
        glColor3f(r, g, b)
        
        # Calculate sticker size (inset from piece edges)
        size = self.config.piece_size / 2.0 - self.config.sticker_inset
        offset = self.config.piece_size / 2.0 + 0.001  # Slight offset to avoid z-fighting
        
        glBegin(GL_QUADS)
        
        if face == 'U':  # Top face
            glNormal3f(0, 1, 0)
            glVertex3f(-size,  offset, -size)
            glVertex3f( size,  offset, -size)
            glVertex3f( size,  offset,  size)
            glVertex3f(-size,  offset,  size)
        
        elif face == 'D':  # Bottom face
            glNormal3f(0, -1, 0)
            glVertex3f(-size, -offset, -size)
            glVertex3f(-size, -offset,  size)
            glVertex3f( size, -offset,  size)
            glVertex3f( size, -offset, -size)
        
        elif face == 'L':  # Left face
            glNormal3f(-1, 0, 0)
            glVertex3f(-offset, -size, -size)
            glVertex3f(-offset,  size, -size)
            glVertex3f(-offset,  size,  size)
            glVertex3f(-offset, -size,  size)
        
        elif face == 'R':  # Right face
            glNormal3f(1, 0, 0)
            glVertex3f(offset, -size, -size)
            glVertex3f(offset, -size,  size)
            glVertex3f(offset,  size,  size)
            glVertex3f(offset,  size, -size)
        
        elif face == 'F':  # Front face
            glNormal3f(0, 0, 1)
            glVertex3f(-size, -size, offset)
            glVertex3f(-size,  size, offset)
            glVertex3f( size,  size, offset)
            glVertex3f( size, -size, offset)
        
        elif face == 'B':  # Back face
            glNormal3f(0, 0, -1)
            glVertex3f(-size, -size, -offset)
            glVertex3f( size, -size, -offset)
            glVertex3f( size,  size, -offset)
            glVertex3f(-size,  size, -offset)
        
        glEnd()
    
    def start_move_animation(self, move, duration: float = 0.3) -> None:
        """Start animating a move.
        
        Parameters
        ----------
        move : Move
            Move to animate
        duration : float
            Animation duration in seconds
        """
        self.animating_move = move
        self.animation_progress = 0.0
        self.animation_axis = move.get_rotation_axis().value.lower()
        self.animation_angle = move.get_rotation_angle()
        self.animation_duration = duration
    
    def update_animation(self, delta_time: float) -> bool:
        """Update move animation.
        
        Parameters
        ----------
        delta_time : float
            Time elapsed since last update
            
        Returns
        -------
        bool
            True if animation is still playing, False if finished
        """
        if not self.animating_move:
            return False
        
        self.animation_progress += delta_time / self.animation_duration
        
        if self.animation_progress >= 1.0:
            self.animation_progress = 1.0
            self.animating_move = None
            return False
        
        return True
    
    def set_wireframe_mode(self, enabled: bool) -> None:
        """Enable/disable wireframe rendering.
        
        Parameters
        ----------
        enabled : bool
            Whether to enable wireframe mode
        """
        self.config.wireframe_mode = enabled
        if enabled:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    def cleanup(self) -> None:
        """Clean up OpenGL resources."""
        if self._cube_vbo:
            self._cube_vbo.delete()
        if self._cube_vao:
            glDeleteVertexArrays(1, [self._cube_vao])