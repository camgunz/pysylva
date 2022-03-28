# Aliases

Aliases simply map one identiifer to another:

```sylva
struct Person {
  name: str,
  age: dec,
}

alias Astronaut: Person
```

They are particularly useful for long import paths:

```sylva
req org.apache.commons.collections4.comparators

alias comparators: org.apache.commons.collections4.comparators
```
