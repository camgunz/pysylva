" Vim syntax file
" Language:     Sylva
" Maintainer:   Charlie Gunyon <charles.gunyon@gmail.com>
" URL:          http://github.com/camgunz/sylva.vim
" TODO:         WIP

if exists("b:current_syntax")
    finish
endif

syntax keyword SylvaType void
syntax keyword SylvaType bool
syntax keyword SylvaType rune
syntax keyword SylvaType num
syntax keyword SylvaType integer
syntax keyword SylvaType int i8 i16 i32 i64 i128 i256
syntax keyword SylvaType uint u8 u16 u32 u64 u128 u256
syntax keyword SylvaType float f16 f32 f64 f128 f256
syntax keyword SylvaType complex c16 c32 c64 c128 c256
syntax keyword SylvaType dec
syntax keyword SylvaType str
syntax keyword SylvaType array
syntax keyword SylvaType struct
syntax keyword SylvaType variant
syntax keyword SylvaType fn
syntax keyword SylvaType fntype
syntax keyword SylvaType range
syntax keyword SylvaType enum
syntax keyword SylvaType cfn cfntype cptr cstr cstruct cunion

syntax keyword SylvaBoolean true false

syntax keyword SylvaConditional if else match switch case default

syntax keyword SylvaRepeat for loop while

syntax keyword SylvaStorageClass const var

syntax keyword SylvaInclude module requirement

syntax keyword SylvaStructure alias implementation interface

syntax keyword SylvaKeyword break continue error iferr return self with

"syntax match SylvaIdentifier "\v\@[a-zA-Z_]+[a-zA-Z0-9_]*"
"syntax match SylvaIdentifier "\v\@[a-zA-Z_]+[a-zA-Z0-9_]*"

syntax match SylvaIdentifier "\v\[a-zA-Z_]+[a-zA-Z0-9_]*"

syntax keyword SylvaFunction die echo exit print

syntax match SylvaNumber "\v<\d+(i|i8|i16|i32|i64|i128|i256|u|u8|u16|u32|u64|u128|u256)?>"
syntax match SylvaNumber "\v<\d+\.\d+(f16|f32|f64|f128|f256)?>"
syntax match SylvaNumber "\v<\d*\.?\d+([Ee]-?)?\d+(f16|f32|f64|f128|f256)?>"
syntax match SylvaNumber "\v<\d+\.\d+(c16|c32|c64|c128|c256)?>"
syntax match SylvaNumber "\v<\d*\.?\d+([Ee]-?)?\d+(c16|c32|c64|c128|c256)?>"
syntax match SylvaNumber "\v<0[xX]\x+(i|i8|i16|i32|i64|i128|i256|u|u8|u16|u32|u64|u128|u256)?>"
syntax match SylvaNumber "\v<0b[01]+(i|i8|i16|i32|i64|i128|i256|u|u8|u16|u32|u64|u128|u256)?>"
syntax match SylvaNumber "\v<0o\o+(i|i8|i16|i32|i64|i128|i256|u|u8|u16|u32|u64|u128|u256)?>"

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
highlight link SylvaNumber       Number
highlight link SylvaOperator     Operator
highlight link SylvaComment      Comment
highlight link SylvaStructure    Structure
highlight link SylvaConditional  Conditional
highlight link SylvaRepeat       Repeat
highlight link SylvaLabel        Label
highlight link SylvaStorageClass StorageClass
highlight link SylvaTodo         Todo
highlight link SylvaType         Type
highlight link SylvaBoolean      Boolean
highlight link SylvaIdentifier   Define
highlight link SylvaInclude      Include
highlight link SylvaFunction     Function
highlight link SylvaSpecial      Macro
highlight link SylvaSingleString String
highlight link SylvaDoubleString String
highlight link SylvaCharacter    Character
highlight link SylvaEscape       SpecialChar

let b:current_syntax = "Sylva"
