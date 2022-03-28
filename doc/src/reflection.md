# Reflection

Sylva implements a small set of reflection attributes and methods. These are
distinguished from normal property access by the use of `::` instead of `.`.

## Array types

* `::size`: returns the size in bytes of the array
* `::count`: returns the number of elements in the array
* `::element_type`: returns the type of the array's elements
* `::name`: returns the name of the array

## Enum types

* `::first`: returns the first value of the enum
* `::last`: returns the last value of the enum
* `::count`: returns the number of values in the enum
* `::each`: a method accepting a function that iterates over the enum's values
* `::name`: returns the name of the enum
* `::size`: returns the size in bytes of an instance of the enum

## Numeric types

* `::min`: returns the minimum value of the numeric type
* `::max`: returns the maximum value of the numeric type
* `::size`: returns the size in bytes of an instance of the numeric type

## Range types

* `::min`: returns the minimum value of the range
* `::max`: returns the maximum value of the range
* `::count`: returns the number of values in the range
* `::each`: a method accepting a function that iterates over the range's values
* `::name`: returns the name of the range
* `::size`: returns the size in bytes of an instance of the range

## Strings

* `::size`: returns the size in bytes of the string
* `::count`: returns the number of codepoints in the string

## Struct types

* `::size`: returns the size in bytes of the struct, including struct padding

## Variant types

* `::size`: returns the size in bytes of the variant, including struct padding

## (Runtime) values

* `::type`: returns the type of the value
