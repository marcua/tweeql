class TupleDescriptor():
    def __init__(self, field_descriptors):
        self.aliases = []
        self.descriptors = {}
        for descriptor in field_descriptors:
            if descriptor.alias in self.descriptors:
                raise QueryException("The alias '%s' appears more than once in your query" % (descriptor.alias))
            self.descriptors[descriptor.alias] = descriptor
            self.aliases.append(descriptor.alias)
    def get_descriptor(self, alias):
        return self.descriptors[alias]
