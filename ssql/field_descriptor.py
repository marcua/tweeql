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
