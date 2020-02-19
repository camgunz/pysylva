# Numbers

## Overview

Working with numbers in Sylva is, frankly, a real pain in the ass.  That's by
design: numbers hide mountains of complexity and failing to deal with it is
very unsafe.  As an example: look at all the problems that could arise from
very basic arithmetic:

```sylva
val number: 200
val another_number: 1
val counts: u8[22, 33]
val bigger_number: number + 1            # Potential overflow
val smaller_number: number - 1           # Potential underflow
val fraction: number / 3                 # Potential insufficient precision
val result: number / another_number      # Potential divide by zero
val count: 4u + 3s + 2.8f32              # What type is `count`?
val second_count: counts[another_number] # Potential out-of-bounds index
```

Sylva provides affordances for dealing with all of these pitfalls, but
generally the programmer is dissuaded from dealing with raw numbers unless
they must.

This is in contrast to most programming languages, which place little to no
restrictions around numbers.  While there typically are "types" (floats, ints,
signed, unsigned, decimals), those types generally indicate what the number can
do (this has a decimal point, this is exact, etc.) vs. what you can do with the
number.  As a result, many programming errors are down to misuse of
numbers--usually either not understanding the semantics of promotion, the
specifics of floating point implementations, or a language's general lack of
rigor when it comes to indexing.

In order to fix all this, many newer languages are placing more restrictions on
what you can do with numbers.  Go doesn't let you mix integers with floats.
Rust defines its overflow semantics.  But these aren't new ideas; for example
Ada allows the programmer to define ranged number types--going beyond typical
bit-width style restrictions.

Sylva recognizes the benefits of all of this.  It uses ranging to ensure that
indexing is safe where it can.  It deliberately disallows mixing numeric types
in arithmetic expressions--even similar base numeric types like integers.  It
requires programmers to define what they want in overflow/underflow cases.

Which brings us to indexing.  Indexing is often very dangerous; we need to
guarantee that an index is valid to do it safely, and we can do that as long as
the target has a fixed size.  For example, with an array of a fixed size of 14,
we know for certain that indexes from 0-13 are valid, and Sylva allows literals
from `0` to `13`.  It would also allow variables so long as their schema
ensures their values are within the 0-13 range.

All of which is to say that dealing with raw numbers is to be avoided.  Build
abstractions on top of them, and use [ranges](ranges.md) (Sylva's preferred
numeric type) wherever possible.

[TODO] What do we do for dynamic targets or variables outside the valid range?
       `with` block?  `switch`?

### Decimals

The default numeric type in Sylva is `decimal`, and for good reason: you more
or less can't mess it up and it behaves like you think numbers behave.  It
represents a continuous range, so you can't get into situations where something
like `range(0.0f32, 0.1f32)` doesn't actually include `0.1f32 - 0.000001f`.  It
doesn't underflow or overflow.  It represents all numbers exactly (given
infinite memory, which is very, very rarely needed) so you can use it for
money.

`decimal`s require no suffix: `35` is a `decimal`.  Rounding behavior, however,
may be specified using the following suffixes:

**Rounding modes**:
- Abort:                `35` (default)
- Round to nearest:     `35rn`
- Round to +Inf:        `35ru`
- Round to -Inf:        `35rd`
- Round towards zero:   `35rz`
- Round away from zero: `35ra`

_(n.b. ordering of all numeric literal suffixes is important, i.e. `35nr` is a
lexer error)_

You can also set a `decimal`s precision and exponent:

```sylva
var number: 35

number.set_max_precision(2)
number.set_max_exponent(2)
```

Note that either of those operations may perform rounding on the value; and if
the rounding mode is "error" (again: the default), this may yield an error.

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
operations does not trigger an error.

**Rounding modes**:
- Round to nearest:     `35f32` (default) no clamping
- Round to +Inf:        `35f32ru` clamps bottom
- Round to -Inf:        `35f32rd` clamps top
- Round towards zero:   `35f32rz` clamps
- Round away from zero: `35f32ra` no clamping

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

## Error handling

Numeric operations that could result in errors must be handled inside a `with`
or `iferr` block:

```sylva
requirement sys

fn main() {
  val number: 200u
  val another_number: 1u
  val counts: u8[22, 33]

  with bigger_number: number + 1 {
    sys.echo("Successfully incremented a number ({bigger_number})!")
  }

  with smaller_number: number - 1 {
    sys.echo("Successfully decremented a number ({smaller_number})!")
  }

  with fraction: number / 3 {
    sys.echo("Successfully decremented a number ({smaller_number})!")
  }
  else err {
    sys.echoerr("Failed to divide a {number} / {3}: {err}")
  }

  with second_count: counts[another_number] {
    sys.echo("Got the 2nd count: {second_count}")
  }
  else err {
    sys.echoerr("Couldn't find the 2nd count: {err}")
  }
}
```

## Bit widths

Sylva supports arbitrary bit widths for `float` and `integer` numbers.  But
keep in mind this is not free; the vast majority of machines support only
specific formats for `float` and `integer` (typically 32/64/80 bit floats and
8/16/32/64 bit integers).  If you specify a bit width not natively supported by
your output target, Sylva will have to emulate those types in software, which
is orders of magnitude slower than performing the calculations on hardware.
Sylva can warn if this is the case, but it would be best to keep this in mind
during planning when considering which numeric types to use.

## Converting between numeric types

Numeric type conversion should be rare, and when it does occur it should be at
the edges of your application.  Internally everything should have a unit, thus
converting between "inventory count of tires" to "number of red bulls drank
today" should seem as nonsensical in your code as it in fact is.  However we
cannot control the world beyond our application, therefore we need a mechanism
to add coherency to these raw values.

...`parse_be_32` etc, or something.
