import sys
from TokenType import TokenType
from Token import Token

class ParseError(Exception):
    """
    Exception caused in the Parser
    """
    pass

class RuntimeError(Exception):
    """
    Exception caused at runtime in the Interpreter
    """

    def __init__(self, token: Token, message: str) -> None:
        self.token: Token = token
        self.message: str = message
        super().__init__(self.message)


class ErrorManager:
    """
    Used to store whether the Lox runtime has seen an error and provides reporting methods
    """

    def __init__(self):
        self.hadError: bool = False

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

    def runtimeError(self, error: RuntimeError):
        print(f"[line {error.token.line}] {error.message}", file=sys.stderr)
        self.hadError = True
