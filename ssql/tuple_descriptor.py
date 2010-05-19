import copy

class TupleDescriptor():
    def __init__(self, field_descriptors):
        self.aliases = []
        self.descriptors = {}
        for descriptor in field_descriptors:
            self.add_descriptor(descriptor)
    def get_descriptor(self, alias):
        return self.descriptors[alias]
    def duplicate(self):
        return copy.deepcopy(self)
    def add_descriptor(self, descriptor):
        if descriptor.alias in self.descriptors:
            if (self.descriptors[descriptor.alias].field_type != FieldType.UNDEFINED) and
               (self.descriptors[descriptor.alias] != descriptor):
                raise QueryException("The alias '%s' appears more than once in your query" % (descriptor.alias))
        else:
            self.aliases.append(descriptor.alias)
        self.descriptors[descriptor.alias] = descriptor
