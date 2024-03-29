#!/usr/bin/env python3

import argparse
import pathlib
import sys

def defineAst(outputDir: str, baseName: str, imports: str, types: list[str]) -> None:
    path: str = pathlib.Path(outputDir) / f"{baseName}.py"
    with open(path, "w") as o:
        o.write(f"""\
# This file is auto-generated from tool/GenerateAst.py
# Do not modify!

{imports}

class {baseName}:
    pass

""")

        for exprClass in types:
            className: str = exprClass[0]
            fieldList: list[str] = exprClass[1:]

            o.write(f"class {className}({baseName}):\n")
            o.write(f"""    def __init__(self, {", ".join(fieldList)}):\n""")
            for field in fieldList:
                arg, type_ = field.split(": ")
                o.write(f"        self.{arg}: {type_} = {arg}\n")

            o.write("\n")

            o.write( "    def accept(self, visitor: any) -> any:\n")
            o.write(f"        return visitor.visit{className}{baseName}(self)\n")
            o.write("\n")

def main(args) -> int:

    # Create the AST classes for expressions
    defineAst(args.output_dir, "Expr",
       "from Token import Token",
        [
            ["Assign",   "name: Token", "value: Expr"],
            ["Binary",   "left: Expr", "operator: Token", "right: Expr"],
            ["Call",     "callee: Expr", "paren: Token", "arguments: list[Expr]"],
            ["Grouping", "expression: Expr"],
            ["Literal",  "value: any"],
            ["Logical",  "left: Expr", "operator: Token", "right: Expr"],
            ["String",   "value: str"],
            ["Ternary",  "condition: Expr", "trueExpr: Expr", "falseExpr: Expr"],
            ["Unary",    "operator: Token", "right: Expr"],
            ["Variable", "name: Token"],
        ]
    )

    # Create the AST classes for statements
    defineAst(args.output_dir, "Stmt",
        "from Token import Token\n"+
        "from Expr import *",
        [
            ["Block",      "statements: list[Stmt]"],
            ["Control",    "control: Token"],
            ["Expression", "expression: Expr"],
            ["For",        "condition: Expr", "initializer: Stmt", "increment: Stmt", "body: Stmt"],
            ["Function",   "name: Token", "params: list[Token]", "body: list[Stmt]"],
            ["If",         "condition: Expr", "thenBranch: Stmt", "elseBranch: Stmt"],
            ["Print",      "expression: Expr"],
            ["Return",     "keyword: Token", "value: Expr"],
            ["Var",        "name: Token", "initializer: Expr"],
            ["While",      "condition: Expr", "body: Stmt"],
        ]
    )

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Generates the expression classes for Lox")
    ap.add_argument("output_dir", help="The output directory to place the generated AST class file", nargs="?", default=pathlib.Path())
    args = ap.parse_args()
    main(args)
