from RuntimeException import RuntimeException
from Token import Token

class Break(RuntimeException):
    """ Custom exception class to handle break statements """

    def __init__(self, keyword: Token):
        super().__init__(keyword, "Cannot break outside of a loop")

class Continue(RuntimeException):
    """ Custom exception class to handle continue statements """

    def __init__(self, keyword: Token):
        super().__init__(keyword, "Cannot continue outside of a loop")

class Return(RuntimeException):
    """ Custom exception class to handle return values """

    def __init__(self, keyword: Token, value: object):
        super().__init__(keyword, "Cannot return from outside a function")
        self.value = value
