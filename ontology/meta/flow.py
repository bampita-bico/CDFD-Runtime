from typing import Dict, Any, List, Optional
from ontology.meta.relationship import Relationship
from ontology.meta.evidence import EvidenceScale

class Flow(Relationship):
    """
    Represents the physical or abstract transfer of intensity (Phi) between entities.
    """
    def __init__(self, flow_id: str, source_id: str, target_id: str, intensity: float,
                 confidence: float = 1.0, evidence: EvidenceScale = EvidenceScale.MODERATE):
        super().__init__(flow_id, source_id, target_id, weight=intensity, 
                         confidence=confidence, evidence=evidence)
    
    @property
    def flow_id(self): return self.id
    
    @property
    def intensity(self): return self.weight
    @intensity.setter
    def intensity(self, val): self.weight = val
    
    def update_intensity(self, new_value: float, source: str = "manual", timestamp: Optional[str] = None):
        self.update_weight(new_value, source, timestamp)
