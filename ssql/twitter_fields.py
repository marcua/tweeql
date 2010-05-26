from field_descriptor import FieldDescriptor
from field_descriptor import FieldType
from tuple_descriptor import TupleDescriptor


def twitter_tuple_descriptor():
    fields = [
        FieldDescriptor("text", ["text"], FieldType.FIELD),
        FieldDescriptor("location", [], FieldType.FUNCTION, None, twitter_user_data_extractor("location")),
    ]
    return TupleDescriptor(fields)

def twitter_user_data_extractor(field):
    def extract(data):
        return getattr(data["user"], field)
    return extract
