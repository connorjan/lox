from Token import Token

class RuntimeException(Exception):

    def __init__(self, token: Token, message: str):
        self.message = message
        self.token = token
