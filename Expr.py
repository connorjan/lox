"""
This code provides the classes for the AST expressions
It is autogenerated from tools/GenerateAst.py
"""

from typing import Any
from Token import Token

class Expr:
    pass

class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: Any) -> Any:
        return visitor.visitBinaryExpr(self)

class Grouping(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: Any) -> Any:
        return visitor.visitGroupingExpr(self)

class Literal(Expr):
    def __init__(self, value: object):
        self.value = value

    def accept(self, visitor: Any) -> Any:
        return visitor.visitLiteralExpr(self)

class Unary(Expr):
    def __init__(self, operator: Token, right: Token):
        self.operator = operator
        self.right = right

    def accept(self, visitor: Any) -> Any:
        return visitor.visitUnaryExpr(self)