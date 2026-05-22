from typing import Dict, List, Optional
from ontology.meta.entity import Entity
from ontology.meta.flow import Flow
from ontology.meta.constraint import Constraint

class OntologyGraph:
    """
    Manages the overall network of Entities, Flows, and Constraints.
    Provides graph mechanics for semantic reasoning over the CDFD simulation.
    """
    def __init__(self):
        self.nodes: Dict[str, Entity] = {}
        self.flows: Dict[str, Flow] = {}
        self.constraints: Dict[str, Constraint] = {}

    def add_entity(self, entity: Entity):
        self.nodes[entity.node_id] = entity

    def add_flow(self, flow: Flow):
        self.flows[flow.flow_id] = flow
        
        # Link to source and target
        if flow.source_id in self.nodes:
            self.nodes[flow.source_id].add_out_flow(flow)
        if flow.target_id in self.nodes:
            self.nodes[flow.target_id].add_in_flow(flow)

    def add_constraint(self, constraint: Constraint):
        self.constraints[constraint.constraint_id] = constraint
        if constraint.target_id in self.nodes:
            self.nodes[constraint.target_id].add_constraint(constraint)

    def get_entity(self, node_id: str) -> Optional[Entity]:
        return self.nodes.get(node_id)
