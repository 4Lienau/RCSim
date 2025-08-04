"""3D scene management for the cube simulator."""

from typing import Optional, Callable, Any
import time

from OpenGL.GL import *

from .window import Window, WindowConfig
from .camera import Camera
from .renderer import CubeRenderer, RenderConfig
from ..cube import Cube


class Scene:
    """Main 3D scene that manages the window, camera, and renderer."""
    
    def __init__(self, 
                 window_config: Optional[WindowConfig] = None,
                 render_config: Optional[RenderConfig] = None):
        """Initialize the scene.
        
        Parameters
        ----------
        window_config : WindowConfig, optional
            Window configuration
        render_config : RenderConfig, optional
            Renderer configuration
        """
        self.window = Window(window_config)
        self.camera = Camera()
        self.renderer = CubeRenderer(render_config)
        self.cube: Optional[Cube] = None
        
        # Timing
        self.last_frame_time = time.time()
        self.delta_time = 0.0
        
        # Input state
        self.mouse_sensitivity = 1.0
        self.zoom_sensitivity = 0.1
        
        # Setup callbacks
        self._setup_callbacks()
    
    def _setup_callbacks(self) -> None:
        """Set up window event callbacks."""
        self.window.on_mouse_drag = self._on_mouse_drag
        self.window.on_mouse_wheel = self._on_mouse_wheel
        self.window.on_key_press = self._on_key_press
        self.window.on_resize = self._on_resize
    
    def _on_mouse_drag(self, dx: int, dy: int, x: int, y: int) -> None:
        """Handle mouse drag for camera control."""
        # Convert screen coordinates to rotation
        rotation_x = dy * self.mouse_sensitivity * 0.5
        rotation_y = dx * self.mouse_sensitivity * 0.5
        
        self.camera.orbit(rotation_y, rotation_x)
    
    def _on_mouse_wheel(self, delta: int) -> None:
        """Handle mouse wheel for camera zoom."""
        zoom_delta = delta * self.zoom_sensitivity
        self.camera.zoom(zoom_delta)
    
    def _on_key_press(self, key: int, mod: int) -> None:
        """Handle keyboard input.
        
        Parameters
        ----------
        key : int
            Key code
        mod : int
            Modifier keys
        """
        import pygame.locals as pg
        
        # Camera controls
        if key == pg.K_r:
            self.camera.reset_to_default()
        elif key == pg.K_f and self.cube:
            self.camera.frame_cube(self.cube.size)
        
        # Rendering controls
        elif key == pg.K_w:
            wireframe = not self.renderer.config.wireframe_mode
            self.renderer.set_wireframe_mode(wireframe)
        
        # Cube controls
        elif self.cube:
            self._handle_cube_input(key, mod)
    
    def _handle_cube_input(self, key: int, mod: int) -> None:
        """Handle cube-specific input.
        
        Parameters
        ----------
        key : int
            Key code
        mod : int
            Modifier keys
        """
        import pygame.locals as pg
        
        # Basic moves
        move_map = {
            pg.K_u: "U",
            pg.K_d: "D", 
            pg.K_l: "L",
            pg.K_n: "R",  # Using 'n' for right since 'r' is used for reset
            pg.K_f: "F",
            pg.K_b: "B",
        }
        
        if key in move_map:
            move = move_map[key]
            
            # Add prime if shift is held
            if mod & pg.KMOD_SHIFT:
                move += "'"
            # Add 2 if ctrl is held  
            elif mod & pg.KMOD_CTRL:
                move += "2"
            
            try:
                self.cube.apply_move(move)
                print(f"Applied move: {move}")
            except Exception as e:
                print(f"Error applying move {move}: {e}")
        
        # Scramble
        elif key == pg.K_SPACE:
            self.cube.scramble()
            print("Scrambled cube")
        
        # Reset
        elif key == pg.K_BACKSPACE:
            self.cube.reset()
            print("Reset cube")
        
        # Undo
        elif key == pg.K_z and (mod & pg.KMOD_CTRL):
            undone = self.cube.undo_last_move()
            if undone:
                print(f"Undone move: {undone}")
            else:
                print("Nothing to undo")
    
    def _on_resize(self, width: int, height: int) -> None:
        """Handle window resize."""
        # Update camera projection
        pass
    
    def set_cube(self, cube: Cube) -> None:
        """Set the cube to display.
        
        Parameters
        ----------
        cube : Cube
            Cube instance to display
        """
        self.cube = cube
        self.renderer.set_cube(cube)
        
        # Frame camera to cube
        self.camera.frame_cube(cube.size)
    
    def render_frame(self) -> None:
        """Render a single frame."""
        # Update timing
        current_time = time.time()
        self.delta_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # Update animations
        self.renderer.update_animation(self.delta_time)
        
        # Set up matrices
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        self.camera.apply_projection_transform(self.window.get_aspect_ratio())
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.camera.apply_view_transform()
        
        # Render the cube
        self.renderer.render()
        
        # Render UI overlay if needed
        self._render_ui()
    
    def _render_ui(self) -> None:
        """Render UI overlay."""
        if not self.cube:
            return
        
        # Switch to 2D rendering for UI
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.window.config.width, self.window.config.height, 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Disable depth testing for UI
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        # Render text info
        self._render_cube_info()
        
        # Restore 3D rendering state
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def _render_cube_info(self) -> None:
        """Render cube information text."""
        # For now, just render basic info without text rendering
        # In a full implementation, you'd use a text rendering library
        
        # Set text color
        glColor3f(1.0, 1.0, 1.0)
        
        # This would render text showing:
        # - Cube size
        # - Move count  
        # - Solved status
        # - Current FPS
        # - Controls help
        
        # For now, we'll skip text rendering as it requires additional setup
        pass
    
    def run(self, target_fps: int = 60) -> None:
        """Run the scene with the main event loop.
        
        Parameters
        ----------
        target_fps : int
            Target frames per second
        """
        # Initialize renderer
        self.renderer.initialize()
        
        # Print controls
        self._print_controls()
        
        # Run main loop
        self.window.run(self.render_frame, target_fps)
    
    def _print_controls(self) -> None:
        """Print control instructions."""
        print("\n" + "="*50)
        print("ADVANCED RUBIK'S CUBE SIMULATOR")
        print("="*50)
        print("Camera Controls:")
        print("  Mouse Drag    - Rotate camera")
        print("  Mouse Wheel   - Zoom in/out")  
        print("  R             - Reset camera")
        print("  F             - Frame cube")
        print("")
        print("Cube Controls:")
        print("  U/D/L/N/F/B   - Basic moves (N=Right)")
        print("  Shift + Move  - Prime moves (counter-clockwise)")
        print("  Ctrl + Move   - Double moves")
        print("  Space         - Scramble")
        print("  Backspace     - Reset cube")
        print("  Ctrl+Z        - Undo move")
        print("")
        print("Rendering:")
        print("  W             - Toggle wireframe")
        print("")
        print("  ESC           - Quit")
        print("="*50)
        
        if self.cube:
            print(f"Cube: {self.cube}")
            print(f"Status: {'Solved' if self.cube.is_solved() else 'Scrambled'}")
        print("")
    
    def stop(self) -> None:
        """Stop the scene."""
        self.window.stop()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.renderer.cleanup()
        self.window.cleanup()