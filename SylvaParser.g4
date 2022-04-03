parser grammar SylvaParser ;

options {
  tokenVocab=SylvaLexer;
}

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

aliasDef : ALIAS singleIdentifier COLON (identifier | typeLiteral) ;

constDef : CONST singleIdentifier COLON constExpr ;

functionDef : FN singleIdentifier functionLiteral ;

implementationDef : IMPL strictIdentifier
                    OPEN_PAREN strictIdentifier CLOSE_PAREN
                    OPEN_BRACE functionDef* CLOSE_BRACE ;

moduleDecl : MOD strictIdentifier ;

requirementDecl : REQ strictIdentifier ;

enumTypeDef : ENUM singleIdentifier OPEN_BRACE constExprPairList CLOSE_BRACE ;

functionTypeDef : FNTYPE singleIdentifier functionTypeLiteral ;

interfaceTypeDef : IFACE singleIdentifier
                   OPEN_BRACE (functionDef | functionTypeDef)* CLOSE_BRACE ;

rangeTypeDef : RANGE singleIdentifier rangeTypeLiteral;

structTypeDef : STRUCT singleIdentifier
                (OPEN_PAREN valueList CLOSE_PAREN)? structTypeLiteral ;

variantTypeDef : VARIANT singleIdentifier
                 (OPEN_PAREN valueList CLOSE_PAREN)?
                 OPEN_BRACE typeLiteralPairList CLOSE_BRACE ;

cblockfunctionTypeDef : CBLOCKFNTYPE singleIdentifier functionTypeLiteral ;

cfunctionTypeDef : CFN singleIdentifier functionTypeLiteral ;

cstructTypeDef : CSTRUCT singleIdentifier
                 OPEN_BRACE typeLiteralPairList CLOSE_BRACE ;

cunionTypeDef : CUNION singleIdentifier
                OPEN_BRACE typeLiteralPairList CLOSE_BRACE ;

ifBlock : IF OPEN_PAREN expr CLOSE_PAREN
          codeBlock (ELSE (ifBlock | codeBlock))? ;

switchBlock : SWITCH OPEN_PAREN expr CLOSE_PAREN OPEN_BRACE (
                defaultBlock | (caseBlock+ defaultBlock?)
              ) CLOSE_BRACE ;

caseBlock: CASE OPEN_PAREN constExpr CLOSE_PAREN codeBlock ;

matchBlock : MATCH OPEN_PAREN expr CLOSE_PAREN OPEN_BRACE (
               defaultBlock | (matchCaseBlock+ defaultBlock?)
             ) CLOSE_BRACE ;

param : STAR? singleIdentifier | AMP singleIdentifier BANG? ;

matchCaseBlock: CASE OPEN_PAREN param COLON singleIdentifier CLOSE_PAREN
                codeBlock ;

defaultBlock: DEFAULT codeBlock ;

forBlock : FOR OPEN_PAREN param COLON (expr | rangeTypeLiteral) CLOSE_PAREN
           codeBlock ;

whileBlock : WHILE OPEN_PAREN expr CLOSE_PAREN codeBlock ;

loopBlock : LOOP codeBlock ;

breakStmt : BREAK ;

continueStmt : CONTINUE ;

letStmt : LET singleIdentifier BANG? COLON expr ;

returnStmt : RETURN expr ;

exprList : (expr COMMA)* (expr COMMA?)? ;

