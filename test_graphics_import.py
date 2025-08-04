#!/usr/bin/env python3
"""Test graphics module imports."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all graphics modules can import successfully."""
    try:
        print("Testing graphics module imports...")
        
        # Test basic imports
        print("  Importing graphics components...")
        from rcsim.graphics.window import Window, WindowConfig
        print("    ✅ Window imported")
        
        from rcsim.graphics.camera import Camera, CameraState
        print("    ✅ Camera imported")
        
        from rcsim.graphics.renderer import CubeRenderer, RenderConfig
        print("    ✅ Renderer imported")
        
        from rcsim.graphics.scene import Scene
        print("    ✅ Scene imported")
        
        # Test cube integration
        print("  Testing cube integration...")
        from rcsim.cube import Cube
        cube = Cube(3)
        print("    ✅ Cube created")
        
        # Test creating graphics objects (without initializing OpenGL)
        window_config = WindowConfig(width=800, height=600)
        render_config = RenderConfig()
        print("    ✅ Configurations created")
        
        # Test camera functionality
        camera = Camera()
        camera.orbit(45, 30)
        camera.zoom(0.1)
        print("    ✅ Camera operations work")
        
        # Test camera state serialization
        state = camera.get_state()
        camera.set_state(state)
        print("    ✅ Camera state serialization works")
        
        print("\n🎉 All graphics module imports successful!")
        print("Graphics system is ready for use.")
        return True
        
    except Exception as e:
        print(f"\n❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)