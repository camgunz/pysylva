# Variants

Variants allow you to define a datatype that has varying shapes.

```sylva
req sys

range Age(0u8c, 250u8c) {
  range Child(0u8c, 17u8c)
  range Adult(18u8c, 250u8c)
}

struct Person {
  variant Child {
    name: str
    age: Age.Child
  }
  variant Adult {
    name: str
    age: Age.Adult
  }
}

fn make_person(name: str, age: Age): *Person {
  match (age) {
    case (Child) {
      return *Child{name: name, age: age}
    }
    case (Adult) {
      return *Adult{name: name, age: age}
    }
  }
}

fn greet(person: &Person, name: str): str {
  match (person) {
    case (Child) {
      return "Yo {name}, I'm {person.name}."
    }
    case (Adult) {
      return "Good day {name}, I'm {person.name}."
    }
  }
}
```

Prefer variants to interfaces; typechecking with `match` is more descriptive,
declarative, explicit, and local.
