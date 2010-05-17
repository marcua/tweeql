from field_descriptor import FieldDescriptor
from field_descriptor import FieldType

class Tuple():
    def __init__(self, data, tuple_descriptor):
        self.tuple_descriptor = tuple_descriptor
    def set_data(data):
        self.__dict__ = data.__dict__
    def set_dict(dict):
        self.__dict__ = dict
    def __getattr__(self, attr):
        field_descriptor = self.tuple_descriptor.get_descriptor(attr)
        if field_descriptor.field_type == FieldType.FUNCTION:
            uf = field_descriptor.underlying_fields
            func = field_descriptor.function
            args = [getattr(self, field) for field in uf]
            result = func(*args)
            setattr(self, attr, result)
            return result
        else:
            raise QueryException("Attribute not defined: %s" % (attr))
    def generate_from_descriptor(self, tuple_descriptor):
        """
            Builds a new tuple from this one based on the tuple_descriptor that
            is passed in.
        """
        tuple = Tuple(tuple_descriptor)
        dict = {}
        for alias in tuple_descriptor.aliases:
            fields = self.tuple_descriptor.get_descriptor(alias).underlying_fields
            for field in fields:
                dict[field] = getattr(self, field)
        tuple.set_dict(dict)
