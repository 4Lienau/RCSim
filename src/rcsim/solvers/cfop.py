"""CFOP (Cross, F2L, OLL, PLL) solver implementation."""

import time
from typing import List, Optional, Tuple
from copy import deepcopy

from .base import BaseSolver, SolutionStep, SolutionPhase
from .algorithms import AlgorithmDatabase
from ..cube import Cube
from ..cube.moves import MoveSequence, Move
from ..cube.state import Position, StandardColors


class CFOPSolver(BaseSolver):
    """CFOP solving method (advanced speedcubing method).
    
    CFOP stands for:
    - Cross: Solve the bottom cross
    - F2L: First Two Layers (corners and edges together)
    - OLL: Orient Last Layer (make top face one color)
    - PLL: Permute Last Layer (position all pieces correctly)
    """
    
    def __init__(self):
        """Initialize the CFOP solver."""
        super().__init__("CFOP (Cross, F2L, OLL, PLL)")
        self.algorithm_db = AlgorithmDatabase()
    
    def can_solve(self, cube: Cube) -> bool:
        """Check if this solver can solve the given cube.
        
        Parameters
        ----------
        cube : Cube
            Cube to check
            
        Returns
        -------
        bool
            True if solver can handle this cube (3x3 only)
        """
        return cube.size == 3
    
    def solve(self, cube: Cube) -> List[SolutionStep]:
        """Solve the cube using CFOP method.
        
        Parameters
        ----------
        cube : Cube
            Cube to solve
            
        Returns
        -------
        List[SolutionStep]
            List of solution steps
        """
        if not self.can_solve(cube):
            raise ValueError(f"CFOP solver only supports 3x3 cubes, got {cube.size}x{cube.size}")
        
        self.reset()
        start_time = time.time()
        
        # Work on a copy so we don't modify the original
        work_cube = cube.clone()
        
        # Step 1: Cross
        step1 = self._solve_cross(work_cube)
        if step1:
            self.solution_steps.append(step1)
            self.total_moves += len(step1.moves)
        
        # Step 2: F2L (First Two Layers)
        step2 = self._solve_f2l(work_cube)
        if step2:
            self.solution_steps.append(step2)
            self.total_moves += len(step2.moves)
        
        # Step 3: OLL (Orient Last Layer)
        step3 = self._solve_oll(work_cube)
        if step3:
            self.solution_steps.append(step3)
            self.total_moves += len(step3.moves)
        
        # Step 4: PLL (Permute Last Layer)
        step4 = self._solve_pll(work_cube)
        if step4:
            self.solution_steps.append(step4)
            self.total_moves += len(step4.moves)
        
        self.solve_time = time.time() - start_time
        
        return self.solution_steps
    
    def _solve_cross(self, cube: Cube) -> Optional[SolutionStep]:
        """Solve the cross on the bottom face.
        
        Parameters
        ----------
        cube : Cube
            Cube to work on
            
        Returns
        -------
        Optional[SolutionStep]
            Solution step if moves were needed
        """
        moves = []
        
        # Check if cross is already solved
        if self._is_cross_solved(cube):
            return None
        
        # Advanced cross solving with inspection
        # This is a simplified implementation
        cross_moves = self._find_cross_solution(cube)
        
        for move_str in cross_moves:
            cube.apply_move(move_str)
            moves.append(Move.parse(move_str))
        
        if not moves:
            return None
        
        return self._create_step(
            SolutionPhase.CROSS,
            "Solve cross",
            MoveSequence(moves),
            "Efficiently solve the bottom cross with look-ahead and planning"
        )
    
    def _solve_f2l(self, cube: Cube) -> Optional[SolutionStep]:
        """Solve F2L (First Two Layers).
        
        Parameters
        ----------
        cube : Cube
            Cube to work on
            
        Returns
        -------
        Optional[SolutionStep]
            Solution step if moves were needed
        """
        moves = []
        
        # Check if F2L is already complete
        if self._is_f2l_complete(cube):
            return None
        
        # Solve each F2L pair
        for pair_num in range(4):
            if self._is_f2l_complete(cube):
                break
            
            pair_moves = self._solve_f2l_pair(cube, pair_num)
            for move_str in pair_moves:
                cube.apply_move(move_str)
                moves.append(Move.parse(move_str))
        
        if not moves:
            return None
        
        return self._create_step(
            SolutionPhase.F2L,
            "Solve F2L pairs",
            MoveSequence(moves),
            "Solve corner-edge pairs efficiently to complete first two layers"
        )
    
    def _solve_oll(self, cube: Cube) -> Optional[SolutionStep]:
        """Solve OLL (Orient Last Layer).
        
        Parameters
        ----------
        cube : Cube
            Cube to work on
            
        Returns
        -------
        Optional[SolutionStep]
            Solution step if moves were needed
        """
        moves = []
        
        # Check if OLL is already solved
        if self._is_oll_solved(cube):
            return None
        
        # Recognize OLL case and apply appropriate algorithm
        oll_case = self._recognize_oll_case(cube)
        oll_algorithm = self._get_oll_algorithm(oll_case)
        
        if oll_algorithm:
            for move in oll_algorithm.moves:
                cube.apply_move(move)
                moves.append(move)
        else:
            # Fallback to 2-look OLL
            moves.extend(self._two_look_oll(cube))
        
        if not moves:
            return None
        
        return self._create_step(
            SolutionPhase.OLL,
            f"Orient last layer (OLL case {oll_case})",
            MoveSequence(moves),
            "Orient all last layer pieces to make the top face one solid color"
        )
    
    def _solve_pll(self, cube: Cube) -> Optional[SolutionStep]:
        """Solve PLL (Permute Last Layer).
        
        Parameters
        ----------
        cube : Cube
            Cube to work on
            
        Returns
        -------
        Optional[SolutionStep]
            Solution step if moves were needed
        """
        moves = []
        
        # Check if already solved
        if cube.is_solved():
            return None
        
        # Recognize PLL case and apply appropriate algorithm
        pll_case = self._recognize_pll_case(cube)
        pll_algorithm = self._get_pll_algorithm(pll_case)
        
        if pll_algorithm:
            for move in pll_algorithm.moves:
                cube.apply_move(move)
                moves.append(move)
        else:
            # Fallback to 2-look PLL
            moves.extend(self._two_look_pll(cube))
        
        if not moves:
            return None
        
        return self._create_step(
            SolutionPhase.PLL,
            f"Permute last layer (PLL case {pll_case})",
            MoveSequence(moves),
            "Position all last layer pieces correctly to complete the solve"
        )
    
    def _find_cross_solution(self, cube: Cube) -> List[str]:
        """Find an efficient cross solution.
        
        Parameters
        ----------
        cube : Cube
            Cube to analyze
            
        Returns
        -------
        List[str]
            List of moves for cross solution
        """
        # This is a simplified cross solver
        # A real implementation would use advanced algorithms
        moves = []
        
        for i in range(15):  # Max moves for cross
            if self._is_cross_solved(cube):
                break
            
            # Try common cross moves
            candidates = ["F", "R", "U", "L", "B", "D", "F'", "R'", "U'", "L'", "B'", "D'"]
            
            # Simple heuristic: try moves that affect cross edges
            for move_str in candidates:
                test_cube = cube.clone()
                test_cube.apply_move(move_str)
                if self._count_cross_edges_correct(test_cube) > self._count_cross_edges_correct(cube):
                    moves.append(move_str)
                    cube.apply_move(move_str)
                    break
            else:
                # If no improvement found, try a random move
                moves.append("U")
                cube.apply_move("U")
        
        return moves
    
    def _solve_f2l_pair(self, cube: Cube, pair_num: int) -> List[str]:
        """Solve a single F2L pair.
        
        Parameters
        ----------
        cube : Cube
            Cube to work on
        pair_num : int
            F2L pair number (0-3)
            
        Returns
        -------
        List[str]
            Moves to solve this pair
        """
        # Simplified F2L pair solving
        moves = []
        
        # Use basic F2L algorithms from database
        f2l_algs = [
            self.algorithm_db.get_algorithm("F2L", "F2L-1"),
            self.algorithm_db.get_algorithm("F2L", "F2L-2"),
            self.algorithm_db.get_algorithm("F2L", "F2L-3"),
        ]
        
        # Try different F2L algorithms
        for alg in f2l_algs:
            if alg:
                for move in alg.moves:
                    moves.append(str(move))
                    cube.apply_move(move)
                break
        
        return moves
    
    def _two_look_oll(self, cube: Cube) -> List[Move]:
        """Fallback 2-look OLL implementation.
        
        Parameters
        ----------
        cube : Cube
            Cube to work on
            
        Returns
        -------
        List[Move]
            Moves for 2-look OLL
        """
        moves = []
        
        # First: Make yellow cross
        if not self._is_yellow_cross_formed(cube):
            cross_alg = self.algorithm_db.get_algorithm("OLL", "OLL 45")
            if cross_alg:
                for i in range(3):  # Max 3 applications
                    if self._is_yellow_cross_formed(cube):
                        break
                    for move in cross_alg.moves:
                        cube.apply_move(move)
                        moves.append(move)
        
        # Second: Orient corners
        if not self._is_oll_solved(cube):
            sune = self.algorithm_db.get_algorithm("Common", "Sune")
            if sune:
                for i in range(6):  # Max 6 applications
                    if self._is_oll_solved(cube):
                        break
                    for move in sune.moves:
                        cube.apply_move(move)
                        moves.append(move)
                    # Rotate to try different positions
                    cube.apply_move("U")
                    moves.append(Move.parse("U"))
        
        return moves
    
    def _two_look_pll(self, cube: Cube) -> List[Move]:
        """Fallback 2-look PLL implementation.
        
        Parameters
        ----------
        cube : Cube
            Cube to work on
            
        Returns
        -------
        List[Move]
            Moves for 2-look PLL
        """
        moves = []
        
        # Use T-Perm and A-Perm for 2-look PLL
        t_perm = self.algorithm_db.get_algorithm("PLL", "T-Perm")
        a_perm = self.algorithm_db.get_algorithm("PLL", "A-Perm A")
        
        # Try different PLL algorithms
        for alg in [t_perm, a_perm]:
            if not alg:
                continue
            
            for i in range(4):  # Try 4 orientations
                if cube.is_solved():
                    break
                
                for move in alg.moves:
                    cube.apply_move(move)
                    moves.append(move)
                
                if cube.is_solved():
                    break
                
                # Rotate top face
                cube.apply_move("U")
                moves.append(Move.parse("U"))
        
        return moves
    
    def _recognize_oll_case(self, cube: Cube) -> str:
        """Recognize the current OLL case.
        
        Parameters
        ----------
        cube : Cube
            Cube to analyze
            
        Returns
        -------
        str
            OLL case identifier
        """
        # Simplified OLL recognition
        top_face = cube.get_face_colors('U')
        yellow_color = StandardColors.YELLOW
        
        # Count yellow pieces on top
        yellow_count = sum(1 for row in top_face for color in row if color == yellow_color)
        
        if yellow_count == 9:
            return "Skip"
        elif yellow_count == 5:  # Cross
            return "Cross"
        elif yellow_count == 3:  # Line or L-shape
            return "Line"
        else:  # Dot
            return "Dot"
    
    def _recognize_pll_case(self, cube: Cube) -> str:
        """Recognize the current PLL case.
        
        Parameters
        ----------
        cube : Cube
            Cube to analyze
            
        Returns
        -------
        str
            PLL case identifier
        """
        # Simplified PLL recognition
        if cube.is_solved():
            return "Skip"
        
        # Count solved sides
        sides = ['F', 'R', 'B', 'L']
        solved_sides = 0
        
        for side in sides:
            face_colors = cube.get_face_colors(side)
            center_color = face_colors[1][1]
            
            # Check if top row matches center
            if all(face_colors[0][i] == center_color for i in range(3)):
                solved_sides += 1
        
        if solved_sides == 0:
            return "H-Perm"
        elif solved_sides == 1:
            return "T-Perm"
        elif solved_sides == 2:
            return "U-Perm"
        else:
            return "A-Perm"
    
    def _get_oll_algorithm(self, case: str):
        """Get OLL algorithm for a case.
        
        Parameters
        ----------
        case : str
            OLL case identifier
            
        Returns
        -------
        Algorithm or None
            Algorithm for the case
        """
        case_map = {
            "Cross": self.algorithm_db.get_algorithm("OLL", "OLL 21"),
            "Line": self.algorithm_db.get_algorithm("OLL", "OLL 45"),
            "Dot": self.algorithm_db.get_algorithm("OLL", "OLL 1"),
        }
        return case_map.get(case)
    
    def _get_pll_algorithm(self, case: str):
        """Get PLL algorithm for a case.
        
        Parameters
        ----------
        case : str
            PLL case identifier
            
        Returns
        -------
        Algorithm or None
            Algorithm for the case
        """
        case_map = {
            "T-Perm": self.algorithm_db.get_algorithm("PLL", "T-Perm"),
            "A-Perm": self.algorithm_db.get_algorithm("PLL", "A-Perm A"),
            "U-Perm": self.algorithm_db.get_algorithm("PLL", "U-Perm A"),
            "H-Perm": self.algorithm_db.get_algorithm("PLL", "H-Perm"),
        }
        return case_map.get(case)
    
    # Helper methods (reuse from LayerByLayerSolver with similar logic)
    def _is_cross_solved(self, cube: Cube) -> bool:
        """Check if cross is solved."""
        bottom_face = cube.get_face_colors('D')
        white_color = StandardColors.WHITE
        edge_positions = [(0, 1), (1, 0), (1, 2), (2, 1)]
        return all(bottom_face[row][col] == white_color for row, col in edge_positions)
    
    def _is_f2l_complete(self, cube: Cube) -> bool:
        """Check if F2L is complete."""
        # Check if first two layers are solved
        bottom_face = cube.get_face_colors('D')
        white_color = StandardColors.WHITE
        
        # Bottom must be all white
        if not all(color == white_color for row in bottom_face for color in row):
            return False
        
        # Middle layer must match centers
        for face in ['F', 'R', 'B', 'L']:
            face_colors = cube.get_face_colors(face)
            center_color = face_colors[1][1]
            
            # Check bottom two rows
            for row in [1, 2]:
                for col in range(3):
                    if face_colors[row][col] != center_color:
                        return False
        
        return True
    
    def _is_oll_solved(self, cube: Cube) -> bool:
        """Check if OLL is solved."""
        top_face = cube.get_face_colors('U')
        yellow_color = StandardColors.YELLOW
        return all(color == yellow_color for row in top_face for color in row)
    
    def _is_yellow_cross_formed(self, cube: Cube) -> bool:
        """Check if yellow cross is formed."""
        top_face = cube.get_face_colors('U')
        yellow_color = StandardColors.YELLOW
        edge_positions = [(0, 1), (1, 0), (1, 2), (2, 1)]
        return all(top_face[row][col] == yellow_color for row, col in edge_positions)
    
    def _count_cross_edges_correct(self, cube: Cube) -> int:
        """Count how many cross edges are correctly placed."""
        bottom_face = cube.get_face_colors('D')
        white_color = StandardColors.WHITE
        edge_positions = [(0, 1), (1, 0), (1, 2), (2, 1)]
        return sum(1 for row, col in edge_positions if bottom_face[row][col] == white_color)