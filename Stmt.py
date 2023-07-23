# This file is auto-generated from tool/GenerateAst.py
# Do not modify!

from Token import Token
from Expr import *

class Stmt:
    pass

class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression: Expr = expression

    def accept(self, visitor: any) -> any:
        return visitor.visitExpressionStmt(self)

class Print(Stmt):
    def __init__(self, expression: Expr):
        self.expression: Expr = expression

    def accept(self, visitor: any) -> any:
        return visitor.visitPrintStmt(self)

class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr):
        self.name: Token = name
        self.initializer: Expr = initializer

    def accept(self, visitor: any) -> any:
        return visitor.visitVarStmt(self)

