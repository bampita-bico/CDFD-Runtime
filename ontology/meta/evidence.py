from enum import IntEnum

class EvidenceScale(IntEnum):
    SPECULATIVE = 0
    THEORETICAL = 1
    WEAK_EMPIRICAL = 2
    MODERATE = 3
    STRONG_EMPIRICAL = 4
    VALIDATED = 5
    DETERMINISTIC = 6
