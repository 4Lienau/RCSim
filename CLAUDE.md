# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Advanced Rubik's Cube Simulator project - a comprehensive 3D cube simulator with realistic graphics, authentic solving algorithms, and extensive customization options. The project aims to create a production-ready application serving both educational and speedcubing training purposes.

## Current Status

**Repository State**: Empty - contains only requirements specification
- No source code has been implemented yet
- Project is in planning/specification phase
- Ready for initial development

## Architecture Requirements

Based on the specification, the project should be structured with:

### Recommended Technology Stack
- **Primary**: Python with Pygame for graphics rendering
- **Alternative**: Web-based implementation with Three.js/WebGL

### Core Module Structure
The codebase should implement modular design with separate components for:

1. **Cube Engine** (`cube/`)
   - Cube state representation and validation
   - Move notation parsing (R, L, U, D, F, B, M, E, S, x, y, z)
   - Legal move validation and history tracking

2. **3D Rendering** (`graphics/`)
   - 3D visualization with lighting and shadows
   - Smooth animation system for rotations
   - Camera controls (rotate, zoom, pan)
   - Material and texture management

3. **Solving Algorithms** (`solvers/`)
   - Layer-by-Layer (Beginner's Method)
   - CFOP (Cross, F2L, OLL, PLL) with complete algorithm sets
   - Optional: Roux and ZZ methods
   - Pattern recognition for automated solving

4. **User Interface** (`ui/`)
   - Control panels and settings
   - Timer functionality and statistics
   - Algorithm trainer and tutorial system
   - Import/export functionality

5. **Utilities** (`utils/`)
   - Scramble generation (WCA-compliant)
   - Notation conversion and validation
   - Performance optimization utilities

## Key Implementation Requirements

### Cube Mechanics
- Support for multiple cube sizes: 2x2 through 10x10
- Authentic physics and realistic proportions
- Intuitive controls (mouse drag, keyboard shortcuts, touch)
- Undo/redo with complete move history

### Solving System Priority
**Critical**: Implement actual solving algorithms, not just move reversal
- Real-time step-by-step solving with explanations
- Algorithm database with pattern recognition
- Performance metrics (solve times, move counts, TPS)

### Performance Standards
- Maintain 60 FPS smooth animation
- Efficient memory usage for larger cubes
- Fast algorithm execution
- Responsive design for multiple devices

### Quality Requirements
- Mathematically correct cube representation
- Well-commented, maintainable code
- Comprehensive error handling
- Intuitive user experience

## Development Workflow

Since this is a new project:

1. **Project Setup**
   ```bash
   # Create virtual environment for Python development
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   
   # Install dependencies (when requirements.txt is created)
   pip install -r requirements.txt
   ```

2. **Testing** (when implemented)
   ```bash
   # Run unit tests
   python -m pytest tests/
   
   # Run with coverage
   python -m pytest --cov=src tests/
   ```

3. **Code Quality** (when linting is set up)
   ```bash
   # Format code
   black src/
   
   # Lint code
   flake8 src/
   ```

## Development Notes

- Prioritize cube logic correctness over visual polish initially
- Implement solving algorithms with proper pattern recognition
- Use standard WCA notation throughout
- Ensure extensibility for future solving methods
- Focus on educational value and authentic speedcubing experience