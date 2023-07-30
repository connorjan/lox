from __future__ import annotations
from ErrorManager import *
from Token import Token

class Environment:

    def __init__(self, errorManager: ErrorManager, enclosing: Environment|None) -> None:
        self.errorManager = errorManager
        self.values: dict[str, any] = {}
        self.enclosing = enclosing

    def define(self, name: str, value: any) -> None:
        self.values[name] = value

    def get(self, name: Token) -> any:
        if name.lexeme in self.values:
            # If the variable is found in this environment
            return self.values[name.lexeme]

        if self.enclosing is not None:
            # If this environment is enclosed by another, try the enclosing one
            return self.enclosing.get(name)

        raise RuntimeError(name, f"Undefined variable: {name.lexeme}")

    def assign(self, name: Token, value: any) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
        elif self.enclosing is not None:
            self.enclosing.assign(name, value)
        else:
            raise RuntimeError(name, f"Undefined variable: {name.lexeme}")
