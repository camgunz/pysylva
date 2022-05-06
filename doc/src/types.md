# Types

Sylva has 11 built-in types:

- `array`/`dynarray`
- `bool`
- `enum`
- `iface`
- `int`/`uint`
- `float`
- `range`
- `rune`
- `str`/`string`
- `struct`
- `variant`

Types are first-class in Sylva; they can be assigned to variables and passed to
detached scopes. They are immutable, they and the return values of their
methods are compile time constants.

Every type implements the `type` interface, which is:

```sylva
iface type {
  ## for scalars, `name` is "str", "int", etc., but for aggregate types it's
  ## the bound name ("Person", "RingBuffer")
  fn name(self: type): &str

  ## type_name is like `name`, but it is always the name of the type, not its
  ## bound name (so "struct" instead of "Person", and so on)
  fn type_name(self: type): &str

  ## number of bytes an instance of this type requires, including padding if
  ## relevant
  fn size(self: type): uint
}
```

## Specific types

Most types have methods beyond just `name` and `size`.

### `array`

* `count`: returns the number of elements in the `array`
* `element_type`: returns the type of the `array`'s elements
* `indices`: returns a `range` of the `array`'s valid indices

## `enum`

* `get`: a method that indexes into the `enum`, usable as:
         `Days.get(Days.indices(0))`
* `first`: returns the first value of the `enum`
* `last`: returns the last value of the `enum`
* `indices`: returns a `range` of the `enum`'s valid indices
* `count`: returns the number of values in the `enum`

## Numeric types

* `min`: returns the minimum value of the numeric type
* `max`: returns the maximum value of the numeric type

### `int`/`uint`

* `signed`: returns `true` if the type is signed or `false` if not

### `range`

* `min`: returns the minimum value of the `range`
* `max`: returns the maximum value of the `range`
* `type`: returns the `range`'s type (`int` or `float`)

#### Integer `range`

* `count`: returns the number of values in the `range`

## `struct`

* `get`: a method that indexes into the `struct`'s fields, usable as:
  `Person.get(Person.field_indices(0))` and returning a "field" type
* `field_indices`: returns a range of the `struct`'s valid indices
* `field_count`: returns the number of fields in the `struct`

## Field types

Field types are the result of calling `get` on a `struct` type, and have the
following attributes and methods:

* `name`: returns the name of the field in the `struct`
* `type`: returns the type of the field in the `struct`

## `variant`

* `get`: a method that indexes into the `variant`'s cases, usable as:
  `Person.get(Person.case_indices(0))` and returning a "case" type
* `case_indices`: returns a range of the `variant`'s valid indices
* `case_count`: returns the number of cases in the `variant`

## Case types

Case types are the result of calling `get` on a `variant` type, and have the
following attributes and methods:

* `name`: returns the name of the case in the `variant`
* `type`: returns the type of the case in the `variant`
