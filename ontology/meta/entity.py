from typing import List, Dict, Any, Optional

class Entity:
    """
    A foundational node in the Universal Ontology.
    An Entity acts as an 'Active Surface' capable of computing its own CDFD Life Number/Regime (Psi_s).
    """
    def __init__(self, node_id: str, name: str, base_s: float = 1.0, base_ms: float = 1.0):
        self.node_id = node_id
        self.name = name

        # CDFD Surface Parameters
        self.S = base_s        # Surface Responsiveness
        self.M_s = base_ms     # Surface Memory (if locked, causes chronic conditions)

        # Connections
        self.in_flows = []
        self.out_flows = []
        self.constraints = []

        # Semantic mapping
        self.metadata: Dict[str, Any] = {}

        # Enterprise Features: Provenance & Security
        self.provenance: Dict[str, Any] = {
            "source": "system_init",
            "timestamp": None,
            "lineage": []
        }
        self.access_control: List[str] = ["PUBLIC"] # CBAC/ABAC tags

    def update_s(self, value: float, source: str = "manual", timestamp: Optional[str] = None):
        self._record_provenance("S", self.S, value, source, timestamp)
        self.S = value

    def update_ms(self, value: float, source: str = "manual", timestamp: Optional[str] = None):
        self._record_provenance("M_s", self.M_s, value, source, timestamp)
        self.M_s = value

    def _record_provenance(self, prop: str, old_val: Any, new_val: Any, source: str, timestamp: Optional[str]):
        self.provenance["lineage"].append({
            "property": prop,
            "old_value": old_val,
            "new_value": new_val,
            "source": source,
            "timestamp": timestamp
        })
        self.provenance["source"] = source
        self.provenance["timestamp"] = timestamp

    def add_in_flow(self, flow):
        self.in_flows.append(flow)

    def add_out_flow(self, flow):
        self.out_flows.append(flow)

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def calculate_psi_s(self) -> float:
        """
        Calculates the Adaptive Ratio: Psi_s = (Phi / C) * S * M_s
        """
        total_phi = sum(f.intensity for f in self.in_flows)
        if total_phi == 0:
            return 0.0

        total_c = sum(c.magnitude for c in self.constraints)
        if total_c <= 0:
            total_c = 1e-6  # Free flow regime, prevent division by zero

        return (total_phi / total_c) * self.S * self.M_s

    def get_regime(self) -> str:
        """
        Maps Psi_s to qualitative ontological regimes.
        """
        psi_s = self.calculate_psi_s()
        if psi_s < 1.0:
            return "Decay/Recession"
        elif abs(psi_s - 1.0) < 0.1:
            return "Near-Critical/Proto-Stable"
        else:
            return "Sustained/Growth"

    def to_dict(self) -> dict:
        return {
            "id": self.node_id,
            "name": self.name,
            "S": self.S,
            "M_s": self.M_s,
            "psi_s": self.calculate_psi_s(),
            "regime": self.get_regime(),
            "provenance": self.provenance,
            "access_control": self.access_control
        }
