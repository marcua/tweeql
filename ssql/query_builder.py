from ssql import operators
from ssql.ssql_parser import gen_parser
from ssql.operators import StatusSource
from ssql.query import Query
from ssql.exceptions import QueryException

class QueryTokens:
    TWITTER = "TWITTER"
    TWITTER_SAMPLE = "TWITTER_SAMPLE"
    LPAREN = "("
    RPAREN = ")"
    AND = "AND"
    OR = "OR"
    CONTAINS = "CONTAINS"

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
        else:
            raise QueryException('Unknown query source: %s' % (source))
    def __get_tree(self, parsed):
        select = parsed.select.asList() #self.__generate_descriptors(parsed.select.asList())
        groupby = parsed.groupby.asList() #self.__generate_descriptors(parsed.groupby.asList())
        where_clause = parsed.where.asList()
        tree = None
        if where_clause == ['']: # no where predicates
            tree = operators.AllowAll() 
        else:
            tree = self.__parse_clauses(where_clause[0][1:])
        #tree = self.__add_aggregate(select, groupby[0][1:], tree)
        #self.__assign_descriptors(parsed, tree)
        return tree
    def __parse_clauses(self, clauses):
        self.__clean_list(clauses)
        if type(clauses) != list: # This is a token, not an expression 
            return clauses
        elif type(clauses[0]) != list: # This is an operator expression
            return self.__parse_operator(clauses)
        else: # This is a combination of expressions w/ AND/OR
            # ands take precedent over ors, so 
            # A and B or C and D -> (A and B) or (C and D)
            ands = []
            ors = []
            i = 0
            while i < len(clauses):
                ands.append(self.__parse_clauses(clauses[i]))
                if i+1 == len(clauses):
                    ors.append(self.__and_or_single(ands))
                else:
                    if clauses[i+1] == QueryTokens.OR:
                        ors.append(self.__and_or_single(ands))
                        ands = []
                    elif clauses[i+1] == QueryTokens.AND:
                        pass
                i += 2
            # TODO: rewrite __and_or_single to handle the ors below just
            # like it does the ands above 
            if len(ors) == 1:
                return ors[0]
            else:
                return operators.Or(ors)
    def __parse_operator(self, clause):
        if len(clause) == 3 and clause[1] == QueryTokens.CONTAINS:
            return operators.Contains(clause[2])
    def __clean_list(self, list):
        self.__remove_all(list, QueryTokens.LPAREN)
        self.__remove_all(list, QueryTokens.RPAREN)

    def __remove_all(self, list, token):
        while token in list:
            list.remove(token)
    def __and_or_single(self, ands):
        if len(ands) == 1:
            return ands[0]
        else:
            return operators.And(ands)
    def __add_aggregate(self, select, groupby, tree):
        # TODO: verify that nothing in FROM is outside of GROUP BY/Aggregate
        if groupby == ['']:
            return tree 
        return tree
                
    def __assign_descriptors(self, parsed, tree):
        # assign root the tupledescriptor
        tree.assign_descriptor(parsed.select)  
