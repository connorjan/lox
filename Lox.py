#!/usr/bin/env python3

import argparse
import sys

import Scanner
from Token import Token

class Lox:

    def __init__(self):
        self.hadError = False

    def run(self, source: str) -> None:
        scanner: Scanner.Scanner = Scanner.Scanner(self, source)
        tokens: list[Token] = scanner.scanTokens()

        for token in tokens:
            print(token)

    def runPrompt(self) -> None:
        try:
            while True:
                line = input("> ")
                self.run(line)
                self.hadError = False
        except (KeyboardInterrupt, EOFError):
            return

    def runFile(self, file: argparse.FileType) -> None:
        source: str = file.read()
        self.run(source)

        if self.hadError:
            sys.exit(1)

    def report(self, line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error {where}: {message}")

    def error(self, line: int, message: str) -> None:
        self.report(line, "", message)


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
