# Contributing to Advanced Rubik's Cube Simulator

Thank you for your interest in contributing to the Advanced Rubik's Cube Simulator! This document provides guidelines and information for contributors.

## 🎯 Project Vision

Our goal is to create the most realistic and educational Rubik's Cube simulator available, featuring:
- Authentic solving algorithms (not just move reversal)
- Realistic 3D graphics and physics
- Educational value for learning speedcubing
- Competition-grade timing and statistics
- Support for multiple cube sizes (2x2 through 10x10)

## 🚀 Getting Started

### Prerequisites
- Python 3.9+ 
- Git
- Basic knowledge of Rubik's Cube solving
- Familiarity with speedcubing notation

### Development Setup
1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/rcsim.git
   cd rcsim
   ```

2. **Set up development environment**
   ```bash
   make setup-dev
   # OR manually:
   chmod +x scripts/setup-dev.sh
   ./scripts/setup-dev.sh
   ```

3. **Activate virtual environment**
   ```bash
   source venv/bin/activate
   ```

4. **Verify setup**
   ```bash
   make test
   make run-headless
   ```

## 💻 Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
# OR
git checkout -b fix/bug-description
# OR  
git checkout -b algorithm/algorithm-name
```

### 2. Make Changes
- Follow the [coding standards](#coding-standards)
- Write tests for new functionality
- Update documentation as needed
- Ensure algorithms are mathematically correct

### 3. Test Your Changes
```bash
# Run all tests
make test

# Run specific test types
make test-unit
make test-integration
make test-performance

# Check code quality
make quality
```

### 4. Commit Changes
```bash
# Stage changes
git add .

# Commit with conventional commit format
git commit -m "feat: add CFOP OLL algorithm recognition"
git commit -m "fix: correct cube state validation"
git commit -m "docs: update API documentation"
```

### 5. Submit Pull Request
- Push your branch to your fork
- Create a pull request using our [PR template](.github/PULL_REQUEST_TEMPLATE.md)
- Ensure all CI checks pass
- Respond to review feedback

## 📝 Coding Standards

### Python Style
- **Formatter**: Black (88 character line length)
- **Import sorting**: isort with Black profile
- **Linting**: Flake8 with plugins
- **Type hints**: Required for all public APIs
- **Docstrings**: NumPy style for all functions/classes

### Example Code Style
```python
from typing import List, Optional
import numpy as np

from rcsim.cube.moves import Move


class CubeSolver:
    """Base class for cube solving algorithms.
    
    This class provides the interface for implementing
    various Rubik's Cube solving methods.
    
    Parameters
    ----------
    cube_size : int
        Size of the cube (2-10)
    method_name : str
        Human-readable name of the solving method
        
    Attributes
    ----------
    cube_size : int
        The size of the cube this solver supports
    method_name : str
        Name of the solving method
    """
    
    def __init__(self, cube_size: int, method_name: str) -> None:
        self.cube_size = cube_size
        self.method_name = method_name
    
    def solve(self, cube_state: "CubeState") -> List[Move]:
        """Generate solution for the given cube state.
        
        Parameters
        ----------
        cube_state : CubeState
            Current state of the cube to solve
            
        Returns
        -------
        List[Move]
            Sequence of moves to solve the cube
            
        Raises
        ------
        ValueError
            If cube_state is invalid or unsolvable
        """
        # Implementation here
        pass
```

### Algorithm Implementation Standards
- **Correctness**: All algorithms must be mathematically verified
- **Notation**: Use standard WCA notation (R, U, R', R2, etc.)
- **Testing**: Include test cases with known scrambles and solutions
- **Documentation**: Explain the algorithm's purpose and when to use it
- **Performance**: Consider time and space complexity

## 🧩 Contributing Algorithms

### Types of Algorithm Contributions
1. **New solving methods** (CFOP, Roux, ZZ, etc.)
2. **Algorithm cases** (OLL, PLL, F2L)
3. **Pattern recognition** improvements
4. **Algorithm optimizations**

### Algorithm Contribution Process
1. **Research**: Ensure the algorithm is well-established and correct
2. **Implementation**: Follow our algorithm interface
3. **Testing**: Provide comprehensive test cases
4. **Documentation**: Include notation, purpose, and usage
5. **Verification**: Have other cubers verify correctness

### Algorithm Template
```python
class NewAlgorithmSolver(ISolver):
    """Implementation of [Algorithm Name] solving method.
    
    [Algorithm description, history, and when to use]
    
    References
    ----------
    - [Link to algorithm source/documentation]
    - [Speedcubing community references]
    """
    
    def solve(self, cube: ICube) -> SolutionResult:
        # Step 1: [Phase description]
        phase1_moves = self._solve_phase1(cube)
        
        # Step 2: [Phase description] 
        phase2_moves = self._solve_phase2(cube)
        
        return SolutionResult(
            steps=phase1_moves + phase2_moves,
            method=self.get_algorithm_name(),
            phases={"phase1": len(phase1_moves), "phase2": len(phase2_moves)}
        )
```

## 🧪 Testing Guidelines

### Test Types
1. **Unit tests**: Test individual functions and classes
2. **Integration tests**: Test component interactions
3. **Algorithm tests**: Verify solving correctness
4. **Performance tests**: Check performance regressions
5. **Property-based tests**: Use Hypothesis for edge cases

### Test Structure
```python
class TestCubeSolver:
    """Test suite for cube solving algorithms."""
    
    def test_solver_solves_scrambled_cube(self):
        """Test that solver correctly solves a scrambled cube."""
        cube = Cube(3)
        scramble = ["R", "U", "R'", "F", "R", "F'"]
        cube.apply_scramble(scramble)
        
        solver = YourSolver()
        solution = solver.solve(cube)
        
        # Apply solution
        for move in solution.steps:
            cube.execute_move(move.move)
            
        assert cube.is_solved()
    
    @pytest.mark.parametrize("scramble", [
        "R U R' U'",
        "F R U' R' F'", 
        "R U2 R' U' R U' R'"
    ])
    def test_solver_handles_various_scrambles(self, scramble):
        """Test solver with different scramble patterns."""
        # Implementation
        pass
```

### Performance Testing
```python
def test_solver_performance(benchmark):
    """Benchmark solver performance."""
    cube = Cube(3)
    solver = YourSolver()
    
    def solve_cube():
        cube.apply_scramble(standard_scramble)
        return solver.solve(cube)
    
    result = benchmark(solve_cube)
    
    # Assert performance requirements
    assert len(result.steps) < 100  # Reasonable move count
```

## 📚 Documentation

### Required Documentation
- **API docs**: Docstrings for all public functions
- **Algorithm docs**: Explanation of algorithm logic
- **Usage examples**: How to use new features
- **Performance notes**: Time/space complexity

### Documentation Style
- Use clear, concise language
- Include code examples
- Explain the "why" not just the "what"
- Use proper speedcubing terminology

## 🐛 Bug Reports

### Before Reporting
1. Search existing issues
2. Try the latest version
3. Reproduce the bug consistently
4. Check if it's a known limitation

### Bug Report Content
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, graphics card)
- Error messages or logs
- Screenshots if applicable

## ✨ Feature Requests

### Good Feature Requests
- Solve a real problem
- Align with project goals
- Include use cases and benefits
- Consider implementation complexity
- Have educational or competitive value

### Feature Categories
- **Cube mechanics**: New cube sizes, move types
- **Algorithms**: New solving methods, optimizations
- **Graphics**: Visual improvements, animations
- **UI/UX**: Interface improvements, accessibility
- **Performance**: Speed optimizations, memory usage
- **Educational**: Tutorials, explanations, training
- **Competition**: Timing, statistics, WCA compliance

## 🔍 Code Review Process

### For Contributors
- Respond to feedback promptly
- Make requested changes
- Ask questions if unclear
- Update tests and documentation

### For Reviewers
- Be constructive and helpful
- Focus on code quality and correctness
- Verify algorithm accuracy
- Test changes locally
- Check documentation completeness

## 🏆 Recognition

Contributors are recognized in:
- README acknowledgments
- Release notes
- Git commit history
- Optional: Hall of Fame for significant contributions

## 📞 Getting Help

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Request Comments**: Code-specific discussions

### Questions Welcome
- Algorithm implementation help
- Code structure questions
- Performance optimization ideas
- Testing strategies
- Documentation improvements

## 📄 Legal

### License
By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

### Code of Conduct
- Be respectful and inclusive
- Focus on technical merit
- Help newcomers learn
- Maintain professional communication
- No harassment or discrimination

## 🎉 Thank You!

Every contribution makes this project better for the entire speedcubing community. Whether you're fixing a typo, implementing a complex algorithm, or improving performance, your work is valued and appreciated!

---

*Happy cubing! 🧩*