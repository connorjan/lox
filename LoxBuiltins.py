import time
from typing import List

import Interpreter
import LoxCallable

class LoxBuiltin(LoxCallable.LoxCallable):

    def __str__(self):
        return f"<native function {self.name}>"

class loxClock(LoxBuiltin):
    """ Returns the current system time as a float in seconds """
    name = "clock"

    def arity(self) -> int:
        return 0

    def call(self, interpreter: Interpreter, arguments: List[object]) -> float:
        return time.time()

class loxPrint(LoxBuiltin):
    """ Prints a value  """
    name = "print"

    def arity(self) -> int:
        return 1

    def call(self, interpreter: Interpreter, arguments: List[object]) -> None:
        print(interpreter.toString(arguments[0]))

class loxString(LoxBuiltin):
    """ Returns the string representation of an object """
    name = "string"

    def arity(self) -> int:
        return 1

    def call(self, interpreter: Interpreter, arguments: List[object]) -> str:
        return interpreter.toString(arguments[0])
