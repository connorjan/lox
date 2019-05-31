import time
from typing import List

import Interpreter
import LoxCallable

class LoxBuiltin(LoxCallable.LoxCallable):

    def __str__(self):
        return f"<native function {self.__class__.__name__}>"

class clock(LoxBuiltin):
    """ Returns the current system time as a float in seconds """

    def arity(self) -> int:
        return 0

    def call(self, interpreter: Interpreter, arguments: List[object]) -> float:
        return time.time()

class string(LoxBuiltin):
    """ Returns the string representation of an object """

    def arity(self) -> int:
        return 1

    def call(self, interpreter: Interpreter, arguments: List[object]) -> str:
        return interpreter.toString(arguments[0])
