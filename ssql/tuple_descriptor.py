import copy
from field_descriptor import FieldDescriptor
from field_descriptor import FieldType
from ssql.exceptions import QueryException

class Tuple():
    def __init__(self):
        self.__tuple_descriptor = None
        self.__data = None
    def set_data(self, data):
        self.__data = data
    def set_tuple_descriptor(self, tuple_descriptor):
        self.__tuple_descriptor = tuple_descriptor
    def get_tuple_descriptor(self):
        return self.__tuple_descriptor
    def __getattr__(self, attr):
        field_descriptor = self.__tuple_descriptor.get_descriptor(attr)
        result = None
        if field_descriptor.field_type == FieldType.FUNCTION:
            uf = field_descriptor.underlying_fields
            func = field_descriptor.function
            args = [getattr(self, field) for field in uf]
            args.insert(0, self.__data)
            result = func(*args)
        elif field_descriptor.underlying_fields[0] in self.__data:
            result = self.__data[field_descriptor.underlying_fields[0]]
        else:
            raise QueryException("Attribute not defined: %s" % (attr))
        setattr(self, attr, result)
        return result
    def generate_from_descriptor(self, tuple_descriptor):
        """
            Builds a new tuple from this one based on the tuple_descriptor that
            is passed in.
        """
        d = {}
        for alias in tuple_descriptor.aliases:
            fields = self.__tuple_descriptor.get_descriptor(alias).underlying_fields
            for field in fields:
                d[field] = getattr(self, field)
        t = Tuple()
        t.set_tuple_descriptor(tuple_descriptor)
        t.set_data(d)
        return t

class TupleDescriptor():
    def __init__(self, field_descriptors = []):
        self.aliases = []
        self.descriptors = {}
        for descriptor in field_descriptors:
            self.add_descriptor(descriptor)
    def get_descriptor(self, alias):
        return self.descriptors.get(alias)
    def duplicate(self):
        return copy.deepcopy(self)
    def add_descriptor_list(self, descriptors):
        for descriptor in descriptors:
            self.add_descriptor(descriptor)
    def add_descriptor(self, descriptor):
        visible = descriptor.visible
        copy_descriptor = True
        if descriptor.alias in self.descriptors:
            if (self.descriptors[descriptor.alias].field_type != FieldType.UNDEFINED) and \
               (descriptor.field_type != FieldType.UNDEFINED) and \
               (self.descriptors[descriptor.alias] != descriptor):
                raise QueryException("The alias '%s' appears more than once in your query" % (descriptor.alias))
            # if one of the descriptors is visible, mark the stored one as
            # visible.
            visible = self.descriptors[descriptor.alias].visible or descriptor.visible
            if descriptor.field_type == FieldType.UNDEFINED:
                copy_descriptor = False
        else:
            self.aliases.append(descriptor.alias)
        if copy_descriptor:
            self.descriptors[descriptor.alias] = descriptor #copy.deepcopy(descriptor)
        self.descriptors[descriptor.alias].visible = visible
