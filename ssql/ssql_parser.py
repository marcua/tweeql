# Started with http://pyparsing.wikispaces.com/file/view/simpleSQL.py 
# ( Copyright (c) 2003, Paul McGuire ) and extended from there
#
from pyparsing import Literal, CaselessLiteral, Word, Upcase, delimitedList, Optional, \
    Combine, Group, alphas, nums, alphanums, ParseException, Forward, oneOf, quotedString, \
    ZeroOrMore, restOfLine, Keyword

def gen_parser():
    # define SQL tokens
    selectStmt = Forward()
    selectToken = Keyword("select", caseless=True)
    fromToken   = Keyword("from", caseless=True)

    ident          = Word( alphas, alphanums + "_$" ).setName("identifier")
    columnName     = Upcase( delimitedList( ident, ".", combine=True ) )
    columnNameList = Group( delimitedList( columnName ) )
    tableName      = Upcase( delimitedList( ident, ".", combine=True ) )
    tableNameList  = Group( delimitedList( tableName ) )

    whereExpression = Forward()
    and_ = Keyword("and", caseless=True)
    or_ = Keyword("or", caseless=True)
    in_ = Keyword("in", caseless=True)

    E = CaselessLiteral("E")
    binop = oneOf("= != < > >= <= eq ne lt le gt ge contains", caseless=True)
    arithSign = Word("+-",exact=1)
    realNum = Combine( Optional(arithSign) + ( Word( nums ) + "." + Optional( Word(nums) )  |
                ( "." + Word(nums) ) ) + 
            Optional( E + Optional(arithSign) + Word(nums) ) )
    intNum = Combine( Optional(arithSign) + Word( nums ) + 
            Optional( E + Optional("+") + Word(nums) ) )

    columnRval = realNum | intNum | quotedString | columnName 
    whereCondition = Group(
            ( columnName + binop + columnRval ) |
            ( columnName + in_ + "(" + delimitedList( columnRval ) + ")" ) |
            ( columnName + in_ + "(" + selectStmt + ")" ) |
            ( "(" + whereExpression + ")" )
            )
    whereExpression << whereCondition + ZeroOrMore( ( and_ | or_ ) + whereExpression ) 

    # define the grammar
    selectStmt      << ( selectToken + 
            ( '*' | columnNameList ).setResultsName( "fields" ) + 
            fromToken + 
            tableNameList.setResultsName( "sources" ) + 
            Optional( Group( CaselessLiteral("where") + whereExpression ), "" ).setResultsName("where") )

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
