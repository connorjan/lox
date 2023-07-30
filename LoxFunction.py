from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Interpreter import Interpreter

import Stmt
from ExecutionFlow import Return
from Environment import Environment
from LoxCallable import LoxCallable

class LoxFunction(LoxCallable):

    def __init__(self, declaration: Stmt.Function) -> None:
        self.declaration: Stmt.Function = declaration

    def __str__(self) -> str:
        return f"<fun {self.declaration.name.lexeme}>"

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: Interpreter, arguments: list[any]) -> any:
        environment = Environment(interpreter.errorManager, interpreter.globals)
        for i, argument in enumerate(arguments):
            environment.define(self.declaration.params[i].lexeme, argument)

        try:
            interpreter.executeBlock(self.declaration.body, environment)
        except Return as ret:
            return ret.value

        raise Exception("Unreachable")
