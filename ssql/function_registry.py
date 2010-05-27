from ssql.exceptions import QueryException

class FunctionRegistry():
    __shared_dict = dict()
    def __init__(self):
        self.__dict__ = self.__shared_dict
        if len(self.__shared_dict.keys()) == 0:
            self.__functions = dict()
    def register(self, alias, function):
        if alias in self.__functions:
            raise QueryException("'%s' has already been registered" % (alias))
        self.__functions[alias] = function
    def get_function(self, alias):
        if alias not in self.__functions:
            raise QueryException("'%s' is not a registered function" % (alias))
        return self.__functions[alias]
