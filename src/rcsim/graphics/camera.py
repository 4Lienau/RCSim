"""3D camera system for cube visualization."""

import numpy as np
from typing import Tuple
from dataclasses import dataclass
import math

from OpenGL.GL import *
from OpenGL.GLU import *


@dataclass
class CameraState:
    """Represents camera state for serialization/deserialization."""
    position: Tuple[float, float, float]
    target: Tuple[float, float, float]
    up: Tuple[float, float, float]
    fov: float
    near_plane: float
    far_plane: float


class Camera:
    """3D camera for viewing the Rubik's Cube.
    
    Provides orbit camera controls suitable for examining a cube from all angles.
    """
    
    def __init__(self, 
                 position: Tuple[float, float, float] = (0, 0, 5),
                 target: Tuple[float, float, float] = (0, 0, 0),
                 up: Tuple[float, float, float] = (0, 1, 0),
                 fov: float = 45.0,
                 near_plane: float = 0.1,
                 far_plane: float = 100.0):
        """Initialize camera.
        
        Parameters
        ----------
        position : Tuple[float, float, float]
            Initial camera position
        target : Tuple[float, float, float] 
            Point camera is looking at
        up : Tuple[float, float, float]
            Up vector
        fov : float
            Field of view in degrees
        near_plane : float
            Near clipping plane distance
        far_plane : float
            Far clipping plane distance
        """
        self.position = np.array(position, dtype=np.float32)
        self.target = np.array(target, dtype=np.float32)
        self.up = np.array(up, dtype=np.float32)
        self.fov = fov
        self.near_plane = near_plane
        self.far_plane = far_plane
        
        # Orbit camera parameters
        self.distance = np.linalg.norm(self.position - self.target)
        self.azimuth = 45.0  # Horizontal rotation in degrees
        self.elevation = 30.0  # Vertical rotation in degrees
        
        # Constraints
        self.min_distance = 1.0
        self.max_distance = 20.0
        self.min_elevation = -89.0
        self.max_elevation = 89.0
        
        # Sensitivity settings
        self.rotation_sensitivity = 0.5
        self.zoom_sensitivity = 0.1
        self.pan_sensitivity = 0.01
        
        self._update_position()
    
    def _update_position(self) -> None:
        """Update camera position based on orbit parameters."""
        # Convert to radians
        azimuth_rad = math.radians(self.azimuth)
        elevation_rad = math.radians(self.elevation)
        
        # Calculate position on sphere around target
        x = self.distance * math.cos(elevation_rad) * math.cos(azimuth_rad)
        y = self.distance * math.sin(elevation_rad)
        z = self.distance * math.cos(elevation_rad) * math.sin(azimuth_rad)
        
        self.position = self.target + np.array([x, y, z], dtype=np.float32)
    
    def orbit(self, delta_azimuth: float, delta_elevation: float) -> None:
        """Orbit camera around target.
        
        Parameters
        ----------
        delta_azimuth : float
            Change in azimuth angle (degrees)
        delta_elevation : float
            Change in elevation angle (degrees)
        """
        self.azimuth += delta_azimuth * self.rotation_sensitivity
        self.elevation += delta_elevation * self.rotation_sensitivity
        
        # Apply constraints
        self.elevation = max(self.min_elevation, min(self.max_elevation, self.elevation))
        
        # Normalize azimuth to [0, 360)
        self.azimuth = self.azimuth % 360.0
        
        self._update_position()
    
    def zoom(self, delta: float) -> None:
        """Zoom camera in/out.
        
        Parameters
        ----------
        delta : float
            Zoom delta (positive = zoom in, negative = zoom out)
        """
        self.distance *= (1.0 - delta * self.zoom_sensitivity)
        self.distance = max(self.min_distance, min(self.max_distance, self.distance))
        self._update_position()
    
    def pan(self, delta_x: float, delta_y: float) -> None:
        """Pan camera target.
        
        Parameters
        ----------
        delta_x : float
            Pan delta in screen X direction
        delta_y : float
            Pan delta in screen Y direction
        """
        # Get camera coordinate system
        forward = self.get_forward_vector()
        right = self.get_right_vector()
        up = self.get_up_vector()
        
        # Calculate pan offset in world space
        pan_scale = self.distance * self.pan_sensitivity
        offset = (-delta_x * right + delta_y * up) * pan_scale
        
        # Move both position and target
        self.target += offset
        self.position += offset
    
    def get_forward_vector(self) -> np.ndarray:
        """Get normalized forward vector (from camera to target)."""
        forward = self.target - self.position
        return forward / np.linalg.norm(forward)
    
    def get_right_vector(self) -> np.ndarray:
        """Get normalized right vector."""
        forward = self.get_forward_vector()
        right = np.cross(forward, self.up)
        return right / np.linalg.norm(right)
    
    def get_up_vector(self) -> np.ndarray:
        """Get normalized up vector."""
        forward = self.get_forward_vector()
        right = self.get_right_vector()
        return np.cross(right, forward)
    
    def get_view_matrix(self) -> np.ndarray:
        """Get 4x4 view matrix.
        
        Returns
        -------
        np.ndarray
            4x4 view matrix
        """
        # Calculate camera coordinate system
        forward = self.get_forward_vector()
        right = self.get_right_vector()
        up = self.get_up_vector()
        
        # Create view matrix (camera to world transform inverse)
        view_matrix = np.eye(4, dtype=np.float32)
        
        # Rotation part
        view_matrix[0, :3] = right
        view_matrix[1, :3] = up
        view_matrix[2, :3] = -forward
        
        # Translation part
        view_matrix[0, 3] = -np.dot(right, self.position)
        view_matrix[1, 3] = -np.dot(up, self.position)
        view_matrix[2, 3] = np.dot(forward, self.position)
        
        return view_matrix
    
    def get_projection_matrix(self, aspect_ratio: float) -> np.ndarray:
        """Get 4x4 perspective projection matrix.
        
        Parameters
        ----------
        aspect_ratio : float
            Viewport aspect ratio (width/height)
            
        Returns
        -------
        np.ndarray
            4x4 projection matrix
        """
        fov_rad = math.radians(self.fov)
        f = 1.0 / math.tan(fov_rad / 2.0)
        
        proj_matrix = np.zeros((4, 4), dtype=np.float32)
        proj_matrix[0, 0] = f / aspect_ratio
        proj_matrix[1, 1] = f
        proj_matrix[2, 2] = (self.far_plane + self.near_plane) / (self.near_plane - self.far_plane)
        proj_matrix[2, 3] = (2.0 * self.far_plane * self.near_plane) / (self.near_plane - self.far_plane)
        proj_matrix[3, 2] = -1.0
        
        return proj_matrix
    
    def apply_view_transform(self) -> None:
        """Apply camera view transform using legacy OpenGL calls."""
        try:
            gluLookAt(
                self.position[0], self.position[1], self.position[2],
                self.target[0], self.target[1], self.target[2],
                self.up[0], self.up[1], self.up[2]
            )
        except:
            # Fallback to manual matrix if GLU not available
            view_matrix = self.get_view_matrix()
            glMultMatrixf(view_matrix.flatten())
    
    def apply_projection_transform(self, aspect_ratio: float) -> None:
        """Apply perspective projection using legacy OpenGL calls.
        
        Parameters
        ----------
        aspect_ratio : float
            Viewport aspect ratio
        """
        try:
            gluPerspective(self.fov, aspect_ratio, self.near_plane, self.far_plane)
        except:
            # Fallback to manual perspective matrix
            proj_matrix = self.get_projection_matrix(aspect_ratio)
            glMultMatrixf(proj_matrix.flatten())
    
    def reset_to_default(self) -> None:
        """Reset camera to default position and orientation."""
        self.distance = 5.0
        self.azimuth = 45.0
        self.elevation = 30.0
        self.target = np.array([0, 0, 0], dtype=np.float32)
        self._update_position()
    
    def frame_cube(self, cube_size: float = 3.0) -> None:
        """Frame the camera to nicely view a cube of given size.
        
        Parameters
        ----------
        cube_size : float
            Size of the cube to frame
        """
        # Calculate distance needed to frame the cube
        diagonal = cube_size * math.sqrt(3)  # Cube diagonal
        fov_rad = math.radians(self.fov)
        self.distance = diagonal / math.tan(fov_rad / 2.0) * 0.8  # Add some padding
        
        self.distance = max(self.min_distance, min(self.max_distance, self.distance))
        self._update_position()
    
    def get_state(self) -> CameraState:
        """Get current camera state for serialization.
        
        Returns
        -------
        CameraState
            Current camera state
        """
        return CameraState(
            position=tuple(self.position),
            target=tuple(self.target),
            up=tuple(self.up),
            fov=self.fov,
            near_plane=self.near_plane,
            far_plane=self.far_plane
        )
    
    def set_state(self, state: CameraState) -> None:
        """Set camera state from serialized data.
        
        Parameters
        ----------
        state : CameraState
            Camera state to restore
        """
        self.position = np.array(state.position, dtype=np.float32)
        self.target = np.array(state.target, dtype=np.float32)
        self.up = np.array(state.up, dtype=np.float32)
        self.fov = state.fov
        self.near_plane = state.near_plane
        self.far_plane = state.far_plane
        
        # Recalculate orbit parameters
        self.distance = np.linalg.norm(self.position - self.target)
        
        # Calculate azimuth and elevation from position
        offset = self.position - self.target
        self.distance = np.linalg.norm(offset)
        
        if self.distance > 0:
            normalized = offset / self.distance
            self.elevation = math.degrees(math.asin(normalized[1]))
            self.azimuth = math.degrees(math.atan2(normalized[2], normalized[0]))
    
    def __str__(self) -> str:
        return f"Camera(pos={self.position}, target={self.target}, dist={self.distance:.2f})"