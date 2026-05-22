from enum import Enum, auto


class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COLON = auto()
    COMMA = auto()
    EOF = auto()


KEYWORDS = {
    "DEFINE", "SET", "LINK", "RUN", "SCENARIO", "OBSERVE",
    "SWEEP", "DISCOVER", "PATIENT", "APPLY", "TO", "MODIFY",
    "Engine", "Field", "Constraint",
    "ANALYZE", "BIFURCATE", "EMERGE", "ATTRACTOR", "INFOFLOW",
    "VACUUM", "KNOT", "SPAWN", "RESOLVE", "SPECTRUM", "Vacuum", "Knot", "Spectrum",
    "SYSTEM", "RULE", "IF", "ACTION",
}


class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"
