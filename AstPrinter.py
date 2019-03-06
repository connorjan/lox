#!/usr/bin/env python3

import Expr
from Token import Token
from TokenType import TokenType

class AstPrinter:
    """ Class to print the abstract syntax tree """

    def __init__(self):
        pass

    def print(self, expr: Expr.Expr) -> str:
        return expr.accept(self)

    def visitBinaryExpr(self, expr: Expr.Binary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visitGroupingExpr(self, expr: Expr.Grouping) -> str:
        return self.parenthesize("group", expr.expression)

    def visitLiteralExpr(self, expr: Expr.Literal) -> str:
        if expr.value is None:
            return None
        else:
            return str(expr.value)

    def visitUnaryExpr(self, expr: Expr.Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name: str, *exprs: Expr) -> str:
        """ Return a list of subexpressions in parentheses """
        s = f"({name}"
        for expr in exprs:
            s += " "
            s += expr.accept(self)
        s += ")"
        return s

def main():
    astPrinter = AstPrinter()
    expression = Expr.Binary(
                    Expr.Unary(
                        Token(TokenType.MINUS, '-', None, 1),
                        Expr.Literal(123)),
                    Token(TokenType.STAR, '*', None, 1),
                    Expr.Grouping(
                        Expr.Literal(45.67)))


    print(astPrinter.print(expression))

if __name__ == '__main__':
    main()
