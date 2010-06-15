class Query():
    def __init__(self, query_tree, source):
        self.query_tree = query_tree
        self.source = source
    def get_tuple_descriptor(self):
        return self.query_tree.get_tuple_descriptor()

class QueryTokens:
    SELECT = "SELECT"
    FROM = "FROM"
    WHERE = "WHERE"
    GROUPBY = "GROUP BY"
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
    EQUALS = "="
    DOUBLE_EQUALS = "=="
    EXCLAIM_EQUALS = "!="
    NULL = "NULL"
    EMPTY_STRING = ""
    NULL_TOKEN = "$$$NULL_TOKEN$$$"
    WHERE_CONDITION = "$$$WHERE_CONDITION$$$"
