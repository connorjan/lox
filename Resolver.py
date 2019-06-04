from __future__ import annotations

import Lox
import Expr
import Interpreter
import Stmt
from Token import Token
from enum import Enum, auto
from typing import Any, Dict, List

class Resolver:
    """
    Class to perform a pass over the AST for the semantic analysis of
    resolving values
    """

    class FunctionType(Enum):
        NONE = auto()
        FUNCTION = auto()

    def __init__(self, interpreter: Interpreter.Interpreter):
        self.interpreter = interpreter
        self.scopes: List[Dict[str, bool]] = []
        self.currentFunction = Resolver.FunctionType.NONE

    # Helper methods
    def resolveFunction(self, function: Stmt.Function, funcType: Resolver.FunctionType) -> None:
        enclosingFunction = self.currentFunction
        self.currentFunction = funcType
        self.beginScope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.endScope()
        self.currentFunction = enclosingFunction

    def resolveLocal(self, expr: Expr.Expr, name: Token) -> None:
        for i in range(len(self.scopes)-1,-1,-1):
            # Work through the scopes from innermost to outermost
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes)-1-i)
                return

    def resolve(self, toResolve: Any) -> None:
        if isinstance(toResolve, list):
            for stmt in toResolve:
                self.resolve(stmt)
        elif isinstance(toResolve, Stmt.Stmt):
            toResolve.accept(self)
        elif isinstance(toResolve, Expr.Expr):
            toResolve.accept(self)
        else:
            raise Exception("Unsupported type to resolve")

    def beginScope(self) -> None:
        self.scopes.append({})

    def endScope(self) -> None:
        self.scopes.pop()

    def declare(self, name: Token) -> None:
        if self.scopes:
            scope = self.scopes[-1] # Get the top of the scope stack
            if name.lexeme in scope:
                Lox.Lox.tokenError(name, f"Variable {name.lexeme} already defined in the current scope")
            else:
                scope[name.lexeme] = False

    def define(self, name: Token) -> None:
        if self.scopes:
            scope = self.scopes[-1] # Get the top of the scope stack
            scope[name.lexeme] = True

    # Visitor methods
    def visitBlockStmt(self, stmt: Stmt.Block) -> None:
        self.beginScope()
        self.resolve(stmt.statements)
        self.endScope()

    def visitBreakStmt(self, stmt: Stmt.Break) -> None:
        return

    def visitContinueStmt(self, stmt: Stmt.Continue) -> None:
        return

    def visitExpressionStmt(self, stmt: Stmt.Expression) -> None:
        self.resolve(stmt.expression)

    def visitFunctionStmt(self, stmt: Stmt.Function) -> None:
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolveFunction(stmt, Resolver.FunctionType.FUNCTION)

    def visitIfStmt(self, stmt: Stmt.If) -> None:
        self.resolve(stmt.condition)
        self.resolve(stmt.thenBranch)
        if stmt.elseBranch is not None:
            self.resolve(stmt.elseBranch)

    def visitReturnStmt(self, stmt: Stmt.Return) -> None:
        if self.currentFunction == Resolver.FunctionType.NONE:
            Lox.Lox.tokenError(stmt.keyword, "Cannot return outside of a function")
        if stmt.value is not None:
            self.resolve(stmt.value)

    def visitVarStmt(self, stmt: Stmt.Var) -> None:
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)

    def visitWhileStmt(self, stmt: Stmt.While) -> None:
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    def visitAssignExpr(self, expr: Expr.Assign) -> None:
        self.resolve(expr.value)
        self.resolveLocal(expr, expr.name)

    def visitBinaryExpr(self, expr: Expr.Binary) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visitCallExpr(self, expr: Expr.Call) -> None:
        self.resolve(expr.callee)
        for argument in expr.arguments:
            self.resolve(argument)

    def visitGroupingExpr(self, expr: Expr.Grouping) -> None:
        self.resolve(expr.expression)

    def visitLiteralExpr(self, expr: Expr.Literal) -> None:
        return

    def visitLogicalExpr(self, expr: Expr.Logical) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visitUnaryExpr(self, expr: Expr.Unary) -> None:
        self.resolve(expr.right)

    def visitVariableExpr(self, expr: Expr.Variable) -> None:
        undefined = object()
        if self.scopes and self.scopes[-1].get(expr.name.lexeme, undefined) is not undefined and self.scopes[-1][expr.name.lexeme] == False:
            Lox.Lox.tokenError(expr.name, "Cannot read local variable in its own initializer")
        else:
            self.resolveLocal(expr, expr.name)
