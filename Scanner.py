from ErrorManager import ErrorManager
from TokenType import TokenType
from Token import Token

class Scanner:

    KEYWORDS: dict[str, TokenType] = {
        "and":    TokenType.AND,
        "class":  TokenType.CLASS,
        "else":   TokenType.ELSE,
        "false":  TokenType.FALSE,
        "for":    TokenType.FOR,
        "fun":    TokenType.FUN,
        "if":     TokenType.IF,
        "nil":    TokenType.NIL,
        "or":     TokenType.OR,
        "print":  TokenType.PRINT,
        "return": TokenType.RETURN,
        "super":  TokenType.SUPER,
        "this":   TokenType.THIS,
        "true":   TokenType.TRUE,
        "var":    TokenType.VAR,
        "while":  TokenType.WHILE,
    }

    def __init__(self, errorManager: ErrorManager, source: str) -> None:
        self.source = source
        self.errorManager = errorManager
        self.tokens: list[Token] = []

        self.start = 0
        self.current = 0
        self.line = 1

    def atEnd(self) -> bool:
        return self.current >= len(self.source)

    def addToken(self, type_: TokenType, literal: any = None) -> None:
        text: str = self.source[self.start:self.current]
        self.tokens.append(Token(type_, text, literal, self.line))

    def advance(self) -> str:
        c: str = self.source[self.current]
        self.current += 1
        return c

    def match(self, excepted: str) -> bool:
        if self.atEnd():
            return False
        if self.source[self.current] != excepted:
            return False

        self.current += 1
        return True

    def peek(self) -> str:
        if self.atEnd():
            return "\0"
        else:
            return self.source[self.current]

    def peekNext(self) -> str:
        if self.current+1 >= len(self.source):
            return "\0"
        else:
            return self.source[self.current+1]

    def string(self) -> None:
        while self.peek() != "\"" and not self.atEnd():
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.atEnd():
            self.errorManager.scanError(self.line, "Unterminated string.")
            return

        # Consume the closing "
        self.advance()

        # Trim the surrounding quotes and add the token
        self.addToken(TokenType.STRING, self.source[self.start+1:self.current-1])

    def blockcomment(self) -> None:
        while self.peek() != "*" and self.peekNext() != "/" and not self.atEnd():
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.atEnd():
            self.errorManager.scanError(self.line, "Unterminated block comment.")
            return

        # Consume the closing "*/"
        self.advance()
        self.advance()

    def number(self) -> None:
        while self.peek().isnumeric():
            self.advance()

        # Look for the fractional part
        if self.peek() == "." and self.peekNext().isnumeric():
            # Consume the .
            self.advance()

            # Consume the fractional part
            while self.peek().isnumeric():
                self.advance()

        num: str = self.source[self.start:self.current]
        if "." in num:
            self.addToken(TokenType.NUMBER, float(num))
        else:
            self.addToken(TokenType.NUMBER, int(num,0))

    def isalpha(self, c: str) -> bool:
        return c.isalpha() or c == "_"

    def isalphanumeric(self, c: str) -> bool:
        return self.isalpha(c) or c.isnumeric()

    def identifier(self) -> None:
        while self.isalphanumeric(self.peek()):
            self.advance()

        text: str = self.source[self.start:self.current]
        type_: TokenType = Scanner.KEYWORDS.get(text, TokenType.IDENTIFIER)
        self.addToken(type_)

    def scanToken(self) -> None:
        c: str = self.advance()

        match c:
            case "(": self.addToken(TokenType.LEFT_PAREN)
            case ")": self.addToken(TokenType.RIGHT_PAREN)
            case "{": self.addToken(TokenType.LEFT_BRACE)
            case "}": self.addToken(TokenType.RIGHT_BRACE)
            case ",": self.addToken(TokenType.COMMA)
            case ".": self.addToken(TokenType.DOT)
            case "-": self.addToken(TokenType.MINUS)
            case "+": self.addToken(TokenType.PLUS)
            case ";": self.addToken(TokenType.SEMICOLON)
            case "&": self.addToken(TokenType.AMPERSAND)
            case "|": self.addToken(TokenType.BAR)
            case "^": self.addToken(TokenType.CARROT)

            case "!" if self.match("="): self.addToken(TokenType.BANG_EQUAL)
            case "!":                    self.addToken(TokenType.BANG)
            case "=" if self.match("="): self.addToken(TokenType.EQUAL_EQUAL)
            case "=":                    self.addToken(TokenType.EQUAL)
            case "<" if self.match("="): self.addToken(TokenType.LESS_EQUAL)
            case "<":                    self.addToken(TokenType.LESS)
            case ">" if self.match("="): self.addToken(TokenType.GREATER_EQUAL)
            case ">":                    self.addToken(TokenType.GREATER)

            case "*" if self.match("*"): self.addToken(TokenType.STAR_STAR)
            case "*":                    self.addToken(TokenType.STAR)

            case "/":
                if self.match("/"):
                    while self.peek() != "\n" and not self.atEnd():
                        self.advance()
                elif self.match("*"):
                    self.blockcomment()
                else:
                    self.addToken(TokenType.SLASH)

            case " " | "\r" | "\t":
                pass

            case "\n":
                self.line += 1

            case "\"":
                self.string()

            case x if x.isnumeric():
                self.number()

            case x if x.isalpha():
                self.identifier()

            case _:
                self.errorManager.scanError(self.line, "Unexpexted character.")

    def scanTokens(self) -> list[Token]:
        while not self.atEnd():
            self.start = self.current
            self.scanToken()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens
