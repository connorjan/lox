from RuntimeException import RuntimeException

class Return(RuntimeException):
    """ Custom exception class to handle return values """

    def __init__(self, value: object):
        self.value = value
