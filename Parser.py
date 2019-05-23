import Lox
import Expr
import Stmt
from TokenType import TokenType
from Token import Token
from typing import List

class ParserException(Exception):
    pass

class Parser:
    """ Class to implement the AST parser """

    """
    // Expression grammar from highest precedence to lowest
    primary        := INT | FLOAT | STRING | "false" | "true" | "nil" | "(" expression ")" | IDENTIFIER ;
    exp            := primary ( "**" primary )* ;
    unary          := ( "~" | !" | "-" ) unary | exp ;
    multiplication := unary ( ( "/" | "*" ) unary )* ;
    addition       := multiplication ( ( "-" | "+" ) multiplication )* ;
    bitshift       := addition ( ( ">>" | "<<" ) addition )* ;
    bitand         := bitshift ("&" bitshift)* ;
    bitxor         := bitand ("^" bitand)* ;
    bitor          := bitxor ("|" bitxor)* ;
    comparison     := bitor ( ( ">" | ">=" | "<" | "<=" ) bitor )* ;
    equality       := comparison ( ( "!=" | "==" ) comparison )* ;
    assignment     := IDENTIFIER "=" assignment | equality ;
    expression     := assignment ;

    // Statement grammar from highest precedence to lowest
    exprStmt       := expression ";" ;
    printStmt      := "print" expression ";" ;
    block          := "{" declaration* "}" ;
    statement      := exprStmt | printStmt | block ;
    varDecl        := "var" IDENTIFIER ( "=" expression )? ";" ;
    declaration    := varDecl | statement ;
    program        := declaration* EOF ;
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Expr.Expr:
        """ Parse expressions into a syntax tree """
        statements: List[Stmt.Stmt] = []
        while not self.atEnd():
            statements.append(self.declaration())
        return statements

    # Some helper methods
    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current-1]

    def atEnd(self) -> bool:
        return self.peek().type == TokenType.EOF

    def advance(self) -> Token:
        if not self.atEnd():
            self.current += 1
            return self.previous()

    def check(self, type_: TokenType) -> bool:
        """ Returns True if the current token is of `type` """
        if self.atEnd():
            return False
        else:
            return self.peek().type == type_

    def match(self, *types) -> bool:
        """ If the current token is in `types` consume it an return True """
        for type_ in types:
            if self.check(type_):
                self.advance()
                return True
        return False

    def error(self, token: Token, message: str) -> ParserException:
        Lox.Lox.tokenError(token, message)
        return ParserException()

    def synchronize(self) -> None:
        self.advance()

        while not self.atEnd():
            if self.previous().type == TokenType.SEMICOLON:
                return
            elif self.peek().type in (  TokenType.CLASS,
                                        TokenType.FUN,
                                        TokenType.VAR,
                                        TokenType.FOR,
                                        TokenType.IF,
                                        TokenType.WHILE,
                                        TokenType.PRINT,
                                        TokenType.RETURN):
                return
            else:
                self.advance()

    # Actual parser methods
    def consume(self, type_: TokenType, message: str) -> Token:
        """ Try to find the closing parenthesis, otherwise error """
        if self.check(type_):
            return self.advance()
        else:
            raise self.error(self.peek(), message)

    def primary(self) -> Expr.Expr:
        """ Parses a primary expression """
        if self.match(TokenType.TRUE):
            return Expr.Literal(True)
        elif self.match(TokenType.FALSE):
            return Expr.Literal(False)
        elif self.match(TokenType.NIL):
            return Expr.Literal(None)
        elif self.match(TokenType.INT, TokenType.FLOAT, TokenType.STRING):
            return Expr.Literal(self.previous().literal)
        elif self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected closing ')' after expression")
            return Expr.Grouping(expr)
        elif self.match(TokenType.IDENTIFIER):
            return Expr.Variable(self.previous())
        else:
            raise self.error(self.peek(), "Expected expression")

    def exp(self) -> Expr.Expr:
        """ Parses an exponent expression """
        expr = self.primary()
        while self.match(TokenType.STAR_STAR):
            operator = self.previous()
            right = self.primary()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def unary(self) -> Expr.Expr:
        """ Parses a unary expression """
        if self.match(TokenType.BANG, TokenType.MINUS, TokenType.TILDE):
            operator = self.previous()
            right = self.unary()
            return Expr.Unary(operator, right)
        else:
            return self.exp()

    def multiplication(self) -> Expr.Expr:
        """ Parses a binary expression of multiplication precedence or higher"""
        expr = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def addition(self) -> Expr.Expr:
        """ Parses a binary expression of additive precedence or higher"""
        expr = self.multiplication()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.multiplication()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def bitshift(self) -> Expr.Expr:
        """ Parses a binary expression of bitshift precedence or higher """
        expr = self.addition()
        while self.match(TokenType.GREATER_GREATER, TokenType.LESS_LESS):
            operator = self.previous()
            right = self.addition()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def bitand(self) -> Expr.Expr:
        """ Parses a binary expression of bitand precedence or higher """
        expr = self.bitshift()
        while self.match(TokenType.AMPER):
            operator = self.previous()
            right = self.bitshift()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def bitxor(self) -> Expr.Expr:
        """ Parses a binary expression of bitxor precedence or higher """
        expr = self.bitand()
        while self.match(TokenType.CARET):
            operator = self.previous()
            right = self.bitand()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def bitor(self) -> Expr.Expr:
        """ Parses a binary expression of bitor precedence or higher """
        expr = self.bitxor()
        while self.match(TokenType.BAR):
            operator = self.previous()
            right = self.bitxor()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def comparison(self) -> Expr.Expr:
        """ Parses a binary expression of comparitive precedence or higher"""
        expr = self.bitor()
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.bitor()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def equality(self) -> Expr.Expr:
        """ Parses a binary expression of equality precedence or higher"""
        expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def assignment(self) -> Expr.Expr:
        """ Parses an assignment expression """
        expr = self.equality()
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, Expr.Variable):
                return Expr.Assign(expr.name, value)
            else:
                self.error(equals, "Invalid assignment target")
        else:
            return expr

    def expression(self) -> Expr.Expr:
        """ Parses an expression starting with the lowest precedence and works up """
        return self.assignment()

    # Methods to deal with statements
    def printStatement(self) -> Stmt.Stmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after value")
        return Stmt.Print(value)

    def expressionStatement(self) -> Stmt.Stmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression")
        return Stmt.Expression(expr)

    def block(self) -> List[Stmt.Stmt]:
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.atEnd():
            statements.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after block")
        return statements

    def statement(self) -> Stmt.Stmt:
        if self.match(TokenType.PRINT):
            return self.printStatement()
        elif self.match(TokenType.LEFT_BRACE):
            return Stmt.Block(self.block())
        else:
            return self.expressionStatement()

    def varDeclaration(self) -> Stmt.Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name")
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration")
        return Stmt.Var(name, initializer)

    def declaration(self) -> Stmt.Stmt:
        try:
            if self.match(TokenType.VAR):
                return self.varDeclaration()
            else:
                return self.statement()
        except ParserException as error:
            self.synchronize()
            return None
