# This file is auto-generated from tool/GenerateAst.py
# Do not modify!

from Token import Token
from Expr import *

class Stmt:
    pass

class Block(Stmt):
    def __init__(self, statements: list[Stmt]):
        self.statements: list[Stmt] = statements

    def accept(self, visitor: any) -> any:
        return visitor.visitBlockStmt(self)

class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression: Expr = expression

    def accept(self, visitor: any) -> any:
        return visitor.visitExpressionStmt(self)

class If(Stmt):
    def __init__(self, condition: Expr, thenBranch: Stmt, elseBranch: Stmt):
        self.condition: Expr = condition
        self.thenBranch: Stmt = thenBranch
        self.elseBranch: Stmt = elseBranch

    def accept(self, visitor: any) -> any:
        return visitor.visitIfStmt(self)

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

class While(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self.condition: Expr = condition
        self.body: Stmt = body

    def accept(self, visitor: any) -> any:
        return visitor.visitWhileStmt(self)

