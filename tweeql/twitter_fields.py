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
    SSQL_USER_ID = "user_id"
    TWITTER_USER_ID = "id"
    SCREEN_NAME = "screen_name"
    LOCATION = "location"
    LANG = "lang"
    CREATED_AT = "created_at"
    PROFILE_IMAGE_URL = "profile_image_url"
    
# built here so we can refer to this field in the GroupBy operator. 
TwitterFields.created_field = FieldDescriptor(TwitterFields.CREATED_AT, [TwitterFields.CREATED_AT], FieldType.FIELD, ReturnType.DATETIME)

def twitter_tuple_descriptor():
    fields = [
        FieldDescriptor(TwitterFields.TEXT, [TwitterFields.TEXT], FieldType.FIELD, ReturnType.STRING),
        FieldDescriptor(TwitterFields.LOCATION, [], FieldType.FUNCTION, ReturnType.STRING, None, twitter_user_data_extractor(TwitterFields.LOCATION)),
        FieldDescriptor(TwitterFields.LANG, [], FieldType.FUNCTION, ReturnType.STRING, None, twitter_user_data_extractor(TwitterFields.LANG)),
        FieldDescriptor(TwitterFields.PROFILE_IMAGE_URL, [], FieldType.FUNCTION, ReturnType.STRING, None, twitter_user_data_extractor(TwitterFields.PROFILE_IMAGE_URL)),
        FieldDescriptor(TwitterFields.SSQL_USER_ID, [], FieldType.FUNCTION, ReturnType.INTEGER, None, twitter_user_data_extractor(TwitterFields.TWITTER_USER_ID)),
        FieldDescriptor(TwitterFields.SCREEN_NAME, [], FieldType.FUNCTION, ReturnType.STRING, None, twitter_user_data_extractor(TwitterFields.SCREEN_NAME)),
        TwitterFields.created_field,
    ]
    return TupleDescriptor(fields)

