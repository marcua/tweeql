# Started with http://pyparsing.wikispaces.com/file/view/simpleSQL.py 
# ( Copyright (c) 2003, Paul McGuire ) and extended from there
#
from pyparsing import Literal, CaselessLiteral, Word, upcaseTokens, delimitedList, Optional, \
    Combine, Group, alphas, nums, alphanums, ParseException, Forward, oneOf, quotedString, \
    ZeroOrMore, restOfLine, Keyword, removeQuotes, downcaseTokens
from tweeql.query import QueryTokens

def gen_parser():
    # define SQL tokens
    selectStmt = Forward()
    selectToken = Keyword(QueryTokens.SELECT, caseless=True)
    fromToken   = Keyword(QueryTokens.FROM, caseless=True)
    intoToken   = Keyword(QueryTokens.INTO, caseless=True)
    groupByToken   = Keyword(QueryTokens.GROUPBY, caseless=True)
    windowToken   = Keyword(QueryTokens.WINDOW, caseless=True)
    asToken = Keyword(QueryTokens.AS, caseless=True).setParseAction(upcaseTokens)
    nullToken = Keyword(QueryTokens.NULL, caseless=False).setParseAction(replace(QueryTokens.NULL_TOKEN))
    
    # Math operators
    E = CaselessLiteral("E")
    binop = oneOf("= != < > >= <= == eq ne lt le gt ge %s" % (QueryTokens.CONTAINS), caseless=True).setParseAction(upcaseTokens)
    arithSign = Word("+-",exact=1)
    realNum = Combine( Optional(arithSign) + ( Word( nums ) + "." + Optional( Word(nums) )  |
                ( "." + Word(nums) ) ) + 
            Optional( E + Optional(arithSign) + Word(nums) ) )
    intNum = Combine( Optional(arithSign) + Word( nums ) + 
            Optional( E + Optional("+") + Word(nums) ) )

    ident          = Word( alphas, alphanums + "_$" ).setName("identifier")
    columnName     = delimitedList( ident, ".", combine=True )
    columnName.setParseAction(label(QueryTokens.COLUMN_NAME))
    aliasName     = delimitedList( ident, ".", combine=True )
    stringLiteral = Forward()
    stringLiteral << quotedString
    stringLiteral.setParseAction(label(QueryTokens.STRING_LITERAL))
    intLiteral = Forward()
    intLiteral << intNum
    intLiteral.setParseAction(label(QueryTokens.INTEGER_LITERAL))
    floatLiteral = Forward()
    floatLiteral << realNum
    floatLiteral.setParseAction(label(QueryTokens.FLOAT_LITERAL))
    columnExpression = Forward()
    columnFunction = Word(alphas, alphanums) + "(" + Optional(delimitedList(Group( floatLiteral ) | Group ( stringLiteral ) | Group( intLiteral ) | columnExpression)) + ")" 
    columnFunction.setParseAction(label(QueryTokens.FUNCTION_OR_AGGREGATE))
    columnExpression << Group ( (columnFunction | columnName) + Optional( asToken + aliasName ) )
    columnExpressionList = Group( delimitedList( columnExpression ) )
    tableName      = delimitedList( ident, ".", combine=True ).setParseAction(upcaseTokens)
    tableNameList  = Group( delimitedList( tableName ) )
    timeExpression = Word( nums ) + oneOf("seconds minutes hours days", caseless=True).setParseAction(downcaseTokens)
   
    stdoutToken = Keyword(QueryTokens.STDOUT, caseless=True).setParseAction(upcaseTokens)
    tableToken = Keyword(QueryTokens.TABLE, caseless=True).setParseAction(upcaseTokens)
    streamToken = Keyword(QueryTokens.STREAM, caseless=True).setParseAction(upcaseTokens)
    intoLocation = stdoutToken | ( tableToken + ident ) | ( streamToken + ident ) 

    whereExpression = Forward()
    and_ = Keyword(QueryTokens.AND, caseless=True).setParseAction(upcaseTokens)
    or_ = Keyword(QueryTokens.OR, caseless=True).setParseAction(upcaseTokens)
    in_ = Keyword(QueryTokens.IN, caseless=True).setParseAction(upcaseTokens)

    columnRval = realNum | intNum | nullToken | columnExpression | quotedString.setParseAction(removeQuotes)
    whereCondition = Group(
            ( columnExpression + binop + columnRval ).setParseAction(label(QueryTokens.WHERE_CONDITION)) |
            ( columnExpression + in_ + "(" + delimitedList( columnRval ) + ")" ).setParseAction(label(QueryTokens.WHERE_CONDITION)) |
            ( columnExpression + in_ + "(" + selectStmt + ")" ).setParseAction(label(QueryTokens.WHERE_CONDITION)) |
            ( "(" + whereExpression + ")" )
            )
    whereExpression << whereCondition + ZeroOrMore( ( and_ | or_ ) + whereExpression ) 

    # define the grammar
    selectStmt      << (  
            Group ( selectToken + columnExpressionList ).setResultsName( "select" ) + 
            fromToken + 
            tableNameList.setResultsName( "sources" ) + 
            Optional(intoToken + intoLocation, "").setResultsName("into") + 
            Optional( Group( CaselessLiteral(QueryTokens.WHERE) + whereExpression ), "" ).setResultsName("where") +
            Optional ( groupByToken + columnExpressionList, "").setResultsName("groupby") +
            Optional ( windowToken + timeExpression, "").setResultsName("window")
            )

    parser = selectStmt

    # define Oracle comment format, and ignore them
    oracleSqlComment = "--" + restOfLine
    parser.ignore( oracleSqlComment )
    
    return parser

