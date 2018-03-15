class BeaverError(BrokenPipeError):
    def __init__(self, message, *args):
        self.message = message
        super(BeaverError, self).__init__(message, *args)