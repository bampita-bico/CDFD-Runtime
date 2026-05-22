from typing import Dict, Any, List, Optional
from ontology.meta.evidence import EvidenceScale

class Relationship:
    def __init__(self, rel_id: str, source_id: str, target_id: str, weight: float,
                 confidence: float = 1.0, evidence: EvidenceScale = EvidenceScale.MODERATE):
        self.id = rel_id
        self.source_id = source_id
        self.target_id = target_id
        self.weight = weight
        self.confidence = confidence
        self.evidence = evidence
        
        self.provenance: Dict[str, Any] = {
            "source": "system_init",
            "timestamp": None,
            "lineage": []
        }
        self.access_control: List[str] = ["PUBLIC"]

    def update_weight(self, new_value: float, source: str = "manual", timestamp: Optional[str] = None):
        self.provenance["lineage"].append({
            "old_weight": self.weight,
            "new_weight": new_value,
            "source": source,
            "timestamp": timestamp
        })
        self.weight = new_value
        self.provenance["source"] = source
        self.provenance["timestamp"] = timestamp

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source_id,
            "target": self.target_id,
            "weight": self.weight,
            "confidence": self.confidence,
            "evidence": int(self.evidence),
            "provenance": self.provenance,
            "access_control": self.access_control
        }
