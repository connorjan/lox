#!/usr/bin/env python3

import argparse
import os
import sys

import Scanner

class Lox:
    # Static variables
    hadError = False

    @classmethod
    def main(cls, args):
        if args.script:
            cls.runFile(args.script)
        else:
            cls.runPrompt()

    @classmethod
    def runFile(cls, file):
        data = file.read()
        cls.run(data)

        if cls.hadError:
            sys.exit(1)

    @classmethod
    def runPrompt(cls):
        while True:
            try:
                data = input(">> ")
                cls.run(data)
                hadError = False
            except (KeyboardInterrupt, EOFError):
                print("")
                break

    @classmethod
    def run(cls, source):
        scanner = Scanner.Scanner(source)
        tokens = scanner.scanTokens()

        for token in tokens:
            print(token)

    @classmethod
    def error(cls, line, message):
        cls.report(line, "", message)

    @classmethod
    def report(cls, line, where, message):
        print(f"[line {line}] Error {where}: {message}")
        cls.hadError = True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Lox interpreter")
    parser.add_argument('script', nargs='?', type=argparse.FileType('r'), default=None)
    args = parser.parse_args()
    Lox.main(args)
