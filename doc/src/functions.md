# Functions

Functions should look very familiar:

```sylva
fn hello(name: str): str {
  return("Hello, {name}!")
}
```

## Type parameterization (generic functions)

Functions can be parameterized with a type:

```sylva
req sys

fn hello (name_type) (name: name_type) {
  sys.echo("Hello, {name}")
}

fn main() {
  hello(dec)(1)
  hello(str)("Barack")
}
```

## Function types

It's often useful to be able to define a function type, for use in structs
or higher-order functions:

```sylva
fntype int_stringer(i: int): str

fn stringify_ints(func: int_stringer, ints: [int])
```

But it's even more useful to use these alongside type parameters:

```sylva
fntype (object_type) serializer(i: object_type): str
fntype (object_type) deserializer(s: str): object_type
alias serializer_u8: serializer(u8)
alias deserializer_u8: deserializer(u8)
```
