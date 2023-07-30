from enum import Enum, auto

class TokenType(Enum):

    # Single-character tokens
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto()
    SLASH = auto()
    AMPERSAND = auto()
    BAR = auto()
    CARROT = auto()
    QUESTION = auto()
    COLON = auto()

    # One or two character tokens
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    GREATER_GREATER = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    LESS_LESS = auto()
    STAR = auto()
    STAR_STAR = auto()

    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    # Keywords
    AND = auto()
    BREAK = auto()
    CLASS = auto()
    CONTINUE = auto()
    ELSE = auto()
    FALSE = auto()
    FUN = auto()
    FOR = auto()
    IF = auto()
    NIL = auto()
    OR = auto()
    PRINT = auto()
    RETURN = auto()
    SUPER = auto()
    THIS = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()

    EOF = auto()
