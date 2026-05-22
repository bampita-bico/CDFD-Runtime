from ontology.meta.entity import Entity
from ontology.meta.process import Process
from ontology.meta.flow import Flow
from ontology.meta.constraint import Constraint

class ElectricalGridProcess(Process):
    """
    Engineered Systems - Power Grid Flow.
    """
    def __init__(self, name="Engineered_PowerGrid"):
        super().__init__(name)

    def add_substation(self, station_id: str, capacity: float) -> Entity:
        """
        S = Transformer/Substation capacity.
        """
        station = Entity(station_id, f"Substation {station_id}", base_s=capacity, base_ms=1.0)
        self.register(station)
        return station

    def inject_power(self, source_id: str, target: Entity, mw: float):
        """
        Phi = Megawatts of active power.
        """
        f = Flow(f"pwr_{source_id}_{target.node_id}", source_id, target.node_id, mw, "power")
        target.add_in_flow(f)
        return f

    def line_impedance(self, target: Entity, impedance: float):
        """
        C = Electrical impedance / resistance of transmission lines.
        """
        c = Constraint(f"imp_{target.node_id}", target.node_id, impedance, is_chronic=True)
        target.add_constraint(c)
        return c
