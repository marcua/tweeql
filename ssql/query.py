class Query():
    def __init__(self, query_tree, source, handler):
        self.query_tree = query_tree
        self.source = source
        self.handler = handler
    def get_tuple_descriptor(self):
        return self.query_tree.get_tuple_descriptor()

class QueryTokens:
    SELECT = "SELECT"
    FROM = "FROM"
    WHERE = "WHERE"
    GROUPBY = "GROUP BY"
    INTO = "INTO"
    WINDOW = "WINDOW"
    TWITTER = "TWITTER"
    TWITTER_SAMPLE = "TWITTER_SAMPLE"
    LPAREN = "("
    RPAREN = ")"
    AND = "AND"
    OR = "OR"
    CONTAINS = "CONTAINS"
    AS = "AS"
    IN = "IN"
    AVG = "AVG"
    COUNT = "COUNT"
    SUM = "SUM"
    MIN = "MIN"
    MAX = "MAX"
    STDOUT = "STDOUT"
    TABLE = "TABLE"
    STREAM = "STREAM"
    EQUALS = "="
    DOUBLE_EQUALS = "=="
    EXCLAIM_EQUALS = "!="
    NULL = "NULL"
    EMPTY_STRING = ""
    STRING_LITERAL = "$$$STRING_LITERAL$$$"
    INTEGER_LITERAL = "$$$INTEGER_LITERAL$$$"
    FLOAT_LITERAL = "$$$FLOAT_LITERAL$$$"
    NULL_TOKEN = "$$$NULL_TOKEN$$$"
    WHERE_CONDITION = "$$$WHERE_CONDITION$$$"
    FUNCTION_OR_AGGREGATE = "$$$FUNCTION_OR_AGGREGATE$$$"
    COLUMN_NAME = "$$$COLUMN_NAME$$$"
