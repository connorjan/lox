import Lox
import Expr
from RuntimeException import RuntimeException
from TokenType import TokenType
from Token import Token
from typing import Tuple

class Interpreter:
    """ Class to interpret expressions """

    def interpret(self, expression: Expr) -> None:
        """ Interpret an expression and print the result """
        try:
            value = self.evaluate(expression)
            print(self.toString(value))
        except RuntimeException as error:
            Lox.Lox.runtimeError(error)

    # Helper methods
    def evaluate(self, expr: Expr.Expr) -> object:
        return expr.accept(self)

    def toBool(self, obj: object) -> bool:
        """ Lox's rules of how objects are converted to bools are the same as Python """
        return bool(obj)

    def toString(self, obj: object) -> str:
        """ Lox really just has to convert 'None' to 'nil' """
        if obj is None:
            return "nil"
        else:
            return str(obj)

    def checkUnaryType(self, operator: Token, right: object, *types: Tuple[type]) -> None:
        """ Checks to see if the operand is in types otherwise error """
        if isinstance(right, types):
            return
        else:
            msg = f"unsupported operand type for unary {operator.lexeme}: '{type(right).__name__}'"
            raise RuntimeException(operator, msg)

    def checkBinaryTypes(self, operator: Token, left: object, right: object, *types: Tuple[type]) -> None:
        """ Checks to see if the operand is in types otherwise error """
        if isinstance(left, types) and isinstance(right, types):
            return
        else:
            msg = f"unsupported operand type(s) for {operator.lexeme}: '{type(left).__name__}' and '{type(right).__name__}'"
            raise RuntimeException(operator, msg)

    # Visitor methods
    def visitLiteralExpr(self, expr: Expr.Literal) -> object:
        return expr.value

    def visitGroupingExpr(self, expr: Expr.Grouping) -> object:
        return self.evaluate(expr.expression)

    def visitUnaryExpr(self, expr: Expr.Unary) -> object:
        right = self.evaluate(expr.right)

        if expr.operator.type == TokenType.TILDE:
            self.checkUnaryType(expr.operator, right, int)
            return ~right
        elif expr.operator.type == TokenType.MINUS:
            self.checkUnaryType(expr.operator, right, int, float)
            return -right
        elif expr.operator.type == TokenType.BANG:
            return not self.toBool(right)

        # Should not be reachable
        raise Exception("Code should not be reachable")

    def visitBinaryExpr(self, expr: Expr.Binary) -> object:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.operator.type == TokenType.STAR_STAR:
            self.checkBinaryTypes(expr.operator, left, right, int, float)
            return left ** right
        elif expr.operator.type == TokenType.SLASH:
            self.checkBinaryTypes(expr.operator, left, right, int, float)
            if right == 0:
                msg = f"division by zero"
                raise RuntimeException(expr.operator, msg)
            else:
                return left / right
        elif expr.operator.type == TokenType.STAR:
            self.checkBinaryTypes(expr.operator, left, right, int, float)
            return left * right
        elif expr.operator.type == TokenType.MINUS:
            self.checkBinaryTypes(expr.operator, left, right, int, float)
            return left - right
        elif expr.operator.type == TokenType.PLUS:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            elif isinstance(left, str) and isinstance(right, str):
                return left + right
            else:
                msg = f"unsupported operand type(s) for {expr.operator.lexeme}: '{type(left).__name__}' and '{type(right).__name__}'"
                raise RuntimeException(expr.operator, msg)
        elif expr.operator.type == TokenType.LESS_LESS:
            self.checkBinaryTypes(expr.operator, left, right, int)
            return left << right
        elif expr.operator.type == TokenType.GREATER_GREATER:
            self.checkBinaryTypes(expr.operator, left, right, int)
            return left >> right
        elif expr.operator.type == TokenType.AMPER:
            self.checkBinaryTypes(expr.operator, left, right, int)
            return left & right
        elif expr.operator.type == TokenType.CARET:
            self.checkBinaryTypes(expr.operator, left, right, int)
            return left ^ right
        elif expr.operator.type == TokenType.BAR:
            self.checkBinaryTypes(expr.operator, left, right, int)
            return left | right
        elif expr.operator.type == TokenType.GREATER:
            self.checkBinaryTypes(expr.operator, left, right, int, float)
            return left > right
        elif expr.operator.type == TokenType.GREATER_EQUAL:
            self.checkBinaryTypes(expr.operator, left, right, int, float)
            return left >= right
        elif expr.operator.type == TokenType.LESS:
            self.checkBinaryTypes(expr.operator, left, right, int, float)
            return left < right
        elif expr.operator.type == TokenType.LESS_EQUAL:
            self.checkBinaryTypes(expr.operator, left, right, int, float)
            return left <= right
        elif expr.operator.type == TokenType.BANG_EQUAL:
            return left != right
        elif expr.operator.type == TokenType.EQUAL_EQUAL:
            return left == right

        # Should not be reachable
        raise Exception("Code should not be reachable")