def test( str ):
    print str,"->"
    parser = gen_parser()
    try:
        tokens = parser.parseString( str )
        print "tokens = ",        tokens
        print "tokens.fields =", tokens.fields
        print "tokens.sources =",  tokens.sources
        print "tokens.where =", tokens.where
    except ParseException, err:
        print " "*err.loc + "^\n" + err.msg
        print err
    print

def label(l):
    """
        Returns a parseaction which prepends the tokens with the label l
    """
    def action(string, loc, tokens):
        newlist = [l]
        newlist.extend(tokens)
        return newlist
    return action

def replace(l):
    """
        Returns a parseaction which replaces the tokens with the token l
    """
    def action(string, loc, tokens):
        return [l]
    return action

def runtests():
    test( "SELECT * from XYZZY, ABC" )
    test( "select * from SYS.XYZZY" )
    test( "Select A from Sys.dual" )
    test( "Select A,B,C from Sys.dual" )
    test( "Select A, B, C from Sys.dual" )
    test( "Select A, B, C from Sys.dual, Table2   " )
    test( "Xelect A, B, C from Sys.dual" )
    test( "Select A, B, C frox Sys.dual" )
    test( "Select" )
    test( "Select &&& frox Sys.dual" )
    test( "Select A from Sys.dual where a in ('RED','GREEN','BLUE')" )
    test( "Select A from Sys.dual where a in ('RED','GREEN','BLUE') and b in (10,20,30)" )
    test( "Select A from Sys.dual where (a in ('RED','GREEN','BLUE') and b in (10,20,30)) OR (b in (10,20,30))" )
    test( "Select A,b from table1,table2 where table1.id eq table2.id -- test out comparison operators" )

if __name__ == '__main__':
    runtests()

"""
Test output:
>pythonw -u simpleSQL.py
SELECT * from XYZZY, ABC ->
tokens =  ['select', '*', 'from', ['XYZZY', 'ABC']]
tokens.fields = *
tokens.sources = ['XYZZY', 'ABC']

select * from SYS.XYZZY ->
tokens =  ['select', '*', 'from', ['SYS.XYZZY']]
tokens.fields = *
tokens.sources = ['SYS.XYZZY']

Select A from Sys.dual ->
tokens =  ['select', ['A'], 'from', ['SYS.DUAL']]
tokens.fields = ['A']
tokens.sources = ['SYS.DUAL']

Select A,B,C from Sys.dual ->
tokens =  ['select', ['A', 'B', 'C'], 'from', ['SYS.DUAL']]
tokens.fields = ['A', 'B', 'C']
tokens.sources = ['SYS.DUAL']

Select A, B, C from Sys.dual ->
tokens =  ['select', ['A', 'B', 'C'], 'from', ['SYS.DUAL']]
tokens.fields = ['A', 'B', 'C']
tokens.sources = ['SYS.DUAL']

Select A, B, C from Sys.dual, Table2    ->
tokens =  ['select', ['A', 'B', 'C'], 'from', ['SYS.DUAL', 'TABLE2']]
tokens.fields = ['A', 'B', 'C']
tokens.sources = ['SYS.DUAL', 'TABLE2']

Xelect A, B, C from Sys.dual ->
^
Expected 'select'
Expected 'select' (0), (1,1)

Select A, B, C frox Sys.dual ->
               ^
Expected 'from'
Expected 'from' (15), (1,16)

Select ->
      ^
Expected '*'
Expected '*' (6), (1,7)

Select &&& frox Sys.dual ->
       ^
Expected '*'
Expected '*' (7), (1,8)

>Exit code: 0
"""
