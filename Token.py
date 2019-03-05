from TokenType import TokenType

class Token:
    """ Stores a token """

    def __init__(self, tokenType: TokenType, lexeme: str, literal: object, line: int):
        self.type = tokenType
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __repr__(self) -> str:
        return f"Token({self.type},{repr(self.lexeme)},{repr(self.literal)},{self.line})"
