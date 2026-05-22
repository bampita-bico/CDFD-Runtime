from ontology.meta.entity import Entity
from ontology.meta.process import Process
from ontology.meta.flow import Flow
from ontology.meta.constraint import Constraint

class NeuroscienceProcess(Process):
    """
    Models nervous-system signaling using CDFD.

    Nociception is represented as high signal flow (Phi) through a neural
    pathway with finite processing capacity (C). This module is a conceptual
    research model for signal-load and constraint-bandwidth experiments; it is
    not medical advice, a treatment protocol, or a claim of analgesic efficacy.
    """
    def __init__(self, name="Neuroscience_Signal_Load"):
        super().__init__(name)

    def define_neural_pathway(self, node_id: str, capacity: float) -> Entity:
        nerve = Entity(node_id, f"Nerve_Pathway_{node_id}", base_s=1.0, base_ms=1.0)
        nerve.add_constraint(Constraint("baseline_capacity", node_id, capacity))
        self.register(nerve)
        return nerve

    def trigger_pain(self, nerve: Entity, pain_stimulus: float):
        """Inject a nociceptive signal into the modeled pathway."""
        nerve.add_in_flow(Flow("pain_signal", "tissue_damage", nerve.node_id, pain_stimulus))

    def apply_capacity_support(self, nerve: Entity, support_capacity: float | None = None):
        """
        Add modeled capacity support and return the resulting regime.

        This is a simulation primitive only. Real nervous-system modulation
        would require clinical validation and safety review.
        """
        total_phi = sum(f.intensity for f in nerve.in_flows)
        if total_phi == 0:
            total_phi = 1.0

        adaptive_c = Constraint(
            "modeled_capacity_support",
            nerve.node_id,
            support_capacity if support_capacity is not None else total_phi,
        )
        nerve.constraints.append(adaptive_c)

        psi_s = nerve.calculate_psi_s()
        return {
            "node_id": nerve.node_id,
            "psi_s": psi_s,
            "status": "modeled_capacity_support_applied",
        }
