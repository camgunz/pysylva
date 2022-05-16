# Aliases and constants

Aliases create a map between an identifier and another identifier or type parameter.

```sylva
req org.apache.commons.collections4.comparators

alias comparators: org.apache.commons.collections4.comparators

struct Person {
  name: str,
  age: u8,
}

alias Astronaut: Person

struct TypeBox(boxed_type) {
  contents: boxed_type
}

alias UintBox: TypeBox(uint)
```

To define a constant value, use `const`:

```sylva
const PLATFORM: "Linux"
```
