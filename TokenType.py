from enum import Enum, auto

class TokenType(Enum):
    """ Enum for each token type """

    # Single character tokens
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
    STAR = auto()
    AMPER = auto()
    BAR = auto()
    TILDE = auto()
    CARET = auto()

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
    STAR_STAR = auto()

    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    INT = auto()
    FLOAT = auto()

    # Keywords
    AND = auto()
    CLASS = auto()
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

    # Other
    EOF = auto()
