# Grammar

Below is Sylva's grammar, written for Lark.

```
%import common.CNAME -> VALUE
%import common.SH_COMMENT -> COMMENT
%import common.WS -> BS
%import common.FLOAT -> _FLOAT

%ignore COMMENT
%ignore BS

INTEGER: /((0[Xx][a-fA-F0-9][a-fA-F0-9_]*)|([0-9][0-9_]*)|(0[Oo][0-7][0-7_]*)|(0[Bb][01]01_]*))(u8|u16|u32|u64|u128|u|i8|i16|i32|i64|i128)?/
FLOAT: _FLOAT /("f16"|"f32"|"f64"|"f128")/
COMPLEX: _FLOAT /("c16"|"c32"|"c64"|"c128")/
RUNE: /'((~[\r\n])|(\\(([abfnrtv\\"'{])|(x[a-fA-F0-9][a-fA-F0-9])|(u[a-fA-F0-9][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9])|(U[a-fA-F0-9][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9]))))?'/
// STRING: /"[^\r\n]*"/
STRING: /"(([^\r\n])|(\\(([abfnrtv\\"'{])|(x[a-fA-F0-9][a-fA-F0-9])|(u[a-fA-F0-9][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9])|(U[a-fA-F0-9][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9]))))*"/

EQUAL:                    "="
COLON:                    ":"
COLON_COLON:              "::"
DOT:                      "."
ELLIPSIS:                 "..."
PLUS_PLUS:                "++"
MINUS_MINUS:              "--"
PLUS:                     "+"
MINUS:                    "-"
TILDE:                    "~"
BANG:                     "!"
STAR:                     "*"
SLASH:                    "\/"
SLASH_SLASH:              "\/\/"
BACKSLASH:                "\\"
PERCENT:                  "%"
STAR_STAR:                "**"
DOUBLE_OPEN_ANGLE:        "<<"
DOUBLE_CLOSE_ANGLE:       ">>"
TRIPLE_CLOSE_ANGLE:       ">>>"
OPEN_ANGLE:               "<"
CLOSE_ANGLE:              ">"
OPEN_ANGLE_EQUAL:         "<="
CLOSE_ANGLE_EQUAL:        ">="
EQUAL_EQUAL:              "=="
BANG_EQUAL:               "!="
AMP:                      "&"
AMP_AMP:                  "&&"
CARET:                    "^"
PIPE:                     "|"
PIPE_PIPE:                "||"
STAR_EQUAL:               "*="
SLASH_EQUAL:              "\/="
SLASH_SLASH_EQUAL:        "\/\/="
PERCENT_EQUAL:            "%="
PLUS_EQUAL:               "+="
MINUS_EQUAL:              "-="
DOUBLE_OPEN_ANGLE_EQUAL:  "<<="
DOUBLE_CLOSE_ANGLE_EQUAL: ">>="
TRIPLE_CLOSE_ANGLE_EQUAL: ">>>="
AMP_EQUAL:                "&="
CARET_EQUAL:              "^="
PIPE_EQUAL:               "|="
TILDE_EQUAL:              "~="
STAR_STAR_EQUAL:          "**="
AMP_AMP_EQUAL:            "&&="
PIPE_PIPE_EQUAL:          "||="
TRUE:                     "true"
FALSE:                    "false"

?value: VALUE

?value_list: value | value ("," value)+ [","] | value ","

_identifier: VALUE ((DOT | COLON_COLON) VALUE)*

?param: value
     | "*" value     -> moveparam
     | "&" value     -> refparam
     | "&" value "!" -> exrefparam

_type_param: _type_expr | _identifier "(" _type_param_list ")" | param

c_array_type_expr: "carray" array_type_expr

c_array_type_def: "carray" VALUE array_type_expr

c_bit_field_type_expr: "cbitfield" "(" _type_param "," INTEGER ")"

c_block_function_type_expr: "cblockfntype" function_type_expr

c_block_function_type_def: "cblockfntype" VALUE function_type_expr

c_function_type_expr: "cfn" function_type_expr

c_function_type_def: "cfn" VALUE function_type_expr

c_pointer_type_expr: "cptr" "(" ( \
  _type_expr | _identifier ["(" _type_param_list ")"]) BANG? \
")" BANG?

c_struct_type_expr: "cstruct" "(" _type_param_pair_list? ")"

c_struct_type_def: "cstruct" VALUE "{" _type_param_pair_list? "}"

c_union_type_expr: "cunion" "(" _type_param_pair_list ")"

c_union_type_def: "cunion" VALUE "{" _type_param_pair_list "}"

c_void_type_expr: "cvoid"

array_type_expr: "[" _type_param "*" (_identifier | INTEGER) "]"
               | "[" _type_param ELLIPSIS "]"

array_type_def: "array" VALUE array_type_expr

enum_type_def: "enum" VALUE "{" _expr_pair_list "}"

function_type_expr: "(" _type_param_pair_list? ")" [return_type]

function_type_def: "fn" VALUE function_type_expr

function_literal: "fn" function_type_expr code_block

function_def: function_type_def code_block

interface_type_def: "iface" VALUE "{" (function_def | function_type_def)* "}"

range_type_expr: ((  FLOAT | _identifier) ".." (  FLOAT | _identifier))
               | ((INTEGER | _identifier) ".." (INTEGER | _identifier))

range_type_def: "range" VALUE range_type_expr

struct_type_expr: "{" _type_param_pair_list? "}"

struct_type_def: "struct" VALUE ["(" value_list ")"] struct_type_expr

variant_type_def: \
  "variant" VALUE ["(" value_list ")"] "{" _type_param_pair_list "}"

_type_expr: STAR? array_type_expr
          | AMP array_type_expr BANG?
          | function_type_expr
          | STAR? range_type_expr
          | AMP range_type_expr BANG?
          | STAR? struct_type_expr
          | AMP struct_type_expr BANG?
          | c_array_type_expr
          | c_bit_field_type_expr
          | c_block_function_type_expr
          | c_function_type_expr
          | c_pointer_type_expr
          | c_struct_type_expr
          | c_union_type_expr
          | c_void_type_expr
          | STAR? _identifier "(" INTEGER ")"
          | AMP _identifier "(" INTEGER ")" BANG?

_type_param_list: _type_param
                | _type_param ("," _type_param)+ [","]
                | _type_param ","

?type_param_pair: VALUE ":" _type_param

_type_param_pair_list: type_param_pair
                     | type_param_pair ("," type_param_pair)+ [","]
                     | type_param_pair ","

module_decl: "mod" _identifier

requirement_decl: "req" _identifier

alias_def: "alias" VALUE ":" _type_param

const_def: "const" VALUE ":" literal_expr

implementation_def: \
  "impl" _identifier ["(" _identifier ")"] "{" function_def* "}"

module: module_decl (requirement_decl
                   | array_type_def
                   | enum_type_def
                   | function_type_def
                   | interface_type_def
                   | range_type_def
                   | struct_type_def
                   | variant_type_def
                   | alias_def
                   | const_def
                   | function_def
                   | implementation_def
                   | c_array_type_def
                   | c_block_function_type_def
                   | c_function_type_def
                   | c_struct_type_def
                   | c_union_type_def)*

return_type: ":" _type_param

_expr_list: expr | expr ("," expr)+ [","] | expr ","

_expr_pair_list: VALUE ":" expr
               | VALUE ":" expr ("," VALUE ":" expr)+ [","]
               | VALUE ":" expr ","

_arg_list: _expr_list | _expr_pair_list

?expr: and_expr ("||" and_expr)* | "(" and_expr ("||" and_expr)* ")" -> or_expr

?and_expr: cmp_expr ("&&" cmp_expr)* | "(" cmp_expr ("&&" cmp_expr)* ")"

?cmp_expr: bor_expr (_cmp_op bor_expr)* | "(" bor_expr (_cmp_op bor_expr)* ")"

?bor_expr: bxor_expr ("|" bxor_expr)* | "(" bxor_expr ("|" bxor_expr)* ")"

?bxor_expr: band_expr ("^" band_expr)* | "(" band_expr ("^" band_expr)* ")"

?band_expr: shift_expr ("&" shift_expr)* | "(" shift_expr ("&" shift_expr)* ")"

?shift_expr: arith_expr (_shift_op arith_expr)*
       | "(" arith_expr (_shift_op arith_expr)* ")"

?arith_expr: mul_expr (_add_op mul_expr)*
       | "(" mul_expr (_add_op mul_expr)* ")"

?mul_expr: inc_dec_expr (_mul_op inc_dec_expr)*
     | "(" inc_dec_expr (_mul_op inc_dec_expr)* ")"

?inc_dec_expr: (inc_dec_expr _inc_dec_op) | unary_expr

?unary_expr: (_unary_op unary_expr) | power_expr

?power_expr: atom_expr ("**" unary_expr)*
       | "(" atom_expr ("**" unary_expr)+ ")"

?atom_expr: atom_expr "(" [_arg_list] ")" -> call_expr
          | atom_expr "[" atom_expr "]"   -> index_expr
          | "(" atom_expr ")"
          | maybe_const_expr

?maybe_const_expr: \
    "*" atom_expr                                      -> move_expr
  | "&" atom_expr                                      -> ref_expr
  | "&" atom_expr "!"                                  -> exref_expr
  | "cptr" "(" atom_expr ")" BANG?                     -> cpointer_expr
  | "cvoid" "(" atom_expr ")" BANG?                    -> cvoid_expr
  | array_type_expr                                    -> array_expr
  | (_identifier | struct_type_expr) "{" _arg_list "}" -> struct_expr
  | function_literal                                   -> function_expr
  | _identifier                                        -> lookup_expr
  | literal_expr

?literal_expr: (TRUE | FALSE)       -> bool_expr
             | COMPLEX              -> complex_expr
             | FLOAT                -> float_expr
             | INTEGER              -> int_expr
             | RUNE                 -> rune_expr
             | STRING               -> string_expr
             | "(" literal_expr ")"

if_block: "if" "(" expr ")" code_block ["else" (if_block | code_block)]

switch_block: "switch" "(" _identifier ")" "{" ( \
  default_block | (case_block+ default_block?) \
) "}"

case_block: "case" "(" maybe_const_expr ")" code_block

match_block: "match" "(" _identifier ")" "{" ( \
  default_block | (match_case_block+ default_block?) \
) "}"

match_case_block: "case" "(" param ":" _identifier ")" code_block

default_block: "default" code_block

for_block: "for" "(" param ":" (expr | range_type_expr) ")" code_block

while_block: "while" "(" expr ")" code_block

loop_block: "loop" code_block

break_stmt: "break"

continue_stmt: "continue"

let_stmt: "let" VALUE BANG? ":" expr

return_stmt: "return" expr

assign_stmt: expr _assign_op expr

code_block: "{" (if_block
               | switch_block
               | match_block
               | for_block
               | while_block
               | loop_block
               | let_stmt
               | assign_stmt
               | return_stmt
               | break_stmt
               | continue_stmt
               | expr)* "}"

!_cmp_op: "<"|">"|"<="|">="|"=="|"!="
!_shift_op: "<<"|">>"|">>>"
!_add_op: "+"|"-"
!_mul_op: "*"|"/"|"//"|"%"
!_inc_dec_op: "++"|"--"
!_unary_op: "+"|"-"|"~"|"!"
!_int_type: ("int" | "i8" | "i16" | "i32" | "i64" | "i128"
           | "uint" | "u8" | "u16" | "u32" | "u64" | "u128")
!_assign_op: \
  EQUAL |                                                                   \
  PLUS_EQUAL | MINUS_EQUAL | PERCENT_EQUAL | CARET_EQUAL | AMP_EQUAL |      \
    STAR_EQUAL | TILDE_EQUAL | PIPE_EQUAL | SLASH_EQUAL |                   \
  SLASH_SLASH_EQUAL | AMP_AMP_EQUAL | PIPE_PIPE_EQUAL | SLASH_SLASH_EQUAL | \
    DOUBLE_OPEN_ANGLE_EQUAL | DOUBLE_CLOSE_ANGLE_EQUAL |                    \
  TRIPLE_CLOSE_ANGLE_EQUAL                                                  \
```
