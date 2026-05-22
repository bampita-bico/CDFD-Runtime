from ontology.meta.entity import Entity
from ontology.meta.process import Process
from ontology.meta.flow import Flow
from ontology.meta.constraint import Constraint

class AtmosphericCirculationProcess(Process):
    """
    Earth Systems - Atmospheric Flow Dynamics.
    """
    def __init__(self, name="Earth_Atmosphere"):
        super().__init__(name)

    def add_air_mass(self, mass_id: str, name: str, heat_capacity: float) -> Entity:
        """
        S = Heat Capacity / Responsiveness of the air mass.
        """
        mass = Entity(mass_id, name, base_s=heat_capacity, base_ms=1.0)
        self.register(mass)
        return mass

    def thermal_flux(self, source_id: str, target_mass: Entity, intensity: float):
        """
        Phi = Solar insolation or thermal heat flux.
        """
        f = Flow(f"heat_{target_mass.node_id}", source_id, target_mass.node_id, intensity, "thermal")
        target_mass.add_in_flow(f)
        return f

    def topographical_constraint(self, mass: Entity, friction: float):
        """
        C = Mountains, Coriolis effect, or ground friction.
        """
        c = Constraint(f"topo_{mass.node_id}", mass.node_id, friction, is_chronic=True)
        mass.add_constraint(c)
        return c
