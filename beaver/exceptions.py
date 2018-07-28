class BeaverError(BrokenPipeError):
    def __init__(self, message, *args):
        self.message = message
        super(BeaverError, self).__init__(message, *args)


class TimeError(BrokenPipeError):
    def __init__(self, message, *args):
        self.message = message
        super(TimeError, self).__init__(message, *args)


class NoTextDataFound(BrokenPipeError):
    def __init__(self, message, *args):
        self.message = message
        super(NoTextDataFound, self).__init__(message, *args)
