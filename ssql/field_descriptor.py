class FieldType():
    AGGREGATE = "AGGREGATE"  # Returns an aggregate
    FUNCTION = "FUNCTION"    # Returns a function over a field
    FIELD = "FIELD"          # Returns a field from the tuple

class ReturnType():
    STRING = "STRING"

class FieldDescriptor():
    AGGREGATE_KEY = "aggregate_factory"
    FUNCTION_KEY = "function"
    def __init__(self, alias, underlying_fields, field_type, **kwargs):
        self.alias = alias
        self.underlying_fields = underlying_fields
        self.field_type = field_type
        if self.field_type == FieldType.AGGREGATE:
            self.aggregate_factory = kwargs[FieldDescriptor.AGGREGATE_KEY]
        elif self.field_type == FieldType.FUNCTION:
            self.function = kwargs[FieldDescriptor.FUNCTION_KEY]
