from field_descriptor import FieldDescriptor
from field_descriptor import FieldType

class Tuple():
    def __init__(self, data, tuple_descriptor):
        self.__dict__ = data.__dict__
        self.tuple_descriptor = tuple_descriptor
    def __getattr__(self, attr):
        field_descriptor = self.tuple_descriptor.get_description(attr)
        if field_descriptor.field_type == FieldType.FUNCTION:
            uf = field_descriptor.underlying_fields
            func = field_descriptor.function
            args = [getattr(self, field) for field in uf]
            result = func(*args)
            setattr(self, attr, result)
            return result
        else:
            raise QueryException("Attribute not defined: %s" % (attr))
