import Expr
import Stmt
import Builtins
from LoxCallable import LoxCallable
from LoxFunction import LoxFunction
from ExecutionFlow import *
from ErrorManager import *
from Token import Token
from TokenType import TokenType
from Environment import Environment

class Interpreter:

    def __init__(self, errorManager: ErrorManager) -> None:
        self.errorManager: ErrorManager = errorManager
        self.globals: Environment = Environment(self.errorManager, None)
        self.environment = self.globals
        self.locals: dict[Expr.Expr, int] = {}

        # Add builtin functions
        self.globals.define("clock", Builtins.Clock())
        self.globals.define("str", Builtins.Str())

    def evaluate(self, expr: Expr.Expr) -> any:
        return expr.accept(self)

    def isTruthy(self, obj: any) -> bool:
        return bool(obj)

    def stringify(self, object: any) -> str:
        if object is None:
            return "nil"
        return str(object)

    def checkTypeOfOperands(self, operator: Token, types: tuple[any], operands: list[any]) -> None:
        for operand in operands:
            if not isinstance(operand, types):
                raise RuntimeError(operator, f"Operand must be one of the following types: {', '.join(str(t.__name__) for t in types)}")
        return

    def resolve(self, expr: Expr.Expr, depth: int) -> None:
        self.locals[expr] = depth

    def lookUpVariable(self, expr: Expr.Variable) -> any:
        distance: int|None = self.locals.get(expr, None)
        if distance is not None:
            return self.environment.getAt(expr.name.lexeme, distance)
        else:
            return self.globals.get(expr.name)

    # Expression visitors

    def visitLiteralExpr(self, expr: Expr.Literal) -> any:
        return expr.value

    def visitStringExpr(self, expr: Expr.String) -> any:
        return expr.value

    def visitVariableExpr(self, expr: Expr.Variable) -> any:
        return self.lookUpVariable(expr)

    def visitGroupingExpr(self, expr: Expr.Grouping) -> any:
        return self.evaluate(expr.expression)

    def visitUnaryExpr(self, expr: Expr.Unary) -> any:
        right: any = self.evaluate(expr.right)

        match expr.operator.type:
            case TokenType.BANG:
                return not self.isTruthy(right)
            case TokenType.MINUS:
                self.checkTypeOfOperands(expr.operator, types=(int,float), operands=[right])
                return -right

        raise Exception("Unreachable")

    def visitLogicalExpr(self, expr: Expr.Logical) -> any:
        left: any = self.evaluate(expr.left)

        if expr.operator.type == TokenType.OR:
            if self.isTruthy(left):
                return left
        if expr.operator.type == TokenType.AND:
            if not self.isTruthy(left):
                return left

        return self.evaluate(expr.right)

    def visitTernaryExpr(self, expr: Expr.Ternary) -> any:
        if self.isTruthy(self.evaluate(expr.condition)):
            return self.evaluate(expr.trueExpr)
        else:
            return self.evaluate(expr.falseExpr)

    def visitBinaryExpr(self, expr: Expr.Binary) -> any:
        left: any = self.evaluate(expr.left)
        right: any = self.evaluate(expr.right)

        # Operand checks
        match expr.operator.type:
            case TokenType.MINUS | TokenType.SLASH | TokenType.STAR | TokenType.GREATER | TokenType.GREATER_EQUAL | TokenType.LESS | TokenType.LESS_EQUAL:
                self.checkTypeOfOperands(expr.operator, types=(int,float), operands=[left, right])
            case TokenType.AMPERSAND | TokenType.BAR | TokenType.CARROT | TokenType.STAR_STAR | TokenType.LESS_LESS | TokenType.GREATER_GREATER:
                self.checkTypeOfOperands(expr.operator, types=(int,), operands=[left, right])

        match expr.operator.type:
            # Arithmetic
            case TokenType.MINUS:
                return left - right
            case TokenType.SLASH:
                return left / right
            case TokenType.STAR:
                return left * right
            case TokenType.STAR_STAR:
                return left ** right
            case TokenType.PLUS:
                if (isinstance(left, (float, int)) and isinstance(right, (float, int))) or (isinstance(left, str) and isinstance(right, str)):
                    return left + right
                raise RuntimeError(expr.operator, f"Cannot add types of {type(left).__name__} and {type(right).__name__}")

            # Bitwise
            case TokenType.AMPERSAND:
                return left & right
            case TokenType.BAR:
                return left | right
            case TokenType.CARROT:
                return left ^ right
            case TokenType.LESS_LESS:
                return left << right
            case TokenType.GREATER_GREATER:
                return left >> right

            # Comparison
            case TokenType.GREATER:
                return left > right
            case TokenType.GREATER_EQUAL:
                return left >= right
            case TokenType.LESS:
                return left < right
            case TokenType.LESS_EQUAL:
                return left <= right

            # Equality
            case TokenType.BANG_EQUAL:
                return bool(left != right)
            case TokenType.EQUAL_EQUAL:
                return bool(left == right)

        raise Exception(f"Unreachable, operator: {expr.operator}")

    def visitCallExpr(self, expr: Expr.Call) -> any:
        callee: any = self.evaluate(expr.callee)
        arguments: list[any] = [self.evaluate(arg) for arg in expr.arguments]

        if not isinstance(callee, LoxCallable):
            raise RuntimeError(expr.paren, "Did not find function or class")
        elif len(arguments) != callee.arity():
            raise RuntimeError(expr.paren, f"Expected {callee.arity()} arguments but got {len(arguments)}")
        return callee.call(self, arguments)

    def visitAssignExpr(self, expr: Expr.Assign) -> any:
        value: any = self.evaluate(expr.value)
        distance: int|None = self.locals.get(expr, None)
        if distance is not None:
            self.environment.assignAt(expr.name, distance, value)
        else:
            self.globals.assign(expr.name, value)
        return value

    # Statement visitors

    def execute(self, stmt: Stmt.Stmt) -> None:
        stmt.accept(self)

    def executeBlock(self, statements: list[Stmt.Stmt], environment: Environment) -> None:
        previous: Environment = self.environment
        try:
            self.environment = environment
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = previous

    def visitBlockStmt(self, stmt: Stmt.Block) -> None:
        self.executeBlock(stmt.statements, Environment(self.errorManager, self.environment))

    def visitControlStmt(self, stmt: Stmt.Control) -> None:
        if stmt.control.type == TokenType.BREAK:
            raise Break(stmt.control)
        elif stmt.control.type == TokenType.CONTINUE:
            raise Continue(stmt.control)
        else:
            raise Exception("Unreachable")

    def visitReturnStmt(self, stmt: Stmt.Return) -> None:
        value: any = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        raise Return(value)

    def visitPrintStmt(self, stmt: Stmt.Print) -> None:
        value: any = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visitExpressionStmt(self, stmt: Stmt.Expression) -> None:
        self.evaluate(stmt.expression)

    def visitForStmt(self, stmt: Stmt.For) -> None:
        if stmt.initializer is not None:
            self.execute(stmt.initializer)

        while self.isTruthy(self.evaluate(stmt.condition)):
            try:
                self.execute(stmt.body)
            except Break:
                break
            except Continue:
                if stmt.increment is not None:
                    self.execute(stmt.increment)
                continue

            if stmt.increment is not None:
                self.execute(stmt.increment)

    def visitFunctionStmt(self, stmt: Stmt.Function) -> None:
        function: LoxFunction = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)
        return None

    def visitIfStmt(self, stmt: Stmt.If) -> None:
        if self.isTruthy(self.evaluate(stmt.condition)):
            self.execute(stmt.thenBranch)
        elif stmt.elseBranch is not None:
            self.execute(stmt.elseBranch)

    def visitVarStmt(self, stmt: Stmt.Var) -> None:
        value: any = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)

    def visitWhileStmt(self, stmt: Stmt.While) -> None:
        while self.isTruthy(self.evaluate(stmt.condition)):
            try:
                self.execute(stmt.body)
            except Break:
                break
            except Continue:
                continue

    def interpret(self, statements: list[Stmt.Stmt]) -> None:
        try:
            for stmt in statements:
                self.execute(stmt)
        except (Break, Continue) as control:
            self.errorManager.runtimeError(RuntimeError(control.token, f"Cannot use {control.token.lexeme} outside of a loop"))
        except RuntimeError as error:
            self.errorManager.runtimeError(error)
