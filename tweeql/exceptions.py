class TweeQLException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class QueryException(TweeQLException):
    pass

class DbException(TweeQLException):
    pass

class SettingsException(TweeQLException):
    pass
