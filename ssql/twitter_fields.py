from datetime import datetime
from field_descriptor import FieldDescriptor
from field_descriptor import FieldType
from field_descriptor import ReturnType
from tuple_descriptor import TupleDescriptor

def twitter_user_data_extractor(field):
    def factory():
        def extract(data):
            return getattr(data[TwitterFields.USER], field)
        return extract
    return factory

class TwitterFields:
    TEXT = "text"
    USER = "user"
    LOCATION = "location"
    LANG = "lang"
    CREATED_AT = "created_at"
    PROFILE_IMAGE_URL = "profile_image_url"
    

def twitter_tuple_descriptor():
    fields = [
        FieldDescriptor(TwitterFields.TEXT, [TwitterFields.TEXT], FieldType.FIELD, ReturnType.STRING),
        FieldDescriptor(TwitterFields.LOCATION, [], FieldType.FUNCTION, ReturnType.STRING, None, twitter_user_data_extractor(TwitterFields.LOCATION)),
        FieldDescriptor(TwitterFields.LANG, [], FieldType.FUNCTION, ReturnType.STRING, None, twitter_user_data_extractor(TwitterFields.LANG)),
        FieldDescriptor(TwitterFields.PROFILE_IMAGE_URL, [], FieldType.FUNCTION, ReturnType.STRING, None, twitter_user_data_extractor(TwitterFields.PROFILE_IMAGE_URL)),
        FieldDescriptor(TwitterFields.CREATED_AT, [TwitterFields.CREATED_AT], FieldType.FIELD, ReturnType.DATETIME)
    ]
    return TupleDescriptor(fields)

