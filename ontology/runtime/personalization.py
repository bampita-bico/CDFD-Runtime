from typing import Dict, Optional

class PersonalizationManager:
    """Manages user-specific relationship weight multipliers."""
    def __init__(self):
        # Mapping: user_id -> rel_id -> multiplier
        self.modifiers: Dict[str, Dict[str, float]] = {}
        
    def set_modifier(self, user_id: str, rel_id: str, multiplier: float):
        if user_id not in self.modifiers:
            self.modifiers[user_id] = {}
        self.modifiers[user_id][rel_id] = multiplier

    def get_multiplier(self, user_id: Optional[str], rel_id: str) -> float:
        if not user_id or user_id not in self.modifiers:
            return 1.0
        return self.modifiers[user_id].get(rel_id, 1.0)
