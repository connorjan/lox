from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Interpreter import Interpreter

import time
from LoxCallable import LoxCallable


class Clock(LoxCallable):

    def __str__(self) -> str:
        return "<builtin function clock>"

    def arity(self) -> int:
        return 0

    def call(self, interpreter: Interpreter, arguments: list[any]) -> float:
        return time.time()
