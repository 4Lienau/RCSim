# User Guide

## Table of Contents

- [Getting Started](#getting-started)
- [Interface Overview](#interface-overview)
- [Basic Controls](#basic-controls)
- [Solving Your First Cube](#solving-your-first-cube)
- [Advanced Features](#advanced-features)
- [Settings and Customization](#settings-and-customization)
- [Competition Mode](#competition-mode)
- [Troubleshooting](#troubleshooting)

## Getting Started

### Installation

1. **Download the simulator** from the releases page
2. **Extract** the files to your preferred location
3. **Run** the application:
   - Windows: Double-click `rcsim.exe`
   - macOS: Open `rcsim.app`
   - Linux: Run `./rcsim` or `python main.py`

### First Launch

When you first open the simulator, you'll see:
- A solved 3x3 Rubik's Cube in the center
- Control panels on the sides
- A timer widget at the top
- Settings menu accessible via the gear icon

## Interface Overview

### Main Window Layout

```
┌─────────────────────────────────────────────────────────┐
│  File  Edit  View  Tools  Help           🕐 00:00.00    │
├─────────────────────────────────────────────────────────┤
│ ┌───────────┐                           ┌─────────────┐ │
│ │           │                           │             │ │
│ │  Control  │        🎲 CUBE 🎲         │  Statistics │ │
│ │   Panel   │                           │    Panel    │ │
│ │           │                           │             │ │
│ └───────────┘                           └─────────────┘ │
├─────────────────────────────────────────────────────────┤
│              Move History: R U R' U R U2 R'             │
└─────────────────────────────────────────────────────────┘
```

### Control Panel

**Scramble Section:**
- **New Scramble**: Generate random scramble
- **Scramble Length**: Adjust from 15-30 moves
- **Apply**: Execute custom scramble sequence

**Solving Section:**
- **Method**: Choose solving approach
  - Layer-by-Layer (Beginner)
  - CFOP (Advanced)
  - Roux (Alternative advanced)
- **Step-by-Step**: Guided solving with explanations
- **Auto Solve**: Watch complete solution
- **Speed**: Control solving animation speed

**Cube Options:**
- **Size**: Switch between 2x2 through 10x10
- **Colors**: Customize face colors
- **Reset**: Return to solved state

### Statistics Panel

**Current Session:**
- Solve count
- Best/worst times
- Current average
- Total solving time

**Historical Statistics:**
- Average of 5 (Ao5)
- Average of 12 (Ao12) 
- Average of 100 (Ao100)
- Personal best records
- Solve graph over time

## Basic Controls

### Mouse Controls

**Cube Rotation:**
- **Left Click + Drag**: Rotate cube faces
- **Right Click + Drag**: Rotate camera view
- **Mouse Wheel**: Zoom in/out
- **Middle Click + Drag**: Pan camera

**Face Selection:**
- **Hover**: Highlight face that will rotate
- **Click**: Select face for rotation
- **Drag**: Execute 90° rotation in drag direction

### Keyboard Controls

**Standard Notation:**
- **R**: Right face clockwise
- **R'** (R + '): Right face counterclockwise  
- **R2**: Right face 180°
- **L**: Left face clockwise
- **U**: Up face clockwise
- **D**: Down face clockwise
- **F**: Front face clockwise
- **B**: Back face clockwise

**Wide Turns:**
- **r** (lowercase): Right wide turn
- **l**: Left wide turn
- **u**: Up wide turn

**Cube Rotations:**
- **x**: Rotate entire cube (R direction)
- **y**: Rotate entire cube (U direction)
- **z**: Rotate entire cube (F direction)

**Control Keys:**
- **Space**: New scramble
- **Enter**: Start/stop timer
- **Ctrl+Z**: Undo move
- **Ctrl+Y**: Redo move
- **Ctrl+R**: Reset cube
- **F11**: Toggle fullscreen

### Touch Controls (Mobile/Tablet)

**Single Touch:**
- **Tap**: Select face
- **Swipe**: Rotate face in swipe direction
- **Long Press**: Open context menu

**Multi-Touch:**
- **Pinch**: Zoom in/out
- **Two-finger Drag**: Rotate camera
- **Three-finger Tap**: Reset camera view

## Solving Your First Cube

### Method 1: Guided Tutorial

1. **Start Tutorial**: Click "Tutorial" in the control panel
2. **Choose Difficulty**: Select "Beginner" for Layer-by-Layer method
3. **Follow Steps**: 
   - Read each step explanation
   - Practice the moves shown
   - Use "Next" when ready to continue
4. **Complete Layers**: Progress through all seven steps:
   - White cross formation
   - White corner completion
   - Middle layer edges
   - Yellow cross
   - Yellow corner orientation
   - Yellow corner permutation  
   - Yellow edge permutation

### Method 2: Step-by-Step Solving

1. **Scramble**: Press Space or click "New Scramble"
2. **Choose Method**: Select "Layer-by-Layer" from dropdown
3. **Start Solving**: Click "Step-by-Step"
4. **Follow Instructions**: 
   - Read the explanation for each step
   - Execute the suggested move
   - Watch piece movement highlights
   - Continue until solved

### Method 3: Watch and Learn

1. **Scramble** the cube
2. **Select** "Auto Solve" from solving section
3. **Choose Speed**: Adjust slider for comfortable viewing
4. **Watch**: Observe the complete solving process
5. **Replay**: Use controls to replay specific sections
6. **Practice**: Try to replicate the moves manually

## Advanced Features

### Algorithm Trainer

Perfect for learning specific algorithm patterns:

1. **Access**: Tools → Algorithm Trainer
2. **Choose Category**:
   - OLL (Orient Last Layer) - 57 cases
   - PLL (Permute Last Layer) - 21 cases
   - F2L (First Two Layers) - Common cases
3. **Practice Mode**:
   - **Recognition**: Identify the case
   - **Execution**: Perform the algorithm
   - **Timed**: Practice with time pressure
4. **Track Progress**: View accuracy and improvement over time

### Pattern Library

Explore famous cube patterns:

1. **Access**: View → Patterns
2. **Browse Categories**:
   - Checkerboard patterns
   - Stripe patterns
   - Cube-in-cube
   - Cross patterns
   - Custom patterns
3. **Apply Pattern**: Click to transform cube
4. **Learn Algorithm**: View the move sequence to create pattern
5. **Save Custom**: Create and save your own patterns

### Advanced Solving Methods

#### CFOP Method
- **Cross**: Efficient cross formation with inspection
- **F2L**: First Two Layers with advanced algorithms
- **OLL**: Orient Last Layer using 57 algorithms
- **PLL**: Permute Last Layer using 21 algorithms

#### Roux Method
- **Block Building**: Left and right 1x2x3 blocks
- **Top Face**: Orient last six edges
- **LSE**: Last Six Edges algorithms

### Multi-Cube Sizes

**2x2 (Pocket Cube):**
- Simplified OLL/PLL algorithms
- Faster solving times
- Good for beginners

**4x4 (Revenge Cube):**
- Parity algorithms required
- Center piece alignment
- Edge pairing techniques

**5x5+ (Professor Cube and larger):**
- Extended center alignment
- Multiple edge pairing phases
- Advanced parity handling

## Settings and Customization

### Visual Settings

**Graphics Quality:**
- **High**: Full effects, reflections, shadows
- **Medium**: Reduced effects for better performance
- **Low**: Basic rendering for older hardware

**Color Schemes:**
- **Standard**: Traditional WCA colors
- **High Contrast**: Better visibility
- **Color Blind**: Deuteranopia/Protanopia friendly
- **Custom**: Create your own color scheme

**Animation Settings:**
- **Speed**: 0.1x to 10x normal speed
- **Smoothness**: Frame rate vs. quality balance
- **Effects**: Enable/disable visual effects

### Control Settings

**Mouse Sensitivity:**
- **Rotation**: Adjust camera rotation speed
- **Face Turn**: Control move execution sensitivity
- **Zoom**: Mouse wheel zoom speed

**Keyboard Mapping:**
- **Standard**: Default QWERTY layout
- **Custom**: Remap any key to any move
- **Profiles**: Save different key configurations

### Timer Settings

**Timing Options:**
- **Precision**: Milliseconds to display (0-3 decimal places)
- **Inspection Time**: 15 seconds standard, customizable
- **Penalties**: DNF and +2 second penalties
- **Auto Start**: Begin timing on first move

**Display Options:**
- **Large Timer**: Full-screen timer mode
- **Session Stats**: Show/hide statistics during solve
- **Split Times**: Track phase completion times

### Audio Settings

**Sound Effects:**
- **Move Sounds**: Click sounds for cube moves
- **Timer Sounds**: Start/stop/penalty sounds
- **Completion**: Celebration sound for successful solves
- **Volume**: Master volume control

## Competition Mode

Simulate official WCA competition conditions:

### Setup Competition Mode

1. **Access**: Tools → Competition Mode
2. **Configure Settings**:
   - **Event**: 3x3, 2x2, 4x4, etc.
   - **Round Type**: Average of 5, Mean of 3
   - **Inspection Time**: 15 seconds
   - **Penalties**: Enable DNF and +2

### Competition Interface

**Timer Display:**
- Large, centered timer
- Inspection countdown
- Penalty indicators

**Controls:**
- **Spacebar Hold**: Ready timer (turns green)
- **Spacebar Release**: Start solve
- **Spacebar Press**: Stop timer
- **Any Key During Inspection**: Start solve early

### Results Management

**Solve Results:**
- Individual solve times
- Penalty tracking (DNF, +2)
- Video recording (if enabled)
- Move count and TPS

**Session Statistics:**
- Current average calculation
- Best/worst solve highlighting
- Standard deviation
- Export results for analysis

### WCA Compliance

**Official Standards:**
- Scramble generation follows WCA guidelines
- Timer precision matches competition standards
- Penalty system matches official rules
- Statistics calculated per WCA methods

## Troubleshooting

### Performance Issues

**Low Frame Rate:**
1. Reduce graphics quality in settings
2. Close other applications
3. Update graphics drivers
4. Use smaller cube sizes (3x3 vs 7x7)

**Slow Algorithm Execution:**
1. Disable step-by-step explanations
2. Increase solving speed setting
3. Use simpler solving methods
4. Restart application to clear memory

### Control Problems

**Mouse Not Responding:**
1. Check mouse sensitivity settings
2. Try keyboard controls instead
3. Restart application
4. Check for driver issues

**Moves Not Registering:**
1. Verify keyboard layout settings
2. Check for key mapping conflicts
3. Use on-screen move buttons
4. Reset controls to default

### Display Issues

**Cube Not Visible:**
1. Reset camera view (Ctrl+Home)
2. Check graphics settings
3. Update graphics drivers
4. Try windowed mode instead of fullscreen

**Colors Not Displaying Correctly:**
1. Check color scheme settings
2. Verify monitor color calibration
3. Try different graphics quality setting
4. Reset visual settings to default

### Audio Problems

**No Sound:**
1. Check system volume
2. Verify audio settings in application
3. Test other audio applications
4. Check Windows audio device settings

### Getting Help

**In-Application Help:**
- Press F1 for context-sensitive help
- Help → User Guide for this manual
- Help → Keyboard Shortcuts for quick reference

**Online Resources:**
- Project website: Documentation and tutorials
- GitHub Issues: Report bugs and request features
- Community Forum: Get help from other users
- Video Tutorials: Step-by-step learning materials

**Contact Support:**
- Email: support@rcsim.org
- Discord: Join our community server
- GitHub: Create an issue for bugs or features

## Tips for Success

### Learning to Solve

1. **Start Simple**: Begin with 2x2 or layer-by-layer method
2. **Practice Regularly**: Short, frequent sessions work best
3. **Use Slow Motion**: Learn moves at comfortable speed
4. **Understand Concepts**: Don't just memorize algorithms
5. **Join Community**: Learn from experienced cubers

### Improving Times

1. **Learn Advanced Methods**: Progress from beginner to CFOP
2. **Practice Algorithms**: Use the algorithm trainer regularly
3. **Improve Recognition**: Practice identifying patterns quickly
4. **Work on Flow**: Smooth execution is faster than rushed moves
5. **Analyze Solves**: Review your solutions for inefficiencies

### Using the Simulator Effectively

1. **Customize Interface**: Set up controls and display to your preference
2. **Track Progress**: Use statistics to monitor improvement
3. **Vary Practice**: Mix different cube sizes and methods
4. **Set Goals**: Work toward specific time or accuracy targets
5. **Stay Patient**: Improvement takes time and consistent practice

---

*Happy cubing! 🧩*