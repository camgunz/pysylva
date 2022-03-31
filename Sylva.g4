grammar Sylva;

module :
  moduleDecl (
    requirementDecl
    | enumTypeDef
    | functionTypeDef
    | interfaceTypeDef
    | rangeTypeDef
    | structTypeDef
    | variantTypeDef
    | aliasDef
    | constDef
    | functionDef
    | implementationDef
    | cblockfunctionTypeDef
    | cfunctionTypeDef
    | cstructTypeDef
    | cunionTypeDef
  )* (moduleDecl | EOF) ;

aliasDef : 'alias' singleIdentifier ':' (identifier | typeLiteral) ;

constDef : 'const' singleIdentifier ':' constExpr ;

functionDef : 'fn' singleIdentifier functionLiteral ;

implementationDef :
  'impl' strictIdentifier '(' strictIdentifier ')' '{' functionDef* '}' ;

moduleDecl : 'mod' strictIdentifier ;

requirementDecl : 'req' strictIdentifier ;

enumTypeDef : 'enum' singleIdentifier '{' constExprPairList '}' ;

functionTypeDef : 'fntype' singleIdentifier functionTypeLiteral ;

interfaceTypeDef : 'iface' singleIdentifier '{' (functionDef | functionTypeDef)* '}' ;

rangeTypeDef : 'range' singleIdentifier rangeTypeLiteral;

structTypeDef : 'struct' singleIdentifier ('(' valueList ')')? structTypeLiteral ;

variantTypeDef :
  'variant' singleIdentifier ('(' valueList ')')? '{' typeLiteralPairList '}' ;

cblockfunctionTypeDef : 'cblockfntype' singleIdentifier functionTypeLiteral ;

cfunctionTypeDef : 'cfn' singleIdentifier functionTypeLiteral ;

cstructTypeDef : 'cstruct' singleIdentifier '{' typeLiteralPairList '}' ;

cunionTypeDef : 'cunion' singleIdentifier '{' typeLiteralPairList '}' ;

ifBlock : 'if' '(' expr ')' codeBlock ('else' (ifBlock | codeBlock))? ;

switchBlock :
  'switch' '(' expr ')' '{' (defaultBlock | (caseBlock+ defaultBlock?)) '}' ;

caseBlock: 'case' '(' constExpr ')' codeBlock ;

matchBlock :
  'match' '(' expr ')' '{' (
    (matchCaseBlock+ defaultBlock?) | defaultBlock
  ) '}' ;

param : '*'? singleIdentifier | '&' singleIdentifier '!'? ;

matchCaseBlock: 'case' '(' param ':' singleIdentifier ')' codeBlock ;

defaultBlock: 'default' codeBlock ;

forBlock : 'for' '(' param ':' (expr | rangeTypeLiteral) ')' codeBlock ;

whileBlock : 'while' '(' expr ')' codeBlock ;

loopBlock : 'loop' codeBlock ;

breakStmt : 'break' ;

continueStmt : 'continue' ;

letStmt : 'let' singleIdentifier '!'? ':' expr ;

returnStmt : 'return' expr ;

exprList : (expr ',')* (expr ','?)? ;

expr :
  literal                                                # LiteralExpr
  | '(' exprList ')'                                     # ParenExpr
  | '[' exprList ']'                                     # ArrayExpr
  | (identifier | carrayTypeLiteral) arrayConstLiteral   # CArrayLiteralExpr
  | 'cptr' '(' expr ')'                                  # CPointerLiteralExpr
  | (identifier | cstructTypeLiteral) '{' exprList '}'   # CStructLiteralExpr
  | (identifier | cunionTypeLiteral) '{' exprList '}'    # CUnionLiteralExpr
  | 'cvoid' '(' expr ')'                                 # CVoidLiteralExpr
  | singleIdentifier                                     # SingleLookupExpr
  | expr ('.' | '::') expr                               # LookupExpr
  | expr '[' expr ']'                                    # IndexExpr
  | expr '(' exprList ')'                                # FunctionCallExpr
  | expr '(' typeLiteralList ')' '(' exprList ')'        # ParamFunctionCallExpr
  | expr ('++' | '--')                                   # IncDecExpr
  | ('+' | '-' | '~' | '!' ) expr                        # UnaryExpr
  | <assoc=right> expr '**' expr                         # PowerExpr
  | expr ('*' | '/' | '//' | '%') expr                   # MulDivModExpr
  | expr ('+' | '-') expr                                # AddSubExpr
  | expr ('<<' | '>>' | '>>>') expr                      # ShiftExpr
  | expr (
      '<' | '>' | '<=' | '>=' | '==' | '!=' | '=='
    ) expr                                               # CmpExpr
  | expr '&' expr                                        # BandExpr
  | expr '^' expr                                        # BxorExpr
  | expr '|' expr                                        # BorExpr
  | expr '&&' expr                                       # AndExpr
  | expr '||' expr                                       # OrExpr
  | '*' expr                                             # OwnedPointerExpr
  | '&' expr '!'?                                        # ReferenceExpr
  ;

