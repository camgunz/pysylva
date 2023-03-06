# Aliases and constants

Aliases create a map between an identifier and another identifier or type parameter.

```sylva
req comparators: org.apache.commons.collections4.comparators

struct Person {
  name: str,
  age: u8,
}

typedef Astronaut: Person

struct TypeBox {
  contents: $boxed_type
}

typedef UintBox: TypeBox($boxed_type: uint)
```

To define a constant value, use `const`:

```sylva
const PLATFORM: "Linux"
```
