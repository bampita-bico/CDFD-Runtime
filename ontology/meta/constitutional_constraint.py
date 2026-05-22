from .constraint import Constraint

class ConstitutionalConstraint(Constraint):
    """
    (Claude Mythos: Constitutional AI)
    An immutable, root-level constraint. Unlike normal physical constraints (C)
    which can be broken by enough flux (Phi), a Constitutional Constraint enforces 
    a hard mathematical floor. It ensures the Engine remains 'Aligned' and prevents
    rogue entities from dividing by zero or causing fatal systemic collapse.
    """
    def __init__(self, target_id: str, absolute_minimum: float):
        super().__init__("CONSTITUTIONAL_ALIGNMENT", target_id, absolute_minimum)
        self.access_control = ["ROOT_ONLY"]
        self.is_immutable = True

    def update_magnitude(self, new_value: float, source: str = "manual", timestamp=None):
        """Overrides normal update. Cannot be weakened below its constitutional minimum."""
        if new_value < self.magnitude:
            # Reject weakening of the constitution
            self.provenance["lineage"].append({
                "action": "rejected_update",
                "attempted_value": new_value,
                "reason": "Violates Constitutional Alignment",
                "source": source,
                "timestamp": timestamp
            })
        else:
            super().update_magnitude(new_value, source, timestamp)
