import Lox
from TokenType import TokenType
from Token import Token

class Scanner:
    """ Lexes the code for tokens """

    # Define our keywords
    keywords = {
        "and"    : TokenType.AND,
        "class"  : TokenType.CLASS,
        "else"   : TokenType.ELSE,
        "false"  : TokenType.FALSE,
        "for"    : TokenType.FOR,
        "fun"    : TokenType.FUN,
        "if"     : TokenType.IF,
        "nil"    : TokenType.NIL,
        "or"     : TokenType.OR,
        "print"  : TokenType.PRINT,
        "return" : TokenType.RETURN,
        "super"  : TokenType.SUPER,
        "this"   : TokenType.THIS,
        "true"   : TokenType.TRUE,
        "var"    : TokenType.VAR,
        "while"  : TokenType.WHILE
    }

    def __init__(self, source: str):
        self.source = source # source of which to scan for tokens
        self.tokens = [] # list of all tokens found in the source
        self.start = 0 # first character of the lexeme being scanned
        self.current = 0 # character we are currently considering
        self.line = 1 # current line number
        self.nestedCommentCount = 0 # count to allow for nested block comment

    def atEnd(self) -> bool:
        """ Returns true when we are at the end of the source """
        return self.current >= len(self.source)

    def scanTokens(self):
        """ Scan for tokens until we are at the end of the source """
        while(not self.atEnd()):
            self.start = self.current
            self.scanToken()

        # Add the end-of-file token at the end of the source
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def addToken(self, tokenType: TokenType, literal: object = None):
        lexeme = self.source[self.start:self.current]
        self.tokens.append(Token(tokenType, lexeme, literal, self.line))

    def scanToken(self):
        """ Find a token """
        c = self.advance()
        if   c == '(': self.addToken(TokenType.LEFT_PAREN)
        elif c == ')': self.addToken(TokenType.RIGHT_PAREN)
        elif c == '{': self.addToken(TokenType.LEFT_BRACE)
        elif c == '}': self.addToken(TokenType.RIGHT_BRACE)
        elif c == ',': self.addToken(TokenType.COMMA)
        elif c == '.': self.addToken(TokenType.DOT)
        elif c == '-': self.addToken(TokenType.MINUS)
        elif c == '+': self.addToken(TokenType.PLUS)
        elif c == ';': self.addToken(TokenType.SEMICOLON)
        elif c == '&': self.addToken(TokenType.AMPER)
        elif c == '|': self.addToken(TokenType.BAR)
        elif c == '~': self.addToken(TokenType.TILDE)
        elif c == '^': self.addToken(TokenType.CARET)
        elif c == '*': self.addToken(TokenType.STAR_STAR if self.match('*') else TokenType.STAR)
        elif c == '!': self.addToken(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
        elif c == '=': self.addToken(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
        elif c == '<': self.addToken(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS_LESS if self.match('<') else TokenType.LESS)
        elif c == '>': self.addToken(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER_GREATER if self.match('>') else TokenType.GREATER)
        elif c == '/':
            if self.match('/'):
                # If the next character is a '/' consume the rest of the line
                while self.peek() != '\n' and not self.atEnd():
                    self.advance()
            elif self.match('*'):
                # If the next character is a '*' consume until '*/'
                self.nestedCommentCount += 1
                while not self.atEnd() and self.nestedCommentCount:
                    c = self.advance()
                    if c == '/' and self.match('*'):
                        self.nestedCommentCount += 1
                    elif c == '*' and self.match('/'):
                        self.nestedCommentCount -= 1
            else:
                # Otherwise it is a regular token
                self.addToken(TokenType.SLASH)
        elif c == ' ' or c == '\r' or c == '\t': pass # Consume white space
        elif c == '\n': self.line += 1 # Increment the line
        elif c == '"': self.string() # Get the string
        else:
            if c.isdigit():
                # Look for number literals here instead of adding a case for each
                self.number()
            elif c.isalpha():
                # Look for an identifier
                self.identifier()
            else:
                Lox.Lox.lineError(self.line, f"Unexpected character: {repr(c)}")

    def advance(self) -> str:
        self.current += 1
        return self.source[self.current-1]

    def match(self, expected: str) -> bool:
        """
        Like a conditional advance, only consumes the current character if it
        matches `expected`
        """
        if self.atEnd() or (self.source[self.current] != expected):
            # If we are at the end or the current charcater does not match
            return False
        else:
            # If the character matches consume it and return True
            self.current += 1
            return True

    def peek(self):
        """ Look at the next character but don't consume it """
        if self.atEnd():
            return '\0'
        else:
            return self.source[self.current]

    def peekNext(self):
        """ Look at the next next character but don't consume it """
        if self.current+1 >= len(self.source):
            return '\0'
        else:
            return self.source[self.current+1]

    def string(self):
        """ Consume a string literal """
        while self.peek() != '"' and not self.atEnd():
            if self.peek() == '\n':
                # Advance the line if we hit a new line
                line += 1
            self.advance()

        # If we find an unterminated string
        if self.atEnd():
            Lox.Lox.lineError(self.line, "Unterminated string")
            return

        # Get the closing '"'
        self.advance()

        # Trim the surrounding quote characters
        value = self.source[self.start+1:self.current-1]
        self.addToken(TokenType.STRING, value)

    def number(self):
        """ Consume a number literal """
        while self.peek().isdigit():
            self.advance()

        if self.peek() == '.' and self.peekNext().isdigit():
            # If we hit a DOT followed by a number consume the dot
            self.advance()
            while self.peek().isdigit():
                # Consume the rest of the digits
                self.advance()

        self.addToken(TokenType.NUMBER, float(self.source[self.start:self.current]))

    def identifier(self):
        while self.peek().isalnum():
            self.advance()

        text = self.source[self.start:self.current]
        tokenType = Scanner.keywords.get(text, None)
        if tokenType is None:
            # If we did not find a keyword it is an identifier
            self.addToken(TokenType.IDENTIFIER)
        else:
            # Otherwise it is a keyword
            self.addToken(tokenType)
