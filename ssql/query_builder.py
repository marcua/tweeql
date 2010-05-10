from ssql import operators
from ssql.ssql_parser import gen_parser
from ssql.operators import StatusSource
from ssql.query import Query

class QueryTokens:
    TWITTER = "TWITTER"
    TWITTER_SAMPLE = "TWITTER_SAMPLE"
    LPAREN = "("
    RPAREN = ")"
    AND = "AND"
    OR = "OR"

def gen_query_builder():
    return QueryBuilder()

class QueryBuilder:
    def __init__(self):
        self.parser = gen_parser()
    def build(self, query_str):
        parsed = self.parser.parseString(query_str)
        source = self.__get_source(parsed)
        tree = self.__get_tree(parsed)
        query = Query(tree, source)
        return query
    def __get_source(self, parsed):
        source = parsed.sources[0]
        if source == QueryTokens.TWITTER:
            return StatusSource.TWITTER_FILTER
        elif source.startswith(QueryTokens.TWITTER_SAMPLE):
            return StatusSource.TWITTER_SAMPLE
    def __get_tree(self, parsed):
        return self.__parse_multi(parsed.where.asList()[0][1:])
    def __parse_multi(self, groups):
        self.__remove_all(groups, QueryTokens.LPAREN)
        self.__remove_all(groups, QueryTokens.RPAREN)
        if len(groups) == 1:
            return self.__parse_single(groups[0])
        else:
            # ands take precedent over ors, so 
            # A and B or C and D -> (A and B) or (C and D)
            ands = []
            ors = []
            i = 0
            while i < len(groups):
                ands.append(self.__parse_multi(groups[i]))
                # TODO: this can be simplified
                if i+1 == len(groups):
                    ors.append(self.__and_or_single(ands))
                else:
                    if groups[i+1] == QueryTokens.OR:
                        ors.append(self.__and_or_single(ands))
                        ands = []
                    elif groups[i+1] == QueryTokens.AND:
                        pass
                i += 2
            
            if len(ors) == 1:
                return ors[0]
            else:
                return operators.Or(ors)
    def __parse_single(self, clause):
        if len(clause) == 3 and clause[1] == "contains":
            return operators.Contains(clause[2].lstrip("'\"").rstrip("'\""))
    def __remove_all(self, list, token):
        while token in list:
            list.remove(token)
    def __and_or_single(self, ands):
        if len(ands) == 1:
            return ands[0]
        else:
            return operators.And(ands)

