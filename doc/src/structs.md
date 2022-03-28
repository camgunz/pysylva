# Structs

Structs work as you'd expect:

```sylva
struct Person {
  name: str,
  age: u8,
}
```

Fields must be specified when creating a struct:

```sylva
struct Person {
  name: str,
  age: u8,
}

fn main() {
  var joe_biden: Person{name: "Joe Biden", age: 78u8}
  var charlie_gunyon: Person{name: "Charlie Gunyon", age: 38u8}
}
```

Structs can have default values, which allows us to skip specifying them:

```sylva
struct Person {
  name: str("")
  age: u8(0)
}

fn main() {
  var person: Person{}
}
```

In most ways Sylva is structurally typed, meaning that if different datatypes
have the same structure they can be used in the same contexts, even if they
have different names. This is where struct literals can be useful:

```sylva
mod main

req sys

struct Person {
  name: str,
  age: u8
}

struct Pet {
  name: str,
  age: u8
}

fn say_greeting(greeter: &{name: str, age: u8}) {
  sys.echo("Yo, I'm {greeter.name}!")
}

fn main() {
  var joe_biden: Person{name: "Joe Biden", age: 78u8}
  var zuzu: Animal{name: "Zuzu", age: 2u8}

  say_greeting(&joe_biden)
  zuzu.say_greeting()
}

```

## Parameterized structs (generic data types)

Type parameters can be passed to struct and variant declarations:

```sylva
struct Person(age_type) {
  name: str
  age: age_type
}
```
