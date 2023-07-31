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

    def ancestor(self, distance: int) -> Environment:
        environment: Environment = self
        for _ in range(distance):
            environment = environment.enclosing
        return environment

    def get(self, name: Token) -> any:
        if name.lexeme in self.values:
            # If the variable is found in this environment
            return self.values[name.lexeme]

        if self.enclosing is not None:
            # If this environment is enclosed by another, try the enclosing one
            return self.enclosing.get(name)

        raise RuntimeError(name, f"Undefined variable: {name.lexeme}")

    def getAt(self, name: str, distance: int) -> any:
        return self.ancestor(distance).values[name]

    def assign(self, name: Token, value: any) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
        elif self.enclosing is not None:
            self.enclosing.assign(name, value)
        else:
            raise RuntimeError(name, f"Undefined variable: {name.lexeme}")

    def assignAt(self, name: Token, distance: int, value: any) -> None:
        self.ancestor(distance).values[name.lexeme] = value