expr :
  literal                                              # LiteralExpr
  | OPEN_PAREN exprList CLOSE_PAREN                    # ParenExpr
  | OPEN_BRACKET exprList CLOSE_BRACKET                # ArrayExpr
  | (identifier | carrayTypeLiteral) arrayConstLiteral # CArrayLiteralExpr
  | CPTR OPEN_PAREN expr CLOSE_PAREN                   # CPointerLiteralExpr
  | (identifier | cstructTypeLiteral)
    OPEN_BRACE exprList CLOSE_BRACE                    # CStructLiteralExpr
  | (identifier | cunionTypeLiteral)
    OPEN_BRACE exprList CLOSE_BRACE                    # CUnionLiteralExpr
  | CVOID OPEN_PAREN expr CLOSE_PAREN                  # CVoidLiteralExpr
  | singleIdentifier                                   # SingleLookupExpr
  | expr (DOT | COLON_COLON) expr                      # LookupExpr
  | expr OPEN_BRACKET expr CLOSE_BRACKET               # IndexExpr
  | expr OPEN_PAREN exprList CLOSE_PAREN               # FunctionCallExpr
  | expr OPEN_PAREN typeLiteralList CLOSE_PAREN
    OPEN_PAREN exprList CLOSE_PAREN                    # ParamFunctionCallExpr
  | expr (PLUS_PLUS | MINUS_MINUS)                     # IncDecExpr
  | (PLUS | MINUS | TILDE | BANG ) expr                # UnaryExpr
  | <assoc=right> expr STAR_STAR expr                  # PowerExpr
  | expr (STAR | SLASH | SLASH_SLASH | PERCENT) expr   # MulDivModExpr
  | expr (PLUS | MINUS) expr                           # AddSubExpr
  | expr (DOUBLE_OPEN_ANGLE | DOUBLE_CLOSE_ANGLE |
          TRIPLE_CLOSE_ANGLE) expr                     # ShiftExpr
  | expr (OPEN_ANGLE | CLOSE_ANGLE |
          OPEN_ANGLE_EQUAL | CLOSE_ANGLE_EQUAL |
          EQUAL_EQUAL | BANG_EQUAL ) expr              # CmpExpr
  | expr AMP expr                                      # BandExpr
  | expr CARET expr                                    # BxorExpr
  | expr PIPE expr                                     # BorExpr
  | expr AMP_AMP expr                                  # AndExpr
  | expr PIPE_PIPE expr                                # OrExpr
  | STAR expr                                          # OwnedPointerExpr
  | AMP expr BANG?                                     # ReferenceExpr
  ;

assignStmt :
  (strictIdentifier | (expr OPEN_BRACKET expr CLOSE_BRACKET))
  ( EQUAL |
    PLUS_EQUAL | MINUS_EQUAL | PERCENT_EQUAL | CARET_EQUAL | AMP_EQUAL |
    STAR_EQUAL | TILDE_EQUAL | PIPE_EQUAL | SLASH_EQUAL | SLASH_SLASH_EQUAL |
    AMP_AMP_EQUAL | PIPE_PIPE_EQUAL | SLASH_SLASH_EQUAL |
    DOUBLE_OPEN_ANGLE_EQUAL | DOUBLE_CLOSE_ANGLE_EQUAL |
    TRIPLE_CLOSE_ANGLE_EQUAL )
  expr ;

codeBlock :
  OPEN_BRACE (
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
  )* CLOSE_BRACE ;

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
  // OPEN_BRACKET constExprList CLOSE_BRACKET |
  OPEN_BRACKET typeLiteral STAR (identifier | intDecimalLiteral) CLOSE_BRACKET ;

rangeConstLiteral :
  identifier OPEN_PAREN (
    decimalLiteral | floatLiteral | integerLiteral
  ) CLOSE_PAREN
  | floatLiteral DOT_DOT floatLiteral OPEN_PAREN floatLiteral CLOSE_PAREN
  | integerLiteral DOT_DOT integerLiteral OPEN_PAREN
      integerLiteral
    CLOSE_PAREN
  | decimalLiteral DOT_DOT decimalLiteral OPEN_PAREN decimalLiteral CLOSE_PAREN
  ;

structConstLiteral : (identifier | structTypeLiteral)
                     OPEN_BRACE constExprList CLOSE_BRACE ;

booleanLiteral : TRUE | FALSE ;

functionLiteral : OPEN_PAREN typeLiteralPairList CLOSE_PAREN
                  (COLON typeLiteral)? codeBlock;

runeLiteral : RUNE_LITERAL ;

// stringLiteral : STRING_LITERAL ;

stringLiteral : DOUBLE_QUOTE templateStringAtom* DOUBLE_QUOTE ;

