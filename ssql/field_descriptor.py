class FieldType():
    AGGREGATE = "AGGREGATE"  # Returns an aggregate
    FUNCTION = "FUNCTION"    # Returns a function over a field
    FIELD = "FIELD"          # Returns a field from the tuple
    LITERAL = "LITERAL"      # Returns a literal (string, int, or float)
    UNDEFINED = "UNDEFINED"  # Not a legitimate field---shouldn't appear in parsed query

class ReturnType():
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    STRING = "STRING"
    DATETIME = "DATETIME"
    UNDEFINED = "UNDEFINED"  # Not a legitimate type---shouldn't appear in parsed query

class FieldDescriptor():
    def __init__(self, alias, underlying_fields, field_type, return_type, aggregate_factory=None, func_factory=None, literal_value=None):
        self.alias = alias
        self.underlying_fields = underlying_fields
        self.field_type = field_type
        self.return_type = return_type
        self.aggregate_factory = aggregate_factory
        self.func_factory = func_factory
        self.function = None
        if func_factory != None:
            self.function = func_factory()
        self.literal_value = literal_value
        self.visible = True
    def __eq__(self, other):
        if isinstance(other, FieldDescriptor):
            return (self.alias == other.alias) and \
               (self.underlying_fields == other.underlying_fields) and \
               (self.field_type == other.field_type) and \
               (self.return_type == other.return_type) and \
               (self.aggregate_factory == other.aggregate_factory) and \
               (self.func_factory == other.func_factory) and \
               (self.literal_value == other.literal_value)
        else:
            return NotImplemented
    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        else:
            return not result
