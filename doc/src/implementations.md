# Implementations

Implementations allow the programmer to define a set of functionality for a
specific shape of data. Any type can have implementations.

## Basic implementations

In their most basic form, implementations can add functionality to a type's
instances.

```sylva
req sys

struct Person {
  name: str
  age: u8
}

impl Person {
  fn say_hey(self: &Person) {
    sys.echo("Hey, I'm {self.name}")
  }
}
```

Implementations have access to their type's type parameters:

```sylva
req sys

variant IndexResult(element_type) {
  OK: &element_type
  Fail: str("No element at index")
}

struct Slots(element_type) {
  first: element_type,
  second: element_type,
  third: element_type
}

impl Slots {
  fn get_first(self: &Slots): &Slots.type_params["element_type"] {
    return &slots.first
  }
}

fn main() {
  let treemoji = Slots(rune){
    first: '🌲',
    second: '🌴',
    third: '🌳',
  }

  sys.echo("First tree: {treemoji.get_first()}")
}
```

Implementations are also used to implement interfaces for types:

```sylva
req sys

iface Nameable {
  fn get_name_ref(self: &Nameable): &String
  fn set_name(self: &Nameable, new_name: *String)
}

struct Person {
  name: *str,
  age: u8
}

impl Nameable(Person) {
  fn get_name_ref(self: &Person): &String {
    return self.name
  }

  fn set_name(self: &Nameable, new_name: *String) {
    self.name = *new_name
  }
}
```
