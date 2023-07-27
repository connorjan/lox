import Expr
import Stmt
from ErrorManager import *
from Token import Token
from TokenType import TokenType
from Environment import Environment

class Interpreter:

    def __init__(self, errorManager: ErrorManager) -> None:
        self.errorManager: ErrorManager = errorManager
        self.environment: Environment = Environment(self.errorManager)

    def visitLiteralExpr(self, expr: Expr.Literal) -> any:
        return expr.value

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

    # Expression visitors

    def visitVariableExpr(self, expr: Expr.Variable) -> any:
        return self.environment.get(expr.name)

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

    def visitBinaryExpr(self, expr: Expr.Binary) -> any:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

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

    def visitAssignExpr(self, expr: Expr.Assign) -> any:
        value: any = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
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

    def visitPrintStmt(self, stmt: Stmt.Print) -> None:
        value: any = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visitExpressionStmt(self, stmt: Stmt.Expression) -> None:
        self.evaluate(stmt.expression)

    def visitVarStmt(self, stmt: Stmt.Var) -> None:
        value: any = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)

    def interpret(self, statements: list[Stmt.Stmt]) -> None:
        try:
            for stmt in statements:
                self.execute(stmt)
        except RuntimeError as error:
            self.errorManager.runtimeError(error)
