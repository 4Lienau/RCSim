"""Base classes for cube solving algorithms."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum

from ..cube import Cube
from ..cube.moves import MoveSequence


class SolutionPhase(Enum):
    """Phases of cube solving."""
    CROSS = "cross"
    F2L = "f2l"
    OLL = "oll"
    PLL = "pll"
    LAYER1 = "layer1"
    LAYER2 = "layer2"
    LAYER3 = "layer3"
    COMPLETE = "complete"


@dataclass
class SolutionStep:
    """Represents a single step in the solving process."""
    phase: SolutionPhase
    description: str
    moves: MoveSequence
    explanation: str
    cube_state_before: Optional[str] = None
    cube_state_after: Optional[str] = None
    efficiency_score: Optional[float] = None


class BaseSolver(ABC):
    """Abstract base class for cube solving algorithms."""
    
    def __init__(self, name: str):
        """Initialize the solver.
        
        Parameters
        ----------
        name : str
            Name of the solving method
        """
        self.name = name
        self.solution_steps: List[SolutionStep] = []
        self.total_moves = 0
        self.solve_time = 0.0
    
    @abstractmethod
    def solve(self, cube: Cube) -> List[SolutionStep]:
        """Solve the given cube.
        
        Parameters
        ----------
        cube : Cube
            Cube to solve
            
        Returns
        -------
        List[SolutionStep]
            List of solution steps
        """
        pass
    
    @abstractmethod
    def can_solve(self, cube: Cube) -> bool:
        """Check if this solver can solve the given cube.
        
        Parameters
        ----------
        cube : Cube
            Cube to check
            
        Returns
        -------
        bool
            True if solver can handle this cube
        """
        pass
    
    def get_full_solution(self, cube: Cube) -> MoveSequence:
        """Get the complete solution as a single move sequence.
        
        Parameters
        ----------
        cube : Cube
            Cube to solve
            
        Returns
        -------
        MoveSequence
            Complete solution sequence
        """
        steps = self.solve(cube)
        all_moves = []
        for step in steps:
            all_moves.extend(step.moves)
        return MoveSequence(all_moves)
    
    def get_solution_summary(self) -> Dict[str, Any]:
        """Get summary statistics for the last solution.
        
        Returns
        -------
        Dict[str, Any]
            Summary statistics
        """
        if not self.solution_steps:
            return {}
        
        phase_counts = {}
        for step in self.solution_steps:
            phase = step.phase.value
            if phase not in phase_counts:
                phase_counts[phase] = 0
            phase_counts[phase] += len(step.moves)
        
        return {
            'solver': self.name,
            'total_steps': len(self.solution_steps),
            'total_moves': self.total_moves,
            'solve_time': self.solve_time,
            'moves_per_second': self.total_moves / max(self.solve_time, 0.001),
            'phase_breakdown': phase_counts,
            'average_moves_per_step': self.total_moves / len(self.solution_steps)
        }
    
    def explain_solution(self) -> str:
        """Get detailed explanation of the solution.
        
        Returns
        -------
        str
            Formatted explanation
        """
        if not self.solution_steps:
            return f"No solution found using {self.name}"
        
        explanation = [f"{self.name} Solution ({self.total_moves} moves):"]
        explanation.append("=" * 50)
        
        for i, step in enumerate(self.solution_steps, 1):
            explanation.append(f"\nStep {i}: {step.description}")
            explanation.append(f"Phase: {step.phase.value.upper()}")
            explanation.append(f"Moves: {step.moves}")
            explanation.append(f"Explanation: {step.explanation}")
            
            if step.efficiency_score:
                explanation.append(f"Efficiency: {step.efficiency_score:.2f}/5.0")
        
        explanation.append(f"\nTotal moves: {self.total_moves}")
        if self.solve_time > 0:
            explanation.append(f"Solve time: {self.solve_time:.3f}s")
            explanation.append(f"Speed: {self.total_moves/self.solve_time:.1f} moves/second")
        
        return "\n".join(explanation)
    
    def _create_step(self, phase: SolutionPhase, description: str, 
                    moves: MoveSequence, explanation: str) -> SolutionStep:
        """Create a solution step.
        
        Parameters
        ----------
        phase : SolutionPhase
            Phase of solving
        description : str
            Brief description
        moves : MoveSequence
            Moves for this step
        explanation : str
            Detailed explanation
            
        Returns
        -------
        SolutionStep
            Created step
        """
        return SolutionStep(
            phase=phase,
            description=description,
            moves=moves,
            explanation=explanation
        )
    
    def reset(self) -> None:
        """Reset solver state for a new solve."""
        self.solution_steps.clear()
        self.total_moves = 0
        self.solve_time = 0.0