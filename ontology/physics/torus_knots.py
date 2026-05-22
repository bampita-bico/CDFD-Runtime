from ontology.meta.entity import Entity
from ontology.meta.process import Process
from ontology.meta.flow import Flow
from ontology.meta.constraint import Constraint

class TorusKnotProcess(Process):
    """
    Maps the topological Torus Knot (Z3) symmetry to the Universal Ontology.
    Knots act as localized, chronic constraints (M_s locking) on the chiral flux,
    giving rise to emergent particle mass.
    """
    def __init__(self, name="TorusKnot_Dynamics"):
        super().__init__(name)

    def spawn_knot(self, parent_vacuum: Entity, knot_type: str = "lepton_mode") -> Entity:
        """
        A topological knot emerges from the vacuum surface as a distinct Entity.
        """
        knot = Entity(f"knot_{knot_type}", f"Torus Knot ({knot_type})", base_s=0.5, base_ms=2.0)
        knot.metadata["knot_type"] = knot_type
        self.register(knot)
        
        # The knot inherently draws chiral flux from the vacuum
        f = Flow(f"vortex_{knot.node_id}", parent_vacuum.node_id, knot.node_id, intensity=1.0, flow_type="vortex_coupling")
        knot.add_in_flow(f)
        parent_vacuum.add_out_flow(f)
        
        return knot

    def stabilize_mass(self, knot: Entity, mass_energy: float):
        """
        The knot's topology provides a rigid constraint against decay, equivalent to particle mass.
        """
        c = Constraint(f"mass_{knot.node_id}", knot.node_id, magnitude=mass_energy, is_chronic=True)
        knot.add_constraint(c)
        return c
