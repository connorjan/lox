# This file is auto-generated from tool/GenerateAst.py
# Do not modify!

from Token import Token

class Expr:
    pass

class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left: Expr = left
        self.operator: Token = operator
        self.right: Expr = right

    def accept(self, visitor: any) -> any:
        return visitor.visitBinaryExpr(self)

class Grouping(Expr):
    def __init__(self, expression: Expr):
        self.expression: Expr = expression

    def accept(self, visitor: any) -> any:
        return visitor.visitGroupingExpr(self)

class Literal(Expr):
    def __init__(self, value: any):
        self.value: any = value

    def accept(self, visitor: any) -> any:
        return visitor.visitLiteralExpr(self)

class Unary(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator: Token = operator
        self.right: Expr = right

    def accept(self, visitor: any) -> any:
        return visitor.visitUnaryExpr(self)

