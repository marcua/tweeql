from datetime import datetime
from field_descriptor import FieldDescriptor
from field_descriptor import FieldType
from tuple_descriptor import TupleDescriptor

def twitter_user_data_extractor(field):
    def extract(data):
        return getattr(data[TwitterFields.USER], field)
    return extract

def created_time(data):
    return datetime.strptime(data[TwitterFields.CREATED_AT], "%a %b %d %H:%M:%S %z %Y")

class TwitterFields:
    TEXT = "text"
    USER = "user"
    LOCATION = "location"
    CREATED_AT = "created_at"

    created_field = FieldDescriptor(CREATED_AT, [CREATED_AT], FieldType.FIELD)
    #created_field = FieldDescriptor(CREATED_AT, [], FieldType.FUNCTION, None, created_time)
    

def twitter_tuple_descriptor():
    fields = [
        FieldDescriptor(TwitterFields.TEXT, [TwitterFields.TEXT], FieldType.FIELD),
        FieldDescriptor(TwitterFields.LOCATION, [], FieldType.FUNCTION, None, twitter_user_data_extractor(TwitterFields.LOCATION)),
        TwitterFields.created_field,
    ]
    return TupleDescriptor(fields)

