#!/usr/bin/env python3

import argparse
from typing import List
import os

def defineType(writer, baseName: str, className: str, fieldList: str):
    writer.write(f"\n")
    writer.write(f"class {className}({baseName}):\n")

    # Initializer
    writer.write(f"    def __init__(self, {fieldList}):\n")

    # Store the parameters in class members
    fields = fieldList.split(", ")
    for field in fields:
        name = field.split(": ")[0].strip()
        writer.write(f"        self.{name} = {name}\n")

    # Define the accept method for the visitors
    writer.write("\n")
    writer.write(f"    def accept(self, visitor: Any) -> Any:\n")
    writer.write(f"        return visitor.visit{className}{baseName}(self)\n")

def defineAst(outputDir: str, baseName: str, types: List[str], imports=None) -> None:
    imports = [] if imports is None else imports
    os.makedirs(outputDir, exist_ok=True)
    outputPath = os.path.join(outputDir, f"{baseName}.py")
    with open(outputPath, 'w') as writer:
        writer.write(f"\"\"\"\n")
        writer.write(f"This code provides the classes for the AST expressions\n")
        writer.write(f"It is autogenerated from tools/GenerateAst.py\n")
        writer.write(f"\"\"\"\n")
        writer.write(f"\n")
        writer.write(f"from typing import Any, List\n")
        writer.write(f"from Token import Token\n")
        for import_ in imports:
            writer.write(f"{import_}\n")
        writer.write(f"\n")
        writer.write(f"class {baseName}:\n")
        writer.write("    pass\n")

        for exprType in types:
            className = exprType[:exprType.find(':')].strip()
            fields = exprType[exprType.find(':')+1:].strip()
            defineType(writer, baseName, className, fields)

def main(args):
    defineAst(args.output, "Expr", [
        "Assign   : name: Token, value: Expr",
        "Binary   : left: Expr, operator: Token, right: Expr",
        "Call     : callee: Expr, paren: Token, arguments: List[Expr]",
        "Grouping : expression: Expr",
        "Literal  : value: object",
        "Logical  : left: Expr, operator: Token, right: Expr",
        "Unary    : operator: Token, right: Token",
        "Variable : name: Token"
    ])

    defineAst(args.output, "Stmt", [
        "Block      : statements: List[Stmt]",
        "Expression : expression: Expr.Expr",
        "Function   : name: Token, params: List[Token], body: List[Stmt]",
        "If         : condition: Expr.Expr, thenBranch: Stmt, elseBranch: Stmt",
        "Print      : expression: Expr.Expr",
        "Return     : keyword: Token, value: Expr.Expr",
        "While      : condition: Expr.Expr, body: Stmt",
        "Var        : name: Token, initializer: Expr.Expr"
    ],
    imports=[
        "import Expr"
    ])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate the abstract syntax tree structures")
    parser.add_argument('output', metavar="<output directory>", help="The output directory for the ASTs")
    args = parser.parse_args()
    main(args)
