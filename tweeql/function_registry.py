from tweeql.exceptions import QueryException

class FunctionInformation():
    def __init__(self, func_factory, return_type):
        self.func_factory = func_factory
        self.return_type = return_type

class FunctionRegistry():
    __shared_dict = dict()
    def __init__(self):
        self.__dict__ = self.__shared_dict
        if len(self.__shared_dict.keys()) == 0:
            self.__functions = dict()
    def register(self, alias, function_information):
        if alias in self.__functions:
            raise QueryException("'%s' has already been registered" % (alias))
        self.__functions[alias] = function_information
    def get_function(self, alias):
        if alias not in self.__functions:
            raise QueryException("'%s' is not a registered function" % (alias))
        return self.__functions[alias]
