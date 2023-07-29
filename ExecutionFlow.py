"""
Various classes to control exectuion flow
"""

from Token import Token

class Break(Exception):

    def __init__(self, token: Token) -> None:
        self.token: Token = token

class Continue(Exception):

    def __init__(self, token: Token) -> None:
        self.token: Token = token

