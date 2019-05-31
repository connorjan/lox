import Interpreter
from typing import List

class LoxCallable:
    """ Base class for callable objects """

    def __str__(self):
        raise NotImplementedError

    def arity(self) -> int:
        raise NotImplementedError

    def call(self, interpreter: Interpreter, arguments: List[object]) -> object:
        raise NotImplementedError
