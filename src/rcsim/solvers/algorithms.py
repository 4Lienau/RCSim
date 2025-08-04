"""Algorithm database for common cube solving algorithms."""

from typing import Dict, List, Optional
from dataclasses import dataclass

from ..cube.moves import MoveSequence


@dataclass
class Algorithm:
    """Represents a solving algorithm/case."""
    name: str
    moves: MoveSequence
    description: str
    category: str
    difficulty: int  # 1-5 scale
    frequency: float  # How often this case appears (0-1)
    
    def __str__(self) -> str:
        return f"{self.name}: {self.moves}"


class AlgorithmDatabase:
    """Database of common solving algorithms."""
    
    def __init__(self):
        """Initialize the algorithm database."""
        self.algorithms: Dict[str, Dict[str, Algorithm]] = {}
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize the database with common algorithms."""
        # OLL (Orient Last Layer) algorithms
        self._add_oll_algorithms()
        
        # PLL (Permute Last Layer) algorithms  
        self._add_pll_algorithms()
        
        # F2L (First Two Layers) algorithms
        self._add_f2l_algorithms()
        
        # Common sequences
        self._add_common_sequences()
    
    def _add_oll_algorithms(self) -> None:
        """Add OLL algorithms to the database."""
        oll_algs = [
            # Dot cases (simplified to use only basic moves)
            Algorithm("OLL 1", MoveSequence.parse("R U2 R2 F R F' U2 R' F R F'"),
                     "Dot case - all edges flipped", "OLL", 3, 0.02),
            Algorithm("OLL 2", MoveSequence.parse("F R U R' U' F' R U R' U' R U R' U' F R U R' U' F'"),
                     "Dot case - alternate (simplified)", "OLL", 4, 0.02),
            
            # Cross cases
            Algorithm("OLL 21", MoveSequence.parse("R U R' U R U' R' U R U2 R'"),
                     "Cross case - H shape", "OLL", 2, 0.04),
            Algorithm("OLL 22", MoveSequence.parse("R U2 R2 U' R2 U' R2 U2 R"),
                     "Cross case - Pi shape", "OLL", 2, 0.04),
            
            # Line cases  
            Algorithm("OLL 45", MoveSequence.parse("F R U R' U' F'"),
                     "Line case - simple", "OLL", 1, 0.08),
            Algorithm("OLL 46", MoveSequence.parse("R' U' R' F R F' U R"),
                     "Line case - alternate", "OLL", 2, 0.08),
            
            # L cases (simplified)
            Algorithm("OLL 47", MoveSequence.parse("F' L' U' L U F"),
                     "L shape case (simplified)", "OLL", 2, 0.04),
            Algorithm("OLL 48", MoveSequence.parse("F R U R' U' F'"),
                     "L shape case - mirror (simplified)", "OLL", 2, 0.04),
            
            # T cases
            Algorithm("OLL 33", MoveSequence.parse("R U R' U' R' F R F'"),
                     "T shape case", "OLL", 2, 0.04),
            Algorithm("OLL 34", MoveSequence.parse("R U R2 U' R' F R U R U' F'"),
                     "T shape case - alternate", "OLL", 3, 0.04),
        ]
        
        self.algorithms["OLL"] = {alg.name: alg for alg in oll_algs}
    
    def _add_pll_algorithms(self) -> None:
        """Add PLL algorithms to the database."""
        pll_algs = [
            # Adjacent corner swaps
            Algorithm("T-Perm", MoveSequence.parse("R U R' F' R U R' U' R' F R2 U' R'"),
                     "T permutation - adjacent corners", "PLL", 2, 0.08),
            Algorithm("J-Perm A", MoveSequence.parse("R' U L' U2 R U' R' U2 R L U'"),
                     "J permutation - adjacent corners", "PLL", 3, 0.08),
            Algorithm("J-Perm B", MoveSequence.parse("R U R' F' R U R' U' R' F R2 U' R'"),
                     "J permutation - adjacent corners", "PLL", 3, 0.08),
            
            # Diagonal corner swaps
            Algorithm("Y-Perm", MoveSequence.parse("F R U' R' U' R U R' F' R U R' U' R' F R F'"),
                     "Y permutation - diagonal corners", "PLL", 4, 0.04),
            Algorithm("V-Perm", MoveSequence.parse("R' U R' U' B' R' B2 U' R' U R' B R B"),
                     "V permutation - diagonal corners (no rotation)", "PLL", 4, 0.04),
            
            # Edge cycles
            Algorithm("U-Perm A", MoveSequence.parse("R U' R U R U R U' R' U' R2"),
                     "U permutation - 3-cycle edges", "PLL", 2, 0.08),
            Algorithm("U-Perm B", MoveSequence.parse("R2 U R U R' U' R' U' R' U R'"),
                     "U permutation - 3-cycle edges", "PLL", 2, 0.08),
            Algorithm("Z-Perm", MoveSequence.parse("R' U' R U' R U R U' R' U R U R2 U' R'"),
                     "Z permutation - opposite edge swap (simplified)", "PLL", 4, 0.04),
            Algorithm("H-Perm", MoveSequence.parse("R U R' U R U' R D R' U' R D' R' U2 R'"),
                     "H permutation - opposite edge swap (simplified)", "PLL", 4, 0.04),
            
            # Corner + edge cycles
            Algorithm("A-Perm A", MoveSequence.parse("R' F R' B2 R F' R' B2 R2"),
                     "A permutation - 3-cycle", "PLL", 2, 0.08),
            Algorithm("A-Perm B", MoveSequence.parse("R B' R F2 R' B R F2 R2"),
                     "A permutation - 3-cycle", "PLL", 2, 0.08),
        ]
        
        self.algorithms["PLL"] = {alg.name: alg for alg in pll_algs}
    
    def _add_f2l_algorithms(self) -> None:
        """Add F2L algorithms to the database."""
        f2l_algs = [
            # Basic F2L cases
            Algorithm("F2L-1", MoveSequence.parse("R U' R'"),
                     "Basic F2L - corner above slot, edge in place", "F2L", 1, 0.1),
            Algorithm("F2L-2", MoveSequence.parse("F R F'"),
                     "Basic F2L - edge above slot, corner in place", "F2L", 1, 0.1),
            Algorithm("F2L-3", MoveSequence.parse("R U R' U' R U R'"),
                     "Basic F2L - both pieces above", "F2L", 1, 0.05),
            
            # Common F2L cases
            Algorithm("F2L-27", MoveSequence.parse("R U2 R' U' R U R'"),
                     "F2L case 27 - corner and edge separated", "F2L", 2, 0.03),
            Algorithm("F2L-32", MoveSequence.parse("R U R' U2 R U' R'"),
                     "F2L case 32 - edge flipped", "F2L", 2, 0.03),
            Algorithm("F2L-37", MoveSequence.parse("R U' R' U R U' R'"),
                     "F2L case 37 - corner twisted", "F2L", 2, 0.03),
        ]
        
        self.algorithms["F2L"] = {alg.name: alg for alg in f2l_algs}
    
    def _add_common_sequences(self) -> None:
        """Add common sequences and triggers."""
        common_algs = [
            # Sexy move and variations
            Algorithm("Sexy Move", MoveSequence.parse("R U R' U'"),
                     "Most common trigger sequence", "Common", 1, 1.0),
            Algorithm("Sledgehammer", MoveSequence.parse("R' F R F'"),
                     "Another common trigger", "Common", 1, 0.8),
            
            # Sune family
            Algorithm("Sune", MoveSequence.parse("R U R' U R U2 R'"),
                     "Classic Sune sequence", "Common", 1, 0.6),
            Algorithm("Anti-Sune", MoveSequence.parse("R U2 R' U' R U' R'"),
                     "Reverse Sune sequence", "Common", 1, 0.6),
            
            # Niklas
            Algorithm("Niklas", MoveSequence.parse("R U' L' U R' U' L"),
                     "Niklas commutator", "Common", 2, 0.3),
            
            # 4-move triggers
            Algorithm("Right Hand", MoveSequence.parse("R U R' U'"),
                     "Right hand trigger", "Trigger", 1, 1.0),
            Algorithm("Left Hand", MoveSequence.parse("L' U' L U"),
                     "Left hand trigger", "Trigger", 1, 0.8),
        ]
        
        self.algorithms["Common"] = {alg.name: alg for alg in common_algs}
    
    def get_algorithm(self, category: str, name: str) -> Optional[Algorithm]:
        """Get a specific algorithm by category and name.
        
        Parameters
        ----------
        category : str
            Algorithm category (OLL, PLL, F2L, Common)
        name : str
            Algorithm name
            
        Returns
        -------
        Optional[Algorithm]
            Algorithm if found, None otherwise
        """
        return self.algorithms.get(category, {}).get(name)
    
    def get_algorithms_by_category(self, category: str) -> List[Algorithm]:
        """Get all algorithms in a category.
        
        Parameters
        ----------
        category : str
            Algorithm category
            
        Returns
        -------
        List[Algorithm]
            List of algorithms in category
        """
        return list(self.algorithms.get(category, {}).values())
    
    def search_algorithms(self, query: str) -> List[Algorithm]:
        """Search for algorithms by name or description.
        
        Parameters
        ----------
        query : str
            Search query
            
        Returns
        -------
        List[Algorithm]
            Matching algorithms
        """
        results = []
        query_lower = query.lower()
        
        for category_algs in self.algorithms.values():
            for alg in category_algs.values():
                if (query_lower in alg.name.lower() or 
                    query_lower in alg.description.lower()):
                    results.append(alg)
        
        return sorted(results, key=lambda x: x.frequency, reverse=True)
    
    def get_all_categories(self) -> List[str]:
        """Get all available algorithm categories.
        
        Returns
        -------
        List[str]
            List of category names
        """
        return list(self.algorithms.keys())
    
    def get_algorithm_count(self) -> Dict[str, int]:
        """Get count of algorithms by category.
        
        Returns
        -------
        Dict[str, int]
            Count by category
        """
        return {cat: len(algs) for cat, algs in self.algorithms.items()}
    
    def add_custom_algorithm(self, algorithm: Algorithm) -> None:
        """Add a custom algorithm to the database.
        
        Parameters
        ----------
        algorithm : Algorithm
            Algorithm to add
        """
        if algorithm.category not in self.algorithms:
            self.algorithms[algorithm.category] = {}
        
        self.algorithms[algorithm.category][algorithm.name] = algorithm