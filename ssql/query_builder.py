from ssql import operators
from ssql.ssql_parser import gen_parser
from ssql.operators import StatusSource
from ssql.query import Query
from ssql.exceptions import QueryException
from ssql.twitter_fields import twitter_tuple_descriptor

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
        self.unnamed_operator_counter = 0
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
        select = parsed.select.asList()[1:]
        where_clause = parsed.where.asList()
        groupby = parsed.groupby.asList()
        tree = self.__parse_where(where_clause)
        tree = self.__add_aggregate(select, groupby, tree)
        #self.__assign_descriptors(parsed, tree)
        return tree
    def __parse_where(self, where_clause):
        tree = None
        if where_clause == ['']: # no where predicates
            tree = operators.AllowAll() 
        else:
            tree = self.__parse_clauses(where_clause[0][1:])
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
        twitter_td = twitter_tuple_descriptor()
        tuple_descriptor = TupleDescriptor()
        fields_to_verify = []
        for field in chain(select, groupby):
            (field_descriptor, verify) = self.__parse_field(field, twitter_td)
            fields_to_verify.extend(verify)
            tuple_descriptor.add_descriptor(field_descriptor)
        for field in fields_to_verify:
            self.__verify_and_fix_field(field, tuple_descriptor)
        
        # at this point, tuple_descriptor should contain a tuple descriptor
        # with fields/aliases that are correct (we would have gotten an
        # exception otherwise.  built select_descriptor/group_descriptor
        # from it
        select_descriptor = TupleDescriptor()
        group_descriptor = TupleDescriptor()
        for field in select:
            (field_descriptor, verify) = self.__parse_field(field, tuple_descriptor)
            select_decriptor.add_descriptor(field_descriptor)
        for field in group:
            (field_descriptor, verify) = self.__parse_field(field, tuple_descriptor)
            group_decriptor.add_descriptor(field_descriptor)
          
        aggregates = []
        for alias in select_descriptor.aliases:
            select_descriptor.get(
        make sure all select is either an aggregate function or in the group by
        assign tuple descriptors all the way down

        if groupby == ['']:
            return tree 
        return tree
    def __parse_field(self, field, tuple_descriptor, alias_on_complex_types)
        alias = None
        type = None
        underlying = None
        aggregate_factory = None
        function = None
        fields_to_verify = []
        field_backup = field

        self.__clean_list(field)
       
        # parse aliases if they exist
        if (len(field) >= 3) and (field[-2] == QueryTokens.AS):
            alias = field[-1]
            field = field[:-2]

        if len(field) == 1: # field or alias
            if alias == None:
                alias = field[0]
            field_descriptor = tuple_descriptor.get_descriptor(field[0])
            if field_descriptor == None: # underlying field not yet defined.  mark to check later
                type = FieldType.UNDEFINED
                underlying = [field[0]]
                # check alias and underlying once this process is done to
                # find yet-undefined fields
                fields_to_verify.append(field[0])
                fields_to_verify.append(alias)
            else: # field found, copy information
                type = field_descriptor.field_type
                underlying = field_descriptor.underlying_field
                aggregate_factory = field_descriptor.aggregate_factory
                function = field_descriptor.function
        elif len(field) > 1: # function or aggregate  
            if alias == None:
                if alias_on_complex_types:
                    raise QueryException("Must specify alias (AS clause) for '%s'" % ("".join(field)))
                else:
                    self.unnamed_operator_counter += 1
                    alias = "operand%d" % (self.unnamed_operator_counter)
            underlying_fields = field[1:]
            fields_to_verify.extend(underlying_fields)
            aggregate_factory = get_aggregate_factory(field[0])
            if aggregate_factory != None: # found an aggregate function
                type = FieldType.AGGREGATE
            else:
                function = get_function(field[0])
                if function != None:
                    type = FieldType.FUNCTION
                else:
                    raise QueryException("'%s' is neither an aggregate or a registered function" % (field[0]))
        else:
            raise QueryException("Empty field clause found: %s" % ("".join(field_backup))

        fd = FieldDescriptor(alias, underlying_fields, field_type, aggregate_factory, function)
        return (fd, fields_to_verify)
    
    def __verify_and_fix_field(self, field, tuple_descriptor):
        field_descriptor = tuple_descriptor.get_descriptor(field)
        if field_descriptor == None:
            raise QueryException("Field '%s' is neither a builtin field nor an alias" % (field))
        elif field_descriptor.field_type == FieldType.UNDEFINED:
            referenced_field_descriptor = \
                self.__verify_and_fix_field(field_descriptor.underlying_fields[0], tuple_descriptor)
            field_descriptor.underlying_fields = referenced_field_descriptor.underlying_fields
            field_descriptor.field_type = referenced_field_descriptor.field_type
            field_descriptor.aggregate_factory = referenced_field_descriptor.aggregate_factory
            field_descriptor.function = referenced_field_descriptor.function
        return field_descriptor
    def __assign_descriptors(self, parsed, tree):
        # assign root the tupledescriptor
        tree.assign_descriptor(parsed.select)  
