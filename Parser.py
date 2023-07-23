import Expr
from ErrorManager import *
from Token import Token
from TokenType import TokenType

class Parser:

    def __init__(self, errorManager: ErrorManager, tokens: list[Token]) -> None:
        self.errorManager = errorManager
        self.tokens: list[Token] = tokens
        self.current = 0

    # Helper methods

    def previous(self) -> Token:
        return self.tokens[self.current-1]

    def peek(self) -> Token:
        return self.tokens[self.current]

    def atEnd(self) -> bool:
        return self.peek().type == TokenType.EOF

    def advance(self) -> None:
        if not self.atEnd():
            self.current += 1
        return self.previous()

    def check(self, type_: TokenType) -> bool:
        if self.atEnd():
            return False
        return self.peek().type == type_

    def match(self, *types: list[TokenType]) -> bool:
        for type_ in types:
            if self.check(type_):
                self.advance()
                return True
        return False

    def error(self, token: Token, message: str) -> ParseError:
        self.errorManager.parseError(token, message)
        return ParseError()

    def consume(self, type_: TokenType, message: str) -> Token:
        if self.check(type_):
            return self.advance()

        raise self.error(self.peek(), message)

    def synchronize(self) -> None:
        self.advance()

        while not self.atEnd():
            if self.previous().type == TokenType.SEMICOLON:
                return

            match self.peek.type():
                case TokenType.CLASS | TokenType.FUN | TokenType.VAR | TokenType.FOR | TokenType.IF | TokenType.WHILE | TokenType.PRINT | TokenType.RETURN:
                    return

            self.advance()

    # Grammer logic

    def expression(self) -> Expr.Expr:
        """
        expression := equality
        """
        return self.equality()

    def equality(self) -> Expr.Expr:
        """
        equality := comparison ( ( "!=" | "==" ) comparison )*
        """
        expr: Expr.Expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self.previous()
            right: Expr.Expr = self.comparison()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def comparison(self) -> Expr.Expr:
        """
        comparison := term ( ( ">" | ">=" | "<" | "<=" ) term )*
        """
        expr: Expr.Expr = self.term()
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator: Token = self.previous()
            right: Expr.Expr = self.term()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def term(self) -> Expr.Expr:
        """
        term := factor ( ( "+" | "-" ) factor )*
        """
        expr: Expr.Expr = self.factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator: Token = self.previous()
            right: Expr.Expr = self.factor()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def factor(self) -> Expr.Expr:
        """
        factor := bitwise ( ( "*" | "/" ) bitwise )*
        """
        expr: Expr.Expr = self.bitwise()
        while self.match(TokenType.STAR, TokenType.SLASH):
            operator: Token = self.previous()
            right: Expr.Expr = self.bitwise()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def bitwise(self) -> Expr.Expr:
        """
        bitwise := exp ( ( "&" | "|" | "^" ) exp )*
        """
        expr: Expr.Expr = self.exp()
        while self.match(TokenType.AMPERSAND, TokenType.BAR, TokenType.CARROT):
            operator: Token = self.previous()
            right: Expr.Expr = self.exp()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def exp(self) -> Expr.Expr:
        """
        exp := unary ( "**" unary )*
        """
        expr: Expr.Expr = self.unary()
        while self.match(TokenType.STAR_STAR):
            operator: Token = self.previous()
            right: Expr.Expr = self.unary()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def unary(self) -> Expr.Expr:
        """
        unary :=  ( "!" | "-" ) unary
                | primary
        """
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self.previous()
            right: Expr.Expr = self.unary()
            return Expr.Unary(operator, right)
        return self.primary()

    def primary(self) -> Expr.Expr:
        """
        primary := NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")"
        """
        if self.match(TokenType.FALSE): return Expr.Literal(False)
        if self.match(TokenType.TRUE): return Expr.Literal(True)
        if self.match(TokenType.NIL): return Expr.Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Expr.Literal(self.previous().literal)

        if self.match(TokenType.LEFT_PAREN):
            expr: Expr.Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected closing ')' after expression")
            return Expr.Grouping(expr)

        raise self.error(self.peek(), "Expected valid expression")

    # Start parsing

    def parse(self) -> Expr.Expr:
        try:
            return self.expression()
        except ParseError:
            return None
