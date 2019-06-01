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
    arguments      := expression ( "," expression )* ;
    call           := primary ( "(" arguments? ")" )* ;
    exp            := call ( "**" call )* ;
    unary          := ( "~" | !" | "-" ) unary | exp ;
    multiplication := unary ( ( "/" | "*" ) unary )* ;
    addition       := multiplication ( ( "-" | "+" ) multiplication )* ;
    bitshift       := addition ( ( ">>" | "<<" ) addition )* ;
    bitand         := bitshift ("&" bitshift)* ;
    bitxor         := bitand ("^" bitand)* ;
    bitor          := bitxor ("|" bitxor)* ;
    comparison     := bitor ( ( ">" | ">=" | "<" | "<=" ) bitor )* ;
    equality       := comparison ( ( "!=" | "==" ) comparison )* ;
    logic_and      := equality ( "and" equality )* ;
    logic_or       := logic_and ( "or" logic_and )* ;
    assignment     := IDENTIFIER "=" assignment | logic_or ;
    expression     := assignment ;

    // Statement grammar from highest precedence to lowest
    breakStmt      := "break" ";" ;
    continueStmt   := "continue" ";" ;
    exprStmt       := expression ";" ;
    forStmt        := "for" "(" ( varDecl | exprStmt | ";" ) expression? ";" expression? ")" statement ;
    ifStmt         := "if" "(" expression ")" statement ( "else" statement )? ;
    returnStmt     := "return" expression? ";" ;
    whiteStmt      := "while" "(" expression ")" statement ;
    block          := "{" declaration* "}" ;
    statement      := breakStmt | continueStmt | exprStmt | ifStmt | returnStmt | whileStmt | block ;
    parameters     := IDENTIFIER ( "," IDENTIFIER )* ;
    function       := IDENTIFIER "(" parameters? ")" block ;
    funDecl        := "fun" function ;
    varDecl        := "var" IDENTIFIER ( "=" expression )? ";" ;
    declaration    := funDecl | varDecl | statement ;
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

    def arguments(self) -> Expr.Expr:
        pass

    def finishCall(self, callee: Expr.Expr) -> Expr.Expr:
        arguments: List[Expr.Expr] = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 32:
                    self.error(self.peek(), "Cannot have more than 32 arguments")
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break
        paren = self.consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments")
        return Expr.Call(callee, paren, arguments)

    def call(self) -> Expr.Expr:
        expr = self.primary()
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finishCall(expr)
            else:
                break
        return expr

    def exp(self) -> Expr.Expr:
        """ Parses an exponent expression """
        expr = self.call()
        while self.match(TokenType.STAR_STAR):
            operator = self.previous()
            right = self.call()
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

    def logic_and(self) -> Expr.Expr:
        expr = self.equality()
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Expr.Logical(expr, operator, right)
        return expr

    def logic_or(self) -> Expr.Expr:
        expr = self.logic_and()
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logic_and()
            expr = Expr.Logical(expr, operator, right)
        return expr

    def assignment(self) -> Expr.Expr:
        """ Parses an assignment expression """
        expr = self.logic_or()
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
    def breakStatement(self) -> Stmt.Stmt:
        keyword = self.previous()
        self.consume(TokenType.SEMICOLON, "Expected ';' after break statement")
        return Stmt.Break(keyword)

    def continueStatement(self) -> Stmt.Stmt:
        keyword = self.previous()
        self.consume(TokenType.SEMICOLON, "Expected ';' after continue statement")
        return Stmt.Continue(keyword)

    def expressionStatement(self) -> Stmt.Stmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression")
        return Stmt.Expression(expr)

    def forStatement(self) -> Stmt.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'for'")

        # Parse the initializer
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.varDeclaration()
        else:
            initializer = self.expressionStatement()

        # Parse the condition
        if not self.check(TokenType.SEMICOLON):
            # If there is not just a semicolon then parse the expression
            condition = self.expression()
        else:
            condition = None
        self.consume(TokenType.SEMICOLON, "Expected ';' after 'for' condition")

        # Parse the increment
        if not self.check(TokenType.RIGHT_PAREN):
            # If there is not an empty increment expression
            increment = self.expression()
        else:
            increment = None
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after 'for'")

        # Parse the body
        body = self.statement()

        # Desugar the for loop
        if increment is not None:
            # If there is an increment expression add it to the body
            body = Stmt.Block([body, Stmt.Expression(increment)])

        if condition is None:
            # If there is no condition default is True
            condition = Expr.Literal(True)

        # Convert the body to a while statement
        body = Stmt.While(condition, body)

        if initializer is not None:
            # If there is an initializer put it at the beginning of the block
            body = Stmt.Block([initializer, body])

        return body

    def ifStatement(self) -> Stmt.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after 'if' condition")

        thenBranch = self.statement()
        elseBranch = None
        if self.match(TokenType.ELSE):
            elseBranch = self.statement()
        else:
            elseBranch = None

        return Stmt.If(condition, thenBranch, elseBranch)

    def returnStatement(self) -> Stmt.Stmt:
        keyword = self.previous()
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        else:
            value = None
        self.consume(TokenType.SEMICOLON, "Expected ';' after return statement")
        return Stmt.Return(keyword, value)

    def whileStatement(self) -> Stmt.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after 'while' condition")
        body = self.statement()
        return Stmt.While(condition, body)

    def block(self) -> List[Stmt.Stmt]:
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.atEnd():
            statements.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after block")
        return statements

    def statement(self) -> Stmt.Stmt:
        if self.match(TokenType.BREAK):
            return self.breakStatement()
        elif self.match(TokenType.CONTINUE):
            return self.continueStatement()
        elif self.match(TokenType.IF):
            return self.ifStatement()
        elif self.match(TokenType.FOR):
            return self.forStatement()
        elif self.match(TokenType.RETURN):
            return self.returnStatement()
        elif self.match(TokenType.WHILE):
            return self.whileStatement()
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

    def function(self, kind: str, token: Token) -> Stmt.Function:
        name = self.consume(TokenType.IDENTIFIER, f"Expected {kind} name after {token.lexeme}")
        self.consume(TokenType.LEFT_PAREN, f"Expected '(' after {kind} name")
        parameters: List[Token] = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 32:
                    self.error(self.peek(), "Cannot have more than 32 parameters")
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expected parameter name"))
                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters")
        self.consume(TokenType.LEFT_BRACE, f"Expected '{{' before {kind} body")
        body = self.block()
        return Stmt.Function(name, parameters, body)

    def declaration(self) -> Stmt.Stmt:
        try:
            if self.match(TokenType.FUN):
                return self.function("function", self.previous())
            elif self.match(TokenType.VAR):
                return self.varDeclaration()
            else:
                return self.statement()
        except ParserException as error:
            self.synchronize()
            return None
