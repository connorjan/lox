from __future__ import annotations

from RuntimeException import RuntimeException
from Token import Token
from typing import Dict

class Environment:
    """ Class to store the variables and their values """

    def __init__(self, enclosing=None):
        self.values: Dict[str, object] = {}
        self.enclosing: Environment = enclosing;

    def ancestor(self, distance: int) -> Environment:
        """ Get an environment at a specified distance """
        environment = self
        for i in range(distance):
            environment = environment.enclosing
        return environment

    def assignAt(self, distance: int, name: Token, value: object) -> None:
        """ Assign a value to an enviroment at a specified distance """
        self.ancestor(distance).values[name.lexeme] = value

    def define(self, name: str, value: object) -> None:
        """ Creates a new variable with value """
        self.values[name] = value

    def get(self, name: Token) -> object:
        """ Gets the value from a variable """
        if name.lexeme in self.values:
            # The variable is in the current scope
            return self.values[name.lexeme]
        elif self.enclosing is not None:
            # Try looking in the enclosing (outer) scope
            return self.enclosing.get(name)
        else:
            raise RuntimeException(name, f"Undefined variable '{name.lexeme}'")

    def getAt(self, distance: int, name: str) -> object:
        """ Get a value from an enviroment at a specified distance """
        return self.ancestor(distance).values[name]

    def assign(self, name: Token, value: object) -> None:
        """ Assigns a value to an existing variable """
        if name.lexeme in self.values:
            # The variable exists in the current scope
            self.values[name.lexeme] = value
        elif self.enclosing is not None:
            # Try assigning to a variable in the enclosing scope
            self.enclosing.assign(name, value)
        else:
            raise RuntimeException(name, f"Undefined variable '{name.lexeme}'")
