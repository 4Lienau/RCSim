"""Window management using Pygame and OpenGL."""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from typing import Tuple, Optional, Callable
from dataclasses import dataclass

from ..cube import Cube


@dataclass
class WindowConfig:
    """Configuration for the graphics window."""
    width: int = 800
    height: int = 600
    title: str = "Advanced Rubik's Cube Simulator"
    resizable: bool = True
    vsync: bool = True
    msaa_samples: int = 4
    background_color: Tuple[float, float, float, float] = (0.1, 0.1, 0.15, 1.0)


class Window:
    """Main application window with OpenGL context."""
    
    def __init__(self, config: Optional[WindowConfig] = None):
        """Initialize the window.
        
        Parameters
        ----------
        config : WindowConfig, optional
            Window configuration, uses defaults if None
        """
        self.config = config or WindowConfig()
        self.running = False
        self.clock = None
        
        # Event callbacks
        self.on_key_press: Optional[Callable[[int, int], None]] = None
        self.on_mouse_click: Optional[Callable[[int, int, int], None]] = None
        self.on_mouse_drag: Optional[Callable[[int, int, int, int], None]] = None
        self.on_mouse_wheel: Optional[Callable[[int], None]] = None
        self.on_resize: Optional[Callable[[int, int], None]] = None
        
        self._mouse_pressed = False
        self._last_mouse_pos = (0, 0)
        
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize Pygame and OpenGL."""
        pygame.init()
        
        # Set OpenGL attributes - use compatibility profile for legacy OpenGL
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 2)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 1)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        
        if self.config.msaa_samples > 0:
            pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
            pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, self.config.msaa_samples)
        
        # Create display
        flags = OPENGL | DOUBLEBUF
        if self.config.resizable:
            flags |= RESIZABLE
        
        self.screen = pygame.display.set_mode(
            (self.config.width, self.config.height), 
            flags
        )
        pygame.display.set_caption(self.config.title)
        
        # Enable VSync if requested
        if self.config.vsync:
            pygame.display.gl_set_attribute(pygame.GL_SWAP_CONTROL, 1)
        
        # Initialize OpenGL
        self._setup_opengl()
        
        # Create clock for frame rate control
        self.clock = pygame.time.Clock()
    
    def _setup_opengl(self) -> None:
        """Configure OpenGL state."""
        # Enable depth testing
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        
        # Enable face culling
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)
        
        # Enable blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Enable multisampling if available
        if self.config.msaa_samples > 0:
            glEnable(GL_MULTISAMPLE)
        
        # Set clear color
        glClearColor(*self.config.background_color)
        
        # Set initial viewport
        self.set_viewport(self.config.width, self.config.height)
    
    def set_viewport(self, width: int, height: int) -> None:
        """Set OpenGL viewport.
        
        Parameters
        ----------
        width : int
            Viewport width
        height : int 
            Viewport height
        """
        glViewport(0, 0, width, height)
        self.config.width = width
        self.config.height = height
    
    def get_aspect_ratio(self) -> float:
        """Get current aspect ratio."""
        return self.config.width / max(self.config.height, 1)
    
    def clear(self) -> None:
        """Clear the screen."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    def swap_buffers(self) -> None:
        """Swap front and back buffers."""
        pygame.display.flip()
    
    def handle_events(self) -> bool:
        """Handle pygame events.
        
        Returns
        -------
        bool
            True if should continue running, False to quit
        """
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            
            elif event.type == KEYDOWN:
                if self.on_key_press:
                    self.on_key_press(event.key, event.mod)
                
                # Handle escape key
                if event.key == K_ESCAPE:
                    return False
            
            elif event.type == MOUSEBUTTONDOWN:
                self._mouse_pressed = True
                self._last_mouse_pos = event.pos
                
                if self.on_mouse_click:
                    self.on_mouse_click(event.button, event.pos[0], event.pos[1])
            
            elif event.type == MOUSEBUTTONUP:
                self._mouse_pressed = False
            
            elif event.type == MOUSEMOTION:
                if self._mouse_pressed and self.on_mouse_drag:
                    dx = event.pos[0] - self._last_mouse_pos[0]
                    dy = event.pos[1] - self._last_mouse_pos[1]
                    self.on_mouse_drag(dx, dy, event.pos[0], event.pos[1])
                
                self._last_mouse_pos = event.pos
            
            elif event.type == MOUSEWHEEL:
                if self.on_mouse_wheel:
                    self.on_mouse_wheel(event.y)
            
            elif event.type == VIDEORESIZE:
                self.set_viewport(event.w, event.h)
                if self.on_resize:
                    self.on_resize(event.w, event.h)
        
        return True
    
    def run(self, render_callback: Callable[[], None], target_fps: int = 60) -> None:
        """Run the main event loop.
        
        Parameters
        ----------
        render_callback : Callable[[], None]
            Function to call for rendering each frame
        target_fps : int, optional
            Target frames per second, defaults to 60
        """
        self.running = True
        
        while self.running:
            # Handle events
            if not self.handle_events():
                break
            
            # Clear screen
            self.clear()
            
            # Render
            render_callback()
            
            # Swap buffers
            self.swap_buffers()
            
            # Control frame rate
            self.clock.tick(target_fps)
    
    def stop(self) -> None:
        """Stop the event loop."""
        self.running = False
    
    def get_fps(self) -> float:
        """Get current FPS."""
        return self.clock.get_fps() if self.clock else 0.0
    
    def cleanup(self) -> None:
        """Clean up resources."""
        pygame.quit()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()