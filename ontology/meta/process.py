from typing import List
from .entity import Entity

class Process:
    """
    A Process governs the temporal evolution of Entities over time,
    dynamically altering S, M_s, Phi, or C according to CDFD rules.
    """
    def __init__(self, name: str):
        self.name = name
        self.entities: List[Entity] = []

    def register(self, entity: Entity):
        self.entities.append(entity)

    def step(self, dt: float):
        """
        Advances the process by timestep dt.
        To be overridden by domain-specific processes (e.g., Metabolism, MarketDynamics).
        """
        pass
