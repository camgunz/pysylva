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
* `type`: returns the type of the `enum`'s values

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

* `index_field`: a method that indexes into the `struct`'s fields, usable as:
  `Person.index_field(Person.field_indices(0))` and returning a "field" type
* `get_field`: a method that indexes into the `struct`'s fields, usable as:
  `Person.get_field("name")` and returning a "field" type
* `field_indices`: returns a range of the `struct`'s valid field indices
* `field_count`: returns the number of fields in the `struct`
* `field_names`: returns an array of the `struct`'s field names
* `index_type_param`: a method that indexes into the `struct`'s type
  params, usable as: `Person.index_type_param(Person.type_param_indices(0))`
  and returning a type
* `get_type_param`: a method that indexes into the `struct`'s type params,
  usable as: `Person.get_type_param("name")` and returning a type
* `type_param_indices`: returns a range of the `struct`'s valid type param
  indices
* `type_param_count`: returns the number of the `struct`'s type params
* `type_param_names`: returns an array of the `struct`'s type param names

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
* `case_names`: returns an array of the `variant`'s case names
* `index_type_param`: a method that indexes into the `variant`'s type
  params, usable as: `Person.index_type_param(Person.type_param_indices(0))`
  and returning a type
* `get_type_param`: a method that indexes into the `variant`'s type params,
  usable as: `Person.get_type_param("name")` and returning a type
* `type_param_indices`: returns a range of the `variant`'s valid type param
  indices
* `type_param_count`: returns the number of the `variant`'s type params
* `type_param_names`: returns an array of the `variant`'s type param names

## Case types

Case types are the result of calling `get` on a `variant` type, and have the
following attributes and methods:

* `name`: returns the name of the case in the `variant`
* `type`: returns the type of the case in the `variant`
