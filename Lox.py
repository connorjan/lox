#!/usr/bin/env python3

import argparse
import readline # Use GNU readline features for the REPL
import sys

import Expr
from ErrorManager import *
from Token import Token
from Scanner import Scanner
from Parser import Parser
from Interpreter import Interpreter
from AstPrinter import AstPrinter

class Lox:

    def __init__(self):
        self.errorManager = ErrorManager()
        self.interpreter = Interpreter(self.errorManager)

    def run(self, source: str) -> None:
        scanner: Scanner = Scanner(self.errorManager, source)
        tokens: list[Token] = scanner.scanTokens()
        parser: Parser = Parser(self.errorManager, tokens)
        expression: Expr.Expr = parser.parse()

        if self.errorManager.hadError:
            return

        # astPrinter = AstPrinter()
        # print(astPrinter.print(expression))
        self.interpreter.interpret(expression)

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
