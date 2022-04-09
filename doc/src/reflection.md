# Reflection

Sylva implements a small set of reflection attributes and methods. These are
distinguished from normal property access by the use of `::` instead of `.`.

## Array types

* `::name`: returns 'array' as the name of the type
* `::size`: returns the size in bytes of the array
* `::count`: returns the number of elements in the array
* `::element_type`: returns the type of the array's elements
* `::indices`: returns a range of the array's valid indices

## Bool types

* `::name`: returns `bool` as the name of the type

## Enum types

* `::name`: returns 'enum' as the name of the type
* `::get`: a method that indexes into the enum, usable as:
           `Days::get(Days::indices(0))`
* `::first`: returns the first value of the enum
* `::last`: returns the last value of the enum
* `::indices`: returns a range of the enum's valid indices
* `::count`: returns the number of values in the enum
* `::name`: returns the name of the enum
* `::size`: returns the size in bytes of an instance of the enum

## Numeric types

* `::name`: returns `int`, `float` or `complex` as the name of the type
* `::min`: returns the minimum value of the numeric type
* `::max`: returns the maximum value of the numeric type
* `::size`: returns the size in bytes of an instance of the numeric type

## Integer numeric types

* `::signed`: returns `true` if the type is signed or `false` if not

## All range types

* `::min`: returns the minimum value of the range
* `::max`: returns the maximum value of the range
* `::size`: returns the size in bytes of an instance of the range
* `::type`: returns the range's type

## Integer range types

* `::count`: returns the number of values in the range

## Rune types

* `::name`: returns 'rune' as the name of the type

## Strings

* `::name`: returns 'str' as the name of the type
* `::size`: returns the size in bytes of the string
* `::count`: returns the number of codepoints in the string

## Struct types

* `::name`: returns 'struct' as the name of the type
* `::size`: returns the size in bytes of the struct, including struct padding

## Variant types

* `::name`: returns 'variant' as the name of the type
* `::size`: returns the size in bytes of the variant, including struct padding

## (Runtime) values

* `::type`: returns the type of the value
* `::bytes`: returns a `&[i8 * value::type::size]`, the bytes of the value
