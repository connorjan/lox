"""
This code provides the classes for the AST expressions
It is autogenerated from tools/GenerateAst.py
"""

from typing import Any, List
from Token import Token

class Expr:
    pass

class Assign(Expr):
    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

    def accept(self, visitor: Any) -> Any:
        return visitor.visitAssignExpr(self)

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

class Logical(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: Any) -> Any:
        return visitor.visitLogicalExpr(self)

class Unary(Expr):
    def __init__(self, operator: Token, right: Token):
        self.operator = operator
        self.right = right

    def accept(self, visitor: Any) -> Any:
        return visitor.visitUnaryExpr(self)

class Variable(Expr):
    def __init__(self, name: Token):
        self.name = name

    def accept(self, visitor: Any) -> Any:
        return visitor.visitVariableExpr(self)
