import Expr
import Stmt
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

            match self.peek().type:
                case TokenType.CLASS | TokenType.FUN | TokenType.VAR | TokenType.FOR | TokenType.IF | TokenType.WHILE | TokenType.PRINT | TokenType.RETURN:
                    return

            self.advance()

    # Statement grammer

    """
    program := declaration* EOF
    """

    def declaration(self) -> Stmt.Stmt:
        """
        declaration := varDeclaration | statement
        """
        try:
            if self.match(TokenType.VAR):
                return self.varDeclaration()
            return self.statement()
        except ParseError as e:
            self.synchronize()

    def varDeclaration(self) -> Stmt.Stmt:
        """
        varDeclaration := "var" IDENTIFIER ( "=" expression )? ";"
        """
        name: Token = self.consume(TokenType.IDENTIFIER, "Expected a valid variable name")
        initializer: Expr.Expr | None = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected \";\" at the end of the statement")
        return Stmt.Var(name, initializer)

    def statement(self) -> Stmt.Stmt:
        """
        statement :=      expressionStatement
                        | forStatement
                        | ifStatement
                        | printStatement
                        | whileStatement
                        | block
        """
        if self.match(TokenType.FOR):
            return self.forStatement()
        elif self.match(TokenType.IF):
            return self.ifStatement()
        elif self.match(TokenType.PRINT):
            return self.printStatement()
        elif self.match(TokenType.WHILE):
            return self.whileStatement()
        elif self.match(TokenType.LEFT_BRACE):
            return Stmt.Block(self.block())

        return self.expressionStatement()

    def forStatement(self) -> Stmt.Stmt:
        """
        forStatement := "for" "(" ( varDeclaration | expressionStatement | ";" ) expression? ";" expression? ")" statement
        """
        self.consume(TokenType.LEFT_PAREN, "Expected opening \"(\"")
        initializer: Stmt.Stmt | None = None
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.varDeclaration()
        else:
            initializer = self.expressionStatement()

        condition: Expr.Expr | None = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected \";\" after loop condition")

        increment: Expr.Expr | None = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()

        self.consume(TokenType.RIGHT_PAREN, "Expected closing \")\"")

        # Desugar the for loop into a whileStatement
        body: Stmt.Stmt = self.statement()

        if increment is not None:
            body = Stmt.Block([
                body,
                Stmt.Expression(increment)
            ])

        if condition is None:
            condition = Expr.Literal(True)

        body = Stmt.While(condition, body)

        if initializer is not None:
            body = Stmt.Block([
                initializer,
                body
            ])

        return body

    def ifStatement(self) -> Stmt.Stmt:
        """
        ifStatement := "if" "(" expression ")" statement ( "else" statement )?
        """
        self.consume(TokenType.LEFT_PAREN, "Expected opening \"(\"")
        condition: Expr.Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected closing \")\"")

        thenBranch: Stmt.Stmt = self.statement()
        elseBranch: Stmt.Stmt = None
        if self.match(TokenType.ELSE):
            elseBranch = self.statement()

        return Stmt.If(condition, thenBranch, elseBranch)

    def whileStatement(self) -> Stmt.Stmt:
        """
        whileStatement := "while" "(" expression ")" statement
        """
        self.consume(TokenType.LEFT_PAREN, "Expected opening \"(\"")
        condition: Expr.Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected closing \")\"")
        body: Stmt.Stmt = self.statement()

        return Stmt.While(condition, body)

    def block(self) -> list[Stmt.Stmt]:
        """
        block := "{" declaration* "}"
        """
        statements: list[Stmt.Stmt] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.atEnd():
            statements.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expected closing \"}\" after block")
        return statements

    def printStatement(self) -> Stmt.Stmt:
        """
        printStatement := "print" expression ";"
        """
        value: Expr.Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected \";\" at the end of the expression")
        return Stmt.Print(value)

    def expressionStatement(self) -> Stmt.Stmt:
        """
        expressionStatement := expression ";"
        """
        expression: Expr.Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected \";\" at the end of the expression")
        return Stmt.Expression(expression)

    # Expression grammer

    def expression(self) -> Expr.Expr:
        """
        expression := assignment
        """
        return self.assignment()

    def assignment(self) -> Expr.Expr:
        """
        assignment := IDENTIFIER "=" assignment | logical_or
        """
        expr: Expr.Expr = self.logical_or()

        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: Expr.Expr = self.assignment()

            if isinstance(expr, Expr.Variable):
                name: Token = expr.name
                return Expr.Assign(name, value)

            self.error(equals, "Invalid assignment target")

        return expr

    def logical_or(self) -> Expr.Expr:
        """
        logical_or := logical_and ( "or" logical_and )*
        """
        expr: Expr.Expr = self.logical_and()
        while self.match(TokenType.OR):
            operator: Token = self.previous()
            right: Expr.Expr = self.logical_and()
            expr = Expr.Logical(expr, operator, right)
        return expr

    def logical_and(self) -> Expr.Expr:
        """
        logical_and := equality ( "and" equality )*
        """
        expr: Expr.Expr = self.equality()
        while self.match(TokenType.AND):
            operator: Token = self.previous()
            right: Expr.Expr = self.equality()
            expr = Expr.Logical(expr, operator, right)
        return expr

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
        comparison := bitwise ( ( ">" | ">=" | "<" | "<=" ) bitwise )*
        """
        expr: Expr.Expr = self.bitwise()
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator: Token = self.previous()
            right: Expr.Expr = self.bitwise()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def bitwise(self) -> Expr.Expr:
        """
        bitwise := shift ( ( "&" | "|" | "^" ) shift )*
        """
        expr: Expr.Expr = self.shift()
        while self.match(TokenType.AMPERSAND, TokenType.BAR, TokenType.CARROT, TokenType.LESS_LESS, TokenType.GREATER_GREATER):
            operator: Token = self.previous()
            right: Expr.Expr = self.shift()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def shift(self) -> Expr.Expr:
        """
        shift := term ( ( "<<" | ">>" ) term )*
        """
        expr: Expr.Expr = self.term()
        while self.match(TokenType.AMPERSAND, TokenType.BAR, TokenType.CARROT, TokenType.LESS_LESS, TokenType.GREATER_GREATER):
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
        factor := exp ( ( "*" | "/" ) exp )*
        """
        expr: Expr.Expr = self.exp()
        while self.match(TokenType.STAR, TokenType.SLASH):
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
        primary := NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")" | IDENTIFIER
        """
        if self.match(TokenType.FALSE): return Expr.Literal(False)
        if self.match(TokenType.TRUE): return Expr.Literal(True)
        if self.match(TokenType.NIL): return Expr.Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Expr.Literal(self.previous().literal)

        if self.match(TokenType.IDENTIFIER):
            return Expr.Variable(self.previous())

        if self.match(TokenType.LEFT_PAREN):
            expr: Expr.Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected closing ')' after expression")
            return Expr.Grouping(expr)

        raise self.error(self.peek(), "Expected valid expression")

    # Start parsing

    def parse(self) -> list[Stmt.Stmt]:
        statements: list[Stmt.Stmt] = []
        while not self.atEnd():
            statements.append(self.declaration())
        return statements
