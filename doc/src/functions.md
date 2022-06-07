# Functions

Functions should look familiar:

```sylva
fn hello(name: str): str {
  return("Hello, {name}!")
}
```

## Type parameterization (generic functions)

Functions can be parameterized with a type using `@`:

```sylva
mod main

req sys

fn hello (name: @name_type) {
  sys.echo("Hello, {name}")
}

fn main() {
  hello(1)
  hello("Barack")
}
```

## Function types

It's often useful to be able to define a function type, for use in structs
or higher-order functions. This is accomplished in Sylva simply by leaving off
the code block.

```sylva
fn int_stringer(i: int): str

fn stringify_ints(func: int_stringer, ints: &[int...])
```
