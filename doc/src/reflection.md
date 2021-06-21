# Reflection

Sylva implements a small set of reflection attributes and methods. These are
distinguished from normal property access by the use of `::` instead of `.`.

## Arrays

* `::size`: returns the size in bytes of the array
* `::count`: returns the number of elements in the array
* `::element_type`: returns the type of the array's elements

## Enums

* `::first`: returns the first value of the enum
* `::last`: returns the last value of the enum

## Interfaces

## Ranges

* `::min`: returns the minimum value of the range
* `::max`: returns the maximum value of the range
* `::count`: returns the number of values in the range
* `::each`: a method accepting a function that iterates over the range's values

## Strings

* `::size`: returns the size in bytes of the string
* `::count`: returns the number of codepoints in the string

## Structs

* `::size`: returns the size in bytes of the struct, including struct padding

## (Runtime) Values

* `::type`: returns the type of the value

## Variants

* `::size`: returns the size in bytes of the variant
