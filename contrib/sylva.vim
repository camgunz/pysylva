" Vim syntax file
" Language:     Sylva
" Maintainer:   Charlie Gunyon <charles.gunyon@gmail.com>
" URL:          http://github.com/camgunz/sylva.vim
" TODO:         WIP

if exists("b:current_syntax")
    finish
endif

syntax keyword SylvaType bool
syntax keyword SylvaType rune
syntax keyword SylvaType int i8 i16 i32 i64 i128
syntax keyword SylvaType uint u8 u16 u32 u64 u128
syntax keyword SylvaType float f16 f32 f64 f128
syntax keyword SylvaType complex c16 c32 c64 c128
syntax keyword SylvaType dec
syntax keyword SylvaType str
syntax keyword SylvaType array
syntax keyword SylvaType struct
syntax keyword SylvaType variant
syntax keyword SylvaType fn
syntax keyword SylvaType fntype
syntax keyword SylvaType range
syntax keyword SylvaType enum
syntax keyword SylvaType carray cbitfield cptr cstr cstruct cunion cvoid
syntax keyword SylvaType cfn cfntype cblockfntype

syntax keyword SylvaBoolean true false

syntax keyword SylvaConditional if else switch case match default

syntax keyword SylvaRepeat loop while for

syntax keyword SylvaStorageClass let

syntax keyword SylvaInclude mod req

syntax keyword SylvaStructure alias const impl iface

syntax keyword SylvaKeyword break continue

"syntax match SylvaIdentifier "\v<\[\$\@]?[a-zA-Z_]+[a-zA-Z0-9_]*>"

syntax keyword SylvaStatement return

syntax match SylvaInt "\v<[+-]?\d+(i|i8|i16|i32|i64|i128|u|u8|u16|u32|u64|u128)?>"
syntax match SylvaInt "\v<[+-]?0[xX]\x+(i|i8|i16|i32|i64|i128|u|u8|u16|u32|u64|u128)?>"
syntax match SylvaInt "\v<[+-]?0[bB][01]+(i|i8|i16|i32|i64|i128|u|u8|u16|u32|u64|u128)?>"
syntax match SylvaInt "\v<[+-]?0[oO]\o+(i|i8|i16|i32|i64|i128|u|u8|u16|u32|u64|u128)?>"

syntax match SylvaFloat "\v<[+-]?\d+\.\d+([eE][+-]?\d+)?(f|f16|f32|f64|f128)>"
syntax match SylvaFloat "\v<[+-]?\.\d+([eE][+-]?\d+)?(f|f16|f32|f64|f128)>"
syntax match SylvaFloat "\v<[+-]?\d+([eE][+-]?\d+)?(f|f16|f32|f64|f128)>"

syntax match SylvaDecimal "\v[+-]?<\d+\.\d+([eE][+-]?\d+)>"
syntax match SylvaDecimal "\v[+-]?<\.\d+([eE][+-]?\d+)>"
syntax match SylvaDecimal "\v[+-]?<\d+([eE][+-]?\d+)>"
syntax match SylvaDecimal "\v[+-]?<\d+\.\d+>"
syntax match SylvaDecimal "\v[+-]?<\.\d+>"
syntax match SylvaDecimal "\v[+-]?<\d+>"

syntax match SylvaOperator "\v[~!%^&*\-+|<>/=]"

syntax keyword SylvaTodo TODO FIXME NOTE

syntax match SylvaComment "\v#.*$" contains=SylvaTodo,SylvaDocString

syntax match SylvaEscapeError display contained /\\./
syntax match SylvaEscape display contained /\\\([nrt0\\'"]\|x\x\{2}\)/
syntax match SylvaEscapeUnicode display contained /\\\(u\x\{4}\|U\x\{8}\)/
syntax match SylvaEscapeUnicode display contained /\\u{\x\{1,6}}/

syntax region SylvaSingleString start=/"/ skip=/\\'/ end=/"/ contains=SylvaEscape,SylvaEscapeUnicode,SylvaEscapeError

syntax match SylvaCharacterInvalid display contained /b\?'\zs[\n\r\t']\ze'/
syntax match SylvaCharacterInvalidUnicode display contained /b'\zs[^[:cntrl:][:graph:][:alnum:][:space:]]\ze'/
syntax match SylvaCharacter /b'\([^\\]\|\\\(.\|x\x\{2}\)\)'/ contains=SylvaEscape,SylvaEscapeError,SylvaCharacterInvalid,SylvaCharacterInvalidUnicode
syntax match SylvaCharacter /'\([^\\]\|\\\(.\|x\x\{2}\|u\x\{4}\|U\x\{8}\|u{\x\{1,6}}\)\)'/ contains=SylvaEscape,SylvaEscapeUnicode,SylvaEscapeError,SylvaCharacterInvalid

highlight link SylvaKeyword      Keyword
highlight link SylvaLabel        Label
highlight link SylvaInt          SylvaNumber
highlight link SylvaFloat        SylvaNumber
highlight link SylvaDecimal      SylvaNumber
highlight link SylvaNumber       Number
highlight link SylvaOperator     Operator
highlight link SylvaComment      Comment
highlight link SylvaStructure    Structure
highlight link SylvaConditional  Conditional
highlight link SylvaRepeat       Repeat
highlight link SylvaStorageClass StorageClass
highlight link SylvaTodo         Todo
highlight link SylvaType         Type
highlight link SylvaBoolean      Boolean
highlight link SylvaInclude      Include
highlight link SylvaStatement    Statement
highlight link SylvaSpecial      Macro
highlight link SylvaSingleString String
highlight link SylvaDoubleString String
highlight link SylvaCharacter    Character
highlight link SylvaEscape       SpecialChar

let b:current_syntax = "Sylva"
