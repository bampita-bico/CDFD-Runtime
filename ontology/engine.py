import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

from ontology.meta.process import Process
from ontology.runtime.graph_mechanics import OntologyGraph
from ontology.runtime.personalization import PersonalizationManager
from ontology.runtime.regime_tagging import RegimeTagger
from ontology.runtime.relationship_prop import RelationshipPropagator

if TYPE_CHECKING:
    from engine.state import State

logger = logging.getLogger(__name__)


class CDFLOntologyEngine:
    """Minimal semantic layer for CDFL bookkeeping labels."""

    _registry: Dict[str, type] = {}

    def __init__(self) -> None:
        self.graph = OntologyGraph()
        self.p13n_manager = PersonalizationManager()
        self.propagator = RelationshipPropagator(self.graph, self.p13n_manager)
        self.tagger = RegimeTagger(self.graph)
        self.step_count = 0
        self.active_processes: Dict[str, Process] = {}

    @classmethod
    def build_registry(cls) -> None:
        """Legacy domain ontology modules were archived; keep an empty registry."""
        cls._registry = {}
        logger.info("[Ontology] Slim runtime registry active (0 archived domain processes).")

    @classmethod
    def register_discovered_type(cls, name: str, process_class: type) -> None:
        cls._registry[name] = process_class
        logger.info("[Ontology Engine] Registered schema: %s", name)

    def instantiate_domain(self, domain_key: str) -> Optional[Process]:
        if domain_key in self._registry:
            if domain_key not in self.active_processes:
                process_class = self._registry[domain_key]
                self.active_processes[domain_key] = process_class()
            return self.active_processes[domain_key]
        return None

    def evaluate_semantic_node(
        self,
        domain_key: str,
        node_id: str,
        phi: float,
        c: float,
        s: float = 1.0,
        ms: float = 1.0,
    ) -> str:
        process = self.instantiate_domain(domain_key)
        if process and getattr(process, "is_discovered", False):
            regime_prefix = f"*[DISCOVERED]* {process.name} -> "
        else:
            regime_prefix = f"[{domain_key.upper()}] Node '{node_id}' evaluating -> "

        c = max(c, 1e-6)
        psi_s = (phi / c) * s * ms

        if psi_s < 1.0:
            regime = "Decay/Necrosis/Collapse"
        elif abs(psi_s - 1.0) < 0.1:
            regime = "Stable/Critical Equilibrium"
        else:
            regime = "Over-flux/Growth/Hyperinflation"

        return regime_prefix + regime

    def sync_from_state(self, numeric_state: "State") -> None:
        _ = numeric_state

    def step(self, dt: float, numeric_state: "State"):
        self.step_count += 1
        self.sync_from_state(numeric_state)
        return self.tagger.detect_anomalies()