templateStringAtom :
  STRING_ATOM
  | STRING_START_EXPRESSION expr TEMPLATE_CLOSE_BRACE
  ;

intDecimalLiteral : INT_DECIMAL ;

decimalLiteral : INT_DECIMAL | FLOAT_DECIMAL ;

complexLiteral : COMPLEX ;

floatLiteral : FLOAT ;

integerLiteral : INTEGER ;

singleIdentifier : (VALUE | INT_TYPE | FLOAT_TYPE) ;

strictIdentifier : singleIdentifier (DOT singleIdentifier)* ;

identifier : singleIdentifier ((DOT | COLON_COLON) singleIdentifier)* ;

constExprList : (constExpr COMMA)* (constExpr COMMA?)? ;

constExprPairList : (singleIdentifier COLON constExpr COMMA)*
                    (singleIdentifier COLON constExpr COMMA?)? ;

arrayTypeLiteral :
  OPEN_BRACKET typeLiteral ELLIPSIS CLOSE_BRACKET |
  OPEN_BRACKET typeLiteral STAR (identifier | intDecimalLiteral) CLOSE_BRACKET
  ;

functionTypeLiteral : OPEN_PAREN typeLiteralPairList CLOSE_PAREN
                      (COLON typeLiteral)? ;

paramTypeLiteral : identifier OPEN_PAREN typeLiteralList CLOSE_PAREN ;

rangeTypeLiteral : 
  (  floatLiteral | identifier) DOT_DOT (  floatLiteral | identifier) |
  (integerLiteral | identifier) DOT_DOT (integerLiteral | identifier) |
  (decimalLiteral | identifier) DOT_DOT (decimalLiteral | identifier) ;

structTypeLiteral : OPEN_BRACE typeLiteralPairList CLOSE_BRACE ;

carrayTypeLiteral :
  CARRAY OPEN_PAREN typeLiteral (COMMA intDecimalLiteral)? CLOSE_PAREN ;

cbitfieldTypeLiteral :
  CBITFIELD OPEN_PAREN (INT_TYPE) COMMA intDecimalLiteral CLOSE_PAREN ;

cblockfunctionTypeLiteral : CBLOCKFNTYPE functionTypeLiteral ;

cfunctionTypeLiteral : CFNTYPE functionTypeLiteral ;

cstructTypeLiteral : CSTRUCT OPEN_PAREN typeLiteralPairList CLOSE_PAREN ;

cunionTypeLiteral : CUNION OPEN_PAREN typeLiteralPairList CLOSE_PAREN ;

cpointerTypeLiteral : CPTR OPEN_PAREN typeLiteral BANG? CLOSE_PAREN ;

cvoidTypeLiteral : CVOID;

typeLiteral :
  STAR? arrayTypeLiteral
  | AMP arrayTypeLiteral BANG?
  | functionTypeLiteral
  | STAR? paramTypeLiteral
  | AMP paramTypeLiteral BANG?
  | STAR? rangeTypeLiteral
  | AMP rangeTypeLiteral BANG?
  | STAR? structTypeLiteral
  | AMP structTypeLiteral BANG?
  | carrayTypeLiteral
  | cbitfieldTypeLiteral
  | cblockfunctionTypeLiteral
  | cfunctionTypeLiteral
  | cpointerTypeLiteral
  | cstructTypeLiteral
  | cunionTypeLiteral
  | cvoidTypeLiteral
  | STAR? identifier
  | AMP identifier BANG?
  | STAR? identifier OPEN_PAREN constExpr CLOSE_PAREN
  | AMP identifier OPEN_PAREN constExpr CLOSE_PAREN BANG?
  ;

typeLiteralList : (typeLiteral COMMA)* (typeLiteral COMMA?)? ;

typeLiteralPairList : (singleIdentifier COLON typeLiteral COMMA)*
                      (singleIdentifier COLON typeLiteral COMMA?)? ;

valueList : (singleIdentifier COMMA)* (singleIdentifier COMMA?)? ;
