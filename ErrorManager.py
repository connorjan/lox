from TokenType import TokenType
from Token import Token

class ErrorManager:

    def __init__(self):
        self.hadError = False

    def report(self, line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error {where}: {message}")

    def scanError(self, line: int, message: str) -> None:
        self.hadError = True
        self.report(line, "", message)

    def parseError(self, token: Token, message: str) -> None:
        self.hadError = True
        if token.type == TokenType.EOF:
            self.report(token.line, "at end", message)
        else:
            self.report(token.line, f"at \"{token.lexeme}\"", message)
