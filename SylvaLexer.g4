lexer grammar SylvaLexer ;

options { superClass=BaseSylvaLexer; }

OPEN_BRACKET :             '[' ;
CLOSE_BRACKET :            ']' ;
OPEN_PAREN :               '(' ;
CLOSE_PAREN :              ')' ;
OPEN_BRACE :               '{' ;
CLOSE_BRACE :              {not self.inTemplate}? '}' ;
TEMPLATE_CLOSE_BRACE :     {self.inTemplate}? '}' -> popMode ;
COMMA :                    ',' ;
EQUAL :                    '=' ;
COLON :                    ':' ;
COLON_COLON :              '::' ;
DOT :                      '.' ;
DOT_DOT :                  '..' ;
ELLIPSIS :                 '...' ;
PLUS_PLUS :                '++' ;
MINUS_MINUS :              '--' ;
PLUS :                     '+' ;
MINUS :                    '-' ;
TILDE :                    '~' ;
BANG :                     '!' ;
STAR :                     '*' ;
SLASH :                    '/' ;
SLASH_SLASH :              '//' ;
BACKSLASH :                '\\' ;
PERCENT :                  '%' ;
STAR_STAR :                '**' ;
HASH :                     '#' ;
DOUBLE_OPEN_ANGLE :        '<<' ;
DOUBLE_CLOSE_ANGLE :       '>>' ;
TRIPLE_CLOSE_ANGLE :       '>>>' ;
OPEN_ANGLE :               '<' ;
CLOSE_ANGLE :              '>' ;
OPEN_ANGLE_EQUAL :         '<=' ;
CLOSE_ANGLE_EQUAL :        '>=' ;
EQUAL_EQUAL :              '==' ;
BANG_EQUAL :               '!=' ;
AMP :                      '&' ;
AMP_AMP :                  '&&' ;
CARET :                    '^' ;
PIPE :                     '|' ;
PIPE_PIPE :                '||' ;
STAR_EQUAL :               '*=' ;
SLASH_EQUAL :              '/=' ;
SLASH_SLASH_EQUAL :        '//=' ;
PERCENT_EQUAL :            '%=' ;
PLUS_EQUAL :               '+=' ;
MINUS_EQUAL :              '-=' ;
DOUBLE_OPEN_ANGLE_EQUAL :  '<<=' ;
DOUBLE_CLOSE_ANGLE_EQUAL : '>>=' ;
TRIPLE_CLOSE_ANGLE_EQUAL : '>>>=' ;
AMP_EQUAL :                '&=' ;
CARET_EQUAL :              '^=' ;
PIPE_EQUAL :               '|=' ;
TILDE_EQUAL :              '~=' ;
STAR_STAR_EQUAL :          '**=' ;
AMP_AMP_EQUAL :            '&&=' ;
PIPE_PIPE_EQUAL :          '||=' ;
TRUE :                     'true' ;
FALSE :                    'false' ;
ENUM :                     'enum' ;
FN :                       'fn' ;
FNTYPE :                   'fntype' ;
RANGE :                    'range' ;
STRUCT :                   'struct' ;
VARIANT :                  'variant' ;
CARRAY :                   'carray' ;
CBITFIELD :                'cbitfield' ;
CPTR :                     'cptr' ;
CSTR :                     'cstr' ;
CSTRUCT :                  'cstruct' ;
CUNION :                   'cunion' ;
CVOID :                    'cvoid' ;
CFN :                      'cfn' ;
CFNTYPE :                  'cfntype' ;
CBLOCKFNTYPE :             'cblockfntype' ;
IF :                       'if' ;
ELSE :                     'else' ;
SWITCH :                   'switch' ;
CASE :                     'case' ;
MATCH :                    'match' ;
DEFAULT :                  'default' ;
LOOP :                     'loop' ;
WHILE :                    'while' ;
FOR :                      'for' ;
LET :                      'let' ;
MOD :                      'mod' ;
REQ :                      'req' ;
ALIAS :                    'alias' ;
CONST :                    'const' ;
IMPL :                     'impl' ;
IFACE :                    'iface' ;
BREAK :                    'break' ;
CONTINUE :                 'continue' ;
RETURN :                   'return' ;

// STRING_LITERAL : '"' (NonStringChar | EscapedValue)* '"' ;

DOUBLE_QUOTE : '"' {self.enterTemplate()} -> pushMode(TEMPLATE);

RUNE_LITERAL : '\'' (UnicodeValue | HexByteValue) '\'' ;

INT_DECIMAL : IntNum ;

FLOAT_DECIMAL : (FloatNum Exponent?) | (IntNum Exponent) ;

COMPLEX : ((FloatNum Exponent?) | (DecNum Exponent)) ComplexType ;

FLOAT : ((FloatNum Exponent?) | (DecNum Exponent)) FloatType ;

FLOAT_TYPE : FloatType ;

INTEGER : IntNum IntType ;

INT_TYPE : IntType ;

VALUE : [a-zA-Z_][a-zA-Z0-9_]* ;

COMMENT : '#' .*? [\r\n] -> skip ;

BS : [ \t\r\n]+ -> skip ;

// fragment NonStringChar : ~["\\] ;

// fragment NonStringChar : ~["] ;

fragment NonStringChar : ~["] ;

fragment FloatNum : (DecNum '.' DecNum) | ('.' DecNum) ;

fragment IntNum : (HexNum | DecNum | OctNum | BinNum) ;

fragment HexNum : '0'[Xx][a-fA-F0-9][a-fA-F0-9_]* ;

fragment DecNum : [0-9][0-9_]* ;

fragment OctNum : '0'[Oo][0-7][0-7_]* ;

fragment BinNum : '0'[Bb][0-1][0-1_]* ;

fragment Exponent : [Ee][+-]?[0-9][0-9_]* ;

fragment ComplexType : ('c16' | 'c32' | 'c64' | 'c128') ;

fragment FloatType : ('f16' | 'f32' | 'f64' | 'f128') ;

fragment IntType : [ui]('8' | '16' | '32' | '64' | '128')? ;

fragment HexDigit : [a-fA-F0-9] ;

fragment EscapedValue :
    '\\' (
      'u' HexDigit HexDigit HexDigit HexDigit
      | 'U' HexDigit HexDigit HexDigit HexDigit HexDigit HexDigit HexDigit HexDigit
      | [abfnrtv\\'"{]
      | 'x' HexDigit HexDigit
    )
    ;

fragment UnicodeValue : ~[\r\n'] | LittleUValue | BigUValue | EscapedValue ;

fragment HexByteValue : '\\' 'x'  HexDigit HexDigit ;

fragment LittleUValue : '\\' 'u' HexDigit HexDigit HexDigit HexDigit ;

fragment BigUValue :
  '\\' 'U' HexDigit HexDigit HexDigit HexDigit HexDigit HexDigit HexDigit HexDigit ;

mode TEMPLATE ;

DOUBLE_QUOTE_INSIDE : '"' {self.exitTemplate()} -> type(DOUBLE_QUOTE), popMode ;
STRING_START_EXPRESSION :  '{' -> pushMode(DEFAULT_MODE) ;
STRING_ATOM : (NonStringChar | EscapedValue | BACKSLASH) ;
