import re
from dsl.tokens import Token, TokenType, KEYWORDS

_PATTERNS = [
    (r'#[^\r\n]*',          None),
    (r'"[^"]*"',           TokenType.STRING),
    (r"'[^']*'",           TokenType.STRING),
    (r'\d+\.\d+',          TokenType.NUMBER),
    (r'\d+',               TokenType.NUMBER),
    (r'\{',                TokenType.LBRACE),
    (r'\}',                TokenType.RBRACE),
    (r'\[',                TokenType.LBRACKET),
    (r'\]',                TokenType.RBRACKET),
    (r':',                 TokenType.COLON),
    (r',',                 TokenType.COMMA),
    (r'[A-Za-zΦΨα-ω_][\w\.]*', TokenType.IDENTIFIER),
]

_MASTER = re.compile(
    '|'.join(f'(?P<T{i}>{p})' for i, (p, _) in enumerate(_PATTERNS))
)
_TYPE_MAP = {f'T{i}': t for i, (_, t) in enumerate(_PATTERNS)}


def tokenize(code):
    tokens = []
    for m in _MASTER.finditer(code):
        group = m.lastgroup
        value = m.group()
        ttype = _TYPE_MAP[group]
        if ttype is None:
            continue
        if ttype == TokenType.IDENTIFIER and value in KEYWORDS:
            ttype = TokenType.KEYWORD
        if ttype == TokenType.NUMBER:
            value = float(value)
        elif ttype == TokenType.STRING:
            value = value[1:-1]
        tokens.append(Token(ttype, value))
    tokens.append(Token(TokenType.EOF, None))
    return tokens
