# Variants

Variants allow you to define a datatype that has varying shapes.

```sylva
req sys

variant Age {
  Child: 0u8..17u8,
  Adult: 18u8..250u8,
}

variant Person {
  Child: {
    name: str,
    age: Age.Child,
  },
  Adult: {
    name: str,
    age: Age.Adult,
  }
}

fn make_person(name: str, age: Age): *Person {
  match (age) {
    case (child_age: Child) {
      return *Person.Child{name: name, age: child_age}
    }
    case (adult_age: Adult) {
      return *Person.Adult{name: name, age: adult_age}
    }
  }
}

fn greet(person: &Person, name: str): str {
  match (person) {
    case (c: Child) {
      return "Yo {name}, I'm {c.name}."
    }
    case (a: Adult) {
      return "Good day {name}, I'm {a.name}."
    }
  }
}
```

## Matching

Dealing with a variant's different incarnations requires the `match` statement.
`match` is much like `switch`: it comprises a scoped code block for each
possible value. The core difference is that its code blocks are defined per
variation, rather than per value.

```sylva
req sys

variant TrafficLight {
  Red: {
    flashing: bool(true),
  },
  Yellow: {
    timeout: float(+0f32),
  },
  Green: {
    whatever: uint(1u),
  }
}

fn main() {
  let tl: TrafficLight.Red{}

  match (tl) {
    case (red: Red) {
      sys.echo("Current flashing status: {red.flashing}.")
    }
    case (yellow: Yellow) {
      sys.echo("You have {yellow.timeout}s to make it!")
    }
    case (green: Green) {
      sys.echo("Anything goes ({green.whatever})....")
    }
  }
}
```
