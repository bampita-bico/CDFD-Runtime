import logging
from ontology.runtime.graph_mechanics import OntologyGraph
from ontology.runtime.personalization import PersonalizationManager

logger = logging.getLogger(__name__)

class RelationshipPropagator:
    """
    Handles how pressure, flow intensity, and constraints cascade through the Ontology
    using Meaning-Blind Mechanics (Layer 1).
    """
    def __init__(self, graph: OntologyGraph, p13n_manager: PersonalizationManager = None):
        self.graph = graph
        self.p13n_manager = p13n_manager or PersonalizationManager()

    def _get_regime_factor(self, node):
        if hasattr(node, "regime"):
            # Can be string or method
            r = node.regime() if callable(node.regime) else node.regime
            if r == "overload": return 1.2
            if r == "constrained": return 0.8
        return 1.0

    def propagate_flow_change(self, start_node_id: str, phi_delta: float, 
                              decay_factor: float = 0.5, user_id: str = None):
        """
        Propagates a change in flow using the advanced equation:
        Impact = SourceChange * Weight * Confidence * RegimeFactor * DecayFactor * PersonalModifier
        """
        start_node = self.graph.get_entity(start_node_id)
        if not start_node:
            return

        # Simple BFS cascade
        queue = [(start_node, phi_delta)]
        visited = set()

        while queue:
            current, delta = queue.pop(0)
            if current.node_id in visited:
                continue
            visited.add(current.node_id)

            if not getattr(current, 'out_flows', None):
                continue
            
            # Layer 1: Meaning-Blind Regime Factor
            regime_factor = self._get_regime_factor(current)
            
            for flow in current.out_flows:
                # Layer 2: Meta-Ontology attributes (fallback for legacy flows)
                weight = getattr(flow, 'weight', getattr(flow, 'intensity', 1.0))
                confidence = getattr(flow, 'confidence', 1.0)
                rel_id = getattr(flow, 'id', getattr(flow, 'flow_id', None))
                
                # Layer 5: Personalization
                personal_mod = self.p13n_manager.get_multiplier(user_id, rel_id)
                
                # Advanced Propagation Equation
                impact = delta * weight * confidence * regime_factor * decay_factor * personal_mod
                
                if hasattr(flow, 'weight'):
                    flow.weight += impact
                elif hasattr(flow, 'intensity'):
                    flow.intensity += impact

                target_node = self.graph.get_entity(getattr(flow, 'target_id', getattr(flow, 'target', None)))
                if target_node and target_node.node_id not in visited:
                    if abs(impact) > 1e-4:
                        queue.append((target_node, impact))
