class Query():
    def __init__(self, query_tree, source):
        self.query_tree = query_tree
        self.source = source

class QueryTokens:
    SELECT = "SELECT"
    FROM = "FROM"
    WHERE = "WHERE"
    GROUPBY = "GROUP BY"
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
    TEXT = "text" # TODO: this is a field name.  should it be in QueryTokens?
    WHERE_CONDITION = "$$$WHERE_CONDITION$$$"
