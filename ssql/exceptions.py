class SSQLException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class QueryException(SSQLException):
    pass

class DbException(SSQLException):
    pass

class SettingsException(SSQLException):
    pass
