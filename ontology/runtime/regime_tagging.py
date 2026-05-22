from typing import Dict
from ontology.runtime.graph_mechanics import OntologyGraph

class RegimeTagger:
    """
    Monitors the semantic graph and tags Entities with their CDFD Regime (Decay, Stable, Growth).
    Useful for triggering systemic alerts (e.g. disease onset, economic collapse).
    """
    def __init__(self, graph: OntologyGraph):
        self.graph = graph

    def tag_all(self) -> Dict[str, str]:
        """
        Evaluates Psi_s for every node and returns a mapping of node_id -> Regime.
        """
        tags = {}
        for node_id, entity in self.graph.nodes.items():
            tags[node_id] = entity.get_regime()
        return tags

    def detect_anomalies(self) -> Dict[str, str]:
        """
        Returns only nodes that are in Decay/Recession due to high constraint or low flow.
        """
        tags = self.tag_all()
        return {nid: reg for nid, reg in tags.items() if reg == "Decay/Recession"}
