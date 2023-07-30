# This file is auto-generated from tool/GenerateAst.py
# Do not modify!

from Token import Token

class Expr:
    pass

class Assign(Expr):
    def __init__(self, name: Token, value: Expr):
        self.name: Token = name
        self.value: Expr = value

    def accept(self, visitor: any) -> any:
        return visitor.visitAssignExpr(self)

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

class Logical(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left: Expr = left
        self.operator: Token = operator
        self.right: Expr = right

    def accept(self, visitor: any) -> any:
        return visitor.visitLogicalExpr(self)

class Ternary(Expr):
    def __init__(self, condition: Expr, trueExpr: Expr, falseExpr: Expr):
        self.condition: Expr = condition
        self.trueExpr: Expr = trueExpr
        self.falseExpr: Expr = falseExpr

    def accept(self, visitor: any) -> any:
        return visitor.visitTernaryExpr(self)

class Unary(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator: Token = operator
        self.right: Expr = right

    def accept(self, visitor: any) -> any:
        return visitor.visitUnaryExpr(self)

class Variable(Expr):
    def __init__(self, name: Token):
        self.name: Token = name

    def accept(self, visitor: any) -> any:
        return visitor.visitVariableExpr(self)

