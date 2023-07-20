from TokenType import TokenType

class Token:

    def __init__(self, type_: TokenType, lexeme: str, literal: any, line: int) -> None:
        self.type_: TokenType = type_
        self.lexeme: str = lexeme
        self.literal: any = literal
        self.line: int = line

    def __str__(self) -> str:
        return f"Type={self.type_} Lexeme={self.lexeme} Literal={self.literal}"
