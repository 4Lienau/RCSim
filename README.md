# Advanced Rubik's Cube Simulator

A highly realistic, fully functional Rubik's Cube simulator with complete 3D visualization, authentic solving algorithms, and comprehensive customization options. Built to replicate the look, feel, and behavior of a real Rubik's Cube as closely as possible.

## Features

### 🎯 Core Functionality
- **Multiple cube sizes**: 2x2, 3x3, 4x4, 5x5, 6x6, 7x7, 8x8, 9x9, and 10x10
- **Realistic 3D rendering** with proper lighting, shadows, and reflections
- **Smooth animations** with physics-based rotations
- **Intuitive controls**: Mouse drag, keyboard shortcuts, and touch support
- **Authentic solving algorithms** (not just move reversal)

### 🧩 Solving System
- **Layer-by-Layer method** (beginner-friendly)
- **CFOP method** with complete algorithm sets:
  - 57 OLL (Orient Last Layer) algorithms
  - 21 PLL (Permute Last Layer) algorithms
  - Advanced F2L (First Two Layers) techniques
- **Real-time step-by-step solving** with explanations
- **Algorithm database** with pattern recognition
- **Performance analysis** and optimization suggestions

### 🎮 User Experience
- **WCA-compliant timer** with inspection time
- **Competition-style scrambling** following official guidelines
- **Customizable color schemes** including color-blind friendly options
- **Tutorial system** for learning cube solving
- **Statistics tracking** with solve history and averages
- **Algorithm trainer** for practicing specific patterns

### ⚡ Performance
- **60 FPS smooth animation** on modern hardware
- **Adaptive quality scaling** for different cube sizes
- **Memory optimization** for large cubes (up to 10x10)
- **Mobile-responsive design** with touch optimization

## Technology Stack

### Primary Implementation
- **Python** with PyOpenGL or ModernGL for graphics rendering
- **NumPy** for efficient mathematical operations
- **Pygame** for window management and input handling

### Alternative Implementations
- **Unity with C#** for desktop/mobile deployment
- **Web-based** with Three.js/WebGL for browser compatibility

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/rcsim.git
cd rcsim

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the simulator
python main.py
```

## Quick Start

### Basic Controls
- **Mouse**: Click and drag to rotate cube faces
- **Keyboard**: Use standard notation (R, L, U, D, F, B, etc.)
- **Spacebar**: Generate new scramble
- **Enter**: Start/stop timer
- **Ctrl+Z**: Undo move
- **Ctrl+Y**: Redo move

### Solving Your First Cube
1. Press **Spacebar** to scramble the cube
2. Click **Tutorial** to learn basic solving steps
3. Use **Step-by-step solving** to see the solution process
4. Practice with the **Algorithm Trainer** for specific cases

## Architecture

The simulator follows a modular, layered architecture:

```
┌─────────────────────────────────────────┐
│           Presentation Layer            │
│  UI Components | Controls | Displays    │
├─────────────────────────────────────────┤
│          Application Layer              │
│  Use Cases | Orchestration | Services   │
├─────────────────────────────────────────┤
│            Domain Layer                 │
│  Cube Logic | Solving | Patterns        │
├─────────────────────────────────────────┤
│         Infrastructure Layer            │
│  Graphics | Storage | External APIs     │
└─────────────────────────────────────────┘
```

### Core Modules
- **`cube/`**: Cube state management and move validation
- **`solvers/`**: Algorithm implementations and pattern recognition
- **`graphics/`**: 3D rendering and animation system
- **`ui/`**: User interface and control panels
- **`utils/`**: Scrambling, notation parsing, and utilities

## Development

### Project Structure
```
rcsim/
├── src/
│   ├── cube/           # Cube engine and state management
│   ├── solvers/        # Solving algorithms and pattern recognition
│   ├── graphics/       # 3D rendering and animations
│   ├── ui/            # User interface components
│   └── utils/         # Utilities and helpers
├── tests/             # Unit and integration tests
├── docs/              # Documentation
├── assets/            # 3D models, textures, sounds
└── examples/          # Example scripts and tutorials
```

### Testing
```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test module
pytest tests/test_cube.py
```

### Code Quality
```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Ensure all tests pass: `pytest`
5. Submit a pull request

### Contribution Guidelines
- Follow PEP 8 style guidelines
- Add unit tests for new functionality
- Update documentation for API changes
- Ensure solving algorithms are mathematically correct
- Maintain 60 FPS performance standards

## Algorithm Implementation

The simulator implements **authentic solving algorithms**, not simple move reversal:

### Layer-by-Layer Method
1. **Cross formation** on bottom face
2. **First layer corners** completion
3. **Middle layer edges** insertion
4. **Last layer cross** (OLL algorithms)
5. **Corner orientation** and **permutation**
6. **Edge permutation** to complete solve

### CFOP Method
- **Cross**: Efficient cross solving with inspection
- **F2L**: Advanced First Two Layers with pair recognition
- **OLL**: Complete 57-algorithm set for last layer orientation
- **PLL**: Complete 21-algorithm set for last layer permutation

### Pattern Recognition
- Real-time case identification for OLL/PLL
- Optimized hash-based pattern matching
- Look-ahead capabilities for advanced solving

## Performance Optimization

### Cube Size Scaling
- **2x2-3x3**: Full quality rendering with all effects
- **4x4-5x5**: Medium quality with essential effects
- **6x6+**: Optimized rendering with reduced effects

### Memory Management
- Compressed representation for large cubes
- Object pooling for frequent allocations
- Progressive asset loading
- Automatic garbage collection optimization

### Rendering Optimizations
- Level-of-detail (LOD) based on camera distance
- Frustum culling for off-screen pieces
- Instanced rendering for identical geometry
- Texture atlasing to reduce draw calls

## Educational Features

### Tutorial System
- Interactive step-by-step lessons
- Visual highlighting of relevant pieces
- Progress tracking and skill assessment
- Multiple difficulty levels

### Algorithm Trainer
- Practice specific OLL/PLL cases
- Timed algorithm execution
- Mistake detection and correction
- Performance improvement tracking

### Solve Analysis
- Move efficiency scoring
- Time breakdown by phase
- Optimization suggestions
- Comparison with optimal solutions

## Competition Features

### WCA Compliance
- Official scrambling algorithms
- Standard timing procedures
- Inspection time handling
- Result format compatibility

### Statistics Tracking
- Single solve times
- Average of 5/12/100 calculations
- Personal best tracking
- Detailed solve history
- Export capabilities for analysis

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- World Cube Association (WCA) for standardized notation and procedures
- Speedcubing community for algorithm development and optimization
- Open source graphics libraries enabling realistic 3D rendering

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-username/rcsim/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/rcsim/discussions)
- **Wiki**: [Project Wiki](https://github.com/your-username/rcsim/wiki)

---

*Built with ❤️ for the speedcubing community*