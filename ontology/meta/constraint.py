from typing import Dict, Any, List, Optional
from ontology.meta.relationship import Relationship
from ontology.meta.evidence import EvidenceScale

class Constraint(Relationship):
    """
    Represents the resistance or friction (C) applied to a target entity.
    """
    def __init__(self, constraint_id: str, target_id: str, magnitude: float, source_id: str = "ENVIRONMENT",
                 confidence: float = 1.0, evidence: EvidenceScale = EvidenceScale.MODERATE, **kwargs):
        super().__init__(constraint_id, source_id, target_id, weight=magnitude,
                         confidence=confidence, evidence=evidence)
        
    @property
    def constraint_id(self): return self.id
    
    @property
    def magnitude(self): return self.weight
    @magnitude.setter
    def magnitude(self, val): self.weight = val
    
    def update_magnitude(self, new_value: float, source: str = "manual", timestamp: Optional[str] = None):
        self.update_weight(new_value, source, timestamp)
