from enum import Enum, auto
import Expr
import Stmt
from ErrorManager import ErrorManager
from Interpreter import Interpreter
from Token import Token

class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()

class LoopType(Enum):
    NONE = auto()
    FOR = auto()
    WHILE = auto()

class Resolver:

    def __init__(self, errorManager: ErrorManager, interpreter: Interpreter) -> None:
        self.errorManager = errorManager
        self.interpreter: Interpreter = interpreter
        self.scopes: list[dict[str,bool]] = []

        self.currentFunction = FunctionType.NONE;
        self.currentLoop = LoopType.NONE;

    # Helper methods

    def resolve(self, statements: Expr.Expr | Stmt.Stmt | list[Expr.Expr | Stmt.Stmt]) -> None:
        if isinstance(statements, list):
            for stmt in statements:
                stmt.accept(self)
        else:
            statements.accept(self)

    def resolveLocal(self, expr: Expr.Expr, name: Token) -> None:
        """
        Walk up the scopes from innermost to outermost and tell the interpreter which scope to use for the variable lookup
        """
        for i,scope in enumerate(self.scopes):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, len(self.scopes)-1-i)

    def resolveFunction(self, function: Stmt.Function, type: FunctionType) -> None:
        enclosingType: FunctionType = self.currentFunction
        self.currentFunction = type
        self.beginScope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.endScope()
        self.currentFunction = enclosingType

    def beginScope(self) -> None:
        self.scopes.append({})

    def endScope(self) -> None:
        self.scopes.pop()

    def declare(self, name: Token) -> None:
        if self.scopes:
            if name.lexeme in self.scopes[-1]:
                self.errorManager.parseError(name, f"Cannot redefine variable {name.lexeme}")
            self.scopes[-1][name.lexeme] = False

    def define(self, name: Token) -> None:
        if self.scopes:
            self.scopes[-1][name.lexeme] = True

    # Statement Visitors

    def visitBlockStmt(self, stmt: Stmt.Block) -> None:
        self.beginScope()
        self.resolve(stmt.statements)
        self.endScope()

    def visitControlStmt(self, stmt: Stmt.Control) -> None:
        if self.currentLoop == LoopType.NONE:
            self.errorManager.parseError(stmt.control, f"Cannot use {stmt.control.lexeme} outside of a loop")
        return

    def visitExpressionStmt(self, stmt: Stmt.Expression) -> None:
        self.resolve(stmt.expression)

    def visitFunctionStmt(self, stmt: Stmt.Function) -> None:
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolveFunction(stmt, FunctionType.FUNCTION)

    def visitForStmt(self, stmt: Stmt.For) -> None:
        enclosingLoop: LoopType = self.currentLoop
        self.currentLoop = LoopType.FOR
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        if stmt.condition is not None:
            self.resolve(stmt.condition)
        if stmt.increment is not None:
            self.resolve(stmt.increment)
        self.resolve(stmt.body)
        self.currentLoop = enclosingLoop

    def visitIfStmt(self, stmt: Stmt.If) -> None:
        self.resolve(stmt.condition)
        self.resolve(stmt.thenBranch)
        if stmt.elseBranch is not None:
            self.resolve(stmt.elseBranch)

    def visitPrintStmt(self, stmt: Stmt.Print) -> None:
        self.resolve(stmt.expression)

    def visitReturnStmt(self, stmt: Stmt.Return) -> None:
        if self.currentFunction == FunctionType.NONE:
            self.errorManager.parseError(stmt.keyword, "Can't return outside of a function")
        if stmt.value is not None:
            self.resolve(stmt.value)

    def visitVarStmt(self, stmt: Stmt.Var) -> None:
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)

    def visitWhileStmt(self, stmt: Stmt.While) -> None:
        enclosingLoop: LoopType = self.currentLoop
        self.currentLoop = LoopType.WHILE
        self.resolve(stmt.condition)
        self.resolve(stmt.body)
        self.currentLoop = enclosingLoop

    # Expression visitors

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

    def visitStringExpr(self, expr: Expr.String) -> None:
        return

    def visitTernaryExpr(self, expr: Expr.Ternary) -> None:
        self.resolve(expr.condition)
        self.resolve(expr.trueExpr)
        self.resolve(expr.falseExpr)

    def visitUnaryExpr(self, expr: Expr.Unary) -> None:
        self.resolve(expr.right)

    def visitVariableExpr(self, expr: Expr.Variable) -> None:
        if self.scopes and self.scopes[-1].get(expr.name.lexeme, None) == False:
            self.errorManager.parseError(expr.name, "Can't read local variable in its own initializer")
        self.resolveLocal(expr, expr.name)


