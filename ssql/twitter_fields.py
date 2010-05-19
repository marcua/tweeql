from field_descriptor import FieldDescriptor
from field_descriptor import FieldType
from tuple_descriptor import TupleDescriptor

def twitter_tuple_descriptor():
    fields = [
        FieldDescriptor("status", "status", FieldType.FIELD),
    ]
    return TupleDescriptor(fields)
