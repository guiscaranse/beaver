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


class InsufficientText(BrokenPipeError):
    def __init__(self, message, *args):
        self.message = message
        super(InsufficientText, self).__init__(message, *args)


class IncompatibleLanguage(BrokenPipeError):
    def __init__(self, message, *args):
        self.message = message
        super(IncompatibleLanguage, self).__init__(message, *args)
