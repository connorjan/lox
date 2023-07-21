#!/usr/bin/env python3

import Expr
from Token import Token
from TokenType import TokenType

class AstPrinter:

    def print(self, expr: Expr.Expr) -> str:
        return expr.accept(self)

    def parenthesize(self, name: str, *exprs):
        return f"""({name} {" ".join(expr.accept(self) for expr in exprs)})"""

    def visitBinaryExpr(self, expr: Expr.Binary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visitGroupingExpr(self, expr: Expr.Grouping) -> str:
        return self.parenthesize("group", expr.expression)

    def visitLiteralExpr(self, expr: Expr.Literal) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visitUnaryExpr(self, expr: Expr.Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)

if __name__ == "__main__":
    e = Expr.Binary(
        left=Expr.Unary(
            operator=Token(TokenType.MINUS, "-", None, 1),
            right=Expr.Literal(123)
        ),
        operator=Token(TokenType.STAR, "*", None, 1),
        right=Expr.Grouping(
            Expr.Literal(3.1415)
        )
    )

    ap = AstPrinter()
    print(ap.print(e))
