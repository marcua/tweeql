from tweeql.exceptions import QueryException

class StreamTypes():
    STREAMING = 1
    STATIC = 2

class StreamInformation():
    def __init__(self, stream_type, tuple_descriptor, stream_querier):
        self.stream_type = stream_type
        self.tuple_descriptor = tuple_descriptor
        self.stream_querier = stream_querier

class StreamRegistry():
    __shared_dict = dict()
    def __init__(self):
        self.__dict__ = self.__shared_dict
        if len(self.__shared_dict.keys()) == 0:
            self.__streams = dict()
    def register(self, alias, stream_information):
        if alias in self.__streams:
            raise QueryException("'%s' has already been registered" % (alias))
        self.__streams[alias] = stream_information
    def get_stream(self, alias):
        if alias not in self.__streams:
            raise QueryException("'%s' is not a registered stream" % (alias))
        return self.__streams[alias]
