#!/usr/bin/env python3

import argparse
import os
import sys

import AstPrinter
import Parser
import Scanner
import Interpreter
from LoxError import LoxError
from RuntimeException import RuntimeException
from Token import Token
from TokenType import TokenType

class Lox:
    # Static properties
    interpreter = Interpreter.Interpreter()

    @classmethod
    def main(cls, args) -> None:
        if args.script:
            cls.runFile(args.script)
        else:
            if not os.name == "nt":
                # If not running on Windows add support for GNU readline
                import readline
                readline.parse_and_bind("tab: complete")
            cls.runPrompt()

    @classmethod
    def runFile(cls, file) -> None:
        data = file.read()
        cls.run(data)

        if LoxError.hadError or LoxError.hadRuntimeError:
            sys.exit(1)

    @classmethod
    def runPrompt(cls) -> None:
        while True:
            try:
                data = input(">> ")
                cls.run(data)
                LoxError.hadError = False
            except (KeyboardInterrupt, EOFError):
                print("")
                break

    @classmethod
    def run(cls, source: str) -> None:
        scanner = Scanner.Scanner(source)
        tokens = scanner.scanTokens()

        parser = Parser.Parser(tokens)
        statements = parser.parse()

        if LoxError.hadError:
            return
        else:
            cls.interpreter.interpret(statements)

    @classmethod
    def report(cls, line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error {where}: {message}")
        LoxError.hadError = True

    @classmethod
    def lineError(cls, line: int, message: str) -> None:
        cls.report(line, "", message)

    @classmethod
    def tokenError(cls, token: Token, message: str) -> None:
        if token.type == TokenType.EOF:
            cls.report(token.line, "at end", message)
        else:
            cls.report(token.line, f"at '{token.lexeme}'", message)

    @classmethod
    def runtimeError(cls, error: RuntimeException):
        print(f"{error.__class__.__name__}: {error.message}\n[line {error.token.line}]")
        LoxError.hadRuntimeError = True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Lox interpreter")
    parser.add_argument('script', nargs='?', type=argparse.FileType('r'), default=None)
    args = parser.parse_args()
    Lox.main(args)