assignStmt :
  (strictIdentifier | (expr '[' expr ']'))
  ( '=' |
    '+=' | '-=' | '%=' | '^=' | '&=' | '*=' | '~=' | '|=' | '/=' |
    '&&=' | '||=' | '//=' | '<<=' | '>>=' |
    '>>>=' )
  expr ;

codeBlock :
  '{' (
    ifBlock
    | switchBlock
    | matchBlock
    | forBlock
    | whileBlock
    | loopBlock
    | letStmt
    | assignStmt
    | returnStmt
    | breakStmt
    | continueStmt
    | expr
  )* '}' ;

constExpr : literal | identifier ;

literal :
  arrayConstLiteral
  | rangeConstLiteral
  | structConstLiteral
  | booleanLiteral
  | functionLiteral
  | decimalLiteral
  | floatLiteral
  | integerLiteral
  | runeLiteral
  | stringLiteral
  ;

arrayConstLiteral :
  // '[' constExprList ']' |
  '[' typeLiteral '*' (identifier | intDecimalLiteral) ']' ;

rangeConstLiteral :
  identifier '(' (decimalLiteral | floatLiteral | integerLiteral) ')'
  | floatLiteral '..' floatLiteral '(' floatLiteral ')'
  | integerLiteral '..' integerLiteral '(' integerLiteral ')'
  | decimalLiteral '..' decimalLiteral '(' decimalLiteral ')'
  ;

structConstLiteral : (identifier | structTypeLiteral) '{' constExprList '}' ;

booleanLiteral : 'true' | 'false' ;

functionLiteral : '(' typeLiteralPairList ')' (':' typeLiteral)? codeBlock;

runeLiteral : RUNE ;

stringLiteral : STRING ;

intDecimalLiteral : INT_DECIMAL ;

decimalLiteral : INT_DECIMAL | FLOAT_DECIMAL ;

floatLiteral : FLOAT ;

integerLiteral : INTEGER ;

singleIdentifier : (VALUE | INT_TYPE | FLOAT_TYPE) ;

strictIdentifier : singleIdentifier ('.' singleIdentifier)* ;

identifier : singleIdentifier (('.' | '::') singleIdentifier)* ;

constExprList : (constExpr ',')* (constExpr ','?)? ;

constExprPairList : (singleIdentifier ':' constExpr ',')* (singleIdentifier ':' constExpr ','?)? ;

arrayTypeLiteral :
  '[' typeLiteral '...' ']' |
  '[' typeLiteral '*' (identifier | intDecimalLiteral) ']' ;

functionTypeLiteral : '(' typeLiteralPairList ')' (':' typeLiteral)? ;

paramTypeLiteral : identifier '(' typeLiteralList ')' ;

rangeTypeLiteral : 
  (  floatLiteral | identifier) '..' (  floatLiteral | identifier) |
  (integerLiteral | identifier) '..' (integerLiteral | identifier) |
  (decimalLiteral | identifier) '..' (decimalLiteral | identifier) ;

structTypeLiteral : '{' typeLiteralPairList '}' ;

carrayTypeLiteral : 'carray' '(' typeLiteral (',' intDecimalLiteral)? ')' ;

