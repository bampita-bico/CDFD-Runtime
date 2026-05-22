from abc import ABC, abstractmethod


class DomainAdapter(ABC):
    @abstractmethod
    def map_to_engine(self, data):
        """Convert real-world data → (phi scalar, C scalar)."""

    def evolve(self, state, dt=0.01):
        """Apply domain-specific rules each step (optional override)."""

    @abstractmethod
    def interpret(self, state):
        """Convert engine state → human-readable result string."""
