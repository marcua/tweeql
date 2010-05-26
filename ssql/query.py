class Query():
    def __init__(self, query_tree, source):
        self.query_tree = query_tree
        self.source = source

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
    EXCLAIM_EQUALS = "!="
    NULL = "NULL"
    EMPTY_STRING = ""
    WHERE_CONDITION = "$$$WHERE_CONDITION$$$"