cbitfieldTypeLiteral :
  'cbitfield' '(' (
    INT_TYPE
  ) ',' intDecimalLiteral ')' ;

cblockfunctionTypeLiteral : 'cblockfntype' functionTypeLiteral ;

cfunctionTypeLiteral : 'cfntype' functionTypeLiteral ;

cstructTypeLiteral : 'cstruct' '(' typeLiteralPairList ')' ;

cunionTypeLiteral : 'cunion' '(' typeLiteralPairList ')' ;

cpointerTypeLiteral : 'cptr' '(' typeLiteral '!'? ')' ;

cvoidTypeLiteral : 'cvoid';

typeLiteral :
  '*'? arrayTypeLiteral
  | '&' arrayTypeLiteral '!'?
  | functionTypeLiteral
  | '*'? paramTypeLiteral
  | '&' paramTypeLiteral '!'?
  | '*'? rangeTypeLiteral
  | '&' rangeTypeLiteral '!'?
  | '*'? structTypeLiteral
  | '&' structTypeLiteral '!'?
  | carrayTypeLiteral
  | cbitfieldTypeLiteral
  | cblockfunctionTypeLiteral
  | cfunctionTypeLiteral
  | cpointerTypeLiteral
  | cstructTypeLiteral
  | cunionTypeLiteral
  | cvoidTypeLiteral
  | '*'? identifier
  | '&' identifier '!'?
  | '*'? identifier '(' constExpr ')'
  | '&' identifier '(' constExpr ')' '!'?
  ;

typeLiteralList : (typeLiteral ',')* (typeLiteral ','?)? ;

typeLiteralPairList :
  (singleIdentifier ':' typeLiteral ',')* (singleIdentifier ':' typeLiteral ','?)? ;

valueList : (singleIdentifier ',')* (singleIdentifier ','?)? ;

fragment NonStringChar : ~["\\] ;

fragment FloatNum : (DecNum '.' DecNum) | ('.' DecNum) ;

fragment IntNum : (HexNum | DecNum | OctNum | BinNum) ;

fragment HexNum : '0'[Xx][a-fA-F0-9][a-fA-F0-9_]* ;

fragment DecNum : [0-9][0-9_]* ;

fragment OctNum : '0'[Oo][0-7][0-7_]* ;

fragment BinNum : '0'[Bb][0-1][0-1_]* ;

fragment Exponent : [Ee][+-]?[0-9][0-9_]* ;

fragment FloatType : ('f16' | 'f32' | 'f64') ;

fragment IntType : [ui]('8' | '16' | '32' | '64' | '128')? ;

fragment HexDigit : [a-fA-F0-9] ;

fragment EscapedValue :
    '\\' (
      'u' HexDigit HexDigit HexDigit HexDigit
      | 'U' HexDigit HexDigit HexDigit HexDigit HexDigit HexDigit HexDigit HexDigit
      | [abfnrtv\\'"]
      | 'x' HexDigit HexDigit
    )
    ;

fragment UnicodeValue : ~[\r\n'] | LittleUValue | BigUValue | EscapedValue ;

fragment HexByteValue : '\\' 'x'  HexDigit HexDigit ;

fragment LittleUValue : '\\' 'u' HexDigit HexDigit HexDigit HexDigit ;

fragment BigUValue :
  '\\' 'U' HexDigit HexDigit HexDigit HexDigit HexDigit HexDigit HexDigit HexDigit ;

STRING : '"' (NonStringChar | EscapedValue)* '"' ;

RUNE : '\'' (UnicodeValue | HexByteValue) '\'' ;

INT_DECIMAL : IntNum ;

FLOAT_DECIMAL : (FloatNum Exponent?) | (IntNum Exponent) ;

FLOAT : ((FloatNum Exponent?) | (DecNum Exponent)) FloatType ;

FLOAT_TYPE : FloatType ;

INTEGER : IntNum IntType ;

INT_TYPE : IntType ;

VALUE : [a-zA-Z_][a-zA-Z0-9_]* ;

COMMENT : '#' .*? [\r\n] -> skip ;

BS : [ \t\r\n]+ -> skip ;
