import ControlException
import LoxCallable
import Interpreter
import Stmt
from Environment import Environment
from typing import List

class LoxFunction(LoxCallable.LoxCallable):
    """ LoxCallable derived class to represent functions """

    def __init__(self, declaration: Stmt.Function, closure: Environment):
        self.declaration = declaration

        # Stores the environment that exists at the time when the function is *declared*
        self.closure = closure

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: Interpreter, arguments: List[object]) -> object:
        # Create a new environment starting from the closure
        environment = Environment(self.closure)

        # For each of the parameter tokens from the funcion declaration,
        # define the passed argument value to the parameter name
        for i, parameter in enumerate(self.declaration.params):
            environment.define(parameter.lexeme, arguments[i])

        # Catch a return statement as to not continue execution
        try:
            interpreter.executeBlock(self.declaration.body, environment)
        except ControlException.Return as returnValue:
            return returnValue.value

        # If there was no return statement, return None by default
        return None

    def __str__(self):
        return f"<function {self.declaration.name.lexeme}>"
