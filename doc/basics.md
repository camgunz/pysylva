# Basics

_accessible, readable, that compiles quickly, is stable and has a natural way
to do async operations_

Sylva should seem familiar to anyone experienced with mainstream programming
languages:

```sylva
fn main() {
  echo("Hello, world!");
}
```

Something a little more engineered:

```sylva
requirement sys
requirement random

range PersonAge(0u8c, 250u8c) {
  range ChildAge(0u8c, 17u8c)
  range AdultAge(18u8c, 250u8c)
}

variant Person(name: str) {
  struct Child {
    age: ChildAge
  }
  struct Adult {
    age: AdultAge
  }
}

fn make_person(name: str, age: PersonAge): *Person {
  match(age) {
    case(ChildAge) {
      return Person.Child{name: name, age: age}
    }
    case(PersonAge) {
      return Person.Adult{name: name, age: age}
    }
  }
}

fn greet(person: &Person, name: str): str {
  match(person) {
    case(Person.Child) {
      return("Yo {name}, I'm {person.name}.")
    }
    case(Person.Adult) {
      return("Good day {name}, I'm {person.name}.")
    }
  }
}

fn perform_greeting(person: &Person, greetee_name: str): str {
  sys.echo(person.greet(greetee_name))
  return("{person.name} successfully greeted {greetee_name}")
}

fn print_usage() {
  sys.echo("Usage: greet [ greeter_name1 ] [ greeter_name2 ] [ greetee_name ]")
}

fn main() {
  with(greeter_name1: sys.argv[1],
       greeter_name2: sys.argv[2],
       greetee_name:  sys.argv[3]) {
    val greeters: [
      make_person(greeter_name1, random.random_range(PersonAge))
      make_person(greeter_name2, random.random_range(PersonAge))
    ]
    val results: [
      greeters -> fn(greeter: &person) {
        return(person.perform_greeting(greetee_name))
      }
    ]

    for(n, result: results) {
      sys.echo("Result {n}: {result}")
    }
  }
  else {
    print_usage()
  }
}
```
