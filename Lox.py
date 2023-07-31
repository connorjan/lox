#!/usr/bin/env python3

import argparse
import readline # Use GNU readline features for the REPL
import sys

import Expr
import Stmt
from ErrorManager import *
from Token import Token
from Scanner import Scanner
from Parser import Parser
from Interpreter import Interpreter
from Resolver import Resolver

class Lox:

    def __init__(self):
        self.errorManager = ErrorManager()
        self.interpreter = Interpreter(self.errorManager)

    def run(self, source: str) -> None:
        # Scan / lex the source input into a list of tokens
        scanner: Scanner = Scanner(self.errorManager, source)
        tokens: list[Token] = scanner.scanTokens()

        # Convert the list of tokens into an AST
        parser: Parser = Parser(self.errorManager, tokens)
        statements: list[Stmt.Stmt] = parser.parse()

        if self.errorManager.hadError:
            return

        # Pass over the AST and resolve refrences to variables
        resolver: Resolver = Resolver(self.errorManager, self.interpreter)
        resolver.resolve(statements)

        if self.errorManager.hadError:
            return

        # Run the interpreter
        self.interpreter.interpret(statements)

    def runPrompt(self) -> None:
        try:
            while True:
                line = input("> ")
                self.run(line)
                self.errorManager.hadError = False
        except (KeyboardInterrupt, EOFError):
            return

    def runFile(self, file: argparse.FileType) -> None:
        source: str = file.read()
        self.run(source)

        if self.errorManager.hadError:
            sys.exit(1)

def main(args) -> int:
    lox = Lox()
    if args.file:
        lox.runFile(args.file)
    else:
        lox.runPrompt()

    return 0

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", help="A lox script to execute", type=argparse.FileType(mode="r"))
    args = ap.parse_args()
    main(args)
