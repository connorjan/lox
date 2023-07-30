from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Interpreter import Interpreter

from abc import *

class LoxCallable(ABC):

    @abstractmethod
    def call(self, interpreter: Interpreter, arguments: list[any]) -> any:
        ...

    @abstractmethod
    def arity(self) -> int:
        ...
