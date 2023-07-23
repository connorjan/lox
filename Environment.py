from ErrorManager import *
from Token import Token

class Environment:

    def __init__(self, errorManager: ErrorManager) -> None:
        self.errorManager = errorManager
        self.values: dict[str, any] = {}

    def define(self, name: str, value: any) -> None:
        self.values[name] = value

    def get(self, name: Token) -> any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        raise RuntimeError(name, f"Undefined variable: {name.lexeme}")

    def assign(self, name: Token, value: any) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
        else:
            raise RuntimeError(name, f"Undefined variable: {name.lexeme}")
