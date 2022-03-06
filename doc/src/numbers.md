# Numbers

## Overview

Working with numbers in Sylva is, frankly, a real pain in the ass.  That's by
design: numbers hide mountains of complexity and failing to appreciate it can
be very unsafe.  As an example: look at all the problems that could arise from
very basic arithmetic:

```sylva
fn main() {
  var number: 200
  var another_number: 1
  var counts: [22u8, 33u8]
  var bigger_number: number + 1            # Potential overflow
  var smaller_number: number - 1           # Potential underflow
  var fraction: number / 3                 # Potential insufficient precision
  var result: number / another_number      # Potential divide by zero
  var count: 4u + 3i + 2.8f32              # What type is `count`?
  var second_count: counts[another_number] # Potential out-of-bounds index
}
```

Sylva provides affordances for dealing with all of these pitfalls, but
generally the programmer is dissuaded from dealing with raw numbers unless
they must.

Minimize your interactions with raw numbers. Build abstractions on top of them,
and use [ranges](ranges.html) (Sylva's core numeric type) wherever possible.

### Decimals

The default numeric type in Sylva is `decimal`, and for good reason: you more
or less can't mess it up and it behaves like you think numbers behave.  It
represents a continuous range, so you can't get into situations where something
like `range(0.0f32, 0.1f32)` doesn't actually include `0.1f32 - 0.000001f32`.
It doesn't underflow or overflow.  It represents all numbers exactly (given
infinite memory, which is very, very rarely needed) so you can use it for
money.

`decimal`s require no suffix: `35` is a `decimal`.  Rounding behavior, however,
may be specified using the following suffixes:

**Rounding/Clamping modes**:
- `35`: Round to nearest, no clamping (default)
- `35rf`: Fail
- `35ru`: Round to +Inf, clamps bottom
- `35rd`: Round to -Inf, clamps top
- `35rz`: Round towards zero, clamps top and bottom
- `35ra`: Round away from zero, no clamping

_(n.b. ordering of all numeric literal suffixes is important, i.e. `35ur` is a
lexer error)_

You can also set a `decimal`s precision and exponent:

```sylva
fn main() {
  var number: 35

  number.set_max_precision(2)
  number.set_max_exponent(2)
}
```

Note that either of those operations may perform rounding on the value; and if
the rounding mode is "fail" (again: the default), this may result in a failure.

The chief downside to `decimal` is speed, they use more memory and require
some extra instructions to perform calculations on them.  Usage can also lead
to memory allocation.

### Floats

`float` literals use `f` followed by a bit width, e.g. `19f32`.  This is
**required** for `float`s, otherwise the compiler won't know these aren't
`decimal`s.  `float`s support all the overflow and imprecision handlers
`decimal`s do:

`float`s handle overflow and imprecision according to their rounding mode.
Notably: they do not wrap, and clamping is a function of the rounding mode
listed below.  `float`s are imprecise by their nature: they have fixed exponent
and precision sizes, and rounding modes.  As a result, imprecision in `float`
operations cannot be configured to trigger an error.

**Rounding/Clamping modes**:
- `35f32`: Round to nearest, no clamping (default)
- `35f32ru` Round to +Inf, clamps bottom
- `35f32rd` Round to -Inf, clamps top
- `35f32rz` Round towards zero, clamps top and bottom
- `35f32ra` Round away from zero, no clamping

### Integers

`integer` literals use either `i` or `u` for signed and unsigned respectively.
These must be followed by a bit width, e.g. `35i64`.  This is **required** for
`integer`s, otherwise the compiler won't know these aren't `decimal`s.

`integer`s are imprecise by their nature: they always drop the fractional
component of any operation.  Furthermore they cannot represent infinity,
positive, negative, or otherwise.  As a result, there are no imprecision
handlers, and the only overflow handler options are `wrap` or `clamp`.

**Overflow Handlers**:
- Abort: `35u8` (default)
- Wrap:  `35u8w`
- Clamp: `35i8c`

## Handling failures

Numeric operations that could result in errors return
[`Result`s](failures.html):

```sylva
req sys

fn main() {
  var number: 200u
  var another_number: 1u
  var counts: u8[22, 33]
  var inc_res = number + 1

  match (inc_res) {
    case (OK) {
      sys.echo("Succesfully incremented a number ({inc_res.value})!")
    }
    case (Failure) {
      sys.echoexit("Failed to increment a number: {inc_res.message})")
    }
  }
}
```

## Converting between numeric types

Numeric type conversion should be rare, and when it does occur it should be at
the edges of your application.  Internally everything should have a unit, thus
converting between "inventory count of tires" to "number of red bulls drank
today" should seem as nonsensical in your code as it in fact is.  However we
cannot control the world beyond our application, therefore we need a mechanism
to add coherency to these raw values.

[TODO] ...`parse_be_32` etc, or something.
