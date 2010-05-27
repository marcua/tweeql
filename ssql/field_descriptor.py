class FieldType():
    AGGREGATE = "AGGREGATE"  # Returns an aggregate
    FUNCTION = "FUNCTION"    # Returns a function over a field
    FIELD = "FIELD"          # Returns a field from the tuple
    UNDEFINED = "UNDEFINED"  # Not a legitimate field---shouldn't appear in parsed query

class ReturnType():
    STRING = "STRING"

class FieldDescriptor():
    def __init__(self, alias, underlying_fields, field_type, aggregate_factory=None, function=None):
        self.alias = alias
        self.underlying_fields = underlying_fields
        self.field_type = field_type
        self.aggregate_factory = aggregate_factory
        self.function = function
        self.visible = True
    def __eq__(self, other):
        if isinstance(other, FieldDescriptor):
            return (self.alias == other.alias) and \
               (self.underlying_fields == other.underlying_fields) and \
               (self.field_type == other.field_type) and \
               (self.aggregate_factory == other.aggregate_factory) and \
               (self.function == other.function)
        else:
            return NotImplemented
    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        else:
            return not result

