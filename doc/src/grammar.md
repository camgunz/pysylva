# Grammar

Below is Sylva's grammar written for ANTLR4.

```
grammar Sylva;

module :
  moduleDecl? (
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
  )* EOF ;

aliasDef : 'alias' VALUE ':' (identifier | typeLiteral) ;

constDef : 'const' VALUE ':' constExpr ;

functionDef : 'fn' VALUE functionLiteral ;

implementationDef :
  'impl' strictIdentifier '(' strictIdentifier ')' '{' functionDef* '}' ;

moduleDecl : 'mod' strictIdentifier ;

requirementDecl : 'req' strictIdentifier ;

enumTypeDef : 'enum' VALUE '{' constExprPairList '}' ;

functionTypeDef : 'fntype' VALUE functionTypeLiteral ;

interfaceTypeDef : 'iface' VALUE '{' (functionDef | functionTypeDef)* '}' ;

rangeTypeDef : 'range' VALUE rangeTypeLiteral;

structTypeDef : 'struct' VALUE ('(' valueList ')')? structTypeLiteral ;

variantTypeDef :
  'variant' VALUE ('(' valueList ')')? '{' typeLiteralPairList '}' ;

ifBlock : 'if' '(' expr ')' codeBlock ('else' (ifBlock | codeBlock))? ;

switchBlock :
  'switch' '(' expr ')' '{' (defaultBlock | (caseBlock+ defaultBlock?)) '}' ;

caseBlock: 'case' '(' constExpr ')' codeBlock ;

matchBlock :
  'match' '(' expr ')' '{' (
    (matchCaseBlock+ defaultBlock?) | defaultBlock
  ) '}' ;

param : '*'? VALUE | '&' VALUE '!'? ;

matchCaseBlock: 'case' '(' param ':' VALUE ')' codeBlock ;

defaultBlock: 'default' codeBlock ;

forBlock : 'for' '(' param ':' (expr | rangeTypeLiteral) ')' codeBlock ;

whileBlock : 'while' '(' expr ')' codeBlock ;

loopBlock : 'loop' codeBlock ;

breakStmt : 'break' ;

continueStmt : 'continue' ;

letStmt : 'let' VALUE '!'? ':' expr ;

returnStmt : 'return' expr ;

exprList : (expr ',')* (expr ','?)? ;

expr :
  literal                                         # LiteralExpr
  | expr '[' expr ']'                             # IndexExpr
  | expr '(' exprList ')'                         # FunctionCallExpr
  | expr '(' typeLiteralList ')' '(' exprList ')' # ParamFunctionCallExpr
  | VALUE                                         # SingleLookupExpr
  | expr ('.' | '::') expr                        # LookupExpr
  | '(' exprList ')'                              # ParenExpr
  | '[' exprList ']'                              # ArrayExpr
  | expr ('++' | '--')                            # IncDecExpr
  | ('+' | '-' | '~' | '!' ) expr                 # UnaryExpr
  | <assoc=right> expr '**' expr                  # PowerExpr
  | expr ('*' | '/' | '//' | '%') expr            # MulDivModExpr
  | expr ('+' | '-') expr                         # AddSubExpr
  | expr ('<<' | '>>' | '>>>') expr               # ShiftExpr
  | expr (
      '<' | '>' | '<=' | '>=' | '==' | '!=' | '=='
    ) expr                                        # CmpExpr
  | expr '&' expr                                 # BandExpr
  | expr '^' expr                                 # BxorExpr
  | expr '|' expr                                 # BorExpr
  | expr '&&' expr                                # AndExpr
  | expr '||' expr                                # OrExpr
  | '*' expr                                      # OwnedPointerExpr
  | '&' expr '!'?                                 # ReferenceExpr
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

runeLiteral : '\'' .? '\'' ;

stringLiteral : '"' .*? '"' ;

intDecimalLiteral : INT_DECIMAL ;

decimalLiteral : INT_DECIMAL | FLOAT_DECIMAL ;

floatLiteral : FLOAT ;

integerLiteral : INTEGER ;

strictIdentifier : VALUE ('.' VALUE)* ;

identifier : VALUE (('.' | '::') VALUE)* ;

constExprList : (constExpr ',')* (constExpr ','?)? ;

constExprPairList : (VALUE ':' constExpr ',')* (VALUE ':' constExpr ','?)? ;

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

cbitfieldTypeLiteral : 'cbitfield' '(' intDecimalLiteral ',' intDecimalLiteral ')' ;

cblockfunctionTypeLiteral : 'cblockfntype' functionTypeLiteral ;

cfunctionTypeLiteral : 'cfntype' functionTypeLiteral ;

cfunctionLiteral : 'cfn' functionTypeLiteral ;

cpointerTypeLiteral : 'cptr' '(' typeLiteral '!'? ')' ;

cstructTypeLiteral : 'cstruct' '(' typeLiteralPairList ')' ;

cunionTypeLiteral : 'cunion' '(' typeLiteralPairList ')' ;

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
  | cfunctionLiteral
  | cpointerTypeLiteral
  | cstructTypeLiteral
  | cunionTypeLiteral
  | '*'? identifier
  | '&' identifier '!'?
  | '*'? identifier '(' constExpr ')'
  | '&' identifier '(' constExpr ')' '!'?
  ;

typeLiteralList : (typeLiteral ',')* (typeLiteral ','?)? ;

typeLiteralPairList :
  (VALUE ':' typeLiteral ',')* (VALUE ':' typeLiteral ','?)? ;

valueList : (VALUE ',')* (VALUE ','?)? ;

INT_DECIMAL : IntNum ;

FLOAT_DECIMAL : (FloatNum Exponent?) | (IntNum Exponent) ;

FLOAT : ((FloatNum Exponent?) | (DecNum Exponent)) FloatType ;

INTEGER : IntNum IntType ;

fragment FloatNum : (DecNum '.' DecNum) | ('.' DecNum) ;

fragment IntNum : (HexNum | DecNum | OctNum | BinNum) ;

fragment HexNum : '0'[Xx][a-fA-F0-9][a-fA-F0-9_]* ;

fragment DecNum : [0-9][0-9_]* ;

fragment OctNum : '0'[Oo][0-7][0-7_]* ;

fragment BinNum : '0'[Bb][0-1][0-1_]* ;

fragment Exponent : [Ee][+-]?[0-9][0-9_]* ;

fragment FloatType : ('f16' | 'f32' | 'f64') ;

fragment IntType : [ui]('8' | '16' | '32' | '64' | '128')? ;

VALUE : [a-zA-Z_][a-zA-Z0-9_]* ;

COMMENT : '#' .*? [\r\n] -> skip ;

BS : [ \t\r\n]+ -> skip ;
```
